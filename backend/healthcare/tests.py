from django.contrib.auth.models import User
from rest_framework.test import APITestCase

from .models import AccessPermission, AuditLog, Doctor, MedicalRecord, Patient, UserProfile


class SharingAccessTests(APITestCase):
	def setUp(self):
		self.patient_user = User.objects.create_user("patient", password="Pass12345!")
		self.doctor_user = User.objects.create_user("doctor", password="Pass12345!")
		UserProfile.objects.create(user=self.patient_user, role=UserProfile.Role.PATIENT)
		UserProfile.objects.create(user=self.doctor_user, role=UserProfile.Role.DOCTOR)
		self.patient = Patient.objects.create(name="Patient Test", user=self.patient_user)
		self.doctor = Doctor.objects.create(name="Dr Test", specialty="Cardiology", user=self.doctor_user)
		self.record = MedicalRecord.objects.create(patient=self.patient, title="Analyse", content="Fictive", created_by=self.patient_user)

	def test_patient_can_authorize_and_revoke_doctor(self):
		self.client.force_authenticate(self.patient_user)
		response = self.client.post(f"/api/patients/{self.patient.pk}/permissions/", {"doctor_id": self.doctor.pk}, format="json")
		self.assertEqual(response.status_code, 200)
		self.assertTrue(AccessPermission.objects.filter(patient=self.patient, doctor=self.doctor, revoked_at__isnull=True).exists())

		response = self.client.post(f"/api/patients/{self.patient.pk}/permissions/{self.doctor.pk}/revoke/", format="json")
		self.assertEqual(response.status_code, 200)
		self.assertIsNotNone(AccessPermission.objects.get(patient=self.patient, doctor=self.doctor).revoked_at)
		self.assertEqual(AuditLog.objects.filter(patient=self.patient).count(), 2)

	def test_doctor_gets_403_after_access_is_revoked(self):
		AccessPermission.objects.create(patient=self.patient, doctor=self.doctor)
		self.client.force_authenticate(self.doctor_user)
		response = self.client.get(f"/api/medical-records/{self.record.pk}/")
		self.assertEqual(response.status_code, 200)

		permission = AccessPermission.objects.get(patient=self.patient, doctor=self.doctor)
		permission.revoked_at = permission.granted_at
		permission.save(update_fields=["revoked_at"])
		response = self.client.get(f"/api/medical-records/{self.record.pk}/")
		self.assertEqual(response.status_code, 403)
		self.assertTrue(AuditLog.objects.filter(action=AuditLog.Action.ACCESS_DENIED).exists())

	def test_anonymous_user_is_rejected(self):
		response = self.client.get("/api/medical-records/")
		self.assertEqual(response.status_code, 401)
