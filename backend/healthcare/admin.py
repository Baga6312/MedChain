from django.contrib import admin

from .models import AccessPermission, Appointment, AuditLog, Doctor, MedicalRecord, Patient

admin.site.register(Doctor)
admin.site.register(Patient)
admin.site.register(Appointment)
admin.site.register(MedicalRecord)
admin.site.register(AccessPermission)
# Read-only: the audit trail is evidence. Exposing it in the change form would
# let an admin edit history, which is worse than having no history at all.
admin.site.register(AuditLog, readonly_fields=[f.name for f in AuditLog._meta.fields])