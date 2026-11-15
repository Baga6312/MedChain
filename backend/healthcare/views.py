from django.db import transaction
from django.db.models import Q
from django.utils import timezone
from rest_framework import permissions, status, viewsets
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response

from .generics.mixins import StrictCrudMixin
from .models import (
    Appointment,
    Doctor,
    MedicalRecord,
    Patient,
    TreatmentEpisode,
    TreatmentEvent,
    TreatmentPhase,
    UserProfile,
)
from .serializers import (
    AppointmentSerializer,
    DoctorSerializer,
    MedicalRecordSerializer,
    PatientSerializer,
    TreatmentEventSerializer,
    TreatmentPhaseSerializer,
)


def _bad(detail):
    return Response({"detail": detail}, status=status.HTTP_400_BAD_REQUEST)


def _is_admin(user):
    return user.is_staff or user.is_superuser or (
        hasattr(user, "profile") and user.profile.role == UserProfile.Role.ADMIN
    )


class RoleFilteredMixin:
    def _admin_only_write(self):
        if not _is_admin(self.request.user):
            return Response(
                {"detail": "Only administrators can modify this resource."},
                status=status.HTTP_403_FORBIDDEN,
            )

    def create(self, request, *args, **kwargs):
        denied = self._admin_only_write()
        if denied:
            return denied
        return super().create(request, *args, **kwargs)

    def update(self, request, *args, **kwargs):
        denied = self._admin_only_write()
        if denied:
            return denied
        return super().update(request, *args, **kwargs)

    def partial_update(self, request, *args, **kwargs):
        denied = self._admin_only_write()
        if denied:
            return denied
        return super().partial_update(request, *args, **kwargs)

    def destroy(self, request, *args, **kwargs):
        denied = self._admin_only_write()
        if denied:
            return denied
        return super().destroy(request, *args, **kwargs)

    def get_queryset(self):
        queryset = super().get_queryset()
        user = self.request.user
        if _is_admin(user):
            return queryset
        return queryset.none()


class DoctorViewSet(RoleFilteredMixin, StrictCrudMixin, viewsets.ModelViewSet):
    queryset = Doctor.objects.all()
    serializer_class = DoctorSerializer

    not_found_message = "Doctor not found."
    deleted_message = "Doctor has been deleted"
    updated_message = "Doctor updated."
    created_message = None  # return serialized object

    def get_queryset(self):
        if _is_admin(self.request.user):
            return self.queryset
        patient = Patient.objects.filter(user=self.request.user).first()
        doctor = Doctor.objects.filter(user=self.request.user).first()
        if patient:
            return self.queryset
        if doctor:
            return self.queryset.filter(pk=doctor.pk)
        return self.queryset.none()

    def validate_create(self, serializer):
        if Doctor.objects.filter(name=serializer.validated_data["name"]).exists():
            return _bad("A doctor with this name already exists.")

    def validate_update(self, serializer, instance):
        d = serializer.validated_data
        if Doctor.objects.filter(name=d["name"]).exclude(pk=instance.pk).exists():
            return _bad("Another doctor already has this name.")


class PatientViewSet(RoleFilteredMixin, StrictCrudMixin, viewsets.ModelViewSet):
    queryset = Patient.objects.all()
    serializer_class = PatientSerializer

    not_found_message = "Patient not found."
    deleted_message = "patient has been deleted"
    updated_message = "Patient updated."
    created_message = "Patient has been created successfully."

    def get_queryset(self):
        if _is_admin(self.request.user):
            return self.queryset
        patient = Patient.objects.filter(user=self.request.user).first()
        doctor = Doctor.objects.filter(user=self.request.user).first()
        if patient:
            return self.queryset.filter(pk=patient.pk)
        if doctor:
            return self.queryset.filter(treatment_episodes__doctor=doctor).distinct()
        return self.queryset.none()

    def validate_create(self, serializer):
        d = serializer.validated_data
        if Patient.objects.filter(Q(name=d["name"]) | Q(phone=d["phone"])).exists():
            return _bad("A patient with this name or phone already exists.")

    def validate_update(self, serializer, instance):
        d = serializer.validated_data
        if Patient.objects.filter(
            Q(name=d["name"]) | Q(phone=d["phone"])
        ).exclude(pk=instance.pk).exists():
            return _bad("Another patient already has this name or phone.")


