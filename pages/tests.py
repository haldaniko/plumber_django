from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from .admin import EDITABLE_SITE_TEXT_KEYS
from .models import SiteText


class SiteTextAdminTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = get_user_model().objects.create_superuser(
            username="admin",
            email="admin@example.com",
            password="password",
        )
        for key in EDITABLE_SITE_TEXT_KEYS:
            SiteText.objects.update_or_create(
                key=key,
                defaults={"label": key.replace("_", " ").title(), "text": f"Text for {key}"},
            )

    def setUp(self):
        self.client.force_login(self.user)
        self.url = reverse("admin:pages_sitetext_changelist")

    def test_editor_groups_texts_in_page_order(self):
        response = self.client.get(self.url)

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "admin/pages/sitetext/change_list.html")
        content = response.content.decode()
        headings = (
            "Browser and search engines",
            "Hero section",
            "Services section",
            "Projects section",
            "Company section",
            "Request section",
        )
        positions = [content.index(heading) for heading in headings]
        self.assertEqual(positions, sorted(positions))
        self.assertEqual(content.count("<textarea"), len(EDITABLE_SITE_TEXT_KEYS))
        self.assertContains(response, "Service card 1")
        self.assertNotContains(response, "Name of the painting service.")

    def test_editor_saves_all_text_fields_together(self):
        data = {
            f"{key}-text": f"Updated {key}"
            for key in EDITABLE_SITE_TEXT_KEYS
        }
        data["_save_site_texts"] = "Save site texts"

        response = self.client.post(self.url, data)

        self.assertRedirects(response, self.url)
        self.assertEqual(
            SiteText.objects.get(key="request_title").text,
            "Updated request_title",
        )

# Create your tests here.
