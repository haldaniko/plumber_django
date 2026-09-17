from django.db import migrations


HIDDEN_HERO_TEXT_KEYS = (
    "hero_headline_line_1",
    "hero_headline_line_2",
    "hero_summary_line_1",
    "hero_summary_line_2",
)


def remove_hidden_hero_texts(apps, schema_editor):
    SiteText = apps.get_model("pages", "SiteText")
    SiteText.objects.filter(key__in=HIDDEN_HERO_TEXT_KEYS).delete()


class Migration(migrations.Migration):

    dependencies = [
        ("pages", "0007_merge_request_title_text"),
    ]

    operations = [
        migrations.RunPython(remove_hidden_hero_texts, migrations.RunPython.noop),
    ]
