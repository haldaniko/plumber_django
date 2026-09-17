from django import forms
from django.contrib import admin, messages
from django.db import transaction
from django.db.models import Case, IntegerField, Value, When
from django.http import HttpResponseRedirect
from django.template.response import TemplateResponse
from django.utils.html import format_html

from .models import (
    LegalPage,
    ProjectCase,
    ProjectCaseImage,
    ProjectTag,
    RequestSubmission,
    SiteImage,
    SiteSettings,
    SiteText,
)


SITE_TEXT_SECTIONS = (
    {
        "number": "SEO",
        "title": "Browser and search engines",
        "description": "Page information that is not displayed inside the site content.",
        "groups": (
            {
                "title": "Page settings",
                "fields": (
                    ("meta_title", "Browser tab title", "Also used as the page title by search engines."),
                ),
            },
        ),
    },
    {
        "number": "01",
        "title": "Hero section",
        "description": "The first screen at the top of the home page.",
        "groups": (
            {
                "title": "Introductory text",
                "fields": (
                    ("hero_subtitle", "Small heading", "Short line above the introductory heading."),
                    ("hero_intro_title", "Introductory heading", "Heading in the compact text block."),
                    ("hero_intro_text", "Introductory paragraph", "Paragraph below the introductory heading."),
                ),
            },
            {
                "title": "Main heading",
                "fields": (
                    ("hero_headline_line_1", "First line", "Top line of the large heading."),
                    ("hero_headline_line_2", "Second line", "Bottom line of the large heading."),
                ),
            },
            {
                "title": "Summary",
                "fields": (
                    ("hero_summary_line_1", "First line", "Top line below the main heading."),
                    ("hero_summary_line_2", "Second line", "Bottom line below the main heading."),
                ),
            },
        ),
    },
    {
        "number": "02",
        "title": "Services section",
        "description": "Section heading, introduction, and the three service cards.",
        "groups": (
            {
                "title": "Section heading",
                "fields": (
                    ("services_subtitle", "Small heading", "Short line above the main section heading."),
                    ("services_title_line_1", "Heading, first line", "Top line of the section heading."),
                    ("services_title_line_2", "Heading, second line", "Emphasized bottom line of the section heading."),
                    ("services_intro", "Introductory paragraph", "Text shown beside the section heading."),
                ),
            },
            {
                "title": "Painting card",
                "fields": (
                    ("service_painting_title", "Card title", "Name of the painting service."),
                    ("service_painting_text", "Card description", "Description below the painting title."),
                ),
            },
            {
                "title": "Flooring card",
                "fields": (
                    ("service_flooring_title", "Card title", "Name of the flooring service."),
                    ("service_flooring_text", "Card description", "Description below the flooring title."),
                ),
            },
            {
                "title": "Custom projects card",
                "fields": (
                    ("service_custom_title", "Card title", "Name of the custom projects service."),
                    ("service_custom_text", "Card description", "Description below the custom projects title."),
                ),
            },
        ),
    },
    {
        "number": "03",
        "title": "Projects section",
        "description": "Heading above the project gallery and the estimate banner below it.",
        "groups": (
            {
                "title": "Section heading",
                "fields": (
                    ("projects_subtitle", "Small heading", "Short line above the projects heading."),
                    ("projects_title", "Main heading", "Large heading above the project gallery."),
                    ("projects_intro", "Introductory paragraph", "Text below the projects heading."),
                ),
            },
            {
                "title": "Free estimates banner",
                "fields": (
                    ("free_estimates_title", "Banner heading", "Highlighted text above the banner paragraph."),
                    ("free_estimates_text", "Banner paragraph", "Supporting text next to the request button."),
                ),
            },
        ),
    },
    {
        "number": "04",
        "title": "Company section",
        "description": "Company introduction displayed below the project gallery.",
        "groups": (
            {
                "title": "About the company",
                "fields": (
                    ("company_title", "Section heading", "Main heading for the company introduction."),
                    ("company_paragraph_1", "First paragraph", "First company information paragraph."),
                    ("company_paragraph_2", "Second paragraph", "Second company information paragraph."),
                ),
            },
        ),
    },
    {
        "number": "05",
        "title": "Request section",
        "description": "Final section with buttons for choosing a request type.",
        "groups": (
            {
                "title": "Section heading",
                "fields": (
                    ("request_title", "Main heading", "Heading above the request type buttons."),
                ),
            },
        ),
    },
)

EDITABLE_SITE_TEXT_KEYS = tuple(
    key
    for section in SITE_TEXT_SECTIONS
    for group in section["groups"]
    for key, _label, _help_text in group["fields"]
)


