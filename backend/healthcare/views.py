from django.db.models import Q
from rest_framework import status, viewsets
from rest_framework.response import Response

from .generics.mixins import StrictCrudMixin
from .models import Appointment, Doctor, MedicalRecord, Patient
from .serializers import (
    AppointmentSerializer,
    DoctorSerializer,
    MedicalRecordSerializer,
    PatientSerializer,
)


def _bad(detail):
    return Response({"detail": detail}, status=status.HTTP_400_BAD_REQUEST)


class DoctorViewSet(StrictCrudMixin, viewsets.ModelViewSet):
    queryset = Doctor.objects.all()
    serializer_class = DoctorSerializer

    not_found_message = "Doctor not found."
    deleted_message = "Doctor has been deleted"
    updated_message = "Doctor updated."
    created_message = None  # return serialized object

    def validate_create(self, serializer):
        d = serializer.validated_data
        if Doctor.objects.filter(Q(pk=d["id"]) | Q(name=d["name"])).exists():
            return _bad("A doctor with this id or name already exists.")

    def validate_update(self, serializer, instance):
        d = serializer.validated_data
        if Doctor.objects.filter(name=d["name"]).exclude(pk=instance.pk).exists():
            return _bad("Another doctor already has this name.")


class PatientViewSet(StrictCrudMixin, viewsets.ModelViewSet):
    queryset = Patient.objects.all()
    serializer_class = PatientSerializer

    not_found_message = "Patient not found."
    deleted_message = "patient has been deleted"
    updated_message = "Patient updated."
    created_message = "Patient has been created successfully."

    def validate_create(self, serializer):
        d = serializer.validated_data
        if Patient.objects.filter(
            Q(pk=d["id"]) | Q(name=d["name"]) | Q(phone=d["phone"])
        ).exists():
            return _bad("A patient with this id, name or phone already exists.")

    def validate_update(self, serializer, instance):
        d = serializer.validated_data
        if Patient.objects.filter(
            Q(name=d["name"]) | Q(phone=d["phone"])
        ).exclude(pk=instance.pk).exists():
            return _bad("Another patient already has this name or phone.")


class AppointmentViewSet(StrictCrudMixin, viewsets.ModelViewSet):
    queryset = Appointment.objects.all()
    serializer_class = AppointmentSerializer
    http_method_names = ["get", "post", "put", "delete"]

    not_found_message = "Appointment not found."
    deleted_message = None  # 204 No Content
    updated_message = "Appointment updated."
    created_message = "Appointment created."

    def validate_create(self, serializer):
        patient = serializer.validated_data["patient"]
        doctor = serializer.validated_data["doctor"]

        if Appointment.objects.filter(patient=patient).exclude(doctor=doctor).exists():
            return _bad("This patient is already assigned to a different doctor.")

        if Appointment.objects.filter(
            patient=patient,
            doctor=doctor,
            status__in=[Appointment.Status.PENDING, Appointment.Status.ON_GOING],
        ).exists():
            return _bad("This patient already has an ongoing appointment with this doctor.")

    def validate_update(self, serializer, instance):
        patient = serializer.validated_data["patient"]
        doctor = serializer.validated_data["doctor"]
        if (
            Appointment.objects.filter(patient=patient)
            .exclude(doctor=doctor)
            .exclude(pk=instance.pk)
            .exists()
        ):
            return _bad("This patient is already assigned to a different doctor.")


class MedicalRecordViewSet(StrictCrudMixin, viewsets.ModelViewSet):
    queryset = MedicalRecord.objects.all()
    serializer_class = MedicalRecordSerializer

    not_found_message = "Medical record not found."
    deleted_message = "Medical record has been deleted"
    updated_message = "Medical record updated."
    created_message = None  # return serialized object

    def validate_create(self, serializer):
        if MedicalRecord.objects.filter(pk=serializer.validated_data["id"]).exists():
            return _bad("A medical record with this id already exists.")