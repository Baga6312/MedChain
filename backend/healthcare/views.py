from django.db.models import Q
from django.shortcuts import get_object_or_404
from django.utils import timezone
from drf_spectacular.utils import OpenApiResponse, extend_schema
from rest_framework import serializers, status, viewsets
from rest_framework.authtoken.models import Token
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.throttling import ScopedRateThrottle
from rest_framework.views import APIView

from .authz import (
    ADMIN,
    DOCTOR,
    PATIENT,
    audit,
    can_write_for,
    forbidden,
    pk_of,
    profile_of,
    require_admin,
    role_of,
    visible_patient_ids,
)
from .generics.mixins import StrictCrudMixin
from .models import AccessPermission, Appointment, AuditLog, Doctor, MedicalRecord, Patient
from .serializers import (
    AccessGrantSerializer,
    AppointmentSerializer,
    DoctorSerializer,
    MedicalRecordSerializer,
    PatientSerializer,
)


def _bad(detail):
    return Response({"detail": detail}, status=status.HTTP_400_BAD_REQUEST)


class DoctorViewSet(StrictCrudMixin, viewsets.ModelViewSet):
    # The class-level queryset stays: drf-spectacular reads it when generating
    # the schema, before get_queryset() is ever called.
    queryset = Doctor.objects.all()
    serializer_class = DoctorSerializer

    not_found_message = "Doctor not found."
    deleted_message = "Doctor has been deleted"
    updated_message = "Doctor updated."
    created_message = None  # return serialized object

    def get_queryset(self):
        role = role_of(self.request.user)
        if role == ADMIN:
            return Doctor.objects.all()
        if role == DOCTOR:
            profile = profile_of(self.request.user, "doctor_profile")
            return Doctor.objects.filter(pk=profile.pk) if profile else Doctor.objects.none()
        if role == PATIENT:
            # A patient sees only the doctors holding an active grant on their
            # own chart, so the list doubles as the grant picker.
            patient = profile_of(self.request.user, "patient_profile")
            if patient is None:
                return Doctor.objects.none()
            return Doctor.objects.filter(
                patient_permissions__patient=patient,
                patient_permissions__revoked_at__isnull=True,
            ).distinct()
        return Doctor.objects.none()

    def validate_create(self, serializer):
        err = require_admin(self.request.user)
        if err:
            return err
        if Doctor.objects.filter(name=serializer.validated_data["name"]).exists():
            return _bad("A doctor with this name already exists.")

    def validate_update(self, serializer, instance):
        err = require_admin(self.request.user)
        if err:
            return err
        d = serializer.validated_data
        if Doctor.objects.filter(name=d["name"]).exclude(pk=instance.pk).exists():
            return _bad("Another doctor already has this name.")

    def validate_destroy(self, request, instance):
        # Admin only. A doctor's appointments are CASCADE, so a patient or a
        # peer doctor deleting one would destroy rows they cannot even see.
        return require_admin(request.user)


class PatientViewSet(StrictCrudMixin, viewsets.ModelViewSet):
    queryset = Patient.objects.all()
    serializer_class = PatientSerializer

    not_found_message = "Patient not found."
    deleted_message = "patient has been deleted"
    updated_message = "Patient updated."
    created_message = "Patient has been created successfully."

    def get_queryset(self):
        role = role_of(self.request.user)
        if role == ADMIN:
            return Patient.objects.all()
        if role == PATIENT:
            profile = profile_of(self.request.user, "patient_profile")
            return Patient.objects.filter(pk=profile.pk) if profile else Patient.objects.none()
        if role == DOCTOR:
            ids = visible_patient_ids(self.request.user)
            return Patient.objects.filter(pk__in=ids) if ids else Patient.objects.none()
        return Patient.objects.none()

    def validate_create(self, serializer):
        err = require_admin(self.request.user)
        if err:
            return err
        d = serializer.validated_data
        if Patient.objects.filter(Q(name=d["name"]) | Q(phone=d["phone"])).exists():
            return _bad("A patient with this name or phone already exists.")

    def validate_update(self, serializer, instance):
        err = require_admin(self.request.user)
        if err:
            return err
        d = serializer.validated_data
        if Patient.objects.filter(
            Q(name=d["name"]) | Q(phone=d["phone"])
        ).exclude(pk=instance.pk).exists():
            return _bad("Another patient already has this name or phone.")

    def validate_destroy(self, request, instance):
        # Admin only. Patient rows cascade to appointments and medical records,
        # so the blast radius of letting a patient delete their own row reaches
        # their doctors' schedules.
        return require_admin(request.user)


