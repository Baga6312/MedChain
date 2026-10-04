from rest_framework.routers import DefaultRouter

from .views import AppointmentViewSet, DoctorViewSet, MedicalRecordViewSet, PatientViewSet

router = DefaultRouter()
router.register("doctors", DoctorViewSet)
router.register("patients", PatientViewSet)
router.register("appointments", AppointmentViewSet)
router.register("medical-records", MedicalRecordViewSet)

urlpatterns = router.urls