from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("healthcare", "0008_treatmenteEpisode_links"),
    ]

    operations = [
        migrations.RenameIndex(
            model_name="sessiontoken",
            new_name="healthcare__user_id_ea200b_idx",
            old_name="healthcare__user_id_9a9d8f_idx",
        ),
        migrations.RenameIndex(
            model_name="sessiontoken",
            new_name="healthcare__expires_df91b4_idx",
            old_name="healthcare__expires_7f6d7f_idx",
        ),
    ]
