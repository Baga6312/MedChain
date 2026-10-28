from django.db import migrations


def create_profile_records(apps, schema_editor):
    UserProfile = apps.get_model("healthcare", "UserProfile")
    Doctor = apps.get_model("healthcare", "Doctor")
    Patient = apps.get_model("healthcare", "Patient")

    for profile in UserProfile.objects.select_related("user").all():
        user = profile.user
        name = f"{user.first_name} {user.last_name}".strip() or user.email or user.username
        if profile.role == "doctor":
            Doctor.objects.get_or_create(
                user_id=user.pk,
                defaults={"name": name, "specialty": "À définir"},
            )
        elif profile.role == "patient":
            Patient.objects.get_or_create(
                user_id=user.pk,
                defaults={"name": name, "phone": profile.phone},
            )


class Migration(migrations.Migration):
    dependencies = [
        ("healthcare", "0006_link_profiles_to_records"),
    ]

    operations = [
        migrations.RunPython(create_profile_records, migrations.RunPython.noop),
    ]
