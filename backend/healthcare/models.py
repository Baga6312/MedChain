import uuid

from django.conf import settings
from django.db import models
from .blockchain import ledger


class UserProfile(models.Model):
    class Role(models.TextChoices):
        PATIENT = "patient", "Patient"
        DOCTOR = "doctor", "Doctor"
        ADMIN = "admin", "Administrator"

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="profile",
    )
    role = models.CharField(max_length=20, choices=Role.choices, default=Role.PATIENT)
    phone = models.CharField(max_length=20, blank=True)
    address = models.CharField(max_length=255, blank=True)
    avatar = models.ImageField(upload_to="avatars/", blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)


class AuditLog(models.Model):
    class Result(models.TextChoices):
        SUCCESS = "success", "Success"
        DENIED = "denied", "Denied"

    actor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="audit_events",
    )
    action = models.CharField(max_length=100)
    target_type = models.CharField(max_length=100, blank=True)
    target_id = models.CharField(max_length=100, blank=True)
    result = models.CharField(max_length=20, choices=Result.choices, default=Result.SUCCESS)
    detail = models.TextField(blank=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]


class SecurityAlert(models.Model):
    class Severity(models.TextChoices):
        LOW = "low", "Low"
        MEDIUM = "medium", "Medium"
        HIGH = "high", "High"
        CRITICAL = "critical", "Critical"

    class Status(models.TextChoices):
        OPEN = "open", "Open"
        RESOLVED = "resolved", "Resolved"

    title = models.CharField(max_length=200)
    detail = models.TextField()
    severity = models.CharField(max_length=20, choices=Severity.choices, default=Severity.MEDIUM)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.OPEN)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="security_alerts",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    resolved_at = models.DateTimeField(null=True, blank=True)
    resolved_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="resolved_security_alerts",
    )

    class Meta:
        ordering = ["-created_at"]


class Doctor(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="doctor_record",
    )
    name = models.CharField(max_length=100)
    specialty = models.CharField(max_length=100)


class Patient(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="patient_record",
    )
    name = models.CharField(max_length=100)
    birth_date = models.DateField(null=True, blank=True)
    phone = models.CharField(max_length=20, blank=True)


class Appointment(models.Model):
    class Status(models.TextChoices):
        PENDING = "pending", "Pending"
        ON_GOING = "on_going", "On going"
        COMPLETED = "completed", "Completed"

    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name="appointments")
    doctor = models.ForeignKey(Doctor, on_delete=models.CASCADE, related_name="appointments")
    treatment_episode = models.ForeignKey(
        "TreatmentEpisode",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="appointments",
    )
    date = models.DateTimeField()
    notes = models.TextField(blank=True)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.PENDING)



    
class MedicalRecord(models.Model):
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name="medical_records")
    treatment_episode = models.ForeignKey(
        "TreatmentEpisode",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="medical_records",
    )
    title = models.CharField(max_length=200)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class TreatmentEpisode(models.Model):
    class Status(models.TextChoices):
        REQUESTED = "requested", "Requested"
        ACTIVE = "active", "Active"
        ABANDONED = "abandoned", "Abandoned"
        COMPLETED = "completed", "Completed"

    patient = models.ForeignKey(
        Patient,
        on_delete=models.CASCADE,
        related_name="treatment_episodes",
    )
    doctor = models.ForeignKey(
        Doctor,
        on_delete=models.CASCADE,
        related_name="treatment_episodes",
    )
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.REQUESTED,
    )
    reason = models.CharField(max_length=255, blank=True)
    notes = models.TextField(blank=True)
    started_at = models.DateTimeField(null=True, blank=True)
    abandoned_at = models.DateTimeField(null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]
        constraints = [
            models.UniqueConstraint(
                fields=["patient", "doctor"],
                condition=models.Q(status__in=["requested", "active"]),
                name="one_open_episode_per_patient_doctor",
            ),
        ]


