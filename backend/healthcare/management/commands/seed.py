from datetime import timedelta

from django.core.management.base import BaseCommand
from django.utils import timezone

from healthcare.models import Appointment, Doctor, Patient


class Command(BaseCommand):
    help = "Seed the database with test data"

    def handle(self, *args, **kwargs):
        if Doctor.objects.exists():
            self.stdout.write("Already seeded")
            return

        doctors = [
            Doctor.objects.create(name=f"Doctor {i}", specialty=spec)
            for i, spec in enumerate(["Cardiology", "Neurology", "Pediatrics"], 1)
        ]
        patients = [
            Patient.objects.create(name=f"Patient {i}", phone=f"2000000{i}")
            for i in range(1, 6)
        ]
        for i, pat in enumerate(patients):
            Appointment.objects.create(
                patient=pat,
                doctor=doctors[i % len(doctors)],
                date=timezone.now() + timedelta(days=i + 1),
                notes="Seeded appointment",
            )
        self.stdout.write(self.style.SUCCESS("Seed done"))
