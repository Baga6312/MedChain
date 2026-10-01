from django.contrib import admin

from .models import AccessPermission, AuditLog, MedicalRecord, UserProfile


admin.site.register((UserProfile, MedicalRecord, AccessPermission, AuditLog))

from .models import Appointment, Doctor, Patient

admin.site.register(Doctor)
admin.site.register(Patient)
admin.site.register(Appointment)