class AppointmentViewSet(RoleFilteredMixin, StrictCrudMixin, viewsets.ModelViewSet):
    """Business rules live in AppointmentSerializer.validate()."""

    queryset = Appointment.objects.all()
    serializer_class = AppointmentSerializer
    http_method_names = ["get", "post", "put", "delete"]

    not_found_message = "Appointment not found."
    deleted_message = None  # 204 No Content
    updated_message = "Appointment updated."
    created_message = "Appointment created."

    def get_queryset(self):
        if _is_admin(self.request.user):
            return self.queryset
        patient = Patient.objects.filter(user=self.request.user).first()
        doctor = Doctor.objects.filter(user=self.request.user).first()
        if patient:
            return self.queryset.filter(patient=patient)
        if doctor:
            return self.queryset.filter(treatment_episode__doctor=doctor)
        return self.queryset.none()


class MedicalRecordViewSet(RoleFilteredMixin, StrictCrudMixin, viewsets.ModelViewSet):
    queryset = MedicalRecord.objects.all()
    serializer_class = MedicalRecordSerializer

    not_found_message = "Medical record not found."
    deleted_message = "Medical record has been deleted"
    updated_message = "Medical record updated."
    created_message = None  # return serialized object

    def get_queryset(self):
        if _is_admin(self.request.user):
            return self.queryset
        patient = Patient.objects.filter(user=self.request.user).first()
        doctor = Doctor.objects.filter(user=self.request.user).first()
        if patient:
            return self.queryset.filter(patient=patient)
        if doctor:
            return self.queryset.filter(treatment_episode__doctor=doctor)
        return self.queryset.none()


class TreatmentEpisodeViewSet(RoleFilteredMixin, StrictCrudMixin, viewsets.ModelViewSet):
    queryset = TreatmentEpisode.objects.select_related("patient", "doctor").all()
    serializer_class = None
    http_method_names = ["get", "post", "patch"]

    def get_queryset(self):
        queryset = self.queryset
        user = self.request.user
        if _is_admin(user):
            return queryset
        profile = getattr(user, "profile", None)
        if profile is None:
            return queryset.none()
        if profile.role == UserProfile.Role.PATIENT:
            patient = Patient.objects.filter(user=user).first()
            return queryset.filter(patient=patient) if patient else queryset.none()
        if profile.role == UserProfile.Role.DOCTOR:
            doctor = Doctor.objects.filter(user=user).first()
            return queryset.filter(doctor=doctor) if doctor else queryset.none()
        return queryset.none()

    def list(self, request, *args, **kwargs):
        rows = self.get_queryset()
        return Response(_episode_data(rows))

    def retrieve(self, request, *args, **kwargs):
        return Response(_episode_data([self.get_object()])[0])

    def create(self, request, *args, **kwargs):
        if getattr(request.user, "profile", None).role != UserProfile.Role.PATIENT:
            return _bad("Only patients can request a treatment.")
        patient = Patient.objects.filter(user=request.user).first()
        doctor = Doctor.objects.filter(pk=request.data.get("doctor")).first()
        if not patient or not doctor:
            return _bad("A valid patient and doctor are required.")
        episode = TreatmentEpisode.objects.create(
            patient=patient,
            doctor=doctor,
            reason=str(request.data.get("reason", "")).strip(),
            notes=str(request.data.get("notes", "")).strip(),
        )
        return Response(_episode_data([episode])[0], status=status.HTTP_201_CREATED)

    def partial_update(self, request, *args, **kwargs):
        episode = self.get_object()
        role = getattr(request.user, "profile", None).role
        new_status = request.data.get("status")
        if new_status not in {
            TreatmentEpisode.Status.ACTIVE,
            TreatmentEpisode.Status.ABANDONED,
            TreatmentEpisode.Status.COMPLETED,
        }:
            return _bad("A valid treatment status is required.")
        if role == UserProfile.Role.DOCTOR:
            if new_status == TreatmentEpisode.Status.ACTIVE and episode.status != TreatmentEpisode.Status.REQUESTED:
                return _bad("Only requested treatments can be activated.")
            if new_status == TreatmentEpisode.Status.COMPLETED and episode.status != TreatmentEpisode.Status.ACTIVE:
                return _bad("Only active treatments can be completed.")
        elif role == UserProfile.Role.PATIENT:
            if new_status != TreatmentEpisode.Status.ABANDONED:
                return _bad("Patients can only abandon a treatment.")
        elif not _is_admin(request.user):
            return _bad("You cannot change this treatment.")

        episode.status = new_status
        now = timezone.now()
        if new_status == TreatmentEpisode.Status.ACTIVE:
            episode.started_at = now
        elif new_status == TreatmentEpisode.Status.ABANDONED:
            episode.abandoned_at = now
        elif new_status == TreatmentEpisode.Status.COMPLETED:
            episode.completed_at = now
        episode.save()
        return Response(_episode_data([episode])[0])


