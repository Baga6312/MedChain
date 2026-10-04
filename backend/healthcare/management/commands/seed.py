from datetime import timedelta

from django.core.management.base import BaseCommand
from django.utils import timezone

from healthcare.models import Appointment, Doctor, MedicalRecord, Patient


class Command(BaseCommand):
    help = "Seed the database with test data"

    def handle(self, *args, **kwargs):
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