# Generated by Django 5.0.3 on 2024-05-20 22:25

from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("app", "0003_folders_name_folder_eng"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="folders",
            name="name_folder_eng",
        ),
    ]