def _episode_data(rows):
    return [
        {
            "id": row.id,
            "patient": row.patient_id,
            "patient_name": row.patient.name,
            "doctor": row.doctor_id,
            "doctor_name": row.doctor.name,
            "status": row.status,
            "reason": row.reason,
            "notes": row.notes,
            "started_at": row.started_at,
            "abandoned_at": row.abandoned_at,
            "completed_at": row.completed_at,
            "created_at": row.created_at,
        }
        for row in rows
    ]


def _timeline_episode(user, episode_id):
    queryset = TreatmentEpisode.objects.select_related("patient", "doctor")
    if _is_admin(user):
        return queryset.filter(pk=episode_id).first()
    profile = getattr(user, "profile", None)
    if profile is None:
        return None
    if profile.role == UserProfile.Role.PATIENT:
        return queryset.filter(pk=episode_id, patient__user=user).first()
    if profile.role == UserProfile.Role.DOCTOR:
        return queryset.filter(pk=episode_id, doctor__user=user).first()
    return None


def _phase_data(phase):
    return TreatmentPhaseSerializer(phase).data


def _event_data(event):
    return TreatmentEventSerializer(event).data


@api_view(["GET"])
@permission_classes([permissions.IsAuthenticated])
def treatment_timeline(request, episode_id):
    episode = _timeline_episode(request.user, episode_id)
    if episode is None:
        return Response({"detail": "Treatment episode not found."}, status=status.HTTP_404_NOT_FOUND)
    phases = episode.phases.all()
    events = episode.events.select_related("author").all()
    return Response({
        "treatment_episode": episode.id,
        "phases": [_phase_data(phase) for phase in phases],
        "events": [_event_data(event) for event in events],
    })


@api_view(["POST"])
@permission_classes([permissions.IsAuthenticated])
def treatment_phase_list(request, episode_id):
    episode = _timeline_episode(request.user, episode_id)
    if episode is None:
        return Response({"detail": "Treatment episode not found."}, status=status.HTTP_404_NOT_FOUND)
    if not _is_admin(request.user) and getattr(getattr(request.user, "profile", None), "role", None) != UserProfile.Role.DOCTOR:
        return Response({"detail": "Only doctors can create treatment phases."}, status=status.HTTP_403_FORBIDDEN)

    next_sequence = (episode.phases.order_by("-sequence_number").values_list("sequence_number", flat=True).first() or 0) + 1
    serializer = TreatmentPhaseSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    phase = serializer.save(treatment_episode=episode, sequence_number=next_sequence)
    return Response(_phase_data(phase), status=status.HTTP_201_CREATED)