class AppointmentViewSet(StrictCrudMixin, viewsets.ModelViewSet):
    """Business rules live in AppointmentSerializer.validate()."""

    queryset = Appointment.objects.all()
    serializer_class = AppointmentSerializer
    http_method_names = ["get", "post", "put", "delete"]

    not_found_message = "Appointment not found."
    deleted_message = None  # 204 No Content
    updated_message = "Appointment updated."
    created_message = "Appointment created."

    def get_queryset(self):
        role = role_of(self.request.user)
        if role == ADMIN:
            return Appointment.objects.all()
        if role == PATIENT:
            ids = visible_patient_ids(self.request.user)
            return Appointment.objects.filter(patient_id__in=ids) if ids else Appointment.objects.none()
        if role == DOCTOR:
            # A doctor sees appointments on granted charts *that are theirs*.
            # Filtering on patient alone would expose appointments between the
            # patient and a different doctor.
            profile = profile_of(self.request.user, "doctor_profile")
            ids = visible_patient_ids(self.request.user)
            if profile is None or not ids:
                return Appointment.objects.none()
            return Appointment.objects.filter(patient_id__in=ids, doctor=profile)
        return Appointment.objects.none()

    def _validate_write(self, serializer):
        """Return a 403 Response if this caller may not write the payload."""
        user = self.request.user
        role = role_of(user)
        patient_id = pk_of(serializer.validated_data.get("patient"))
        doctor_id = pk_of(serializer.validated_data.get("doctor"))
        if role == ADMIN:
            return None
        if role == PATIENT:
            if patient_id not in visible_patient_ids(user):
                return forbidden("You can only manage your own appointments.")
            return None
        if role == DOCTOR:
            profile = profile_of(user, "doctor_profile")
            if profile is None or doctor_id != profile.pk:
                return forbidden("You can only manage your own appointments.")
            if patient_id not in visible_patient_ids(user):
                return forbidden("This patient has not authorized you.")
            return None
        return forbidden()

    def validate_create(self, serializer):
        return self._validate_write(serializer)

    def validate_update(self, serializer, instance):
        err = self._validate_write(serializer)
        if err:
            return err
        new_status = serializer.validated_data.get("status")
        if new_status is not None and new_status != instance.status:
            # Status is the clinical lifecycle of the visit, so it belongs to
            # the clinician running it -- never to the patient.
            user = self.request.user
            profile = profile_of(user, "doctor_profile")
            if role_of(user) != ADMIN and (profile is None or instance.doctor_id != profile.pk):
                return forbidden("Only the assigned doctor or an administrator can change the status.")
        return None

    def validate_destroy(self, request, instance):
        user = request.user
        role = role_of(user)
        if role == ADMIN:
            return None
        if role == PATIENT and instance.patient_id in visible_patient_ids(user):
            return None
        if role == DOCTOR and instance.doctor_id == getattr(
            profile_of(user, "doctor_profile"), "pk", None
        ):
            return None
        return forbidden("You cannot delete this appointment.")


class MedicalRecordViewSet(StrictCrudMixin, viewsets.ModelViewSet):
    queryset = MedicalRecord.objects.all()
    serializer_class = MedicalRecordSerializer

    not_found_message = "Medical record not found."
    deleted_message = "Medical record has been deleted"
    updated_message = "Medical record updated."
    created_message = None  # return serialized object

    def get_queryset(self):
        ids = visible_patient_ids(self.request.user)
        if ids is None:
            return MedicalRecord.objects.select_related("patient", "created_by").all()
        if not ids:
            return MedicalRecord.objects.none()
        return MedicalRecord.objects.select_related("patient", "created_by").filter(
            patient_id__in=ids
        )

    def retrieve(self, request, *args, **kwargs):
        """Return 403 (not 404) when a grant was revoked, and audit the read.

        get_queryset() already drops revoked charts, so a plain lookup would
        404 -- which is indistinguishable from "this id does not exist" and
        leaves the denial unlogged. A doctor who once held the grant already
        knew the chart was there, so confirming the revocation leaks nothing.
        """
        err = self._reject_if_dirty(request)
        if err:
            return err
        instance = self.get_queryset().filter(pk=kwargs["pk"]).first()
        if instance is None:
            return self._revoked_denial(request, kwargs["pk"]) or Response(
                {"detail": self.not_found_message}, status=status.HTTP_404_NOT_FOUND
            )
        audit(request.user, AuditLog.Action.VIEW_RECORD, instance.patient, {"record_id": instance.pk})
        return Response(self.get_serializer(instance).data)

    def _revoked_denial(self, request, pk):
        """403 + audit row if this doctor holds a *revoked* grant on this record."""
        profile = profile_of(request.user, "doctor_profile")
        if role_of(request.user) != DOCTOR or profile is None:
            return None
        record = MedicalRecord.objects.filter(pk=pk).first()
        if record is None:
            return None
        revoked = AccessPermission.objects.filter(
            patient_id=record.patient_id, doctor=profile, revoked_at__isnull=False
        ).exists()
        if not revoked:
            return None
        audit(
            request.user,
            AuditLog.Action.ACCESS_DENIED,
            record.patient,
            {"record_id": record.pk, "reason": "revoked"},
        )
        return forbidden("Your access to this medical record has been revoked.")

    def validate_create(self, serializer):
        if not can_write_for(self.request.user, serializer.validated_data["patient"]):
            return forbidden("You cannot create a record for this patient.")
        return None

    def validate_update(self, serializer, instance):
        # Guards the `patient` field too: without this, a caller who owns one
        # chart could PUT and reassign any record in the table onto their chart.
        if not can_write_for(self.request.user, serializer.validated_data["patient"]):
            return forbidden("You cannot move this record to that patient.")
        return None

    def validate_destroy(self, request, instance):
        # Admin only. Records are the artifact the audit trail is about, and
        # deleting one is not reversible by design.
        return require_admin(request.user)

    def perform_create(self, serializer):
        # The author is taken from the request, never from the payload: the
        # serializer does not expose created_by, but a view that trusted the
        # body here would let any caller forge authorship.
        serializer.save(created_by=self.request.user)


