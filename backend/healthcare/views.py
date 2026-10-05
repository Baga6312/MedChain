from rest_framework import status, viewsets
from rest_framework.response import Response

from django.db.models import Q
from .models import Appointment, Doctor, MedicalRecord, Patient
from .serializers import AppointmentSerializer, DoctorSerializer, MedicalRecordSerializer, PatientSerializer


class DoctorViewSet(viewsets.ModelViewSet):
    queryset = Doctor.objects.all()
    serializer_class = DoctorSerializer

    def list(self, request, *args, **kwargs):
        if request.query_params or request.body:
            return Response(
                {"detail": "Error while processing the request."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        return super().list(request, *args, **kwargs)

    def retrieve(self, request, *args, **kwargs):
        if request.query_params or request.body:
            return Response(
                {"detail": "Error while processing the request."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        return super().retrieve(request, *args, **kwargs)

    def create(self, request, *args, **kwargs):
        if request.query_params or request.content_type != "application/json":
            return Response(
                {"detail": "Error while processing the request."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        d = serializer.validated_data

        if Doctor.objects.filter(Q(pk=d["id"]) | Q(name=d["name"])).exists():
            return Response(
                {"detail": "A doctor with this id or name already exists."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        self.perform_create(serializer)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def update(self, request, *args, **kwargs):
        if request.query_params or request.content_type != "application/json":
            return Response(
                {"detail": "Error while processing the request."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        data = request.data
        if not isinstance(data, dict) or "id" not in data:
            return Response(
                {"detail": "'id' is required in the body."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        instance = Doctor.objects.filter(pk=data["id"]).first()
        if instance is None:
            return Response(
                {"detail": "Doctor not found."},
                status=status.HTTP_404_NOT_FOUND,
            )

        payload = {k: v for k, v in data.items() if k != "id"}
        payload["id"] = instance.pk
        serializer = self.get_serializer(instance, data=payload)
        serializer.is_valid(raise_exception=True)
        d = serializer.validated_data

        if Doctor.objects.filter(name=d["name"]).exclude(pk=instance.pk).exists():
            return Response(
                {"detail": "Another doctor already has this name."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        self.perform_update(serializer)
        return Response({"detail": "Doctor updated."}, status=status.HTTP_200_OK)

    def destroy(self, request, *args, **kwargs):
        if request.query_params or request.body:
            return Response(
                {"detail": "Error while processing the request."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        instance = Doctor.objects.filter(pk=kwargs["pk"]).first()
        if instance is None:
            return Response(
                {"detail": "Doctor not found."},
                status=status.HTTP_404_NOT_FOUND,
            )
        self.perform_destroy(instance)
        return Response({"detail": "Doctor has been deleted"}, status=status.HTTP_200_OK)

class PatientViewSet(viewsets.ModelViewSet):
    queryset = Patient.objects.all()
    serializer_class = PatientSerializer

    def list(self, request, *args, **kwargs):
        if (request.query_params and request.body) or request.query_params or request.body :
            return Response(
                {"detail": "Error while processing the request."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        return super().list(request, *args, **kwargs)

    def retrieve(self, request, *args, **kwargs):
        if request.query_params or request.body:
            return Response(
                {"detail": "Error while processing the request."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        return super().retrieve(request, *args, **kwargs)

    def create(self, request, *args, **kwargs):
        if request.query_params or request.content_type != "application/json":
            return Response(
                {"detail": "Error while processing the request."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        d = serializer.validated_data

        if Patient.objects.filter(
            Q(pk=d["id"]) | Q(name=d["name"]) | Q(phone=d["phone"])
        ).exists():
            return Response(
                {"detail": "A patient with this id, name or phone already exists."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        self.perform_create(serializer)
        return Response(
            {"detail": "Patient has been created successfully."},
             status=status.HTTP_201_CREATED
            )

    def update(self, request, *args, **kwargs):
        if request.query_params or request.content_type != "application/json":
            return Response(
                {"detail": "Error while processing the request."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        data = request.data
        if not isinstance(data, dict) or "id" not in data:
            return Response(
                {"detail": "'id' is required in the body."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        instance = Patient.objects.filter(pk=data["id"]).first()
        if instance is None:
            return Response(
                {"detail": "Patient not found."},
                status=status.HTTP_404_NOT_FOUND,
            )

        payload = {k: v for k, v in data.items() if k != "id"}
        payload["id"] = instance.pk
        serializer = self.get_serializer(instance, data=payload)
        serializer.is_valid(raise_exception=True)
        d = serializer.validated_data

        if Patient.objects.filter(
            Q(name=d["name"]) | Q(phone=d["phone"])
        ).exclude(pk=instance.pk).exists():
            return Response(
                {"detail": "Another patient already has this name or phone."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        self.perform_update(serializer)
        return Response({"detail": "Patient updated."}, status=status.HTTP_200_OK)

    def destroy(self, request, *args, **kwargs):
        if request.query_params or request.body:
            return Response(
                {"detail": "Error while processing the request."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        instance = Patient.objects.filter(pk=kwargs["pk"]).first()
        if instance is None:
            return Response(
                {"detail": "Patient not found."},
                status=status.HTTP_404_NOT_FOUND,
            )
        self.perform_destroy(instance)
        return Response({"detail": "patient has been deleted"}, status=status.HTTP_200_OK)



class AppointmentViewSet(viewsets.ModelViewSet):
    queryset = Appointment.objects.all()
    serializer_class = AppointmentSerializer
    http_method_names = ["get", "post", "put", "delete"]

    def list(self, request, *args, **kwargs):
        if request.query_params or request.body:
            return Response(
                {"detail": "Error while processing the request."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        return super().list(request, *args, **kwargs)

    def create(self, request, *args, **kwargs):
        if request.query_params or request.content_type != "application/json":
            return Response(
                {"detail": "Error while processing the request."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        patient = serializer.validated_data["patient"]
        doctor = serializer.validated_data["doctor"]

        other_doctor = Appointment.objects.filter(patient=patient).exclude(doctor=doctor).first()
        if other_doctor:
            return Response(
                {"detail": "This patient is already assigned to a different doctor."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        active_with_doctor = Appointment.objects.filter(
            patient=patient, doctor=doctor, status__in=[Appointment.Status.PENDING, Appointment.Status.ON_GOING]
        ).exists()
        if active_with_doctor:
            return Response(
                {"detail": "This patient already has an ongoing appointment with this doctor."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        self.perform_create(serializer)
        return Response({"detail": "Appointment created."}, status=status.HTTP_201_CREATED)

    def retrieve(self, request, *args, **kwargs):
        if request.query_params or request.body:
            return Response(
                {"detail": "Error while processing the request."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        return super().retrieve(request, *args, **kwargs)

    def update(self, request, *args, **kwargs):
        if request.query_params or request.content_type != "application/json":
            return Response(
                {"detail": "Error while processing the request."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        data = request.data
        if not isinstance(data, dict) or "id" not in data:
            return Response(
                {"detail": "'id' is required in the body."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        instance = Appointment.objects.filter(pk=data["id"]).first()
        if instance is None:
            return Response(
                {"detail": "Appointment not found."},
                status=status.HTTP_404_NOT_FOUND,
            )

        payload = {k: v for k, v in data.items() if k != "id"}
        serializer = self.get_serializer(instance, data=payload)
        serializer.is_valid(raise_exception=True)

        patient = serializer.validated_data["patient"]
        doctor = serializer.validated_data["doctor"]
        other_doctor = (
            Appointment.objects.filter(patient=patient)
            .exclude(doctor=doctor)
            .exclude(pk=instance.pk)
            .exists()
        )
        if other_doctor:
            return Response(
                {"detail": "This patient is already assigned to a different doctor."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        self.perform_update(serializer)
        return Response({"detail": "Appointment updated."}, status=status.HTTP_200_OK)

    def destroy(self, request, *args, **kwargs):
        if request.query_params or request.body:
            return Response(
                {"detail": "Error while processing the request."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        instance = Appointment.objects.filter(pk=kwargs["pk"]).first()
        if instance is None:
            return Response(
                {"detail": "Appointment not found."},
                status=status.HTTP_404_NOT_FOUND,
            )
        self.perform_destroy(instance)
        return Response(status=status.HTTP_204_NO_CONTENT)



        
class MedicalRecordViewSet(viewsets.ModelViewSet):
    queryset = MedicalRecord.objects.all()
    serializer_class = MedicalRecordSerializer

    def list(self, request, *args, **kwargs):
        if request.query_params or request.body:
            return Response(
                {"detail": "Error while processing the request."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        return super().list(request, *args, **kwargs)

    def retrieve(self, request, *args, **kwargs):
        if request.query_params or request.body:
            return Response(
                {"detail": "Error while processing the request."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        return super().retrieve(request, *args, **kwargs)

    def create(self, request, *args, **kwargs):
        if request.query_params or request.content_type != "application/json":
            return Response(
                {"detail": "Error while processing the request."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        d = serializer.validated_data

        if MedicalRecord.objects.filter(pk=d["id"]).exists():
            return Response(
                {"detail": "A medical record with this id already exists."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        self.perform_create(serializer)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def update(self, request, *args, **kwargs):
        if request.query_params or request.content_type != "application/json":
            return Response(
                {"detail": "Error while processing the request."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        data = request.data
        if not isinstance(data, dict) or "id" not in data:
            return Response(
                {"detail": "'id' is required in the body."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        instance = MedicalRecord.objects.filter(pk=data["id"]).first()
        if instance is None:
            return Response(
                {"detail": "Medical record not found."},
                status=status.HTTP_404_NOT_FOUND,
            )

        payload = {k: v for k, v in data.items() if k != "id"}
        payload["id"] = instance.pk
        serializer = self.get_serializer(instance, data=payload)
        serializer.is_valid(raise_exception=True)

        self.perform_update(serializer)
        return Response({"detail": "Medical record updated."}, status=status.HTTP_200_OK)

    def destroy(self, request, *args, **kwargs):
        if request.query_params or request.body:
            return Response(
                {"detail": "Error while processing the request."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        instance = MedicalRecord.objects.filter(pk=kwargs["pk"]).first()
        if instance is None:
            return Response(
                {"detail": "Medical record not found."},
                status=status.HTTP_404_NOT_FOUND,
            )
        self.perform_destroy(instance)
        return Response({"detail": "Medical record has been deleted"}, status=status.HTTP_200_OK)