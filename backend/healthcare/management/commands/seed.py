import os

from datetime import timedelta

from django.core.management.base import BaseCommand, CommandError
from django.contrib.auth import get_user_model
from django.utils import timezone

from healthcare.models import Appointment, Doctor, MedicalRecord, Patient, UserProfile


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

        doctors = [
            Doctor.objects.get_or_create(name=f"Doctor {i}", defaults={"specialty": spec})[0]
            for i, spec in enumerate(["Cardiology", "Neurology", "Pediatrics"], 1)
        ]
        patients = [
            Patient.objects.get_or_create(name=f"Patient {i}", defaults={"phone": f"2000000{i}"})[0]
            for i in range(1, 6)
        ]
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

        self.stdout.write(self.style.SUCCESS("Seed done"))