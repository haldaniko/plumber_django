from django.contrib import admin
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
    list_display = ("label", "key", "updated_at")
    search_fields = ("label", "key", "text")
    readonly_fields = ("key",)
    fields = ("label", "key", "text")


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
