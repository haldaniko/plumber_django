from pathlib import PurePosixPath
from urllib.parse import unquote

from django.http import Http404
from django.shortcuts import render


AVAILABLE_PAGES = {
    "Commode Fixing.html",
    "Gas Pipe Leakage.html",
    "Industrial Plumber.html",
    "Kitchen Inspection.html",
    "Kitchen Pipe.html",
    "Lekage Pipe Repair.html",
    "Toilet Pipe Cleaning.html",
    "Washing Pipe Repair.html",
    "about.html",
    "blog-2.html",
    "blog-details.html",
    "blog.html",
    "contact.html",
    "index-2.html",
    "index.html",
    "portfolio.html",
    "service-1.html",
    "service-2.html",
    "service-details.html",
    "team.html",
}


def _clean_page_name(page: str = "") -> str:
    page = unquote(page or "index.html").replace("\\", "/").lstrip("/")
    if not page:
        page = "index.html"

    path = PurePosixPath(page)
    if any(part in {"", ".", ".."} for part in path.parts):
        raise Http404("Page not found")

    page = str(path)
    if page not in AVAILABLE_PAGES:
        raise Http404("Page not found")
    return page


def page(request, page: str = ""):
    return render(request, f"plumber/{_clean_page_name(page)}")
