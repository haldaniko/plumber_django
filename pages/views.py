import json

from django.contrib import messages
from django.shortcuts import redirect, render
from django.views.decorators.http import require_POST

from .models import ProjectCase, ProjectTag, RequestSubmission, SiteSettings


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


@require_POST
def submit_request(request):
    request_type = request.POST.get("request_type") or RequestSubmission.GENERAL
    valid_types = {choice[0] for choice in RequestSubmission.REQUEST_TYPE_CHOICES}
    if request_type not in valid_types:
        request_type = RequestSubmission.GENERAL

    name = request.POST.get("name", "").strip()
    phone = request.POST.get("phone", "").strip()
    message = request.POST.get("message", "").strip()

    if name and phone:
        RequestSubmission.objects.create(
            name=name,
            phone=phone,
            message=message,
            request_type=request_type,
        )
        messages.success(request, "Your request has been submitted.")
    else:
        messages.error(request, "Please enter your name and phone number.")

    return redirect("/#contact")
