from django.conf import settings
from django.db import models


class Doctor(models.Model):
    name = models.CharField(max_length=100)
    specialty = models.CharField(max_length=100)
    # Link to the account allowed to act as this doctor. Nullable so the seed can
    # run before any user exists; the derived role in authz.py reads this link.
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="doctor_profile",
    )


class Patient(models.Model):
    name = models.CharField(max_length=100)
    birth_date = models.DateField(null=True, blank=True)
    phone = models.CharField(max_length=20, blank=True)
    # See Doctor.user. One account at most per patient, one patient at most per
    # account, so neither side can be used to widen access to a second chart.
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="patient_profile",
    )


class Appointment(models.Model):
    class Status(models.TextChoices):
        PENDING = "pending", "Pending"
        ON_GOING = "on_going", "On going"
        COMPLETED = "completed", "Completed"

    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name="appointments")
    doctor = models.ForeignKey(Doctor, on_delete=models.CASCADE, related_name="appointments")
    date = models.DateTimeField()
    notes = models.TextField(blank=True)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.PENDING)


class MedicalRecord(models.Model):
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name="medical_records")
    title = models.CharField(max_length=200)
    content = models.TextField()
    # Author of the entry, assigned server-side in perform_create. Never
    # accepted from the request body: a client-supplied author is forgeable.
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name="created_medical_records",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class AccessPermission(models.Model):
    """A patient's explicit grant of chart access to one doctor.

    Revocation is a soft flag rather than a row delete so the grant history
    survives and a revoked doctor can still be told "revoked" instead of the
    indistinguishable "not found".
    """

    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name="access_permissions")
    doctor = models.ForeignKey(Doctor, on_delete=models.CASCADE, related_name="patient_permissions")
    granted_at = models.DateTimeField(auto_now_add=True)
    revoked_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=("patient", "doctor"),
                name="unique_patient_doctor_permission",
            ),
        ]


class AuditLog(models.Model):
    class Action(models.TextChoices):
        LOGIN = "LOGIN", "Login"
        LOGIN_FAILED = "LOGIN_FAILED", "Failed login"
        VIEW_RECORD = "VIEW_RECORD", "Record viewed"
        GRANT_ACCESS = "GRANT_ACCESS", "Access granted"
        REVOKE_ACCESS = "REVOKE_ACCESS", "Access revoked"
        ACCESS_DENIED = "ACCESS_DENIED", "Access denied"

    # PROTECT, not SET_NULL: the point of this table is to survive account
    # deletion, and a nulled actor turns "who did this" into "whoever". Nullable
    # so a failed login, which has no authenticated user, can still be logged.
    actor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name="audit_logs",
    )
    action = models.CharField(max_length=30, choices=Action.choices)
    # SET_NULL: deleting a chart should not delete the evidence that it was
    # read. The actor link above is the one that must not be broken.
    patient = models.ForeignKey(
        Patient,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="audit_logs",
    )
    # Non-identifying context (ids, resource types). Never credentials.
    details = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)