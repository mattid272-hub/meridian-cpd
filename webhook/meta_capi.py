"""Meta Pixel and Conversions API for Meridian CPD, behind the cookie choice.

Nothing here does anything unless two things are true:
  1. The Railway variables are set: META_PIXEL_ID (the Meta dataset, "Meridian CPD") for the
     browser pixel on the My CPD pages, and META_CAPI_TOKEN as well for anything sent from
     this server. Either one missing: no script tag and no server event.
  2. The visitor chose Accept on the cookie banner. The choice is the first-party cookie
     mcpd_consent ("yes" or "no") on .meridiancpd.co.uk, set by consent.js, so a choice made
     on the site carries to the app and back. No "yes", nothing is sent (PECR).

Events and deduplication
  - PageView, ViewContent, InitiateCheckout and Contact happen in the browser. consent.js
    fires each one with an eventID and posts the same name and id to POST /meta/event, which
    forwards it here. Meta keeps one of the two (same event_name and event_id).
  - Lead (a free course, MERIDIAN10) and Purchase (a paid course, series or subscription,
    with value and currency) are sent from this server only, when the buyer's browser
    reaches /thanks. The browser pixel is not loaded on /thanks because its address carries
    the checkout session id, which must not go to Meta, so there is no browser copy to
    duplicate. The event id is a hash of the session id, so a reload of /thanks is dropped
    by Meta as a repeat.

Only Lead and Purchase carry an email address, and only as Meta asks for it: lower-cased,
trimmed and SHA-256 hashed. Nothing is ever raised from here: a failed send is logged and the
page carries on.
"""
import hashlib
import json
import os
import time
from html import escape as _esc
from urllib.parse import urlsplit

import httpx

CONSENT_COOKIE = "mcpd_consent"
DEFAULT_GRAPH_VERSION = "v24.0"
# The one copy of the banner and pixel code lives on the site; the app loads it from there.
CONSENT_SCRIPT_URL = "https://meridiancpd.co.uk/consent.js"
BROWSER_EVENTS = {"PageView", "ViewContent", "InitiateCheckout", "Contact"}
OUR_HOSTS = ("meridiancpd.co.uk", "www.meridiancpd.co.uk", "app.meridiancpd.co.uk")
MAX_BODY = 4096


def pixel_id() -> str:
    return (os.environ.get("META_PIXEL_ID") or "").strip()


def _token() -> str:
    return (os.environ.get("META_CAPI_TOKEN") or "").strip()


def browser_enabled() -> bool:
    return bool(pixel_id())


def server_enabled() -> bool:
    return bool(pixel_id() and _token())


def consented(request) -> bool:
    return (request.cookies.get(CONSENT_COOKIE) or "") == "yes"


def script_tag() -> str:
    """The banner and pixel for an app page; empty when META_PIXEL_ID is not set. Only for
    pages whose address carries no token, email or session id (see main._PIXEL_PAGES)."""
    pid = pixel_id()
    if not pid or not pid.isdigit():
        return ""
    return (f'<script src="{CONSENT_SCRIPT_URL}" data-pixel="{_esc(pid)}" '
            f'data-capi="/meta/event" defer></script>')


def _sha(value: str) -> str:
    return hashlib.sha256(value.strip().lower().encode()).hexdigest()


def clean_url(url: str) -> str:
    """Scheme, host and path of one of our own pages, nothing else: a query string can carry
    a token or an email address."""
    try:
        parts = urlsplit(str(url or ""))
    except ValueError:
        return ""
    if parts.scheme != "https" or parts.hostname not in OUR_HOSTS:
        return ""
    return f"https://{parts.hostname}{parts.path or '/'}"


def from_our_pages(request) -> bool:
    """A beacon must come from one of our pages (Origin, or Referer if there is no Origin)."""
    src = request.headers.get("origin") or request.headers.get("referer") or ""
    try:
        return urlsplit(src).hostname in OUR_HOSTS
    except ValueError:
        return False


def user_data(request, email: str = "") -> dict:
    fwd = (request.headers.get("x-forwarded-for") or "").split(",")[0].strip()
    ip = fwd or (request.client.host if request.client else "")
    ud = {"client_user_agent": request.headers.get("user-agent", "")[:512]}
    if ip:
        ud["client_ip_address"] = ip
    for name in ("_fbp", "_fbc"):
        v = request.cookies.get(name)
        if v and len(v) < 256:
            ud[name[1:]] = v
    if email:
        ud["em"] = [_sha(email)]
    return ud


