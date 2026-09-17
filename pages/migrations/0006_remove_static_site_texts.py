from django.db import migrations


STATIC_SITE_TEXTS = [
    ("header_address_label", "Header address label", "Address"),
    ("header_phone_label", "Header phone label", "Call us"),
    ("header_email_label", "Header email label", "Send Us Email"),
    ("nav_home", "Navigation: Home", "Home"),
    ("nav_services", "Navigation: Services", "Services"),
    ("nav_projects", "Navigation: Projects", "Projects"),
    ("nav_contact", "Navigation: Contact", "Contact"),
    ("hero_phone_label", "Hero phone label", "Call us"),
    ("button_leave_request", "Button: leave request", "Leave a Request"),
    ("projects_filter_all", "Projects filter: all", "All"),
    ("projects_empty_message", "Projects empty message", "No active projects yet. Add project cases in the admin panel."),
    ("request_option_standard", "Request option: standard", "Standard Request"),
    ("request_option_urgent", "Request option: urgent", "Urgent Request"),
    ("request_option_commercial", "Request option: commercial", "B2B Clients"),
    ("request_option_complex", "Request option: complex", "Complex Request"),
    ("footer_copyright_prefix", "Footer copyright prefix", "Copyright"),
    ("footer_copyright_suffix", "Footer copyright suffix", "All rights reserved."),
    ("footer_privacy_label", "Footer privacy label", "Privacy Policy"),
    ("footer_cookie_label", "Footer cookie label", "Cookie Policy"),
    ("footer_terms_label", "Footer terms label", "Terms of Service"),
    ("request_modal_title", "Request modal title", "Request a Quote"),
    ("form_name_placeholder", "Form name placeholder", "Name"),
    ("form_phone_placeholder", "Form phone placeholder", "Phone"),
    ("form_message_placeholder", "Form message placeholder", "Tell us a little about the project"),
    ("form_submit_button", "Form submit button", "Submit Request"),
    ("legal_back_home", "Legal pages: back link", "Back to Home"),
]


def remove_static_site_texts(apps, schema_editor):
    SiteText = apps.get_model("pages", "SiteText")
    SiteText.objects.filter(key__in=[key for key, _, _ in STATIC_SITE_TEXTS]).delete()


def restore_static_site_texts(apps, schema_editor):
    SiteText = apps.get_model("pages", "SiteText")

    for key, label, text in STATIC_SITE_TEXTS:
        SiteText.objects.update_or_create(
            key=key,
            defaults={"label": label, "text": text},
        )


class Migration(migrations.Migration):

    dependencies = [
        ("pages", "0005_seed_editable_site_content"),
    ]

    operations = [
        migrations.RunPython(remove_static_site_texts, restore_static_site_texts),
    ]
