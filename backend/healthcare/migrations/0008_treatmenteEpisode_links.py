from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ("healthcare", "0007_backfill_profile_records"),
    ]

    operations = [
        migrations.CreateModel(
            name="TreatmentEpisode",
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
                    "status",
                    models.CharField(
                        choices=[
                            ("requested", "Requested"),
                            ("active", "Active"),
                            ("abandoned", "Abandoned"),
                            ("completed", "Completed"),
                        ],
                        default="requested",
                        max_length=20,
                    ),
                ),
                ("reason", models.CharField(blank=True, max_length=255)),
                ("notes", models.TextField(blank=True)),
                ("started_at", models.DateTimeField(blank=True, null=True)),
                ("abandoned_at", models.DateTimeField(blank=True, null=True)),
                ("completed_at", models.DateTimeField(blank=True, null=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                (
                    "doctor",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="treatment_episodes",
                        to="healthcare.doctor",
                    ),
                ),
                (
                    "patient",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="treatment_episodes",
                        to="healthcare.patient",
                    ),
                ),
            ],
            options={
                "ordering": ["-created_at"],
            },
        ),
        migrations.AddConstraint(
            model_name="treatmentepisode",
            constraint=models.UniqueConstraint(
                condition=models.Q(status__in=["requested", "active"]),
                fields=("patient", "doctor"),
                name="one_open_episode_per_patient_doctor",
            ),
        ),
        migrations.AddField(
            model_name="appointment",
            name="treatment_episode",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name="appointments",
                to="healthcare.treatmentepisode",
            ),
        ),
        migrations.AddField(
            model_name="medicalrecord",
            name="treatment_episode",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name="medical_records",
                to="healthcare.treatmentepisode",
            ),
        ),
    ]
