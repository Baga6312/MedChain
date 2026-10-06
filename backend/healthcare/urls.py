"""URL routing for the healthcare API.

The one change from the previous version: `put` and `patch` moved from the list
route to the detail route.

    before:  PUT /api/patients/     with the target id in the request body
    after:   PUT /api/patients/5/   target identified by the URL

That mismatch was the reason views.py could not resolve its target from the URL.
With PUT on the collection route, the body was the only handle on the row.

PATCH is newly bound. It was absent from the mapping entirely, so the
ModelViewSet implementation was unreachable, and partial_update was dead code.

Explicit `as_view({...})` mappings are kept rather than registering the
viewsets with DefaultRouter, because that is the existing convention here and
the route names (which the frontend and any tests may reference) are unchanged.
The trailing `+ router.urls` from the previous version was removed: the router
has no registered viewsets, so it contributed an empty URL list and an unused
import.
"""

from django.urls import path

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
    path("appointments/", appointment_list, name="appointment-list"),
    path("appointments/<int:pk>/", appointment_detail, name="appointment-detail"),
    path("patients/", patient_list, name="patient-list"),
    path("patients/<int:pk>/", patient_detail, name="patient-detail"),
    path("doctors/", doctor_list, name="doctor-list"),
    path("doctors/<int:pk>/", doctor_detail, name="doctor-detail"),
    path("medical-records/", record_list, name="medical-record-list"),
    path("medical-records/<int:pk>/", record_detail, name="medical-record-detail"),
]