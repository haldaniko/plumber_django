from django.core.validators import RegexValidator
from django.db import models


hex_color_validator = RegexValidator(
    regex=r"^#[0-9A-Fa-f]{6}$",
    message="Enter a color in HEX format, for example #5A3E2B.",
)


class SiteSettings(models.Model):
    site_name = models.CharField(max_length=120, default="Spasibo LLC")
    phone = models.CharField(max_length=40, default="+1 845 678 899")
    email = models.EmailField(default="info@example.com")
    address = models.CharField(max_length=255, default="Dallas, TX")
    primary_color = models.CharField(
        max_length=7,
        default="#5A3E2B",
        validators=[hex_color_validator],
        help_text="Main site color in HEX format.",
    )
    logo = models.FileField(upload_to="site/", blank=True)
    favicon = models.FileField(upload_to="site/", blank=True)

    class Meta:
        verbose_name = "Site settings"
        verbose_name_plural = "Site settings"

    def __str__(self):
        return "Site settings"

    @classmethod
    def load(cls):
        settings, _ = cls.objects.get_or_create(pk=1)
        return settings

    @property
    def logo_url(self):
        return self.logo.url if self.logo else "/static/plumber/assets/images/logo.png"

    @property
    def favicon_url(self):
        return self.favicon.url if self.favicon else "/static/plumber/assets/images/favicon.png"


class SiteText(models.Model):
    key = models.SlugField(max_length=120, unique=True)
    label = models.CharField(max_length=160)
    text = models.TextField(blank=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ("label",)

    def __str__(self):
        return self.label


class SiteImage(models.Model):
    key = models.SlugField(max_length=120, unique=True)
    label = models.CharField(max_length=160)
    image = models.FileField(upload_to="site/", blank=True)
    default_path = models.CharField(max_length=255, blank=True)
    alt_text = models.CharField(max_length=160, blank=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ("label",)

    def __str__(self):
        return self.label

    @property
    def url(self):
        return self.image.url if self.image else self.default_path


class LegalPage(models.Model):
    PRIVACY = "privacy-policy"
    COOKIE = "cookie-policy"
    TERMS = "terms-of-service"

    slug = models.SlugField(max_length=80, unique=True)
    title = models.CharField(max_length=160)
    content = models.TextField()
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ("title",)

    def __str__(self):
        return self.title


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


class RequestSubmission(models.Model):
    STANDARD = "standard"
    URGENT = "urgent"
    COMMERCIAL = "commercial"
    COMPLEX = "complex"
    GENERAL = "general"

    REQUEST_TYPE_CHOICES = [
        (STANDARD, "Standard Request"),
        (URGENT, "Urgent Request"),
        (COMMERCIAL, "Commercial B2B Clients"),
        (COMPLEX, "High Complexity Request"),
        (GENERAL, "General Request"),
    ]

    name = models.CharField(max_length=120)
    phone = models.CharField(max_length=60)
    message = models.TextField(blank=True)
    request_type = models.CharField(max_length=20, choices=REQUEST_TYPE_CHOICES, default=GENERAL)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ("-created_at",)

    def __str__(self):
        return f"{self.get_request_type_display()} - {self.name}"
