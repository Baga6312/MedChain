from django.contrib.auth import authenticate
from django.shortcuts import get_object_or_404
from django.utils import timezone
from rest_framework import status, viewsets
from rest_framework.authtoken.models import Token
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import AccessPermission, AuditLog, Appointment, Doctor, MedicalRecord, Patient, UserProfile
from .serializers import AuditLogSerializer, AppointmentSerializer, DoctorSerializer, MedicalRecordSerializer, PatientSerializer


def role(user):
    if user.is_superuser:
        return UserProfile.Role.ADMIN
    return getattr(getattr(user, "profile", None), "role", None)


def patient_for(user):
    return getattr(user, "patient_profile", None)


def doctor_for(user):
    return getattr(user, "doctor_profile", None)


def allowed_patient_ids(user):
    doctor = doctor_for(user)
    if not doctor:
        return Patient.objects.none()
    return Patient.objects.filter(access_permissions__doctor=doctor, access_permissions__revoked_at__isnull=True)


def can_access_patient(user, patient):
    current_role = role(user)
    if current_role == UserProfile.Role.ADMIN:
        return True
    if current_role == UserProfile.Role.PATIENT:
        return patient_for(user) == patient
    if current_role == UserProfile.Role.DOCTOR:
        return AccessPermission.objects.filter(patient=patient, doctor=doctor_for(user), revoked_at__isnull=True).exists()
    return False


def audit(user, action, patient=None, details=None):
    return AuditLog.objects.create(actor=user, action=action, patient=patient, details=details or {})


class LoginView(ObtainAuthToken):
    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        response = super().post(request, *args, **kwargs)
        if response.status_code == status.HTTP_200_OK:
            user = authenticate(username=request.data.get("username"), password=request.data.get("password"))
            if user:
                audit(user, AuditLog.Action.LOGIN)
                response.data["role"] = role(user)
                response.data["username"] = user.username
        return response


class DoctorViewSet(viewsets.ModelViewSet):
    queryset = Doctor.objects.all()
    serializer_class = DoctorSerializer

    def get_queryset(self):
        current_role = role(self.request.user)
        if current_role == UserProfile.Role.ADMIN:
            return Doctor.objects.all()
        if current_role == UserProfile.Role.DOCTOR:
            return Doctor.objects.filter(pk=getattr(doctor_for(self.request.user), "pk", None))
        if current_role == UserProfile.Role.PATIENT:
            return Doctor.objects.filter(patient_permissions__patient=patient_for(self.request.user), patient_permissions__revoked_at__isnull=True)
        return Doctor.objects.none()


class PatientViewSet(viewsets.ModelViewSet):
    queryset = Patient.objects.all()
    serializer_class = PatientSerializer

    def get_queryset(self):
        current_role = role(self.request.user)
        if current_role == UserProfile.Role.ADMIN:
            return Patient.objects.all()
        if current_role == UserProfile.Role.PATIENT:
            return Patient.objects.filter(pk=getattr(patient_for(self.request.user), "pk", None))
        if current_role == UserProfile.Role.DOCTOR:
            return allowed_patient_ids(self.request.user)
        return Patient.objects.none()

    def perform_update(self, serializer):
        serializer.save()


class AppointmentViewSet(viewsets.ModelViewSet):
    queryset = Appointment.objects.all()
    serializer_class = AppointmentSerializer

    def get_queryset(self):
        current_role = role(self.request.user)
        if current_role == UserProfile.Role.ADMIN:
            return Appointment.objects.all()
        if current_role == UserProfile.Role.PATIENT:
            return Appointment.objects.filter(patient=patient_for(self.request.user))
        if current_role == UserProfile.Role.DOCTOR:
            return Appointment.objects.filter(doctor=doctor_for(self.request.user), patient__in=allowed_patient_ids(self.request.user))
        return Appointment.objects.none()


class MedicalRecordViewSet(viewsets.ModelViewSet):
    queryset = MedicalRecord.objects.select_related("patient", "created_by")
    serializer_class = MedicalRecordSerializer

    def get_queryset(self):
        current_role = role(self.request.user)
        if current_role == UserProfile.Role.ADMIN:
            return self.queryset
        if current_role == UserProfile.Role.PATIENT:
            return self.queryset.filter(patient=patient_for(self.request.user))
        if current_role == UserProfile.Role.DOCTOR:
            return self.queryset.filter(patient__in=allowed_patient_ids(self.request.user))
        return self.queryset.none()

    def retrieve(self, request, *args, **kwargs):
        record = get_object_or_404(self.queryset, pk=kwargs["pk"])
        if not can_access_patient(request.user, record.patient):
            audit(request.user, AuditLog.Action.ACCESS_DENIED, record.patient, {"record_id": record.pk})
            return Response({"detail": "Accès refusé à ce dossier médical."}, status=status.HTTP_403_FORBIDDEN)
        audit(request.user, AuditLog.Action.VIEW_RECORD, record.patient, {"record_id": record.pk})
        return Response(self.get_serializer(record).data)

    def perform_create(self, serializer):
        patient = serializer.validated_data["patient"]
        if not can_access_patient(self.request.user, patient):
            audit(self.request.user, AuditLog.Action.ACCESS_DENIED, patient)
            from rest_framework.exceptions import PermissionDenied
            raise PermissionDenied("Vous ne pouvez pas créer une donnée pour ce patient.")
        serializer.save(created_by=self.request.user)


class GrantAccessView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, patient_id):
        patient = get_object_or_404(Patient, pk=patient_id)
        if role(request.user) != UserProfile.Role.PATIENT or patient_for(request.user) != patient:
            return Response({"detail": "Seul le patient concerné peut autoriser un médecin."}, status=status.HTTP_403_FORBIDDEN)
        doctor = get_object_or_404(Doctor, pk=request.data.get("doctor_id"))
        permission, _ = AccessPermission.objects.get_or_create(patient=patient, doctor=doctor)
        permission.revoked_at = None
        permission.save(update_fields=["revoked_at"])
        audit(request.user, AuditLog.Action.GRANT_ACCESS, patient, {"doctor_id": doctor.pk})
        return Response({"detail": "Accès médecin autorisé.", "doctor_id": doctor.pk}, status=status.HTTP_200_OK)


class RevokeAccessView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, patient_id, doctor_id):
        patient = get_object_or_404(Patient, pk=patient_id)
        if role(request.user) != UserProfile.Role.PATIENT or patient_for(request.user) != patient:
            return Response({"detail": "Seul le patient concerné peut révoquer un médecin."}, status=status.HTTP_403_FORBIDDEN)
        permission = get_object_or_404(AccessPermission, patient=patient, doctor_id=doctor_id)
        permission.revoked_at = timezone.now()
        permission.save(update_fields=["revoked_at"])
        audit(request.user, AuditLog.Action.REVOKE_ACCESS, patient, {"doctor_id": doctor_id})
        return Response({"detail": "Accès médecin révoqué."}, status=status.HTTP_200_OK)


class AuditLogViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = AuditLogSerializer

    def get_queryset(self):
        current_role = role(self.request.user)
        if current_role == UserProfile.Role.ADMIN:
            return AuditLog.objects.select_related("actor", "patient").all()
        if current_role == UserProfile.Role.PATIENT:
            return AuditLog.objects.filter(patient=patient_for(self.request.user))
        if current_role == UserProfile.Role.DOCTOR:
            return AuditLog.objects.filter(actor=self.request.user)
        return AuditLog.objects.none()
