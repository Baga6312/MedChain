from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("healthcare", "0010_treatment_timeline"),
    ]

    operations = [
        migrations.AddField(
            model_name="userprofile",
            name="avatar",
            field=models.ImageField(blank=True, null=True, upload_to="avatars/"),
        ),
    ]
