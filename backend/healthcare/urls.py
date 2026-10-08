

from django.urls import path

from .views import (
    AppointmentViewSet,
    DoctorViewSet,
    GrantAccessView,
    LoginView,
    MedicalRecordViewSet,
    PatientViewSet,
    RevokeAccessView,
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
    path("appointments/", appointment_list, name="appointment-list"),
    path("appointments/<int:pk>/", appointment_detail, name="appointment-detail"),
    path("patients/", patient_list, name="patient-list"),
    path("patients/<int:pk>/", patient_detail, name="patient-detail"),
    path("doctors/", doctor_list, name="doctor-list"),
    path("doctors/<int:pk>/", doctor_detail, name="doctor-detail"),
    path("medical-records/", record_list, name="medical-record-list"),
    path("medical-records/<int:pk>/", record_detail, name="medical-record-detail"),
    path("auth/login/", LoginView.as_view(), name="login"),
    path("patients/<int:pk>/permissions/", GrantAccessView.as_view(), name="patient-permissions"),
    path(
        "patients/<int:pk>/permissions/<int:doctor_pk>/revoke/",
        RevokeAccessView.as_view(),
        name="patient-permission-revoke",
    ),
]