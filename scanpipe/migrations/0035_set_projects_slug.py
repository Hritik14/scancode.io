# Generated by Django 4.2.2 on 2023-06-28 09:37

from django.db import migrations


def get_project_slug(project):
    """
    Return a "slug" value for the provided ``project`` based on the slugify name
    attribute combined with the ``short_uuid`` to ensure its uniqueness.
    """
    from django.utils.text import slugify

    short_uuid = str(project.uuid)[0:8]
    return f"{slugify(project.name)}-{short_uuid}"


def set_projects_slug(apps, schema_editor):
    """
    Compute DiscoveredPackage `declared_license_expression_spdx`, when missing,
    from `declared_license_expression`, when available.
    """
    Project = apps.get_model("scanpipe", "Project")

    for project in Project.objects.all():
        project.slug = get_project_slug(project)
        project.save(update_fields=["slug"])


class Migration(migrations.Migration):
    dependencies = [
        ("scanpipe", "0034_project_slug"),
    ]

    operations = [
        migrations.RunPython(set_projects_slug),
    ]