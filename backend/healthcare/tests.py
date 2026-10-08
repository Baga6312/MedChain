"""Authorization contract for the healthcare API.

These are the security tests, not just regression cover: each one asserts that
a specific caller cannot reach a specific row. A refactor that reopens a hole
fails a test here rather than shipping silently.

Covers the trust boundaries in the brief -- authentication, role resolution,
tenant scoping, and every write path (create / update / delete / grant).
"""

from django.contrib.auth import get_user_model
from django.contrib.auth.models import AnonymousUser
from django.core.cache import cache
from django.db.models import ProtectedError
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone
from rest_framework.test import APIClient

from .authz import role_of, visible_patient_ids
from .models import AccessPermission, Appointment, AuditLog, Doctor, MedicalRecord, Patient

User = get_user_model()


class AuthFixtures(TestCase):
    """Two patients, two doctors, plus accounts with no role at all."""

    @classmethod
    def setUpTestData(cls):
        cls.admin = User.objects.create_superuser("root", "r@example.com", "pw-root-1234")
        cls.patient_user = User.objects.create_user("alice", password="pw-alice-1234")
        cls.other_patient_user = User.objects.create_user("bob", password="pw-bob-12345")
        cls.doctor_user = User.objects.create_user("drwho", password="pw-drwho-123")
        cls.stranger_doctor = User.objects.create_user("drno", password="pw-drno-1234")
        # Accounts that must resolve to "no role" -- see RoleResolutionTests.
        cls.unlinked = User.objects.create_user("nobody", password="pw-nobody-123")
        cls.staff_only = User.objects.create_user("clerk", password="pw-clerk-1234", is_staff=True)

        cls.patient = Patient.objects.create(name="Alice", phone="20000001", user=cls.patient_user)
        cls.other_patient = Patient.objects.create(
            name="Bob", phone="20000002", user=cls.other_patient_user
        )
        cls.doctor = Doctor.objects.create(name="Who", specialty="Cardiology", user=cls.doctor_user)
        cls.other_doctor = Doctor.objects.create(
            name="No", specialty="Neurology", user=cls.stranger_doctor
        )

        cls.record = MedicalRecord.objects.create(
            patient=cls.patient, title="Chart", content="sensitive"
        )
        cls.other_record = MedicalRecord.objects.create(
            patient=cls.other_patient, title="Other", content="private"
        )
        cls.appointment = Appointment.objects.create(
            patient=cls.patient, doctor=cls.doctor, date="2026-01-01T10:00:00Z", notes="n"
        )

    def setUp(self):
        # Throttle counters live in the process-wide cache, so a test that
        # deliberately trips the login limit would otherwise 429 every test
        # that runs after it.
        cache.clear()

    def client_for(self, user):
        client = APIClient()
        client.force_authenticate(user=user)
        return client

    def as_patient(self):
        return self.client_for(self.patient_user)

    def as_doctor(self):
        return self.client_for(self.doctor_user)

    def as_admin(self):
        return self.client_for(self.admin)

    def grant(self, patient=None, doctor=None):
        return AccessPermission.objects.create(
            patient=patient or self.patient, doctor=doctor or self.doctor
        )


class AuthenticationTests(AuthFixtures):
    def test_anonymous_cannot_read_any_collection(self):
        client = APIClient()
        for name in ("doctor-list", "patient-list", "appointment-list", "medical-record-list"):
            with self.subTest(resource=name):
                self.assertEqual(client.get(reverse(name)).status_code, 401)

    def test_anonymous_cannot_write(self):
        response = APIClient().post(
            reverse("patient-list"), {"name": "X", "phone": "1"}, format="json"
        )
        self.assertEqual(response.status_code, 401)

    def test_login_returns_token_and_role(self):
        response = APIClient().post(
            reverse("login"), {"username": "alice", "password": "pw-alice-1234"}, format="json"
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["role"], "PATIENT")
        self.assertEqual(response.data["patient_id"], self.patient.pk)
        self.assertTrue(response.data["token"])

    def test_login_token_authenticates_subsequent_calls(self):
        """The credential is only real if it is accepted on the next request."""
        token = APIClient().post(
            reverse("login"), {"username": "alice", "password": "pw-alice-1234"}, format="json"
        ).data["token"]
        client = APIClient()
        client.credentials(HTTP_AUTHORIZATION=f"Token {token}")
        self.assertEqual(client.get(reverse("patient-list")).status_code, 200)

    def test_login_with_wrong_password_is_rejected_and_audited(self):
        response = APIClient().post(
            reverse("login"), {"username": "alice", "password": "wrong"}, format="json"
        )
        self.assertEqual(response.status_code, 400)
        entry = AuditLog.objects.filter(action=AuditLog.Action.LOGIN_FAILED).first()
        self.assertIsNotNone(entry, "failed login must be recorded for brute-force detection")
        # The attempted username is kept; the credential is not.
        self.assertEqual(entry.details["username"], "alice")
        self.assertNotIn("password", entry.details)

    def test_login_is_rate_limited(self):
        """Exercises the shipped 10/min rate rather than a synthetic override,
        so it fails if the throttle stops being wired to the view."""
        from config.settings import REST_FRAMEWORK

        rate = REST_FRAMEWORK["DEFAULT_THROTTLE_RATES"]["login"]
        limit = int(rate.split("/")[0])
        cache.clear()
        client = APIClient()
        statuses = [
            client.post(
                reverse("login"), {"username": "alice", "password": "nope"}, format="json"
            ).status_code
            for _ in range(limit + 2)
        ]
        self.assertIn(429, statuses, f"expected throttling at {limit}/{rate}, got {statuses}")


