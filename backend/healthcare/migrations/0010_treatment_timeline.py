import uuid

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ("healthcare", "0009_rename_session_token_indexes"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name="TreatmentPhase",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "sequence_number",
                    models.PositiveIntegerField(),
                ),
                ("name", models.CharField(max_length=150)),
                (
                    "status",
                    models.CharField(
                        choices=[
                            ("pending", "Pending"),
                            ("active", "Active"),
                            ("completed", "Completed"),
                            ("failed", "Failed"),
                            ("skipped", "Skipped"),
                        ],
                        default="pending",
                        max_length=20,
                    ),
                ),
                ("summary", models.TextField(blank=True)),
                ("failure_reason", models.TextField(blank=True)),
                ("started_at", models.DateTimeField(blank=True, null=True)),
                ("completed_at", models.DateTimeField(blank=True, null=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                (
                    "treatment_episode",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="phases",
                        to="healthcare.treatmentepisode",
                    ),
                ),
            ],
            options={"ordering": ["sequence_number", "created_at"]},
        ),
        migrations.AddConstraint(
            model_name="treatmentphase",
            constraint=models.UniqueConstraint(
                fields=("treatment_episode", "sequence_number"),
                name="unique_phase_sequence_per_episode",
            ),
        ),
        migrations.CreateModel(
            name="TreatmentEvent",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "event_id",
                    models.UUIDField(
                        default=uuid.uuid4,
                        editable=False,
                        unique=True,
                    ),
                ),
                (
                    "event_type",
                    models.CharField(
                        choices=[
                            ("consultation", "Consultation"),
                            ("diagnosis", "Diagnosis"),
                            ("prescription", "Prescription"),
                            ("test", "Test"),
                            ("result", "Result"),
                            ("follow_up", "Follow-up"),
                            ("phase_failed", "Phase failed"),
                            ("phase_completed", "Phase completed"),
                            ("note", "Note"),
                        ],
                        max_length=30,
                    ),
                ),
                ("title", models.CharField(max_length=200)),
                ("description", models.TextField()),
                ("result", models.TextField(blank=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                (
                    "appointment",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name="treatment_events",
                        to="healthcare.appointment",
                    ),
                ),
                (
                    "author",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name="treatment_events",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
                (
                    "treatment_episode",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="events",
                        to="healthcare.treatmentepisode",
                    ),
                ),
                (
                    "treatment_phase",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name="events",
                        to="healthcare.treatmentphase",
                    ),
                ),
            ],
            options={"ordering": ["created_at"]},
        ),
    ]
