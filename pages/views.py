from django.shortcuts import render
import json

from .models import ProjectCase, ProjectTag, SiteSettings


def home(request):
    site_settings = SiteSettings.load()
    tags = list(ProjectTag.objects.filter(is_active=True))
    projects = list(
        ProjectCase.objects.select_related("tag")
        .prefetch_related("images")
        .filter(is_active=True, tag__is_active=True)
    )

    for tag in tags:
        tag.active_count = sum(1 for project in projects if project.tag_id == tag.id)

    for project in projects:
        images = [image.image.url for image in project.images.all() if image.image]
        project.album_json = json.dumps(images)
        project.cover_url = images[0] if images else "/static/plumber/assets/images/gallery/image-1.jpg"

    return render(
        request,
        "plumber/index.html",
        {
            "site_settings": site_settings,
            "project_tags": tags,
            "projects": projects,
        },
    )
