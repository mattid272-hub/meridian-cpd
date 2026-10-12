"""
Shared URL settings for the Meridian CPD app.

Two domains are in play and they are NOT interchangeable:
  - SITE_URL  https://meridiancpd.co.uk      static landing page (GitHub Pages)
  - APP_URL   https://app.meridiancpd.co.uk  this FastAPI app (Railway)

Every link to an app route (/verify, /complete, /my-cpd, /download, /unsubscribe)
must use APP_URL. Older setup notes told people to set BASE_URL to the landing
page domain, which produces dead links, so that value is corrected here.
"""
import os

SITE_URL = "https://meridiancpd.co.uk"
_DEFAULT_APP_URL = "https://app.meridiancpd.co.uk"
_LANDING_HOSTS = {
    "",
    "https://meridiancpd.co.uk",
    "http://meridiancpd.co.uk",
    "https://www.meridiancpd.co.uk",
    "http://www.meridiancpd.co.uk",
}


def _resolve_app_url() -> str:
    raw = (os.environ.get("APP_URL") or os.environ.get("BASE_URL") or "").strip().rstrip("/")
    if raw in _LANDING_HOSTS:
        return _DEFAULT_APP_URL
    return raw


APP_URL = _resolve_app_url()
# Host without the scheme, for printing on certificates and in plain-text emails.
APP_HOST = APP_URL.split("://", 1)[-1]
