from django.contrib import admin
from django.utils.html import format_html

from .models import ProjectCase, ProjectCaseImage, ProjectTag, SiteSettings


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
    fields = ("phone", "email", "address")

    def has_add_permission(self, request):
        return not SiteSettings.objects.exists()


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


admin.site.site_header = "Spasibo LLC"
admin.site.site_title = "Spasibo LLC"
admin.site.index_title = "Site Management"
