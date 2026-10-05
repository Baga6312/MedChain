from rest_framework import serializers

from .models import Appointment, Doctor, MedicalRecord, Patient


class DoctorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Doctor
        fields = ["id", "name", "specialty"]
        extra_kwargs = {
            "id": {"read_only": False, "required": True},
            "name": {"required": True},
            "specialty": {"required": True},
        }


class PatientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Patient
        fields = ["id", "name", "birth_date", "phone"]
        extra_kwargs = {
            "id": {"read_only": False, "required": True},
            "name": {"required": True},
            "birth_date": {"required": True, "allow_null": True},
            "phone": {"required": True},
        }


class AppointmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Appointment
        fields = ["id", "patient", "doctor", "date", "notes", "status"]
        extra_kwargs = {
            "notes": {"required": True, "allow_blank": False},
        }
        

class MedicalRecordSerializer(serializers.ModelSerializer):
    class Meta:
        model = MedicalRecord
        fields = ["id", "patient", "title", "content", "created_at", "updated_at"]
        read_only_fields = ["created_at", "updated_at"]
        extra_kwargs = {
            "id": {"read_only": False, "required": True},
            "patient": {"required": True},
            "title": {"required": True},
            "content": {"required": True},
        }