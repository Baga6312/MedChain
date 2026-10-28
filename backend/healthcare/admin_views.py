from datetime import timedelta

from django.contrib.auth import get_user_model
from django.db import transaction
from django.db.models import Q
from django.utils import timezone
from rest_framework import permissions, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response

from .models import (
    Appointment,
    AuditLog,
    Doctor,
    MedicalRecord,
    Patient,
    SecurityAlert,
    UserProfile,
)


def is_admin(user):
    return user.is_staff or user.is_superuser or (
        hasattr(user, "profile") and user.profile.role == UserProfile.Role.ADMIN
    )


class IsAdmin(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and is_admin(request.user)


def audit(request, action, detail="", target_type="", target_id="", result=AuditLog.Result.SUCCESS):
    AuditLog.objects.create(
        actor=request.user,
        action=action,
        detail=detail,
        target_type=target_type,
        target_id=str(target_id),
        result=result,
        ip_address=request.META.get("REMOTE_ADDR"),
    )


def user_data(user):
    profile = getattr(user, "profile", None)
    return {
        "id": user.id,
        "email": user.email or user.username,
        "first_name": user.first_name,
        "last_name": user.last_name,
        "role": profile.role if profile else ("admin" if user.is_staff else "patient"),
        "is_active": user.is_active,
        "is_staff": user.is_staff,
        "last_login": user.last_login,
        "date_joined": user.date_joined,
    }


def sync_role_record(user, role):
    display_name = f"{user.first_name} {user.last_name}".strip() or user.email or user.username
    if role == UserProfile.Role.DOCTOR:
        Patient.objects.filter(user=user).delete()
        doctor, _ = Doctor.objects.get_or_create(
            user=user,
            defaults={"name": display_name, "specialty": "À définir"},
        )
        return doctor
    if role == UserProfile.Role.PATIENT:
        Doctor.objects.filter(user=user).delete()
        patient, _ = Patient.objects.get_or_create(
            user=user,
            defaults={"name": display_name, "phone": getattr(user.profile, "phone", "")},
        )
        return patient
    Doctor.objects.filter(user=user).delete()
    Patient.objects.filter(user=user).delete()
    return None


@api_view(["GET"])
@permission_classes([permissions.IsAuthenticated])
def current_user(request):
    return Response(user_data(request.user))


@api_view(["GET"])
@permission_classes([IsAdmin])
def dashboard(request):
    audit(request, "admin_dashboard_viewed")
    User = get_user_model()
    month_ago = timezone.now() - timedelta(days=30)
    return Response({
        "users": User.objects.count(),
        "active_users": User.objects.filter(is_active=True).count(),
        "new_users": User.objects.filter(date_joined__gte=month_ago).count(),
        "pending_users": User.objects.filter(is_active=False).count(),
        "role_patients": UserProfile.objects.filter(role=UserProfile.Role.PATIENT).count(),
        "role_doctors": UserProfile.objects.filter(role=UserProfile.Role.DOCTOR).count(),
        "patients": Patient.objects.count(),
        "doctors": Doctor.objects.count(),
        "appointments": Appointment.objects.count(),
        "pending_appointments": Appointment.objects.filter(
            status=Appointment.Status.PENDING
        ).count(),
        "medical_records": MedicalRecord.objects.count(),
        "open_alerts": SecurityAlert.objects.filter(status=SecurityAlert.Status.OPEN).count(),
        "recent_audit_events": AuditLog.objects.count(),
    })


@api_view(["GET", "POST", "PATCH"])
@permission_classes([IsAdmin])
def users(request):
    User = get_user_model()
    if request.method == "GET":
        query = request.query_params.get("q", "").strip()
        rows = User.objects.select_related("profile").order_by("-date_joined")
        if query:
            rows = rows.filter(
                Q(email__icontains=query)
                | Q(username__icontains=query)
                | Q(first_name__icontains=query)
                | Q(last_name__icontains=query)
                | Q(profile__role__icontains=query)
            )
        rows = rows[:100]
        return Response([user_data(user) for user in rows])

    if request.method == "POST":
        email = str(request.data.get("email", "")).strip().lower()
        password = request.data.get("password", "")
        if not email or not password:
            return Response({"detail": "Email and password are required."}, status=400)
        if User.objects.filter(Q(username=email) | Q(email=email)).exists():
            return Response({"detail": "An account with this email already exists."}, status=400)
        user = User(
            username=email,
            email=email,
            first_name=str(request.data.get("first_name", "")).strip(),
            last_name=str(request.data.get("last_name", "")).strip(),
        )
        from django.contrib.auth.password_validation import validate_password
        from django.core.exceptions import ValidationError
        try:
            validate_password(password, user)
        except ValidationError as error:
            return Response({"password": error.messages}, status=400)
        user.set_password(password)
        user.save()
        profile = UserProfile.objects.create(
            user=user,
            role=UserProfile.Role.PATIENT,
            phone=str(request.data.get("phone", "")).strip(),
            address=str(request.data.get("address", "")).strip(),
        )
        sync_role_record(user, profile.role)
        audit(request, "admin_user_created", "Default role: patient.", "user", user.pk)
        return Response(user_data(user), status=status.HTTP_201_CREATED)

    user_id = request.data.get("user_id")
    target = User.objects.filter(pk=user_id).first()
    if target is None:
        return Response({"detail": "User not found."}, status=status.HTTP_404_NOT_FOUND)
    if target.pk == request.user.pk and request.data.get("is_active") is False:
        return Response({"detail": "You cannot deactivate your own account."}, status=400)

    changed = []
    if "is_active" in request.data:
        target.is_active = bool(request.data["is_active"])
        changed.append("status")
    if "role" in request.data:
        role = request.data["role"]
        if role not in UserProfile.Role.values:
            return Response({"detail": "Invalid role."}, status=400)
        with transaction.atomic():
            profile, _ = UserProfile.objects.get_or_create(user=target)
            profile.role = role
            profile.save(update_fields=["role"])
            sync_role_record(target, role)
        changed.append("role")
    target.save(update_fields=["is_active"])
    audit(request, "admin_user_updated", ", ".join(changed), "user", target.pk)
    return Response(user_data(target))


@api_view(["POST"])
@permission_classes([IsAdmin])
def force_logout(request, user_id):
    User = get_user_model()
    target = User.objects.filter(pk=user_id).first()
    if target is None:
        return Response({"detail": "User not found."}, status=404)
    deleted, _ = target.session_tokens.all().delete()
    audit(request, "admin_sessions_revoked", f"{deleted} session(s) revoked.", "user", target.pk)
    return Response({"detail": "User sessions revoked."})


@api_view(["GET"])
@permission_classes([IsAdmin])
def audit_logs(request):
    rows = AuditLog.objects.select_related("actor")[:100]
    return Response([
        {
            "id": row.id,
            "action": row.action,
            "actor": row.actor.email if row.actor else "System",
            "target": f"{row.target_type} #{row.target_id}" if row.target_type else "—",
            "result": row.result,
            "detail": row.detail,
            "created_at": row.created_at,
        }
        for row in rows
    ])


@api_view(["GET", "PATCH"])
@permission_classes([IsAdmin])
def security_alerts(request):
    if request.method == "PATCH":
        alert = SecurityAlert.objects.filter(pk=request.data.get("alert_id")).first()
        if alert is None:
            return Response({"detail": "Alert not found."}, status=404)
        alert.status = SecurityAlert.Status.RESOLVED
        alert.resolved_at = timezone.now()
        alert.resolved_by = request.user
        alert.save(update_fields=["status", "resolved_at", "resolved_by"])
        audit(request, "security_alert_resolved", alert.title, "security_alert", alert.pk)
        return Response({"detail": "Alert resolved."})

    rows = SecurityAlert.objects.select_related("user")[:100]
    return Response([
        {
            "id": row.id,
            "title": row.title,
            "detail": row.detail,
            "severity": row.severity,
            "status": row.status,
            "user": row.user.email if row.user else None,
            "created_at": row.created_at,
        }
        for row in rows
    ])