class SiteTextForm(forms.ModelForm):
    class Meta:
        model = SiteText
        fields = ("text",)
        widgets = {
            "text": forms.Textarea(attrs={"rows": 3}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        key = self.instance.key
        if any(part in key for part in ("paragraph", "_text", "_intro")):
            self.fields["text"].widget.attrs["rows"] = 5


class ProjectCaseImageInline(admin.TabularInline):
    model = ProjectCaseImage
    extra = 1
    fields = ("preview", "image", "alt_text", "sort_order")
    readonly_fields = ("preview",)

    def preview(self, obj):
        if obj and obj.image:
            return format_html('<img src="{}" class="sp-admin-thumb" alt="">', obj.image.url)
        return "-"


@admin.register(SiteSettings)
class SiteSettingsAdmin(admin.ModelAdmin):
    fieldsets = (
        ("Brand", {"fields": ("site_name", "primary_color", "logo_preview", "logo", "favicon_preview", "favicon")}),
        ("Contacts", {"fields": ("phone", "email", "address")}),
    )
    readonly_fields = ("logo_preview", "favicon_preview")

    def logo_preview(self, obj):
        if obj:
            return format_html('<img src="{}" class="sp-admin-thumb" alt="">', obj.logo_url)
        return "-"

    def favicon_preview(self, obj):
        if obj:
            return format_html('<img src="{}" class="sp-admin-favicon" alt="">', obj.favicon_url)
        return "-"

    def has_add_permission(self, request):
        return not SiteSettings.objects.exists()


@admin.register(SiteText)
class SiteTextAdmin(admin.ModelAdmin):
    change_list_template = "admin/pages/sitetext/change_list.html"
    list_display = ("label", "key", "updated_at")
    readonly_fields = ("label", "key")
    fields = ("label", "key", "text")

    def get_queryset(self, request):
        order = Case(
            *[When(key=key, then=Value(index)) for index, key in enumerate(EDITABLE_SITE_TEXT_KEYS)],
            output_field=IntegerField(),
        )
        return (
            super()
            .get_queryset(request)
            .filter(key__in=EDITABLE_SITE_TEXT_KEYS)
            .order_by(order)
        )

    def changelist_view(self, request, extra_context=None):
        if not self.has_view_or_change_permission(request):
            return super().changelist_view(request, extra_context)

        texts_by_key = {item.key: item for item in self.get_queryset(request)}
        sections = []
        forms_by_key = {}

        for section in SITE_TEXT_SECTIONS:
            groups = []
            for group in section["groups"]:
                fields = []
                for key, label, help_text in group["fields"]:
                    site_text = texts_by_key.get(key)
                    if site_text is None:
                        continue
                    form = SiteTextForm(
                        request.POST or None,
                        instance=site_text,
                        prefix=key,
                    )
                    form.fields["text"].label = label
                    form.fields["text"].help_text = help_text
                    if not self.has_change_permission(request, site_text):
                        form.fields["text"].disabled = True
                    forms_by_key[key] = form
                    fields.append({"key": key, "form": form})
                if fields:
                    groups.append({**group, "fields": fields})
            if groups:
                sections.append({**section, "groups": groups})

        if request.method == "POST" and "_save_site_texts" in request.POST:
            if not self.has_change_permission(request):
                messages.error(request, "You do not have permission to edit site texts.")
            elif all([form.is_valid() for form in forms_by_key.values()]):
                with transaction.atomic():
                    for form in forms_by_key.values():
                        if form.has_changed():
                            form.save()
                messages.success(request, "Site texts were saved successfully.")
                return HttpResponseRedirect(request.path)

        context = {
            **self.admin_site.each_context(request),
            "title": "Site texts",
            "opts": self.model._meta,
            "media": self.media,
            "site_text_sections": sections,
            "has_change_permission": self.has_change_permission(request),
        }
        if extra_context:
            context.update(extra_context)
        request.current_app = self.admin_site.name
        return TemplateResponse(request, self.change_list_template, context)

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False


@admin.register(SiteImage)
class SiteImageAdmin(admin.ModelAdmin):
    list_display = ("label", "key", "preview", "updated_at")
    search_fields = ("label", "key", "alt_text")
    readonly_fields = ("key", "preview")
    fields = ("label", "key", "preview", "image", "default_path", "alt_text")

    def preview(self, obj):
        if obj and obj.url:
            return format_html('<img src="{}" class="sp-admin-thumb" alt="">', obj.url)
        return "-"


@admin.register(LegalPage)
class LegalPageAdmin(admin.ModelAdmin):
    list_display = ("title", "slug", "updated_at")
    search_fields = ("title", "slug", "content")
    readonly_fields = ("slug",)
    fields = ("title", "slug", "content")


@admin.register(ProjectTag)
class ProjectTagAdmin(admin.ModelAdmin):
    list_display = ("name", "slug", "is_active", "sort_order")
    list_editable = ("is_active", "sort_order")
    prepopulated_fields = {"slug": ("name",)}
    search_fields = ("name",)


@admin.register(ProjectCase)
class ProjectCaseAdmin(admin.ModelAdmin):
    list_display = ("title", "tag", "is_active", "sort_order", "updated_at")
    list_filter = ("is_active", "tag")
    list_editable = ("is_active", "sort_order")
    search_fields = ("title", "description")
    inlines = (ProjectCaseImageInline,)


@admin.register(RequestSubmission)
class RequestSubmissionAdmin(admin.ModelAdmin):
    list_display = ("name", "phone", "request_type", "created_at")
    list_filter = ("request_type", "created_at")
    search_fields = ("name", "phone", "message")
    fields = ("name", "phone", "request_type", "message", "created_at")

    def get_readonly_fields(self, request, obj=None):
        return tuple(field.name for field in self.model._meta.fields)

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False


admin.site.site_header = "Spasibo LLC"
admin.site.site_title = "Spasibo LLC"
admin.site.index_title = "Site Management"
