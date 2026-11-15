from django.contrib.auth import get_user_model
from rest_framework.test import APIRequestFactory, APITestCase, force_authenticate

from .models import Doctor, Patient, TreatmentEpisode, TreatmentEvent, TreatmentPhase, UserProfile
from .views import treatment_event_list, treatment_phase_detail

U = get_user_model()
factory = APIRequestFactory()


def make_user(name, role):
    user = U.objects.create_user(**{U.USERNAME_FIELD: f"{name}@test.local"}, password="Pass12345!x")
    UserProfile.objects.create(user=user, role=role)
    return user


def call(view, user, data, method="post", **kwargs):
    request = getattr(factory, method)("/x", data, format="json")
    force_authenticate(request, user=user)
    return view(request, **kwargs)


class TreatmentEventRules(APITestCase):
    def setUp(self):
        self.doc_user = make_user("doc", "doctor")
        self.pat_user = make_user("pat", "patient")
        doctor = Doctor.objects.create(user=self.doc_user, name="Doc", specialty="GP")
        patient = Patient.objects.create(user=self.pat_user, name="Pat", phone="1")
        self.ep = TreatmentEpisode.objects.create(patient=patient, doctor=doctor, status="active")
        self.phase = TreatmentPhase.objects.create(
            treatment_episode=self.ep, sequence_number=1, name="Treatment 1"
        )

    def post_event(self, user, **data):
        return call(treatment_event_list, user, data, episode_id=self.ep.id)

    def patch_phase(self, **data):
        return call(treatment_phase_detail, self.doc_user, data, method="patch",
                    episode_id=self.ep.id, phase_id=self.phase.id)

    def test_result_requires_outcome(self):
        r = self.post_event(self.pat_user, event_type="result", title="t", description="d")
        self.assertEqual(r.status_code, 400)

    def test_patient_result_with_outcome(self):
        r = self.post_event(self.pat_user, event_type="result", title="t", description="d",
                            outcome="recovering")
        self.assertEqual(r.status_code, 201)
        self.assertEqual(r.data["outcome"], "recovering")

    def test_system_events_cannot_be_forged(self):
        for kind in ("phase_failed", "phase_completed"):
            r = self.post_event(self.doc_user, event_type=kind, title="t", description="d")
            self.assertEqual(r.status_code, 400)

    def test_failed_needs_reason_then_creates_event(self):
        self.assertEqual(self.patch_phase(status="failed").status_code, 400)
        self.assertEqual(self.patch_phase(status="failed", failure_reason="no effect").status_code, 200)
        self.assertTrue(TreatmentEvent.objects.filter(event_type="phase_failed").exists())

    def test_completed_creates_event(self):
        self.assertEqual(self.patch_phase(status="completed").status_code, 200)
        self.assertTrue(TreatmentEvent.objects.filter(event_type="phase_completed").exists())