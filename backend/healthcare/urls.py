from django.urls import path
from rest_framework.routers import DefaultRouter

from .views import (
	AppointmentViewSet,
	AuditLogViewSet,
	DoctorViewSet,
	GrantAccessView,
	LoginView,
	MedicalRecordViewSet,
	PatientViewSet,
	RevokeAccessView,
)

router = DefaultRouter()
router.register("doctors", DoctorViewSet)
router.register("patients", PatientViewSet)
router.register("appointments", AppointmentViewSet)
router.register("medical-records", MedicalRecordViewSet)
router.register("audit-logs", AuditLogViewSet, basename="audit-log")

urlpatterns = router.urls + [
	path("auth/login/", LoginView.as_view(), name="login"),
	path("patients/<int:patient_id>/permissions/", GrantAccessView.as_view(), name="grant-access"),
	path("patients/<int:patient_id>/permissions/<int:doctor_id>/revoke/", RevokeAccessView.as_view(), name="revoke-access"),
]