class RoleResolutionTests(AuthFixtures):
    def test_unlinked_account_has_no_role_and_sees_nothing(self):
        """No profile must resolve to [], never None -- None means
        'unrestricted' and would hand over the whole table."""
        self.assertIsNone(role_of(self.unlinked))
        self.assertEqual(visible_patient_ids(self.unlinked), [])

    def test_is_staff_is_not_a_role(self):
        """is_staff is the admin-console flag and must not confer API access."""
        self.assertIsNone(role_of(self.staff_only))
        self.assertEqual(visible_patient_ids(self.staff_only), [])
        self.assertEqual(
            self.client_for(self.staff_only).get(reverse("patient-list")).status_code, 200
        )
        self.assertEqual(len(self.client_for(self.staff_only).get(reverse("patient-list")).data), 0)

    def test_admin_is_unrestricted(self):
        self.assertEqual(role_of(self.admin), "ADMIN")
        self.assertIsNone(visible_patient_ids(self.admin))

    def test_anonymous_is_restricted_not_unrestricted(self):
        self.assertIsNone(role_of(AnonymousUser()))
        self.assertEqual(visible_patient_ids(AnonymousUser()), [])


class ReadScopingTests(AuthFixtures):
    def test_patient_sees_only_own_rows(self):
        patients = self.as_patient().get(reverse("patient-list")).data
        self.assertEqual([p["id"] for p in patients], [self.patient.pk])

    def test_doctor_sees_nothing_before_a_grant(self):
        self.assertEqual(len(self.as_doctor().get(reverse("patient-list")).data), 0)

    def test_granted_doctor_sees_that_patient(self):
        self.grant()
        patients = self.as_doctor().get(reverse("patient-list")).data
        self.assertEqual([p["id"] for p in patients], [self.patient.pk])

    def test_revoked_doctor_sees_nothing(self):
        self.grant()
        AccessPermission.objects.update(revoked_at=timezone.now())
        self.assertEqual(len(self.as_doctor().get(reverse("patient-list")).data), 0)

    def test_patient_cannot_read_another_patients_record(self):
        response = self.client_for(self.other_patient_user).get(
            reverse("medical-record-detail", args=[self.record.pk])
        )
        self.assertEqual(response.status_code, 404)

    def test_doctor_cannot_read_another_patients_record(self):
        response = self.as_doctor().get(
            reverse("medical-record-detail", args=[self.other_record.pk])
        )
        self.assertEqual(response.status_code, 404)

    def test_admin_reads_everything(self):
        self.assertEqual(len(self.as_admin().get(reverse("medical-record-list")).data), 2)

    def test_doctor_sees_only_their_own_appointments_on_a_granted_chart(self):
        """A grant covers the chart; it does not expose the patient to a
        different doctor's schedule."""
        self.grant()
        Appointment.objects.create(
            patient=self.patient,
            doctor=self.other_doctor,
            date="2026-02-01T10:00:00Z",
            notes="other",
        )
        rows = self.as_doctor().get(reverse("appointment-list")).data
        self.assertEqual([a["id"] for a in rows], [self.appointment.pk])

    def test_patient_cannot_see_the_doctor_list_when_nothing_is_granted(self):
        """The doctor list doubles as the grant picker, so it must not leak
        the full staff directory."""
        self.assertEqual(len(self.as_patient().get(reverse("doctor-list")).data), 0)