class LoginView(ObtainAuthToken):
    """POST username/password -> auth token plus the caller's resolved role.

    Subclasses ObtainAuthToken rather than re-implementing authentication.
    The credentials are checked exactly once: an earlier version called
    authenticate() again after super().post() had already done it.
    """

    permission_classes = [AllowAny]
    # No authentication on the credential endpoint: a stale token in the header
    # would otherwise 401 before AllowAny ever runs.
    authentication_classes = []
    throttle_classes = [ScopedRateThrottle]
    throttle_scope = "login"

    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data, context={"request": request})
        try:
            serializer.is_valid(raise_exception=True)
        except serializers.ValidationError:
            # Failed logins are the signal for credential stuffing, so they are
            # recorded. Only the attempted username: never the password, and
            # never request.data wholesale.
            audit(None, AuditLog.Action.LOGIN_FAILED, details={"username": request.data.get("username")})
            raise

        user = serializer.validated_data["user"]
        token, _ = Token.objects.get_or_create(user=user)
        audit(user, AuditLog.Action.LOGIN, details={"role": role_of(user)})

        payload = {"token": token.key, "user_id": user.pk, "username": user.username, "role": role_of(user)}
        patient = profile_of(user, "patient_profile")
        if patient is not None:
            payload["patient_id"] = patient.pk
        doctor = profile_of(user, "doctor_profile")
        if doctor is not None:
            payload["doctor_id"] = doctor.pk
        return Response(payload)


@extend_schema(
    request=AccessGrantSerializer,
    responses={200: OpenApiResponse(description="Grant created or reinstated.")},
)
class GrantAccessView(APIView):
    """POST /api/patients/<pk>/permissions/ {"doctor_id": n}

    Patient-only: the grant is the patient's to give, which is why an admin is
    refused here too -- an administrator's implicit access must not become a
    durable share on the patient's behalf.
    """

    permission_classes = [IsAuthenticated]

    def post(self, request, pk):
        patient = get_object_or_404(Patient, pk=pk)
        if role_of(request.user) != PATIENT or patient.pk not in visible_patient_ids(request.user):
            return forbidden("Only the patient concerned can authorize a doctor.")
        # Validated rather than read raw, so a missing or non-integer
        # doctor_id is a 400 field error instead of a silently None lookup.
        serializer = AccessGrantSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        doctor = get_object_or_404(Doctor, pk=serializer.validated_data["doctor_id"])

        # update_or_create, not get_or_create: the (patient, doctor) pair is
        # unique, so re-granting a revoked row must clear revoked_at rather
        # than raise IntegrityError.
        AccessPermission.objects.update_or_create(
            patient=patient, doctor=doctor, defaults={"revoked_at": None}
        )
        audit(request.user, AuditLog.Action.GRANT_ACCESS, patient, {"doctor_id": doctor.pk})
        return Response({"detail": "Access granted.", "doctor_id": doctor.pk})


@extend_schema(request=None, responses={200: OpenApiResponse(description="Grant revoked.")})
class RevokeAccessView(APIView):
    """POST /api/patients/<pk>/permissions/<doctor_pk>/revoke/"""

    permission_classes = [IsAuthenticated]

    def post(self, request, pk, doctor_pk):
        patient = get_object_or_404(Patient, pk=pk)
        if role_of(request.user) != PATIENT or patient.pk not in visible_patient_ids(request.user):
            return forbidden("Only the patient concerned can revoke a doctor.")
        permission = AccessPermission.objects.filter(
            patient=patient, doctor_id=doctor_pk, revoked_at__isnull=True
        ).first()
        if permission is None:
            return Response(
                {"detail": "No active grant for this doctor."}, status=status.HTTP_404_NOT_FOUND
            )

        permission.revoked_at = timezone.now()
        permission.save(update_fields=["revoked_at"])
        audit(request.user, AuditLog.Action.REVOKE_ACCESS, patient, {"doctor_id": doctor_pk})
        return Response({"detail": "Access revoked.", "doctor_id": doctor_pk})