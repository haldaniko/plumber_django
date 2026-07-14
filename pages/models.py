from django.db import models


class SiteSettings(models.Model):
    phone = models.CharField(max_length=40, default="+1 845 678 899")
    email = models.EmailField(default="info@example.com")
    address = models.CharField(max_length=255, default="Dallas, TX")

    class Meta:
        verbose_name = "Site settings"
        verbose_name_plural = "Site settings"

    def __str__(self):
        return "Site settings"

    @classmethod
    def load(cls):
        settings, _ = cls.objects.get_or_create(pk=1)
        return settings


class ProjectTag(models.Model):
    name = models.CharField(max_length=80, unique=True)
    slug = models.SlugField(max_length=90, unique=True)
    is_active = models.BooleanField(default=True)
    sort_order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ("sort_order", "name")

    def __str__(self):
        return self.name


class ProjectCase(models.Model):
    tag = models.ForeignKey(ProjectTag, on_delete=models.PROTECT, related_name="cases")
    title = models.CharField(max_length=160)
    description = models.TextField()
    is_active = models.BooleanField(default=True)
    sort_order = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ("sort_order", "-created_at")

    def __str__(self):
        return self.title


class ProjectCaseImage(models.Model):
    project = models.ForeignKey(ProjectCase, on_delete=models.CASCADE, related_name="images")
    image = models.FileField(upload_to="projects/")
    alt_text = models.CharField(max_length=160, blank=True)
    sort_order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ("sort_order", "id")

    def __str__(self):
        return self.alt_text or f"Image for {self.project}"