class TreatmentPhase(models.Model):
    class Status(models.TextChoices):
        PENDING = "pending", "Pending"
        ACTIVE = "active", "Active"
        COMPLETED = "completed", "Completed"
        FAILED = "failed", "Failed"
        SKIPPED = "skipped", "Skipped"

    treatment_episode = models.ForeignKey(
        TreatmentEpisode,
        on_delete=models.CASCADE,
        related_name="phases",
    )
    sequence_number = models.PositiveIntegerField()
    name = models.CharField(max_length=150)
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.PENDING,
    )
    summary = models.TextField(blank=True)
    failure_reason = models.TextField(blank=True)
    started_at = models.DateTimeField(null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["sequence_number", "created_at"]
        constraints = [
            models.UniqueConstraint(
                fields=["treatment_episode", "sequence_number"],
                name="unique_phase_sequence_per_episode",
            ),
        ]


class TreatmentEvent(models.Model):
    class Outcome(models.TextChoices):
        RECOVERED = "recovered", "Recovered"
        RECOVERING = "recovering", "Recovering"
        NO_IMPROVEMENT = "no_improvement", "No improvement"
        WORSENING = "worsening", "Worsening"

    class EventType(models.TextChoices):
        CONSULTATION = "consultation", "Consultation"
        DIAGNOSIS = "diagnosis", "Diagnosis"
        PRESCRIPTION = "prescription", "Prescription"
        TEST = "test", "Test"
        RESULT = "result", "Result"
        FOLLOW_UP = "follow_up", "Follow-up"
        PHASE_FAILED = "phase_failed", "Phase failed"
        PHASE_COMPLETED = "phase_completed", "Phase completed"
        NOTE = "note", "Note"

    event_id = models.UUIDField(
        default=uuid.uuid4,
        editable=False,
        unique=True,
    )
    treatment_episode = models.ForeignKey(
        TreatmentEpisode,
        on_delete=models.CASCADE,
        related_name="events",
    )
    treatment_phase = models.ForeignKey(
        TreatmentPhase,
        null=True,
        blank=True,
        on_delete=models.PROTECT,
        related_name="events",
    )
    appointment = models.ForeignKey(
        Appointment,
        null=True,
        blank=True,
        on_delete=models.PROTECT,
        related_name="treatment_events",
    )
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="treatment_events",
    )
    event_type = models.CharField(max_length=30, choices=EventType.choices)
    title = models.CharField(max_length=200)
    description = models.TextField()
    result = models.TextField(blank=True)
    outcome = models.CharField(max_length=20, choices=Outcome.choices, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["created_at"]


class SessionToken(models.Model):
    token_hash = models.CharField(max_length=64, unique=True)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="session_tokens",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()

    class Meta:
        indexes = [
            models.Index(fields=["user", "expires_at"]),
            models.Index(fields=["expires_at"]),
        ]

class ImmutableBlockError(Exception):
    pass


class Block(models.Model):
    class Chain(models.TextChoices):
        USER = "user", "User chain"
        DOCTOR = "doctor", "Doctor chain"

    treatment_episode = models.ForeignKey(
        TreatmentEpisode, on_delete=models.PROTECT, related_name="blocks"
    )
    chain = models.CharField(max_length=10, choices=Chain.choices)

    # header
    index = models.PositiveIntegerField()
    prev_hash = models.CharField(max_length=64)
    merkle_root = models.CharField(max_length=64)
    timestamp = models.BigIntegerField()
    nonce = models.BigIntegerField(default=0)
    block_hash = models.CharField(max_length=64, unique=True)

    # body (event is null only for the genesis block)
    event = models.OneToOneField(
        TreatmentEvent, null=True, blank=True,
        on_delete=models.PROTECT, related_name="block",
    )
    tx_hash = models.CharField(max_length=64)
    signature = models.TextField(blank=True)
    payload_enc = models.BinaryField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["treatment_episode_id", "chain", "index"]
        constraints = [
            models.UniqueConstraint(
                fields=["treatment_episode", "chain", "index"],
                name="unique_block_index_per_chain",
            ),
        ]

    @property
    def chain_id(self):
        return f"{self.treatment_episode_id}:{self.chain}"

    def compute_hash(self):
        return ledger.header_hash(
            chain_id=self.chain_id, index=self.index, prev_hash=self.prev_hash,
            merkle_root=self.merkle_root, timestamp=self.timestamp, nonce=self.nonce,
        )

    def save(self, *args, **kwargs):
        if self.pk is not None:
            raise ImmutableBlockError("Blocks cannot be modified.")
        super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        raise ImmutableBlockError("Blocks cannot be deleted.")

class EpisodeKey(models.Model):
    treatment_episode = models.OneToOneField(
        TreatmentEpisode, on_delete=models.PROTECT, related_name="key"
    )
    wrapped_dek = models.BinaryField()
    kek_id = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)

class Anchor(models.Model):
    treatment_episode = models.ForeignKey(TreatmentEpisode, on_delete=models.PROTECT, related_name="anchors")
    chain = models.CharField(max_length=10, choices=Block.Chain.choices)
    block_index = models.PositiveIntegerField()
    block_hash = models.CharField(max_length=64)
    tx_hash = models.CharField(max_length=66)
    eth_block = models.PositiveIntegerField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["created_at"]