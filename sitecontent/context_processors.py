from .models import DEFAULT_UI, NavLink, SiteSettings


def site_content(request):
    try:
        site = SiteSettings.load()
        nav_links = list(NavLink.objects.filter(is_active=True))
        ui = dict(DEFAULT_UI)
        if isinstance(site.interface_text, dict):
            ui.update({k: v for k, v in site.interface_text.items() if v})
    except Exception:
        site = SiteSettings()
        nav_links = []
        ui = dict(DEFAULT_UI)

    return {
        "site": site,
        "nav_links": nav_links,
        "ui": ui,
    }
