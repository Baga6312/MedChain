"""Authorization policy: who is this caller, and what may they touch.

Single source of truth for the role ladder. Every viewset resolves its queryset
and its write guards through these helpers, so the four viewsets cannot drift
apart the way four hand-written copies of the same check did.

Two conventions matter more than anything else in this file:

  * `visible_patient_ids` returns ``None`` for *unrestricted* access and a
    list for a restricted set. An empty list means "restricted to nothing".
    Returning ``None`` by accident would mean "see everything" -- the opposite
    of what a caller with no role should get.
  * ``role_of`` never falls through to a weaker role, and ``is_staff`` is not a
    role. Staff is an admin-console concept and must not confer API access.
"""

from rest_framework import status
from rest_framework.response import Response

from .models import AccessPermission, AuditLog

ADMIN = "ADMIN"
DOCTOR = "DOCTOR"
PATIENT = "PATIENT"


def profile_of(user, attr):
    """Return a reverse one-to-one profile, or None when it is absent.

    The profile FKs are nullable, so the descriptor yields None rather than
    raising -- which means ``hasattr(user, "doctor_profile")`` is True for
    *every* user and would promote the whole table to doctor. Compare to None.
    """
    return getattr(user, attr, None) if (user and user.is_authenticated) else None


def role_of(user):
    """Resolve the caller's role, or None for anonymous / unlinked accounts."""
    if not user or not user.is_authenticated:
        return None
    if user.is_superuser:
        return ADMIN
    if profile_of(user, "doctor_profile") is not None:
        return DOCTOR
    if profile_of(user, "patient_profile") is not None:
        return PATIENT
    return None


def visible_patient_ids(user):
    """Patient ids the caller may read. None means unrestricted (admin only)."""
    role = role_of(user)
    if role == ADMIN:
        return None
    if role == PATIENT:
        patient = profile_of(user, "patient_profile")
        return [patient.pk] if patient is not None else []
    if role == DOCTOR:
        doctor = profile_of(user, "doctor_profile")
        if doctor is None:
            return []
        return list(
            AccessPermission.objects.filter(
                doctor=doctor, revoked_at__isnull=True
            ).values_list("patient_id", flat=True)
        )
    # Anonymous or unlinked account: restricted to nothing, never unrestricted.
    return []


def pk_of(value):
    """Normalize a related field to its id.

    DRF hands back model instances for related fields, not ids, so comparing
    serializer.validated_data["patient"] against a list of ids silently fails
    and every authorized write is rejected.
    """
    return getattr(value, "pk", value)


def can_write_for(user, patient):
    """May the caller write data belonging to this patient?"""
    ids = visible_patient_ids(user)
    if ids is None:  # admin
        return True
    return pk_of(patient) in ids


def forbidden(detail="You do not have permission to perform this action."):
    """403 with a body. Used instead of the 400 helper, which a client cannot
    tell apart from a payload validation error."""
    return Response({"detail": detail}, status=status.HTTP_403_FORBIDDEN)


def require_admin(user):
    """Return a 403 Response unless the caller is a superuser, else None."""
    return None if role_of(user) == ADMIN else forbidden("Administrator role required.")


def audit(user, action, patient=None, details=None):
    """Record one security-relevant event.

    Anonymous callers (failed logins) are stored with a null actor rather than
    dropped: "someone tried to log in as X" is worth keeping even though the
    attempt failed.
    """
    return AuditLog.objects.create(
        actor=user if (user and user.is_authenticated) else None,
        action=action,
        patient=patient,
        details=details or {},
    )