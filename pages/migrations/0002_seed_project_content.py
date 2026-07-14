from django.db import migrations


def seed_content(apps, schema_editor):
    SiteSettings = apps.get_model("pages", "SiteSettings")
    ProjectTag = apps.get_model("pages", "ProjectTag")
    ProjectCase = apps.get_model("pages", "ProjectCase")
    ProjectCaseImage = apps.get_model("pages", "ProjectCaseImage")

    SiteSettings.objects.get_or_create(
        pk=1,
        defaults={
            "phone": "+1 845 678 899",
            "email": "info@example.com",
            "address": "Dallas, TX",
        },
    )

    tags = {}
    for index, (name, slug) in enumerate(
        [
            ("Residential", "residential"),
            ("Commercial", "commercial"),
            ("Repairs", "repairs"),
            ("Installation", "installation"),
        ],
        start=1,
    ):
        tag, _ = ProjectTag.objects.get_or_create(
            slug=slug,
            defaults={"name": name, "sort_order": index, "is_active": True},
        )
        tags[slug] = tag

    cases = [
        (
            "Interior Painting",
            "residential",
            "Interior painting project with careful surface preparation, wall repair, clean masking, and a smooth finish selected to match the room design.",
            "image-1.jpg",
        ),
        (
            "Deck Installation",
            "installation",
            "Outdoor deck work planned for daily use, with material handling, precise installation, and clean finishing around visible edges.",
            "image-2.jpg",
        ),
        (
            "Wall Restoration",
            "repairs",
            "Wall restoration after surface damage, including patching, leveling, sanding, priming, and painting for a clean final result.",
            "image-3.jpg",
        ),
        (
            "Flooring Replacement",
            "commercial",
            "Flooring replacement with old covering removal, material delivery, installation, and finishing details such as trims and baseboards.",
            "image-4.jpg",
        ),
        (
            "Exterior Coating",
            "repairs",
            "Exterior coating and painting work for durable surfaces such as fences, garages, concrete, asphalt, and outdoor structures.",
            "image-5.jpg",
        ),
        (
            "Baseboard Installation",
            "residential",
            "Trim and baseboard installation completed with accurate cuts, clean joints, and finishing work that ties the room together.",
            "image-6.jpg",
        ),
        (
            "Stair Finishing",
            "residential",
            "Stair finishing and repair work focused on solid installation, neat transitions, and a polished surface ready for everyday traffic.",
            "image-7.jpg",
        ),
        (
            "Custom Repair Work",
            "commercial",
            "Custom repair and improvement work for creative or unusual tasks that require flexible planning and hands-on problem solving.",
            "image-8.jpg",
        ),
    ]

    for index, (title, tag_slug, description, image_name) in enumerate(cases, start=1):
        project, _ = ProjectCase.objects.get_or_create(
            title=title,
            defaults={
                "tag": tags[tag_slug],
                "description": description,
                "sort_order": index,
                "is_active": True,
            },
        )
        ProjectCaseImage.objects.get_or_create(
            project=project,
            sort_order=1,
            defaults={
                "image": f"../static/plumber/assets/images/gallery/{image_name}",
                "alt_text": title,
            },
        )


def unseed_content(apps, schema_editor):
    ProjectCase = apps.get_model("pages", "ProjectCase")
    ProjectTag = apps.get_model("pages", "ProjectTag")

    ProjectCase.objects.filter(
        title__in=[
            "Interior Painting",
            "Deck Installation",
            "Wall Restoration",
            "Flooring Replacement",
            "Exterior Coating",
            "Baseboard Installation",
            "Stair Finishing",
            "Custom Repair Work",
        ]
    ).delete()
    ProjectTag.objects.filter(slug__in=["residential", "commercial", "repairs", "installation"]).delete()


class Migration(migrations.Migration):
    dependencies = [
        ("pages", "0001_initial"),
    ]

    operations = [
        migrations.RunPython(seed_content, unseed_content),
    ]
