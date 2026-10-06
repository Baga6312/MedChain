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
        if Doctor.objects.filter(name=serializer.validated_data["name"]).exists():
            return _bad("A doctor with this name already exists.")

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
        if Patient.objects.filter(Q(name=d["name"]) | Q(phone=d["phone"])).exists():
            return _bad("A patient with this name or phone already exists.")

    def validate_update(self, serializer, instance):
        d = serializer.validated_data
        if Patient.objects.filter(
            Q(name=d["name"]) | Q(phone=d["phone"])
        ).exclude(pk=instance.pk).exists():
            return _bad("Another patient already has this name or phone.")


class AppointmentViewSet(StrictCrudMixin, viewsets.ModelViewSet):
    """Business rules live in AppointmentSerializer.validate()."""

    queryset = Appointment.objects.all()
    serializer_class = AppointmentSerializer
    http_method_names = ["get", "post", "put", "delete"]

    not_found_message = "Appointment not found."
    deleted_message = None  # 204 No Content
    updated_message = "Appointment updated."
    created_message = "Appointment created."


class MedicalRecordViewSet(StrictCrudMixin, viewsets.ModelViewSet):
    queryset = MedicalRecord.objects.all()
    serializer_class = MedicalRecordSerializer

    not_found_message = "Medical record not found."
    deleted_message = "Medical record has been deleted"
    updated_message = "Medical record updated."
    created_message = None  # return serialized object