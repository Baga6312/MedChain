import os
from datetime import timedelta

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand
from django.utils import timezone

from healthcare.models import AccessPermission, Appointment, Doctor, MedicalRecord, Patient

# Published in README.md. Demo data only -- override SEED_PASSWORD for any
# shared environment.
SEED_PASSWORD = os.environ.get("SEED_PASSWORD", "DemoPass123!")


class Command(BaseCommand):
    help = "Seed the database with test data"

    def handle(self, *args, **kwargs):
        User = get_user_model()

        def account(username, is_superuser=False):
            # Password is rewritten on every run so the documented demo
            # credentials keep working after a container restart.
            user, created = User.objects.get_or_create(
                username=username, defaults={"is_superuser": is_superuser}
            )
            user.is_superuser = is_superuser
            user.set_password(SEED_PASSWORD)
            user.save()
            return user

        doctors = [
            Doctor.objects.get_or_create(name=f"Doctor {i}", defaults={"specialty": spec})[0]
            for i, spec in enumerate(["Cardiology", "Neurology", "Pediatrics"], 1)
        ]
        patients = [
            Patient.objects.get_or_create(name=f"Patient {i}", defaults={"phone": f"2000000{i}"})[0]
            for i in range(1, 6)
        ]

        # Link accounts to rows by name. Written as an explicit update rather
        # than a get_or_create default: on a database seeded before auth
        # existed, the rows already exist and a default would never be applied,
        # leaving every user with no role.
        for i, doctor in enumerate(doctors, 1):
            doctor.user = account(f"doctor{i}")
            doctor.save(update_fields=["user"])
        for i, patient in enumerate(patients, 1):
            patient.user = account(f"patient{i}")
            patient.save(update_fields=["user"])
        admin_user = account("admin", is_superuser=True)

        for i, pat in enumerate(patients):
            doctor = doctors[i % len(doctors)]
            # Without a grant, doctor1 logs in and sees an empty list, which
            # reads as a broken seed rather than a working one.
            AccessPermission.objects.update_or_create(
                patient=pat, doctor=doctor, defaults={"revoked_at": None}
            )
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

        self.stdout.write(self.style.SUCCESS(f"Seed done. Accounts: patient1..5, doctor1..3, admin ({admin_user.username})"))