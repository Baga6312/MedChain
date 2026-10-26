

from django.urls import path

from .oauth import google_callback, google_login
from .views import (
    AppointmentViewSet,
    DoctorViewSet,
    MedicalRecordViewSet,
    PatientViewSet,
)

doctor_list = DoctorViewSet.as_view({
    "get": "list",
    "post": "create",
})
doctor_detail = DoctorViewSet.as_view({
    "get": "retrieve",
    "put": "update",
    "patch": "partial_update",
    "delete": "destroy",
})

patient_list = PatientViewSet.as_view({
    "get": "list",
    "post": "create",
})
patient_detail = PatientViewSet.as_view({
    "get": "retrieve",
    "put": "update",
    "patch": "partial_update",
    "delete": "destroy",
})

appointment_list = AppointmentViewSet.as_view({
    "get": "list",
    "post": "create",
})
appointment_detail = AppointmentViewSet.as_view({
    "get": "retrieve",
    "put": "update",
    "patch": "partial_update",
    "delete": "destroy",
})

record_list = MedicalRecordViewSet.as_view({
    "get": "list",
    "post": "create",
})
record_detail = MedicalRecordViewSet.as_view({
    "get": "retrieve",
    "put": "update",
    "patch": "partial_update",
    "delete": "destroy",
})

urlpatterns = [
    path("auth/google/login/", google_login, name="google-login"),
    path("auth/google/callback/", google_callback, name="google-callback"),
    path("appointments/", appointment_list, name="appointment-list"),
    path("appointments/<int:pk>/", appointment_detail, name="appointment-detail"),
    path("patients/", patient_list, name="patient-list"),
    path("patients/<int:pk>/", patient_detail, name="patient-detail"),
    path("doctors/", doctor_list, name="doctor-list"),
    path("doctors/<int:pk>/", doctor_detail, name="doctor-detail"),
    path("medical-records/", record_list, name="medical-record-list"),
    path("medical-records/<int:pk>/", record_detail, name="medical-record-detail"),
]