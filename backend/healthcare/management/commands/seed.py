from datetime import timedelta

from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from django.utils import timezone

from healthcare.models import Appointment, Doctor, MedicalRecord, Patient, UserProfile


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
        for index, patient in enumerate(patients, 1):
            user, _ = User.objects.get_or_create(username=f"patient{index}")
            user.set_password("DemoPass123!")
            user.save(update_fields=["password"])
            UserProfile.objects.update_or_create(user=user, defaults={"role": UserProfile.Role.PATIENT})
            patient.user = user
            patient.save(update_fields=["user"])
            if not patient.medical_records.exists():
                MedicalRecord.objects.create(patient=patient, title="Dossier de démonstration", content="Donnée médicale fictive", created_by=user)
        for index, doctor in enumerate(doctors, 1):
            user, _ = User.objects.get_or_create(username=f"doctor{index}")
            user.set_password("DemoPass123!")
            user.save(update_fields=["password"])
            UserProfile.objects.update_or_create(user=user, defaults={"role": UserProfile.Role.DOCTOR})
            doctor.user = user
            doctor.save(update_fields=["user"])
        admin, _ = User.objects.get_or_create(username="admin")
        admin.is_staff = True
        admin.is_superuser = True
        admin.set_password("DemoPass123!")
        admin.save()
        UserProfile.objects.update_or_create(user=admin, defaults={"role": UserProfile.Role.ADMIN})
        self.stdout.write(self.style.SUCCESS("Seed done"))