def event(name: str, event_id: str, url: str, ud: dict, custom: dict | None = None) -> dict:
    ev = {
        "event_name": name,
        "event_time": int(time.time()),
        "event_id": event_id,
        "action_source": "website",
        "user_data": ud,
    }
    if url:
        ev["event_source_url"] = url
    if custom:
        ev["custom_data"] = custom
    return ev


def _clean_custom(raw) -> dict:
    """What a browser beacon may carry: course or series ids, a content type and name, and a
    value in GBP. Anything else is dropped."""
    out: dict = {}
    if not isinstance(raw, dict):
        return out
    ids = raw.get("content_ids")
    if isinstance(ids, list):
        ids = [str(i)[:40] for i in ids if isinstance(i, (str, int))][:5]
        if ids:
            out["content_ids"] = ids
    for k in ("content_type", "content_name", "content_category"):
        v = raw.get(k)
        if isinstance(v, str) and v:
            out[k] = v[:60]
    v = raw.get("value")
    if isinstance(v, (int, float)) and 0 <= v < 1000:
        out["value"] = round(float(v), 2)
        out["currency"] = "GBP"
    return out


def beacon_event(body: bytes, request) -> dict | None:
    """The Conversions API event for one browser beacon, or None if it is not one we send."""
    if not body or len(body) > MAX_BODY:
        return None
    try:
        data = json.loads(body)
    except (ValueError, UnicodeDecodeError):
        return None
    if not isinstance(data, dict):
        return None
    name = data.get("event_name")
    eid = data.get("event_id")
    if name not in BROWSER_EVENTS or not isinstance(eid, str) or not (8 <= len(eid) <= 64):
        return None
    return event(name, eid, clean_url(data.get("event_source_url", "")),
                 user_data(request), _clean_custom(data.get("custom_data")))


def order_event_id(session_id: str) -> str:
    return "order-" + hashlib.sha256(str(session_id).encode()).hexdigest()[:32]


def order_event(session, purchases: list, email: str, request, get=None) -> dict:
    """Lead for a free order (MERIDIAN10, £0), Purchase for a paid one, with value and currency."""
    get = get or (lambda o, k, d=None: (o.get(k, d) if isinstance(o, dict) else getattr(o, k, d)))
    amount = get(session, "amount_total", 0) or 0
    currency = str(get(session, "currency", "") or "gbp").upper()
    ids = list(dict.fromkeys(str(p.get("course_id")) for p in purchases if p.get("course_id")))
    series = next((p.get("series_id") for p in purchases if p.get("series_id")), "")
    if "SUBSCRIPTION" in ids:
        kind = "subscription"
    elif series:
        kind = "series"
    else:
        kind = "course"
    custom = {"content_ids": [series] if series else ids[:5], "content_type": "product",
              "content_name": kind, "currency": currency, "value": round(amount / 100, 2)}
    name = "Purchase" if amount > 0 else "Lead"
    return event(name, order_event_id(get(session, "id", "")), "https://app.meridiancpd.co.uk/thanks",
                 user_data(request, email), custom)


async def send(events: list[dict]) -> bool:
    """Post events to the Conversions API. Never raises."""
    if not events or not server_enabled():
        return False
    version = (os.environ.get("META_GRAPH_VERSION") or DEFAULT_GRAPH_VERSION).strip()
    payload = {"data": events, "access_token": _token()}
    test_code = (os.environ.get("META_TEST_EVENT_CODE") or "").strip()
    if test_code:
        payload["test_event_code"] = test_code
    url = f"https://graph.facebook.com/{version}/{pixel_id()}/events"
    try:
        async with httpx.AsyncClient(timeout=8) as client:
            r = await client.post(url, json=payload)
        if r.status_code >= 400:
            print(f"Meta Conversions API refused {[e['event_name'] for e in events]}: "
                  f"{r.status_code} {r.text[:300]}")
            return False
        return True
    except Exception as e:  # network trouble must never break a page
        print(f"Meta Conversions API send failed: {e}")
        return False
