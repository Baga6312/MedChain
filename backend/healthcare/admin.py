from django.contrib import admin

from .models import Appointment, Doctor, MedicalRecord, Patient

admin.site.register(Doctor)
admin.site.register(Patient)
admin.site.register(Appointment)
admin.site.register(MedicalRecord)