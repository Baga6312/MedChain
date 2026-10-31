from django.db.models import Q
from django.utils import timezone
from rest_framework import status, viewsets
from rest_framework.response import Response

from .generics.mixins import StrictCrudMixin
from .models import Appointment, Doctor, MedicalRecord, Patient, TreatmentEpisode, UserProfile
from .serializers import (
    AppointmentSerializer,
    DoctorSerializer,
    MedicalRecordSerializer,
    PatientSerializer,
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