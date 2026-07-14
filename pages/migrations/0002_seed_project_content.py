from django.core.management import call_command
from django.db import migrations


def load_mock_data(apps, schema_editor):
    call_command("loaddata", "mock_data", verbosity=0)


def unload_mock_data(apps, schema_editor):
    SiteSettings = apps.get_model("pages", "SiteSettings")
    ProjectCase = apps.get_model("pages", "ProjectCase")
    ProjectTag = apps.get_model("pages", "ProjectTag")

    ProjectCase.objects.filter(pk__in=range(1, 9)).delete()
    ProjectTag.objects.filter(pk__in=range(1, 5)).delete()
    SiteSettings.objects.filter(pk=1).delete()


class Migration(migrations.Migration):
    dependencies = [
        ("pages", "0001_initial"),
    ]

    operations = [
        migrations.RunPython(load_mock_data, unload_mock_data),
    ]
