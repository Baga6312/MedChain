

from django.urls import path

from .admin_views import (
    audit_logs,
    current_user,
    dashboard,
    force_logout,
    security_alerts,
    update_profile,
    users,
)
from .auth_views import login, register
from .oauth import google_callback, google_login
from .views import (
    AppointmentViewSet,
    DoctorViewSet,
    MedicalRecordViewSet,
    PatientViewSet,
    TreatmentEpisodeViewSet,
    treatment_event_list,
    treatment_phase_detail,
    treatment_phase_list,
    treatment_timeline,
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

treatment_episode_list = TreatmentEpisodeViewSet.as_view({
    "get": "list",
    "post": "create",
})
treatment_episode_detail = TreatmentEpisodeViewSet.as_view({
    "get": "retrieve",
    "patch": "partial_update",
    "delete": "destroy",
})

urlpatterns = [
    path("auth/login/", login, name="login"),
    path("auth/register/", register, name="register"),
    path("auth/me/", current_user, name="current-user"),
    path("auth/profile/", update_profile, name="update-profile"),
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
    path("treatment-episodes/", treatment_episode_list, name="treatment-episode-list"),
    path(
        "treatment-episodes/<int:pk>/",
        treatment_episode_detail,
        name="treatment-episode-detail",
    ),
    path(
        "treatment-episodes/<int:episode_id>/timeline/",
        treatment_timeline,
        name="treatment-timeline",
    ),
    path(
        "treatment-episodes/<int:episode_id>/phases/",
        treatment_phase_list,
        name="treatment-phase-list",
    ),
    path(
        "treatment-episodes/<int:episode_id>/phases/<int:phase_id>/",
        treatment_phase_detail,
        name="treatment-phase-detail",
    ),
    path(
        "treatment-episodes/<int:episode_id>/events/",
        treatment_event_list,
        name="treatment-event-list",
    ),
    path("admin/dashboard/", dashboard, name="admin-dashboard"),
    path("admin/users/", users, name="admin-users"),
    path("admin/users/<int:user_id>/force-logout/", force_logout, name="admin-force-logout"),
    path("admin/audit-logs/", audit_logs, name="admin-audit-logs"),
    path("admin/security-alerts/", security_alerts, name="admin-security-alerts"),
]