class WriteGuardTests(AuthFixtures):
    def test_patient_cannot_create_patient(self):
        response = self.as_patient().post(
            reverse("patient-list"),
            {"name": "Fake", "phone": "999", "birth_date": None},
            format="json",
        )
        self.assertEqual(response.status_code, 403)

    def test_patient_cannot_create_doctor(self):
        response = self.as_patient().post(
            reverse("doctor-list"), {"name": "Fake", "specialty": "X"}, format="json"
        )
        self.assertEqual(response.status_code, 403)

    def test_patient_cannot_delete_self(self):
        """Patient rows cascade to records and appointments, so a patient
        deleting their own row would destroy clinician-owned data."""
        response = self.as_patient().delete(reverse("patient-detail", args=[self.patient.pk]))
        self.assertEqual(response.status_code, 403)
        self.assertTrue(Patient.objects.filter(pk=self.patient.pk).exists())
        self.assertTrue(MedicalRecord.objects.filter(pk=self.record.pk).exists())

    def test_doctor_cannot_delete_patient(self):
        """The regression this guard exists for: a doctor deleting a granted
        patient took that patient's other doctors' appointments with them."""
        self.grant()
        response = self.as_doctor().delete(reverse("patient-detail", args=[self.patient.pk]))
        self.assertEqual(response.status_code, 403)
        self.assertTrue(Appointment.objects.filter(pk=self.appointment.pk).exists())

    def test_doctor_cannot_delete_another_doctor(self):
        self.grant()
        response = self.as_doctor().delete(reverse("doctor-detail", args=[self.other_doctor.pk]))
        self.assertEqual(response.status_code, 404)  # not in the doctor's queryset
        self.assertTrue(Doctor.objects.filter(pk=self.other_doctor.pk).exists())

    def test_patient_cannot_move_a_record_to_another_patient(self):
        """Scoped reads are not enough: without a guard on the writable
        `patient` FK, an authorized caller re-points the record elsewhere."""
        response = self.as_patient().put(
            reverse("medical-record-detail", args=[self.record.pk]),
            {
                "id": self.record.pk,
                "patient": self.other_patient.pk,
                "title": "Chart",
                "content": "sensitive",
            },
            format="json",
        )
        self.assertEqual(response.status_code, 403)
        self.record.refresh_from_db()
        self.assertEqual(self.record.patient_id, self.patient.pk)

    def test_granted_doctor_cannot_move_a_record_off_the_chart(self):
        """The writable `patient` FK is the hole: scoped reads do not help if
        an authorized caller can re-point a record at another patient."""
        self.grant()
        response = self.as_doctor().put(
            reverse("medical-record-detail", args=[self.record.pk]),
            {
                "id": self.record.pk,
                "patient": self.other_patient.pk,
                "title": "Chart",
                "content": "sensitive",
            },
            format="json",
        )
        self.assertEqual(response.status_code, 403)
        self.record.refresh_from_db()
        self.assertEqual(self.record.patient_id, self.patient.pk)

    def test_doctor_cannot_create_record_without_a_grant(self):
        response = self.as_doctor().post(
            reverse("medical-record-list"),
            {"patient": self.other_patient.pk, "title": "t", "content": "c"},
            format="json",
        )
        self.assertEqual(response.status_code, 403)

    def test_patient_cannot_change_appointment_status(self):
        response = self.as_patient().put(
            reverse("appointment-detail", args=[self.appointment.pk]),
            {
                "id": self.appointment.pk,
                "patient": self.patient.pk,
                "doctor": self.doctor.pk,
                "date": "2026-01-01T10:00:00Z",
                "notes": "n",
                "status": "completed",
            },
            format="json",
        )
        self.assertEqual(response.status_code, 403)
        self.appointment.refresh_from_db()
        self.assertEqual(self.appointment.status, "pending")

    def test_assigned_doctor_can_change_status(self):
        self.grant()
        response = self.as_doctor().put(
            reverse("appointment-detail", args=[self.appointment.pk]),
            {
                "id": self.appointment.pk,
                "patient": self.patient.pk,
                "doctor": self.doctor.pk,
                "date": "2026-01-01T10:00:00Z",
                "notes": "n",
                "status": "completed",
            },
            format="json",
        )
        self.assertEqual(response.status_code, 200)
        self.appointment.refresh_from_db()
        self.assertEqual(self.appointment.status, "completed")

    def test_patient_cannot_create_an_appointment_for_another_patient(self):
        response = self.as_patient().post(
            reverse("appointment-list"),
            {
                "patient": self.other_patient.pk,
                "doctor": self.doctor.pk,
                "date": "2026-03-01T10:00:00Z",
                "notes": "n",
            },
            format="json",
        )
        self.assertEqual(response.status_code, 403)

    def test_record_author_is_taken_from_the_token_not_the_body(self):
        self.grant()
        response = self.as_doctor().post(
            reverse("medical-record-list"),
            {
                "patient": self.patient.pk,
                "title": "t",
                "content": "c",
                "created_by": self.admin.pk,  # forgery attempt; not a serializer field
            },
            format="json",
        )
        self.assertEqual(response.status_code, 201)
        self.assertEqual(MedicalRecord.objects.get(title="t").created_by_id, self.doctor_user.pk)

    def test_admin_can_delete_a_medical_record(self):
        response = self.as_admin().delete(reverse("medical-record-detail", args=[self.record.pk]))
        self.assertEqual(response.status_code, 200)

    def test_non_admin_cannot_delete_a_medical_record(self):
        response = self.as_patient().delete(
            reverse("medical-record-detail", args=[self.record.pk])
        )
        self.assertEqual(response.status_code, 403)

    def test_guards_return_403_not_400(self):
        """A 400 is indistinguishable from a payload error, so a client cannot
        tell 'you may not' from 'your JSON is wrong'."""
        response = self.as_patient().post(
            reverse("patient-list"),
            {"name": "Fake", "phone": "999", "birth_date": None},
            format="json",
        )
        self.assertEqual(response.status_code, 403)
        self.assertIn("detail", response.data)