@api_view(["PATCH"])
@permission_classes([permissions.IsAuthenticated])
def treatment_phase_detail(request, episode_id, phase_id):
    episode = _timeline_episode(request.user, episode_id)
    if episode is None:
        return Response({"detail": "Treatment episode not found."}, status=status.HTTP_404_NOT_FOUND)
    if not _is_admin(request.user) and getattr(getattr(request.user, "profile", None), "role", None) != UserProfile.Role.DOCTOR:
        return Response({"detail": "Only doctors can update treatment phases."}, status=status.HTTP_403_FORBIDDEN)
    phase = episode.phases.filter(pk=phase_id).first()
    if phase is None:
        return Response({"detail": "Treatment phase not found."}, status=status.HTTP_404_NOT_FOUND)

    serializer = TreatmentPhaseSerializer(phase, data=request.data, partial=True)
    serializer.is_valid(raise_exception=True)
    old_status = phase.status
    new_status = serializer.validated_data.get("status", phase.status)
    failure_reason = serializer.validated_data.get("failure_reason", phase.failure_reason)
    if new_status == TreatmentPhase.Status.FAILED and not failure_reason.strip():
        return Response(
            {"failure_reason": "A reason is required when a phase fails."},
            status=status.HTTP_400_BAD_REQUEST,
        )
    now = timezone.now()
    with transaction.atomic():
        phase = serializer.save(
            started_at=now if new_status == TreatmentPhase.Status.ACTIVE and phase.started_at is None else phase.started_at,
            completed_at=now if new_status in {TreatmentPhase.Status.COMPLETED, TreatmentPhase.Status.FAILED} else phase.completed_at,
        )
        if new_status != old_status and new_status in {
            TreatmentPhase.Status.FAILED,
            TreatmentPhase.Status.COMPLETED,
        }:
            failed = new_status == TreatmentPhase.Status.FAILED
            TreatmentEvent.objects.create(
                treatment_episode=episode,
                treatment_phase=phase,
                author=request.user,
                event_type=(
                    TreatmentEvent.EventType.PHASE_FAILED
                    if failed
                    else TreatmentEvent.EventType.PHASE_COMPLETED
                ),
                title=f"Phase {'failed' if failed else 'completed'}: {phase.name}",
                description=(phase.failure_reason if failed else phase.summary) or "-",
            )
    return Response(_phase_data(phase))

@api_view(["POST"])
@permission_classes([permissions.IsAuthenticated])
def treatment_event_list(request, episode_id):
    episode = _timeline_episode(request.user, episode_id)
    if episode is None:
        return Response({"detail": "Treatment episode not found."}, status=status.HTTP_404_NOT_FOUND)
    role = getattr(getattr(request.user, "profile", None), "role", None)
    if not _is_admin(request.user) and role not in {UserProfile.Role.DOCTOR, UserProfile.Role.PATIENT}:
        return Response({"detail": "Only patients and doctors can add timeline events."}, status=status.HTTP_403_FORBIDDEN)

    serializer = TreatmentEventSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    event_type = serializer.validated_data.get("event_type")
    if event_type in {
        TreatmentEvent.EventType.PHASE_FAILED,
        TreatmentEvent.EventType.PHASE_COMPLETED,
    }:
        return Response(
            {"detail": "This event type is system-generated."},
            status=status.HTTP_400_BAD_REQUEST,
        )
    if event_type == TreatmentEvent.EventType.RESULT and not serializer.validated_data.get("outcome"):
        return Response(
            {"outcome": "An outcome is required for result events."},
            status=status.HTTP_400_BAD_REQUEST,
        )

    if role == UserProfile.Role.PATIENT and event_type not in {
        TreatmentEvent.EventType.NOTE,
        TreatmentEvent.EventType.RESULT,
    }:
        return Response(
            {"detail": "Patients can only add notes or results."},
            status=status.HTTP_403_FORBIDDEN,
        )
    phase = serializer.validated_data.get("treatment_phase")
    if phase and phase.treatment_episode_id != episode.id:
        return Response({"detail": "The phase must belong to this treatment episode."}, status=status.HTTP_400_BAD_REQUEST)
    appointment = serializer.validated_data.get("appointment")
    if appointment and appointment.treatment_episode_id != episode.id:
        return Response({"detail": "The appointment must belong to this treatment episode."}, status=status.HTTP_400_BAD_REQUEST)
    event = serializer.save(treatment_episode=episode, author=request.user)
    return Response(_event_data(event), status=status.HTTP_201_CREATED)