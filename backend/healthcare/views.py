from rest_framework import status, viewsets
from rest_framework.response import Response

from .models import Appointment, Doctor, MedicalRecord, Patient
from .serializers import AppointmentSerializer, DoctorSerializer, MedicalRecordSerializer, PatientSerializer


class DoctorViewSet(viewsets.ModelViewSet):
    queryset = Doctor.objects.all()
    serializer_class = DoctorSerializer


class PatientViewSet(viewsets.ModelViewSet):
    queryset = Patient.objects.all()
    serializer_class = PatientSerializer



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

# TODO : implement the validation thru the appointment id and updating the status of the appointment 
# the id of the appointment should be passed for querying then the rest will be updated 
    def update(self, request, *args, **kwargs):
        if request.query_params or request.content_type != "application/json":
            return Response(
                {"detail": "Error while processing the request."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        data = request.data
        if not isinstance(data, dict) or set(data.keys()) != {"status"}:
            return Response(
                {"detail": "Only 'status' is accepted."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        if data["status"] not in Appointment.Status.values:
            return Response(
                {"detail": f"Invalid status. Allowed: {list(Appointment.Status.values)}"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        instance = self.get_object()
        instance.status = data["status"]
        instance.save(update_fields=["status"])
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