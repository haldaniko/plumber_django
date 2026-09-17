from django.db import migrations


REQUEST_TITLE_KEY = "request_title"
REQUEST_TITLE_LABEL = "Request title"
REQUEST_TITLE_DEFAULT = "Tell Us What Kind Of Project You Need"
REQUEST_TITLE_LINE_KEYS = ("request_title_line_1", "request_title_line_2")


def merge_request_title(apps, schema_editor):
    SiteText = apps.get_model("pages", "SiteText")

    first_line = SiteText.objects.filter(key="request_title_line_1").values_list("text", flat=True).first()
    second_line = SiteText.objects.filter(key="request_title_line_2").values_list("text", flat=True).first()
    combined_title = " ".join(part.strip() for part in (first_line, second_line) if part and part.strip())

    SiteText.objects.update_or_create(
        key=REQUEST_TITLE_KEY,
        defaults={
            "label": REQUEST_TITLE_LABEL,
            "text": combined_title or REQUEST_TITLE_DEFAULT,
        },
    )
    SiteText.objects.filter(key__in=REQUEST_TITLE_LINE_KEYS).delete()


def split_request_title(apps, schema_editor):
    SiteText = apps.get_model("pages", "SiteText")

    SiteText.objects.update_or_create(
        key="request_title_line_1",
        defaults={"label": "Request title line 1", "text": "Tell Us What Kind Of"},
    )
    SiteText.objects.update_or_create(
        key="request_title_line_2",
        defaults={"label": "Request title line 2", "text": "Project You Need"},
    )
    SiteText.objects.filter(key=REQUEST_TITLE_KEY).delete()


class Migration(migrations.Migration):

    dependencies = [
        ("pages", "0006_remove_static_site_texts"),
    ]

    operations = [
        migrations.RunPython(merge_request_title, split_request_title),
    ]
