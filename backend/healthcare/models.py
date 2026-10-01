from django.db import models
from django.contrib.auth.models import User


class Doctor(models.Model):
    name = models.CharField(max_length=100)
    specialty = models.CharField(max_length=100)
    user = models.OneToOneField(User, on_delete=models.SET_NULL, null=True, blank=True, related_name="doctor_profile")


class Patient(models.Model):
    name = models.CharField(max_length=100)
    birth_date = models.DateField(null=True, blank=True)
    phone = models.CharField(max_length=20, blank=True)
    user = models.OneToOneField(User, on_delete=models.SET_NULL, null=True, blank=True, related_name="patient_profile")


class Appointment(models.Model):
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name="appointments")
    doctor = models.ForeignKey(Doctor, on_delete=models.CASCADE, related_name="appointments")
    date = models.DateTimeField()
    notes = models.TextField(blank=True) 


class UserProfile(models.Model):
    class Role(models.TextChoices):
        PATIENT = "PATIENT", "Patient"
        DOCTOR = "DOCTOR", "Médecin"
        ADMIN = "ADMIN", "Administrateur"

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="profile")
    role = models.CharField(max_length=20, choices=Role.choices)


class MedicalRecord(models.Model):
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name="medical_records")
    title = models.CharField(max_length=200)
    content = models.TextField()
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name="created_medical_records")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class AccessPermission(models.Model):
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name="access_permissions")
    doctor = models.ForeignKey(Doctor, on_delete=models.CASCADE, related_name="patient_permissions")
    granted_at = models.DateTimeField(auto_now_add=True)
    revoked_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=("patient", "doctor"), name="unique_patient_doctor_permission"),
        ]

    @property
    def is_active(self):
        return self.revoked_at is None


class AuditLog(models.Model):
    class Action(models.TextChoices):
        LOGIN = "LOGIN", "Connexion"
        VIEW_RECORD = "VIEW_RECORD", "Consultation de dossier"
        GRANT_ACCESS = "GRANT_ACCESS", "Autorisation"
        REVOKE_ACCESS = "REVOKE_ACCESS", "Révocation"
        ACCESS_DENIED = "ACCESS_DENIED", "Accès refusé"

    actor = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name="audit_logs")
    action = models.CharField(max_length=30, choices=Action.choices)
    patient = models.ForeignKey(Patient, on_delete=models.SET_NULL, null=True, blank=True, related_name="audit_logs")
    details = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
