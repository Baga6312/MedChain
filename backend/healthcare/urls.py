from django.urls import path
from rest_framework.routers import DefaultRouter

from .views import AppointmentViewSet, DoctorViewSet, MedicalRecordViewSet, PatientViewSet

router = DefaultRouter()
router.register("doctors", DoctorViewSet)
router.register("medical-records", MedicalRecordViewSet)

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
] + router.urls