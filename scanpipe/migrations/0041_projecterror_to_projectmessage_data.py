# Generated by Django 4.2.3 on 2023-07-12 12:13

from django.db import migrations


def migrate_error_to_message_data(apps, schema_editor):
    ProjectError = apps.get_model("scanpipe", "ProjectError")
    ProjectMessage = apps.get_model("scanpipe", "ProjectMessage")
    ERROR = "error"

    for project_error in ProjectError.objects.all():
        ProjectMessage.objects.create(
            project=project_error.project,
            severity=ERROR,
            description=project_error.message,
            model=project_error.model,
            details=project_error.details,
            traceback=project_error.traceback,
        )


def reverse_migrate_message_to_error_data(apps, schema_editor):
    ProjectError = apps.get_model("scanpipe", "ProjectError")
    ProjectMessage = apps.get_model("scanpipe", "ProjectMessage")

    for project_message in ProjectMessage.objects.all():
        ProjectError.objects.create(
            project=project_message.project,
            message=project_message.description,
            model=project_message.model,
            details=project_message.details,
            traceback=project_message.traceback,
        )


class Migration(migrations.Migration):
    dependencies = [
        ("scanpipe", "0040_projectmessage"),
    ]

    operations = [
        migrations.RunPython(
            migrate_error_to_message_data,
            reverse_code=reverse_migrate_message_to_error_data,
        ),
    ]
