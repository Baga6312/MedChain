import os

from datetime import timedelta

from django.core.management.base import BaseCommand, CommandError
from django.contrib.auth import get_user_model
from django.utils import timezone

from healthcare.models import (
    Appointment,
    Doctor,
    MedicalRecord,
    Patient,
    TreatmentEpisode,
    TreatmentEvent,
    TreatmentPhase,
    UserProfile,
)


class Command(BaseCommand):
    help = "Seed the database with test data"

    def handle(self, *args, **kwargs):
        admin_email = os.environ.get("MEDCHAIN_ADMIN_EMAIL")
        admin_password = os.environ.get("MEDCHAIN_ADMIN_PASSWORD")
        if not admin_email or not admin_password:
            raise CommandError(
                "MEDCHAIN_ADMIN_EMAIL and MEDCHAIN_ADMIN_PASSWORD must be set."
            )

        User = get_user_model()
        admin, created = User.objects.get_or_create(
            username=admin_email,
            defaults={
                "email": admin_email,
                "first_name": "MedChain",
                "last_name": "Administrator",
                "is_staff": True,
                "is_superuser": True,
            },
        )
        if created:
            admin.set_password(admin_password)
            admin.save(update_fields=["password"])
        else:
            update_fields = []
            if not admin.is_staff:
                admin.is_staff = True
                update_fields.append("is_staff")
            if not admin.is_superuser:
                admin.is_superuser = True
                update_fields.append("is_superuser")
            if update_fields:
                admin.save(update_fields=update_fields)
        UserProfile.objects.get_or_create(user=admin, defaults={"role": UserProfile.Role.ADMIN})

        demo_password = os.environ.get("MEDCHAIN_DEMO_PASSWORD", "MedChainDemo123!")
        demo_doctor_user, _ = User.objects.get_or_create(
            username="demo.doctor@medchain.local",
            defaults={"email": "demo.doctor@medchain.local", "first_name": "Demo", "last_name": "Doctor"},
        )
        demo_doctor_user.set_password(demo_password)
        demo_doctor_user.save(update_fields=["password"])
        UserProfile.objects.update_or_create(user=demo_doctor_user, defaults={"role": UserProfile.Role.DOCTOR})
        demo_patient_user, _ = User.objects.get_or_create(
            username="demo.patient@medchain.local",
            defaults={"email": "demo.patient@medchain.local", "first_name": "Demo", "last_name": "Patient"},
        )
        demo_patient_user.set_password(demo_password)
        demo_patient_user.save(update_fields=["password"])
        UserProfile.objects.update_or_create(user=demo_patient_user, defaults={"role": UserProfile.Role.PATIENT})
        doctors = [
            Doctor.objects.get_or_create(name=f"Doctor {i}", defaults={"specialty": spec})[0]
            for i, spec in enumerate(["Cardiology", "Neurology", "Pediatrics"], 1)
        ]
        doctors[0].user = demo_doctor_user
        doctors[0].save(update_fields=["user"])
        patients = [
            Patient.objects.get_or_create(name=f"Patient {i}", defaults={"phone": f"2000000{i}"})[0]
            for i in range(1, 6)
        ]
        patients[0].user = demo_patient_user
        patients[0].save(update_fields=["user"])
        for i, pat in enumerate(patients):
            doctor = doctors[i % len(doctors)]
            if not Appointment.objects.filter(patient=pat, doctor=doctor).exists():
                Appointment.objects.create(
                    patient=pat,
                    doctor=doctor,
                    date=timezone.now() + timedelta(days=i + 1),
                    notes="Seeded appointment",
                )
            if not pat.medical_records.exists():
                MedicalRecord.objects.create(
                    patient=pat,
                    title="Demo record",
                    content="Sample medical data",
                )

        episode, _ = TreatmentEpisode.objects.get_or_create(
            patient=patients[0],
            doctor=doctors[0],
            status=TreatmentEpisode.Status.ACTIVE,
            defaults={"reason": "Suivi de démonstration", "notes": "Données de démonstration"},
        )
        phase_specs = [
            ("Évaluation initiale", TreatmentPhase.Status.COMPLETED, "Consultation et collecte des symptômes."),
            ("Traitement prescrit", TreatmentPhase.Status.FAILED, "La première médication n'a pas produit l'effet attendu."),
            ("Bilan de suivi", TreatmentPhase.Status.PENDING, "Rendez-vous de contrôle à venir."),
        ]
        phases = []
        for sequence, (name, phase_status, summary) in enumerate(phase_specs, 1):
            phase, _ = TreatmentPhase.objects.get_or_create(
                treatment_episode=episode,
                sequence_number=sequence,
                defaults={"name": name, "status": phase_status, "summary": summary},
            )
            if sequence == 2:
                phase.status = TreatmentPhase.Status.FAILED
                phase.failure_reason = "Réponse insuffisante au traitement prescrit."
                phase.completed_at = phase.completed_at or timezone.now()
                phase.save(update_fields=["status", "failure_reason", "completed_at"])
            phases.append(phase)
        if not episode.events.exists():
            TreatmentEvent.objects.create(
                treatment_episode=episode,
                treatment_phase=phases[0],
                author=demo_doctor_user,
                event_type=TreatmentEvent.EventType.CONSULTATION,
                title="Consultation initiale",
                description="Le patient décrit une amélioration progressive.",
                result="Poursuite du suivi recommandée.",
            )
            TreatmentEvent.objects.create(
                treatment_episode=episode,
                treatment_phase=phases[1],
                author=demo_patient_user,
                event_type=TreatmentEvent.EventType.NOTE,
                title="Retour du patient",
                description="La première semaine de traitement est bien tolérée.",
            )
        if not TreatmentEvent.objects.filter(
            treatment_episode=episode,
            treatment_phase=phases[1],
            event_type=TreatmentEvent.EventType.PHASE_FAILED,
        ).exists():
            TreatmentEvent.objects.create(
                treatment_episode=episode,
                treatment_phase=phases[1],
                author=demo_doctor_user,
                event_type=TreatmentEvent.EventType.PHASE_FAILED,
                title="Traitement prescrit échoué",
                description=phases[1].failure_reason,
            )

        self.stdout.write(self.style.SUCCESS(
            "Seed done. Demo accounts: demo.patient@medchain.local and "
            f"demo.doctor@medchain.local (password: {demo_password})"
        ))