from django.contrib import admin

from .models import (
    Appointment,
    AuditLog,
    Doctor,
    MedicalRecord,
    Patient,
    SecurityAlert,
    UserProfile,
)

admin.site.register(Doctor)
admin.site.register(Patient)
admin.site.register(Appointment)
admin.site.register(MedicalRecord)
admin.site.register(UserProfile)
admin.site.register(AuditLog)
admin.site.register(SecurityAlert)