class AccessGrantTests(AuthFixtures):
    def test_patient_grants_access_to_doctor(self):
        response = self.as_patient().post(
            reverse("patient-permissions", args=[self.patient.pk]),
            {"doctor_id": self.doctor.pk},
            format="json",
        )
        self.assertEqual(response.status_code, 200)
        self.assertTrue(AccessPermission.objects.filter(patient=self.patient, doctor=self.doctor).exists())
        self.assertEqual(AuditLog.objects.filter(action=AuditLog.Action.GRANT_ACCESS).count(), 1)

    def test_patient_cannot_grant_on_another_patients_chart(self):
        response = self.client_for(self.other_patient_user).post(
            reverse("patient-permissions", args=[self.patient.pk]),
            {"doctor_id": self.doctor.pk},
            format="json",
        )
        self.assertEqual(response.status_code, 403)

    def test_admin_cannot_grant_on_the_patients_behalf(self):
        """An admin's implicit access must not become a durable share."""
        response = self.as_admin().post(
            reverse("patient-permissions", args=[self.patient.pk]),
            {"doctor_id": self.doctor.pk},
            format="json",
        )
        self.assertEqual(response.status_code, 403)

    def test_grant_then_revoke_leaves_the_row_revoked_and_audited(self):
        self.as_patient().post(
            reverse("patient-permissions", args=[self.patient.pk]),
            {"doctor_id": self.doctor.pk},
            format="json",
        )
        response = self.as_patient().post(
            reverse("patient-permission-revoke", args=[self.patient.pk, self.doctor.pk])
        )
        self.assertEqual(response.status_code, 200)
        self.assertIsNotNone(AccessPermission.objects.get(revoked_at__isnull=False).revoked_at)
        self.assertEqual(AuditLog.objects.filter(action=AuditLog.Action.REVOKE_ACCESS).count(), 1)

    def test_regrant_after_revoke_clears_the_flag(self):
        """(patient, doctor) is unique; a naive get_or_create would raise
        IntegrityError on the second grant."""
        AccessPermission.objects.create(patient=self.patient, doctor=self.doctor)
        self.as_patient().post(
            reverse("patient-permission-revoke", args=[self.patient.pk, self.doctor.pk])
        )
        response = self.as_patient().post(
            reverse("patient-permissions", args=[self.patient.pk]),
            {"doctor_id": self.doctor.pk},
            format="json",
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(AccessPermission.objects.count(), 1)
        self.assertIsNone(AccessPermission.objects.get().revoked_at)

    def test_revoked_doctor_gets_403_and_an_audit_row_on_retrieve(self):
        """A bare 404 would be indistinguishable from a nonexistent id and
        would leave the denial unrecorded."""
        self.grant()
        url = reverse("medical-record-detail", args=[self.record.pk])
        self.assertEqual(self.as_doctor().get(url).status_code, 200)

        AccessPermission.objects.update(revoked_at=timezone.now())
        response = self.as_doctor().get(url)
        self.assertEqual(response.status_code, 403)
        entry = AuditLog.objects.filter(
            action=AuditLog.Action.ACCESS_DENIED, actor=self.doctor_user
        ).first()
        self.assertIsNotNone(entry, "denial must be auditable")
        self.assertEqual(entry.details["reason"], "revoked")

    def test_reading_a_record_is_audited(self):
        self.grant()
        self.as_doctor().get(reverse("medical-record-detail", args=[self.record.pk]))
        self.assertEqual(
            AuditLog.objects.filter(
                action=AuditLog.Action.VIEW_RECORD, actor=self.doctor_user
            ).count(),
            1,
        )

    def test_audit_actor_survives_account_deletion(self):
        """AuditLog.actor is PROTECT precisely so history cannot be erased."""
        self.grant()
        self.as_doctor().get(reverse("medical-record-detail", args=[self.record.pk]))
        with self.assertRaises(ProtectedError):
            self.doctor_user.delete()