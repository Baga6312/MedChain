from django.urls import path
from rest_framework.routers import DefaultRouter

from .views import AppointmentViewSet, DoctorViewSet, MedicalRecordViewSet, PatientViewSet

router = DefaultRouter()


doctor_list = DoctorViewSet.as_view({
    "get": "list",
    "post": "create",
    "put": "update",
})
doctor_detail = DoctorViewSet.as_view({
    "get": "retrieve",
    "delete": "destroy",
})


record_list = MedicalRecordViewSet.as_view({
    "get": "list",
    "post": "create",
    "put": "update",
})
record_detail = MedicalRecordViewSet.as_view({
    "get": "retrieve",
    "delete": "destroy",
})



patient_list = PatientViewSet.as_view({
    "get": "list",
    "post": "create",
    "put": "update",
})
patient_detail = PatientViewSet.as_view({
    "get": "retrieve",
    "delete": "destroy",
})


appointment_list = AppointmentViewSet.as_view({
    "get": "list",
    "post": "create",
    "put": "update",
})
appointment_detail = AppointmentViewSet.as_view({
    "get": "retrieve",
    "delete": "destroy",
})



urlpatterns = [
    path("appointments/", appointment_list, name="appointment-list"),
    path("appointments/<int:pk>/", appointment_detail, name="appointment-detail"),
    path("patients/", patient_list, name="patient-list"),
    path("patients/<int:pk>/", patient_detail, name="patient-detail"),
    path("doctors/", doctor_list, name="doctor-list"),
    path("doctors/<int:pk>/", doctor_detail, name="doctor-detail"),
    path("medical-records/", record_list, name="medical-record-list"),
    path("medical-records/<int:pk>/", record_detail, name="medical-record-detail"),
] + router.urls