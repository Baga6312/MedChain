"""Serializers for the healthcare API.

Two changes from the previous version, both required by the views refactor:

  * `id` is read-only on every serializer. Previously it was
    `"read_only": False, "required": True`, which let a client choose its own
    primary key on create and gave PUT a second way to name the target row
    alongside the URL. The server assigns the pk; the URL identifies the row.

  * The appointment business rules moved here from AppointmentViewSet, where
    they were implemented twice and the update() copy was missing one of them.
    validate() runs on create, update and partial update alike, so there is now
    a single implementation the caller cannot route around.
"""

from rest_framework import serializers

from .models import (
    Appointment,
    Doctor,
    MedicalRecord,
    Patient,
    TreatmentEvent,
    TreatmentPhase,
)


class DoctorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Doctor
        fields = ["id", "name", "specialty"]
        read_only_fields = ["id"]
        extra_kwargs = {
            "name": {"required": True},
            "specialty": {"required": True},
        }


class PatientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Patient
        fields = ["id", "name", "birth_date", "phone"]
        read_only_fields = ["id"]
        extra_kwargs = {
            "name": {"required": True},
            "birth_date": {"required": True, "allow_null": True},
            "phone": {"required": True},
        }


class AppointmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Appointment
        fields = ["id", "patient", "doctor", "treatment_episode", "date", "notes", "status"]
        read_only_fields = ["id", "treatment_episode"]
        extra_kwargs = {
            "notes": {"required": True, "allow_blank": False},
        }

    def validate(self, attrs):
        """Enforce the two appointment rules for every write.

        Both rules previously lived in the viewset. They are data invariants,
        not HTTP concerns, and validate() runs for create, update and partial
        update -- the previous split put them in create() and update() with
        different code, and update() never checked the second rule at all.

        Rule 1: a patient is assigned to at most one doctor. An appointment
        that changes the doctor re-checks every other appointment for that
        patient.

        Rule 2: a patient cannot have two active (pending or on-going)
        appointments with the same doctor.

        On update, the appointment being edited is excluded from both lookups.
        Without that exclusion a no-op PUT -- resubmitting the row unchanged --
        would find the row itself and reject itself.
        """
        attrs = super().validate(attrs)

        # A PATCH may supply only one of these, so fall back to the instance
        # being edited. Without this, a partial update of `date` alone would
        # validate against patient=None and match every appointment in the table.
        instance = getattr(self, "instance", None)
        patient = attrs.get("patient", getattr(instance, "patient", None))
        doctor = attrs.get("doctor", getattr(instance, "doctor", None))
        if patient is None or doctor is None:
            # Missing on create, or unset: field validation already reported it.
            return attrs

        others = Appointment.objects.filter(patient=patient)
        if instance is not None:
            others = others.exclude(pk=instance.pk)

        if others.exclude(doctor=doctor).exists():
            raise serializers.ValidationError(
                {"doctor": "This patient is already assigned to a different doctor."}
            )

        active_statuses = [
            Appointment.Status.PENDING,
            Appointment.Status.ON_GOING,
        ]
        if others.filter(doctor=doctor, status__in=active_statuses).exists():
            raise serializers.ValidationError(
                {
                    "doctor": (
                        "This patient already has an ongoing appointment "
                        "with this doctor."
                    )
                }
            )

        return attrs


class MedicalRecordSerializer(serializers.ModelSerializer):
    class Meta:
        model = MedicalRecord
        fields = [
            "id",
            "patient",
            "treatment_episode",
            "title",
            "content",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "treatment_episode", "created_at", "updated_at"]
        extra_kwargs = {
            "patient": {"required": True},
            "title": {"required": True},
            "content": {"required": True},
        }


class TreatmentPhaseSerializer(serializers.ModelSerializer):
    class Meta:
        model = TreatmentPhase
        fields = [
            "id",
            "sequence_number",
            "name",
            "status",
            "summary",
            "failure_reason",
            "started_at",
            "completed_at",
            "created_at",
        ]
        read_only_fields = [
            "id",
            "sequence_number",
            "started_at",
            "completed_at",
            "created_at",
        ]


class TreatmentEventSerializer(serializers.ModelSerializer):
    author_name = serializers.SerializerMethodField()

    class Meta:
        model = TreatmentEvent
        fields = [
            "event_id",
            "treatment_phase",
            "appointment",
            "author",
            "author_name",
            "event_type",
            "title",
            "description",
            "result",
            "created_at",
        ]
        read_only_fields = ["event_id", "author", "author_name", "created_at"]

    def get_author_name(self, obj):
        return obj.author.get_full_name() or obj.author.email