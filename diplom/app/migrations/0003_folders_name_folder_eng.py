# Generated by Django 5.0.3 on 2024-05-20 14:29

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("app", "0002_folders_trees_json_folder_pk"),
    ]

    operations = [
        migrations.AddField(
            model_name="folders",
            name="name_folder_eng",
            field=models.CharField(
                default="moscow",
                max_length=30,
                verbose_name="Название_папки на английском",
            ),
        ),
    ]
