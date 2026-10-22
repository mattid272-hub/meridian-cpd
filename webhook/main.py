"""
Meridian CPD — Stripe Webhook + Course Delivery + Admin Panel + Subscriber Dashboard
Deployed on Railway. Handles:
  - checkout.session.completed → deliver course PDF + log member
  - GET /complete/[token]      → show completion confirmation page
  - POST /complete/[token]     → record completion + issue certificate
  - GET /verify/[cert-number]  → certificate verification page
  - GET /admin                 → admin dashboard (password protected)
  - GET /my-cpd                → subscriber login page
  - GET /my-cpd/dashboard      → subscriber CPD portal (session cookie auth)
"""
import asyncio
import json
import os
import re
import secrets
from contextlib import asynccontextmanager
import uuid
import hmac
import hashlib
import time
from datetime import datetime, timezone, timedelta
from html import escape as _esc

import stripe
from fastapi import FastAPI, HTTPException, Request, Response, Depends, Cookie
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.security import HTTPBasic, HTTPBasicCredentials
import httpx
from supabase import create_client

from email_sender import send_course_email, send_certificate_email, send_unsubscribe_goodbye_email, consent_token
from certificate_generator import generate_certificate
from settings import APP_URL, SITE_URL
import outreach


@asynccontextmanager
async def _lifespan(app):
    # The daily outreach batch runs inside this process (outreach.py). Set
    # OUTREACH_SCHEDULER=off on the hosting service to stop it without a deploy.
    task = None
    if os.environ.get("OUTREACH_SCHEDULER", "on").strip().lower() != "off":
        task = asyncio.create_task(outreach.scheduler_loop(lambda: supabase))
    yield
    if task:
        task.cancel()


app = FastAPI(lifespan=_lifespan)


class _AnswerHeadRequests:
    """FastAPI answers HEAD with 405 Method Not Allowed. Mail link checkers (Outlook Safe
    Links and others) often check a link with HEAD before letting the reader open it, so
    every link in our emails looked broken to them ("Unable to verify this link").
    Answer HEAD with the GET response, without the body. Links that change something on
    GET (unsubscribe) get an empty 200 instead, so a link checker can never trigger them."""

    _NO_SIDE_EFFECTS_ON_HEAD = ("/unsubscribe",)

    def __init__(self, app):
        self.app = app

    async def __call__(self, scope, receive, send):
        if scope.get("type") != "http" or scope.get("method") != "HEAD":
            return await self.app(scope, receive, send)
        if scope.get("path", "").startswith(self._NO_SIDE_EFFECTS_ON_HEAD):
            await send({"type": "http.response.start", "status": 200,
                        "headers": [(b"content-type", b"text/html; charset=utf-8")]})
            await send({"type": "http.response.body", "body": b""})
            return

        async def send_without_body(message):
            if message["type"] == "http.response.body":
                message = {**message, "body": b""}
            await send(message)

        await self.app({**scope, "method": "GET"}, receive, send_without_body)


app.add_middleware(_AnswerHeadRequests)

# ── Clients ───────────────────────────────────────────────────────────────────
stripe.api_key = os.environ["STRIPE_SECRET_KEY"]
WEBHOOK_SECRET = os.environ["STRIPE_WEBHOOK_SECRET"]

supabase = create_client(
    os.environ["SUPABASE_URL"],
    os.environ["SUPABASE_SERVICE_ROLE_KEY"],
)

# All app routes live on the app domain. See settings.py for why BASE_URL is not
# read directly from the environment any more.
BASE_URL = APP_URL
LOGO_URL = os.environ.get("LOGO_URL", "")  # Set this env var when new logo is ready

# PDF URLs are derived automatically from the Supabase project URL + course ID.
# No per-course env vars needed — new courses just need their PDF uploaded to Storage.
_SUPABASE_URL = os.environ["SUPABASE_URL"]
def _pdf_url(course_id: str) -> str:
    return f"{_SUPABASE_URL}/storage/v1/object/public/courses/{course_id}.pdf"

def _logo() -> str:
    """Returns logo HTML — image if LOGO_URL is set, otherwise styled text fallback."""
    if LOGO_URL:
        return f'<img src="{LOGO_URL}" height="50" alt="Meridian CPD" style="margin-bottom:16px;display:block">'
    return '<div style="font-size:22px;font-weight:900;color:#0f2547;letter-spacing:-0.5px;margin-bottom:16px">MERIDIAN <span style="color:#0891b2">CPD</span></div>'

# ── Course catalogue ───────────────────────────────────────────────────────────
# Each entry: course_id, title, cpd_hours, published (YYYY-MM-DD).
# pdf_url is derived automatically — no env vars needed. See _pdf_url().
# Content engine: add new entry with today's date. Admin shows NEW badge for 14 days.
# To add a course: (1) upload PDF to Supabase Storage as {course_id}.pdf,
#                  (2) add entry here with published date. Redeploy. Done.
COURSES = {
    "MER-DEA-001": {"course_id": "MER-DEA-001", "title": "RdSAP 10: What's Changed and Why", "cpd_hours": 2.0, "published": "2026-03-01"},
    "MER-DEA-002": {"course_id": "MER-DEA-002", "title": "Measuring Windows in RdSAP 10", "cpd_hours": 1.0, "published": "2026-03-01"},
    "MER-DEA-003": {"course_id": "MER-DEA-003", "title": "Ventilation in RdSAP 10: PIV, MVHR, Natural", "cpd_hours": 1.0, "published": "2026-03-01"},
    "MER-DEA-004": {"course_id": "MER-DEA-004", "title": "Room in Roof: Type 1 and Type 2", "cpd_hours": 1.0, "published": "2026-03-01"},
    "MER-DEA-005": {"course_id": "MER-DEA-005", "title": "Heating Systems Primary: Boilers, Controls and Data Entry in RdSAP 10", "cpd_hours": 1.0, "published": "2026-03-01"},
    "MER-DEA-006": {"course_id": "MER-DEA-006", "title": "Heating Systems Secondary: Storage Heaters, Direct Electric and Room Heaters", "cpd_hours": 1.0, "published": "2026-03-01"},
    "MER-DEA-007": {"course_id": "MER-DEA-007", "title": "Hot Water Systems in RdSAP 10: Cylinders, Combis and Immersions", "cpd_hours": 1.0, "published": "2026-03-01"},
    "MER-DEA-008": {"course_id": "MER-DEA-008", "title": "Insulation in RdSAP 10: Walls, Roofs, Floors and Common Errors", "cpd_hours": 1.0, "published": "2026-03-01"},
    "MER-DEA-010": {"course_id": "MER-DEA-010", "title": "Lighting and Renewables in RdSAP 10", "cpd_hours": 1.0, "published": "2026-03-01"},
    "MER-DEA-011": {"course_id": "MER-DEA-011", "title": "Solar PV, Battery Storage and PV Diverters in RdSAP 10", "cpd_hours": 1.0, "published": "2026-03-01"},
    "MER-DEA-014": {"course_id": "MER-DEA-014", "title": "EPC Audit Preparation: Building an Evidence File That Stands Up", "cpd_hours": 1.0, "published": "2026-03-01"},
    "MER-DEA-021": {"course_id": "MER-DEA-021", "title": "Airtightness Testing in RdSAP 10", "cpd_hours": 1.0, "published": "2026-03-01"},
    "MER-RA-001":  {"course_id": "MER-RA-001",  "title": "PAS 2035:2023 Overview for Retrofit Assessors", "cpd_hours": 2.0, "published": "2026-03-01"},
    "MER-RA-002":  {"course_id": "MER-RA-002",  "title": "Moisture and PAS 2035:2023: What the Retrofit Assessor Records and Reports", "cpd_hours": 1.0, "published": "2026-03-01"},
    "MER-RA-003":  {"course_id": "MER-RA-003",  "title": "Retrofit Assessment: What PAS 2035:2023 Clause 7 Requires You to Record and Report", "cpd_hours": 1.0, "published": "2026-03-01"},
    "MER-RA-004":  {"course_id": "MER-RA-004",  "title": "Cavity Wall Insulation: Risk Factors and the Retrofit Assessor's Role", "cpd_hours": 1.0, "published": "2026-03-01"},
    "MER-RA-005":  {"course_id": "MER-RA-005",  "title": "Solid Wall Insulation: IWI vs EWI, Risks, Evidence and Assessment", "cpd_hours": 1.0, "published": "2026-03-01"},
    "MER-RA-006":  {"course_id": "MER-RA-006",  "title": "EPR Variation: The RdSAP 10 Transition in ECO4 and GBIS Projects", "cpd_hours": 1.0, "published": "2026-03-01"},
    "MER-RA-007":  {"course_id": "MER-RA-007",  "title": "Heating System Assessment for Retrofit: What the Retrofit Assessor Must Record", "cpd_hours": 1.0, "published": "2026-03-01"},
    "MER-RA-008":  {"course_id": "MER-RA-008",  "title": "Ventilation Assessment in Retrofit: Background Ventilation to MVHR", "cpd_hours": 1.0, "published": "2026-03-01"},
    "MER-RA-009":  {"course_id": "MER-RA-009",  "title": "External Wall Insulation: Planning Permission and Fire Risk", "cpd_hours": 1.0, "published": "2026-03-01"},
    "MER-RA-010":  {"course_id": "MER-RA-010",  "title": "Thermal Bridging in Retrofit Assessment: What Assessors Must Record", "cpd_hours": 1.0, "published": "2026-03-01"},
    "MER-RA-011":  {"course_id": "MER-RA-011",  "title": "Occupancy Assessment: Vulnerable Occupants and Overheating Under PAS 2035:2023", "cpd_hours": 1.0, "published": "2026-03-01"},
    "MER-RA-012":  {"course_id": "MER-RA-012",  "title": "TrustMark Lodgement: What the Retrofit Assessment Must Contain and Who Lodges It", "cpd_hours": 1.0, "published": "2026-03-01"},
    "MER-ALL-001": {"course_id": "MER-ALL-001", "title": "UK Energy Policy 2026: What Assessors Need to Know", "cpd_hours": 1.0, "published": "2026-03-01"},
    "MER-ALL-004": {"course_id": "MER-ALL-004", "title": "Fire Safety in Retrofit: What Every Assessor Must Know", "cpd_hours": 1.0, "published": "2026-03-01"},
    "MER-ALL-005": {"course_id": "MER-ALL-005", "title": "Future Homes Standard 2026: What Energy Assessors Need to Know", "cpd_hours": 1.0, "published": "2026-04-15"},
    "MER-ALL-008": {"course_id": "MER-ALL-008", "title": "Renters' Rights Act 2025: Impact on EPCs and Energy Assessors", "cpd_hours": 1.0, "published": "2026-07-01"},
    "MER-ALL-009": {"course_id": "MER-ALL-009", "title": "Heat Loss Calculations for Heat Pumps: Where the EPC and the Assessor Fit", "cpd_hours": 1.0, "published": "2026-07-15"},
    "MER-ALL-010": {"course_id": "MER-ALL-010", "title": "Damp and Mould Investigations: Scotland's 2026 Duties and the Assessor's Role", "cpd_hours": 1.0, "published": "2026-08-01"},
    "MER-ALL-011": {"course_id": "MER-ALL-011", "title": "Non-Domestic MEES: The EPC E Minimum in Force and the Proposed EPC B Standard for 2031", "cpd_hours": 1.0, "published": "2026-08-01"},
    "MER-ALL-012": {"course_id": "MER-ALL-012", "title": "Whole Life Carbon for Energy Assessors: What It Means and Where It Stands in 2026", "cpd_hours": 1.0, "published": "2026-08-15"},
    "MER-ALL-013": {"course_id": "MER-ALL-013", "title": "Overheating in Existing Homes: PAS 2035 Roles, Part O and TM59 (2026)", "cpd_hours": 1.0, "published": "2026-08-01"},
    "MER-ALL-014": {"course_id": "MER-ALL-014", "title": "SMETER Technology: Measured Building Performance for Energy Assessors", "cpd_hours": 1.0, "published": "2026-08-15"},
    "MER-ALL-015": {"course_id": "MER-ALL-015", "title": "EPC Reform and the Future Home Buying Process: What Assessors Must Know", "cpd_hours": 1.0, "published": "2026-09-01"},
    "MER-ALL-016": {"course_id": "MER-ALL-016", "title": "Scheme Operating Requirements: How They Work and What Changed in 2026", "cpd_hours": 1.0, "published": "2026-09-15"},
    "MER-ALL-017": {"course_id": "MER-ALL-017", "title": "Awaab's Law Phase 2: What Energy Assessors Must Know", "cpd_hours": 1.0, "published": "2026-10-01"},
    # Subscription — welcome email only; library access granted via plan field
    "SUBSCRIPTION": {"course_id": "SUBSCRIPTION", "title": "Annual Subscription — All Courses", "cpd_hours": 0, "published": "2026-03-01"},
}

# ── Courses withdrawn for revision ─────────────────────────────────────────────
# An accuracy check in October 2026 found that these courses contain statements that
# are wrong, out of date or cannot be traced to a source. They are hidden from the
# library, cannot be downloaded and cannot be completed until a corrected edition has
# been written from the source documents and independently checked. To restore a
# course, publish its corrected PDF and delete its ID from this set (and from the same
# list in landing-page/courses.html). Certificates already issued are not affected.
UNDER_REVIEW: set = set()  # nothing withdrawn; add course ids here, or list them in under-review.json


def is_available(course_id: str) -> bool:
    """A course a member can download and complete today."""
    return course_id in COURSES and course_id != "SUBSCRIPTION" and course_id not in UNDER_REVIEW


def _under_review_page(course_id: str) -> HTMLResponse:
    title = str(COURSES.get(course_id, {}).get("title", course_id))
    return HTMLResponse(f"""<!DOCTYPE html>
<html><head><title>Course being updated — Meridian CPD</title>
<meta name="viewport" content="width=device-width,initial-scale=1"></head>
<body style="font-family:Arial,sans-serif;max-width:600px;margin:60px auto;padding:0 20px;color:#1e293b">
<h2 style="color:#0f2547">This course is being updated</h2>
<p style="line-height:1.6"><strong>{title}</strong> ({course_id}) has been withdrawn while we
revise it against the current standards and guidance. The updated edition will appear in
your library as soon as it has been checked, and you will be able to download and complete
it then.</p>
<p style="line-height:1.6">Certificates you already hold are not affected.</p>
<p><a style="color:#0891b2" href="/my-cpd/dashboard">Back to my courses</a> &nbsp;·&nbsp;
<a style="color:#0891b2" href="mailto:hello@meridiancpd.co.uk">hello@meridiancpd.co.uk</a></p>
</body></html>""")


# The withdrawn list is also published with the website (landing-page/under-review.json),
# and the app follows that copy. Restoring a corrected course, or withdrawing one, then
# only needs the website to be updated: no redeploy of this app. If the file cannot be
# read or looks wrong, the list already in memory stays in force.
UNDER_REVIEW_URL = f"{SITE_URL}/under-review.json"
_COURSE_ID_RE = re.compile(r"^MER-[A-Z]{2,4}-\d{3}$")


def _refresh_under_review() -> None:
    try:
        r = httpx.get(UNDER_REVIEW_URL, timeout=5, follow_redirects=True)
        r.raise_for_status()
        ids = r.json().get("under_review")
        if not isinstance(ids, list) or not all(isinstance(i, str) and _COURSE_ID_RE.match(i) for i in ids):
            raise ValueError("unexpected format")
        if set(ids) != UNDER_REVIEW:
            print(f"Withdrawn-course list updated: {len(ids)} course(s) under review")
        UNDER_REVIEW.clear()
        UNDER_REVIEW.update(ids)
    except Exception as e:
        print(f"Withdrawn-course list not refreshed ({type(e).__name__}); keeping the current list")


# ── Catalogue sync ─────────────────────────────────────────────────────────────
# The content engine publishes a new course on the 1st and 15th. It uploads the PDF
# and records the course in courses/catalogue.json in Supabase Storage. Reading that
# file here means a new course appears in the library without a code change or a
# redeploy. The COURSES dict above stays as the built-in baseline: if the catalogue
# is missing or unreadable, nothing is lost.
CATALOGUE_BUCKET = "courses"
CATALOGUE_FILE = "catalogue.json"
CATALOGUE_TTL_SECONDS = 600
_catalogue_checked_at = 0.0


def _merge_catalogue(data) -> int:
    """Add valid, not-yet-known courses from a catalogue payload. Returns how many were added."""
    added = 0
    entries = data.get("courses", {}) if isinstance(data, dict) else {}
    if not isinstance(entries, dict):
        return 0
    for cid, entry in entries.items():
        if cid in COURSES or not isinstance(entry, dict):
            continue
        if not isinstance(cid, str) or not _COURSE_ID_RE.match(cid):
            continue
        title = str(entry.get("title") or "").strip()
        if not title:
            continue
        try:
            hours = float(entry.get("cpd_hours", 1.0))
        except (TypeError, ValueError):
            hours = 1.0
        if not 0 < hours <= 10:
            hours = 1.0
        COURSES[cid] = {
            "course_id": cid,
            "title": title[:200],
            "cpd_hours": hours,
            "published": str(entry.get("published") or "")[:10],
        }
        added += 1
    return added


def refresh_catalogue(force: bool = False) -> None:
    """Pick up newly published courses. Cheap: at most one storage read every 10 minutes."""
    global _catalogue_checked_at
    now = time.time()
    if not force and now - _catalogue_checked_at < CATALOGUE_TTL_SECONDS:
        return
    _catalogue_checked_at = now
    _refresh_under_review()
    try:
        raw = supabase.storage.from_(CATALOGUE_BUCKET).download(CATALOGUE_FILE)
        added = _merge_catalogue(json.loads(raw))
        if added:
            print(f"Catalogue: added {added} newly published course(s)")
    except Exception as e:
        # No catalogue yet, or storage unavailable — the built-in list still applies.
        print(f"Catalogue not loaded ({type(e).__name__}); using built-in course list")


# Stripe price ID → course_id mapping
# Single course payment link maps to MER-DEA-001 (flagship)
# Add more price IDs here as individual course links are created in Stripe
PRICE_TO_COURSE = {
    os.environ.get("STRIPE_PRICE_SINGLE", ""): "MER-DEA-001",
    os.environ.get("STRIPE_PRICE_SUBSCRIPTION", ""): "SUBSCRIPTION",
}


# ── Helpers ────────────────────────────────────────────────────────────────────

def get_or_create_member(email: str, name: str, stripe_customer_id: str, plan: str):
    result = supabase.table("members").select("*").eq("email", email).execute()
    if result.data:
        member = result.data[0]
        # Update plan if upgrading to subscription — always update by email to be safe
        if plan == "subscription" and member["plan"] != "subscription":
            supabase.table("members").update({
                "plan": "subscription",
                "stripe_customer_id": stripe_customer_id,
            }).eq("email", email).execute()
            # Re-fetch to return the updated record
            updated = supabase.table("members").select("*").eq("email", email).execute()
            return updated.data[0]
        return member
    else:
        new_member = {
            "email": email,
            "name": name,
            "plan": plan,
            "stripe_customer_id": stripe_customer_id,
        }
        result = supabase.table("members").insert(new_member).execute()
        return result.data[0]


def log_purchase(member_id: str, course_id: str, session_id: str, amount: float):
    supabase.table("purchases").insert({
        "member_id": member_id,
        "course_id": course_id,
        "stripe_session_id": session_id,
        "amount_gbp": amount / 100,
    }).execute()


def create_completion_token(member_id: str, course_id: str) -> str:
    token = secrets.token_urlsafe(32)
    supabase.table("completions").insert({
        "member_id": member_id,
        "course_id": course_id,
        "completion_token": token,
    }).execute()
    return token


def next_cert_number() -> str:
    year = datetime.now(timezone.utc).year
    result = supabase.table("certificates").select("cert_number").like(
        "cert_number", f"MER-{year}-%"
    ).order("cert_number", desc=True).limit(1).execute()
    if result.data:
        last = result.data[0]["cert_number"]
        n = int(last.split("-")[-1]) + 1
    else:
        n = 1
    return f"MER-{year}-{n:04d}"


# ── Stripe webhook ─────────────────────────────────────────────────────────────

@app.post("/stripe-webhook")
async def stripe_webhook(request: Request):
    payload = await request.body()
    sig = request.headers.get("stripe-signature", "")

    try:
        event = stripe.Webhook.construct_event(payload, sig, WEBHOOK_SECRET)
    except stripe.error.SignatureVerificationError:
        raise HTTPException(status_code=400, detail="Invalid signature")

    etype = event["type"]
    obj = event["data"]["object"]
    if etype == "checkout.session.completed":
        await handle_checkout(obj)
    elif etype in ("customer.subscription.created", "customer.subscription.updated",
                   "customer.subscription.deleted"):
        sync_subscription(obj)
    elif etype in ("invoice.paid", "invoice.payment_succeeded"):
        sub_id = _invoice_subscription_id(obj)
        if sub_id:
            sync_subscription(stripe.Subscription.retrieve(sub_id))
    elif etype == "invoice.payment_failed":
        sub_id = _invoice_subscription_id(obj)
        print(f"ACTION NEEDED: renewal payment failed for customer {_g(obj, 'customer')} "
              f"(subscription {sub_id}, invoice {_g(obj, 'id')}). Stripe will retry; "
              f"access continues until Stripe cancels the subscription.")

    return {"status": "ok"}


# ── Subscription lifecycle ─────────────────────────────────────────────────────
# Access for subscribers follows Stripe: members.subscription_expires_at is set from the
# subscription's current period end (plus a short grace period, in case an event is late)
# and is set to the end date when Stripe ends the subscription. A subscriber with no
# expiry recorded yet keeps access, so a paying customer is never locked out because the
# record has not been synced; use Admin → Members → "Sync from Stripe" to fill it in.

SUB_GRACE_DAYS = 7
_LIVE_STATUSES = {"active", "trialing", "past_due"}


def _g(obj, key, default=None):
    """Read a field from a Stripe object or a plain dict."""
    if obj is None:
        return default
    try:
        v = obj.get(key, default)
    except AttributeError:
        v = getattr(obj, key, default)
    return default if v is None else v


def _period_end(sub):
    """Current period end as a Unix timestamp. Newer Stripe API versions keep it on the
    subscription items rather than the subscription itself."""
    end = _g(sub, "current_period_end")
    if end:
        return end
    items = _g(_g(sub, "items", {}), "data", []) or []
    ends = [_g(i, "current_period_end") for i in items if _g(i, "current_period_end")]
    return max(ends) if ends else None


def _invoice_subscription_id(invoice):
    sub = _g(invoice, "subscription")
    if not sub:  # newer API versions
        sub = _g(_g(_g(invoice, "parent", {}), "subscription_details", {}), "subscription")
    if sub and not isinstance(sub, str):
        sub = _g(sub, "id")
    return sub or None


def subscription_active(member: dict) -> bool:
    """True if this member currently has subscriber access."""
    if (member or {}).get("plan") != "subscription":
        return False
    exp = member.get("subscription_expires_at")
    if not exp:
        return True
    try:
        when = datetime.fromisoformat(str(exp).replace("Z", "+00:00"))
    except ValueError:
        return True
    if when.tzinfo is None:
        when = when.replace(tzinfo=timezone.utc)
    return when > datetime.now(timezone.utc)


def _member_for_customer(customer_id: str):
    if not customer_id:
        return None
    res = supabase.table("members").select("*").eq("stripe_customer_id", customer_id).execute()
    if res.data:
        return res.data[0]
    try:
        email = (_g(stripe.Customer.retrieve(customer_id), "email", "") or "").strip().lower()
    except stripe.error.StripeError as e:
        print(f"Could not look up Stripe customer {customer_id}: {e}")
        return None
    if not email:
        return None
    res = supabase.table("members").select("*").eq("email", email).execute()
    return res.data[0] if res.data else None


def sync_subscription(sub) -> dict | None:
    """Bring one member's subscriber access into line with a Stripe subscription."""
    customer_id = _g(sub, "customer", "")
    if customer_id and not isinstance(customer_id, str):
        customer_id = _g(customer_id, "id", "")
    status = _g(sub, "status", "")
    if status in _LIVE_STATUSES:
        end = _period_end(sub)
        expires = (datetime.fromtimestamp(end, timezone.utc) + timedelta(days=SUB_GRACE_DAYS)) if end else None
    elif status == "incomplete":
        print(f"Subscription {_g(sub, 'id')} for {customer_id} is incomplete (first payment not made); no change.")
        return None
    else:  # canceled, unpaid, incomplete_expired, paused
        ended = _g(sub, "ended_at") or _g(sub, "canceled_at")
        expires = datetime.fromtimestamp(ended, timezone.utc) if ended else datetime.now(timezone.utc)

    member = _member_for_customer(customer_id)
    if not member:
        print(f"ACTION NEEDED: Stripe subscription {_g(sub, 'id')} ({status}) for customer "
              f"{customer_id} matches no member. Check the customer's email in Stripe.")
        return None

    update = {"stripe_customer_id": customer_id,
              "subscription_expires_at": expires.isoformat() if expires else None}
    if status in _LIVE_STATUSES:
        update["plan"] = "subscription"
    elif member.get("plan") != "subscription":
        update.pop("subscription_expires_at")  # a single-course buyer's record is left alone
    supabase.table("members").update(update).eq("id", member["id"]).execute()
    print(f"Subscription {_g(sub, 'id')} for member {member['id']}: {status}, "
          f"access until {update.get('subscription_expires_at') or 'unchanged'}")
    return update


async def handle_checkout(session):
    customer_details = getattr(session, "customer_details", None) or {}
    email = ((getattr(customer_details, "email", None) or customer_details.get("email", "")) if customer_details else "").strip().lower()
    name = (getattr(customer_details, "name", None) or customer_details.get("name", "")) if customer_details else ""
    name = name or (email.split("@")[0].title() if email else "")
    stripe_customer_id = getattr(session, "customer", "") or ""
    session_id = getattr(session, "id", None) or session["id"]
    amount = getattr(session, "amount_total", 0) or 0

    refresh_catalogue()

    # Determine what was purchased
    # client_reference_id carries the course ID set by the buy link (e.g. MER-DEA-001)
    client_ref = getattr(session, "client_reference_id", None) or ""
    line_items = stripe.checkout.Session.list_line_items(session_id, limit=5)
    course_keys: list[str] = []
    plan = "single"
    for item in line_items.data:
        price_id = item.price.id
        course_key = PRICE_TO_COURSE.get(price_id, "")
        if course_key == "SUBSCRIPTION":
            plan = "subscription"
            course_keys.append(course_key)
        elif client_ref and client_ref in COURSES:
            # client_reference_id set on the buy link — use it directly
            course_keys.append(client_ref)
        elif course_key:
            course_keys.append(course_key)
    print(f"Checkout: email={email}, client_ref={client_ref}, course_keys={course_keys}")

    if not email:
        print(f"No email in session {session_id} — skipping")
        return

    member = get_or_create_member(email, name, stripe_customer_id, plan)
    member_id = member["id"]

    if any(k in UNDER_REVIEW for k in course_keys):
        # The course may have been restored in the last few minutes: read the list again.
        refresh_catalogue(force=True)

    for course_key in course_keys:
        course = COURSES.get(course_key)
        if not course:
            continue
        if course["course_id"] == "SUBSCRIPTION":
            # Welcome email for subscription — no specific course PDF yet
            await send_course_email(
                to_email=email,
                to_name=name,
                course_title="Your Meridian CPD Subscription",
                course_id="SUBSCRIPTION",
                pdf_url=None,
                completion_link=None,
                is_subscription=True,
            )
            log_purchase(member_id, "SUBSCRIPTION", session_id, amount)
        elif str(course["course_id"]) in UNDER_REVIEW:
            # Should not happen (withdrawn courses have no buy button), but an old link could
            # still be used. Record the payment and do not send a withdrawn edition.
            cid = str(course["course_id"])
            log_purchase(member_id, cid, session_id, amount)
            print(f"ACTION NEEDED: {cid} was bought while withdrawn for revision "
                  f"(session {session_id}). Nothing was sent. Contact the buyer or refund.")
        else:
            cid = str(course["course_id"])
            token = create_completion_token(member_id, cid)
            completion_link = f"{BASE_URL}/complete/{token}"
            await send_course_email(
                to_email=email,
                to_name=name,
                course_title=str(course["title"]),
                course_id=cid,
                pdf_url=_pdf_url(cid),
                completion_link=completion_link,
                is_subscription=False,
            )
            log_purchase(member_id, cid, session_id, amount)

    if plan == "subscription":
        sub_id = _g(session, "subscription")
        if sub_id and not isinstance(sub_id, str):
            sub_id = _g(sub_id, "id")
        if sub_id:
            try:
                sync_subscription(stripe.Subscription.retrieve(sub_id))
            except Exception as e:  # the welcome email has gone; the subscription events will catch up
                print(f"Could not sync subscription {sub_id} at checkout: {e}")

    print(f"Handled checkout for {email}: {course_keys}")


# ── Correcting the email address on an order ───────────────────────────────────
# Stripe's checkout asks for the email address once, so a typo sends the course to an
# address nobody reads and the buyer is left with nothing. There are two ways back:
#   1. After paying, the payment links send buyers to /thanks (set in Stripe on each
#      payment link: After payment → redirect to
#      https://app.meridiancpd.co.uk/thanks?session_id={CHECKOUT_SESSION_ID}).
#      The page shows the address the course went to and lets the buyer correct it once,
#      within FIX_EMAIL_DAYS of buying. Everything is then sent again to the new address.
#      The checkout session ID in that link is known only to the buyer's browser, which is
#      what shows the order is theirs.
#   2. Admin → Members → Fix email, for anyone who writes in instead.

FIX_EMAIL_DAYS = 7
_EMAIL_RE = re.compile(r"^[^@\s<>\"'(),;:\[\]\\]+@[A-Za-z0-9-]+(\.[A-Za-z0-9-]+)*\.[A-Za-z]{2,}$")
_SESSION_RE = re.compile(r"^cs_(live|test)_[A-Za-z0-9]{10,200}$")


def _clean_email(raw) -> str:
    return str(raw or "").strip().lower()


def _valid_email(email: str) -> bool:
    return len(email) <= 254 and ".." not in email and bool(_EMAIL_RE.match(email))


def _member(member_id: str):
    res = supabase.table("members").select("*").eq("id", member_id).execute()
    return res.data[0] if res.data else None


def _member_by_email(email: str):
    res = supabase.table("members").select("*").eq("email", email).execute()
    return res.data[0] if res.data else None


def _member_purchases(member_id: str) -> list:
    return supabase.table("purchases").select("*").eq("member_id", member_id).execute().data or []


def _order_purchases(session_id: str) -> list:
    return supabase.table("purchases").select("*").eq("stripe_session_id", session_id).execute().data or []


def _paid_session(session_id: str):
    """The completed Stripe checkout session with this ID, or None."""
    if not _SESSION_RE.match(session_id or ""):
        return None
    try:
        s = stripe.checkout.Session.retrieve(session_id)
    except stripe.error.StripeError as e:
        print(f"Could not read checkout session {session_id}: {e}")
        return None
    return s if _g(s, "status") == "complete" else None


def _session_email(s) -> str:
    return _clean_email(_g(_g(s, "customer_details", {}), "email", ""))


def _session_customer(s) -> str:
    cus = _g(s, "customer", "")
    if cus and not isinstance(cus, str):
        cus = _g(cus, "id", "")
    return cus or ""


def _within_fix_window(s) -> bool:
    return time.time() - float(_g(s, "created", 0) or 0) <= FIX_EMAIL_DAYS * 86400


def _real_customer(customer_id: str) -> bool:
    return bool(customer_id) and customer_id.startswith("cus_") and customer_id != "cus_test"


def move_orders(member: dict, purchases: list, new_email: str, rename_ok: bool,
                customer_id: str = "") -> dict:
    """Put these purchases (all belonging to `member`) under `new_email` and return the
    member record that now holds them.

    If nobody has the new address yet and rename_ok is true, the member's address is
    simply changed. Otherwise the purchases, any unused completion links for those
    courses and any subscription move to the member with the new address (created if
    needed); the old record keeps whatever else it had. Certificates already issued are
    never moved."""
    target = _member_by_email(new_email)
    if target and target["id"] == member["id"]:
        return member
    if not target and rename_ok:
        supabase.table("members").update({"email": new_email}).eq("id", member["id"]).execute()
        return {**member, "email": new_email}

    has_sub = any(p.get("course_id") == "SUBSCRIPTION" for p in purchases)
    if not target:
        target = supabase.table("members").insert({
            "email": new_email,
            "name": member.get("name") or "",
            "plan": "subscription" if has_sub else "single",
            "stripe_customer_id": customer_id or "",
        }).execute().data[0]

    for p in purchases:
        q = supabase.table("purchases").update({"member_id": target["id"]})
        q = q.eq("id", p["id"]) if p.get("id") else q.eq("stripe_session_id", p.get("stripe_session_id"))
        q.execute()
    for cid in {p.get("course_id") for p in purchases} - {"SUBSCRIPTION", None}:
        supabase.table("completions").update({"member_id": target["id"]}).eq(
            "member_id", member["id"]).eq("course_id", cid).is_("completed_at", "null").execute()

    if has_sub:
        upd = {"plan": "subscription"}
        if customer_id:
            upd["stripe_customer_id"] = customer_id
        if member.get("subscription_expires_at") and not target.get("subscription_expires_at"):
            upd["subscription_expires_at"] = member["subscription_expires_at"]
        supabase.table("members").update(upd).eq("id", target["id"]).execute()
        target = {**target, **upd}
        left = _member_purchases(member["id"])
        if not any(p.get("course_id") == "SUBSCRIPTION" for p in left):
            # This order is what made the old record a subscriber: undo that.
            undo = {"plan": "single", "subscription_expires_at": None}
            if not customer_id or member.get("stripe_customer_id") == customer_id:
                undo["stripe_customer_id"] = None
            supabase.table("members").update(undo).eq("id", member["id"]).execute()
    return target


def _update_stripe_email(customer_id: str, new_email: str) -> None:
    """Receipts, renewal notices and the billing portal follow the Stripe customer's email."""
    if not _real_customer(customer_id):
        return
    try:
        stripe.Customer.modify(customer_id, email=new_email)
    except stripe.error.StripeError as e:
        print(f"ACTION NEEDED: could not change the email on Stripe customer {customer_id}: {e}")


def _resync_customer(customer_id: str) -> None:
    if not _real_customer(customer_id):
        return
    try:
        for sub in stripe.Subscription.list(customer=customer_id, status="all", limit=10).auto_paging_iter():
            sync_subscription(sub)
    except stripe.error.StripeError as e:
        print(f"Could not re-sync subscriptions for {customer_id}: {e}")


async def resend_order_emails(member: dict, purchases: list) -> int:
    """Send the emails for these purchases again, to the member's current address.
    Reuses the unused completion link where there is one; a course already completed is
    sent without a completion link, so it cannot earn a second certificate."""
    refresh_catalogue()
    email = member["email"]
    name = member.get("name") or email.split("@")[0].title()
    sent = 0
    for cid in dict.fromkeys(p.get("course_id") for p in purchases if p.get("course_id")):
        course = COURSES.get(cid)
        if not course or cid in UNDER_REVIEW:
            continue
        if cid == "SUBSCRIPTION":
            await send_course_email(to_email=email, to_name=name, course_title="Your Meridian CPD Subscription",
                                    course_id="SUBSCRIPTION", pdf_url=None, completion_link=None,
                                    is_subscription=True)
        else:
            rows = supabase.table("completions").select("*").eq("member_id", member["id"]).eq(
                "course_id", cid).execute().data or []
            unused = [r for r in rows if not r.get("completed_at") and r.get("completion_token")]
            if unused:
                link = f"{BASE_URL}/complete/{unused[0]['completion_token']}"
            elif rows:
                link = None
            else:
                link = f"{BASE_URL}/complete/{create_completion_token(member['id'], cid)}"
            await send_course_email(to_email=email, to_name=name, course_title=str(course["title"]),
                                    course_id=cid, pdf_url=_pdf_url(cid), completion_link=link,
                                    is_subscription=False)
        sent += 1
    return sent


def _customer_page(title: str, inner: str, status_code: int = 200, refresh_url: str = "") -> HTMLResponse:
    refresh = f'<meta http-equiv="refresh" content="3;url={_esc(refresh_url)}">' if refresh_url else ""
    return HTMLResponse(f"""<!DOCTYPE html>
<html lang="en"><head>
<meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>{_esc(title)} — Meridian CPD</title>{refresh}
<style>
* {{ box-sizing: border-box; margin: 0; padding: 0; }}
body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif; background: #f8fafc;
       color: #1e293b; padding: 40px 16px; line-height: 1.55; }}
.card {{ background: white; border-radius: 14px; padding: 32px 28px; max-width: 520px; margin: 0 auto;
         box-shadow: 0 4px 24px rgba(0,0,0,0.08); }}
h1 {{ font-size: 22px; color: #0f2547; margin-bottom: 12px; }}
h2 {{ font-size: 16px; color: #0f2547; margin: 28px 0 8px; }}
p {{ font-size: 15px; margin-bottom: 12px; }}
.addr {{ font-size: 18px; font-weight: 700; color: #0f2547; background: #f0f9ff; border: 2px solid #0891b2;
         border-radius: 8px; padding: 12px 14px; margin: 4px 0 14px; word-break: break-all; }}
.small {{ font-size: 13px; color: #64748b; }}
.ok {{ background: #f0fdf4; border: 1px solid #86efac; color: #15803d; padding: 12px 14px; border-radius: 8px;
       font-size: 14px; margin-bottom: 16px; }}
.err {{ background: #fef2f2; border: 1px solid #fca5a5; color: #b91c1c; padding: 12px 14px; border-radius: 8px;
        font-size: 14px; margin-bottom: 16px; }}
label {{ display: block; font-size: 13px; font-weight: 600; color: #374151; margin: 12px 0 6px; }}
input[type=email] {{ width: 100%; padding: 12px 14px; font-size: 16px; border: 1.5px solid #d1d5db; border-radius: 8px; }}
button {{ margin-top: 16px; width: 100%; padding: 13px; background: #0f2547; color: white; font-size: 15px;
          font-weight: 700; border: none; border-radius: 8px; cursor: pointer; }}
button:hover {{ background: #0891b2; }}
a {{ color: #0891b2; }}
.foot {{ margin-top: 28px; border-top: 1px solid #f1f5f9; padding-top: 16px; }}
</style></head><body><div class="card">{_logo()}{inner}
<p class="small foot">Your courses and certificates are always in <a href="{BASE_URL}/my-cpd">My CPD</a>.
Questions: <a href="mailto:hello@meridiancpd.co.uk">hello@meridiancpd.co.uk</a> ·
<a href="{SITE_URL}">meridiancpd.co.uk</a></p></div></body></html>""", status_code=status_code)


def _order_what(purchases: list) -> str:
    ids = list(dict.fromkeys(p.get("course_id") for p in purchases if p.get("course_id")))
    if "SUBSCRIPTION" in ids:
        return "your subscription details"
    titles = [str(COURSES.get(c, {}).get("title", c)) for c in ids]
    return ("your course, <strong>" + _esc(titles[0]) + "</strong>,") if len(titles) == 1 else "your courses"


def _thanks_page(s, purchases: list, member: dict, notice: str = "", status_code: int = 200) -> HTMLResponse:
    email = member.get("email") or ""
    corrected = email != _session_email(s)
    note = f'<div class="err">{notice}</div>' if notice else ""
    if corrected:
        fix = ("<p class='small'>The address on this order has already been corrected once. If it is still "
               "not right, email <a href='mailto:hello@meridiancpd.co.uk'>hello@meridiancpd.co.uk</a> and "
               "we will put it right.</p>")
    elif not _within_fix_window(s):
        fix = ("<p class='small'>If that address is wrong, email "
               "<a href='mailto:hello@meridiancpd.co.uk'>hello@meridiancpd.co.uk</a> and we will put it right.</p>")
    else:
        fix = f"""
  <h2>Is that address wrong?</h2>
  <p>If you mistyped it, enter the right address below and we will send everything again to that address
  instead. You can do this once.</p>
  <form method="post" action="/thanks/email">
    <input type="hidden" name="session_id" value="{_esc(_g(s, 'id', ''))}">
    <label for="email">Correct email address</label>
    <input type="email" id="email" name="email" required autocomplete="email">
    <label for="email2">Type it again</label>
    <input type="email" id="email2" name="email2" required autocomplete="off">
    <button type="submit">Send it to this address instead</button>
  </form>"""
    ask = ""
    if member.get("marketing_consent") is None and email:
        # Asked here as well as in the course email. Nothing is recorded until a button is pressed.
        tok = consent_token(email)
        btn = lambda value, label, primary: (
            f'<form method="post" action="/my-cpd/consent/{value}" style="margin:0;flex:1">'
            f'<input type="hidden" name="email" value="{_esc(email)}"><input type="hidden" name="token" value="{_esc(tok)}">'
            f'<button type="submit" style="margin-top:0;{"" if primary else "background:white;color:#0f2547;border:2px solid #0f2547"}">{label}</button></form>')
        ask = f"""
  <h2>Hear about new courses?</h2>
  <p class="small">Now and then we add courses and tools for assessors. Would you like an email when we do?
  Only if you say yes, and you can change your mind at any time.</p>
  <div style="display:flex;gap:10px">{btn("yes", "Yes, keep me posted", True)}{btn("no", "No thanks", False)}</div>"""
    return _customer_page("Thank you", f"""
  <h1>Thank you for your order</h1>
  {note}
  <p>We have emailed {_order_what(purchases)} to:</p>
  <div class="addr">{_esc(email)}</div>
  <p class="small">It should arrive within a few minutes. If you cannot see it, check your junk or spam folder.</p>
  {ask}
  {fix}""", status_code=status_code)


def _session_id_from(raw) -> str:
    return str(raw or "").strip()


@app.get("/thanks", response_class=HTMLResponse)
async def order_thanks(request: Request):
    """Where the payment links send buyers after paying."""
    sid = _session_id_from(request.query_params.get("session_id"))
    tries = request.query_params.get("n", "0")
    tries = int(tries) if tries.isdigit() else 0
    s = _paid_session(sid)
    if not s:
        return _customer_page("Thank you", """
  <h1>Thank you</h1>
  <p>We could not find the details of this order. If you have just paid, your course is on its way
  by email.</p>
  <p>If nothing arrives within 15 minutes (check your junk folder too), email
  <a href="mailto:hello@meridiancpd.co.uk">hello@meridiancpd.co.uk</a> with your name and the time you
  bought, and we will sort it out.</p>""", status_code=404)

    purchases = _order_purchases(sid)
    if not purchases:
        # Stripe sends the buyer here and tells this app about the order separately, usually
        # within seconds. Wait for it rather than show an empty page.
        if tries < 20:
            return _customer_page("Finishing your order", """
  <h1>Finishing your order…</h1>
  <p>Your payment has gone through. We are setting up your course now; this page will update in a moment.</p>""",
                refresh_url=f"/thanks?session_id={sid}&n={tries + 1}")
        print(f"ACTION NEEDED: buyer is waiting on /thanks but order {sid} has not been recorded.")
        return _customer_page("Thank you", """
  <h1>Thank you for your order</h1>
  <p>Your payment has gone through, but setting up your course is taking longer than usual.
  Your email will follow shortly.</p>
  <p>If nothing arrives within 15 minutes, email
  <a href="mailto:hello@meridiancpd.co.uk">hello@meridiancpd.co.uk</a> and we will send it straight away.</p>""")

    member = _member(purchases[0]["member_id"]) or {}
    return _thanks_page(s, purchases, member)


@app.post("/thanks/email", response_class=HTMLResponse)
async def order_fix_email(request: Request):
    """The buyer corrects the email address they typed at checkout."""
    form = await request.form()
    sid = _session_id_from(form.get("session_id"))
    new_email, again = _clean_email(form.get("email")), _clean_email(form.get("email2"))
    s = _paid_session(sid)
    purchases = _order_purchases(sid) if s else []
    member = _member(purchases[0]["member_id"]) if purchases else None
    if not s or not member:
        return _customer_page("Order not found", """
  <h1>We could not change the address</h1>
  <p>We could not find this order. Please email
  <a href="mailto:hello@meridiancpd.co.uk">hello@meridiancpd.co.uk</a> with the right address, your name and
  the time you bought, and we will send your course there.</p>""", status_code=404)

    old_email = member.get("email") or ""
    problem = ""
    if old_email != _session_email(s):
        problem = "The address on this order has already been corrected once."
    elif not _within_fix_window(s):
        problem = (f"Addresses can only be changed here for {FIX_EMAIL_DAYS} days after buying. "
                   "Email hello@meridiancpd.co.uk and we will put it right.")
    elif not _valid_email(new_email):
        problem = "That does not look like an email address. Please check it and try again."
    elif new_email != again:
        problem = "The two addresses do not match. Please type the same address in both boxes."
    elif new_email == old_email:
        problem = "That is the address we have already used. If it is right, your email is on its way."
    if problem:
        return _thanks_page(s, purchases, member, notice=_esc(problem), status_code=400)

    others = [p for p in _member_purchases(member["id"]) if p.get("stripe_session_id") != sid]
    certs = supabase.table("certificates").select("id").eq("member_id", member["id"]).execute().data or []
    customer_id = _session_customer(s)
    holder = move_orders(member, purchases, new_email, rename_ok=not others and not certs,
                         customer_id=customer_id)
    _update_stripe_email(customer_id, new_email)
    if any(p.get("course_id") == "SUBSCRIPTION" for p in purchases):
        _resync_customer(customer_id)
    print(f"Order {sid}: buyer corrected the email from {old_email} to {new_email}")

    try:
        await resend_order_emails(holder, purchases)
    except Exception as e:
        print(f"ACTION NEEDED: email corrected on order {sid} but resending to {new_email} failed: {e}")
        return _customer_page("Address changed", f"""
  <h1>Address changed</h1>
  <p>Your order is now under <strong>{_esc(new_email)}</strong>, but we could not send the email just now.
  Please email <a href="mailto:hello@meridiancpd.co.uk">hello@meridiancpd.co.uk</a> and we will send it straight away.</p>""")

    return _customer_page("Address changed", f"""
  <h1>Done: sent to the right address</h1>
  <div class="ok">We have sent {_order_what(purchases)} to <strong>{_esc(new_email)}</strong>.</div>
  <p class="small">It should arrive within a few minutes. If you cannot see it, check your junk or spam folder.
  Nothing more about this order will go to the old address.</p>""")


# ── Download gate — marks course as downloaded before serving PDF ──────────────

@app.get("/download/{course_id}")
async def download_course(course_id: str, request: Request):
    """Records that subscriber has downloaded the PDF, then redirects to it.
    Requires active session. Sets downloaded_at on the completion record."""
    session_token = request.cookies.get("session_token")
    email = _verify_session_token(session_token) if session_token else None
    if not email:
        return RedirectResponse("/my-cpd", status_code=302)

    refresh_catalogue()
    if course_id not in COURSES:
        raise HTTPException(status_code=404, detail="Course not found")
    if course_id in UNDER_REVIEW:
        return _under_review_page(course_id)

    # Mark downloaded_at on the completion record if not already set.
    # A database hiccup here must never stop a subscriber getting their PDF.
    try:
        member_res = supabase.table("members").select("id").eq("email", email).execute()
        if member_res.data:
            member_id = member_res.data[0]["id"]
            supabase.table("completions").update({
                "downloaded_at": datetime.now(timezone.utc).isoformat(),
            }).eq("member_id", member_id).eq("course_id", course_id).is_(
                "downloaded_at", "null"
            ).execute()
            print(f"Download recorded: {email} → {course_id}")
    except Exception as e:
        print(f"ERROR recording download for {email} → {course_id}: {e}")

    return RedirectResponse(_pdf_url(course_id), status_code=302)


# ── Completion flow ────────────────────────────────────────────────────────────

@app.get("/complete/{token}", response_class=HTMLResponse)
async def completion_page(token: str):
    result = supabase.table("completions").select(
        "*, members(name, email)"
    ).eq("completion_token", token).is_("completed_at", "null").execute()

    if not result.data:
        return HTMLResponse("""
        <html><body style="font-family:Arial;max-width:600px;margin:60px auto;text-align:center">
        <h2>Link not found</h2>
        <p>This completion link has already been used or is invalid.</p>
        <p>If you need help, email <a href="mailto:hello@meridiancpd.co.uk">hello@meridiancpd.co.uk</a></p>
        </body></html>
        """, status_code=404)

    refresh_catalogue()
    row = result.data[0]
    course_id = row["course_id"]
    if course_id in UNDER_REVIEW:
        return _under_review_page(course_id)
    name = row["members"]["name"] or "there"
    has_downloaded = bool(row.get("downloaded_at"))

    # Gate: subscriber must have downloaded the PDF first
    if not has_downloaded:
        course = COURSES.get(course_id, {})
        course_title = course.get("title", course_id)
        return HTMLResponse(f"""
        <html>
        <head>
          <title>Read Course First — Meridian CPD</title>
          <style>
            body {{ font-family: Arial, sans-serif; max-width: 600px; margin: 60px auto; padding: 0 20px; }}
            h1 {{ color: #0f2547; }}
            .box {{ background: #fff8e1; border: 1px solid #f59e0b; border-radius: 8px;
                    padding: 24px; margin: 24px 0; }}
            .btn {{ display: inline-block; background: #0891b2; color: white; padding: 14px 28px;
                    border-radius: 6px; text-decoration: none; font-weight: bold; font-size: 16px;
                    margin-top: 16px; }}
            .small {{ color: #666; font-size: 13px; margin-top: 20px; }}
          </style>
        </head>
        <body>
          {_logo()}
          <h1>Please read the course first</h1>
          <div class="box">
            <p>Hi {name}, before you can claim your certificate for <strong>{course_title}</strong>,
            you need to download and read the course material.</p>
            <p style="margin-top:12px">This ensures your CPD record accurately reflects the learning you've completed —
            which is what your accreditation body expects to see.</p>
            <a class="btn" href="/download/{course_id}">Download course PDF →</a>
          </div>
          <p class="small">Once you've read the course, return to your
          <a href="{BASE_URL}/my-cpd/dashboard">CPD dashboard</a> and click Mark Complete.</p>
        </body>
        </html>
        """)

    return HTMLResponse(f"""
    <html>
    <head>
      <title>Complete Your CPD — Meridian CPD</title>
      <style>
        body {{ font-family: Arial, sans-serif; max-width: 600px; margin: 60px auto; padding: 0 20px; }}
        h1 {{ color: #0f2547; }}
        .btn {{ background: #0891b2; color: white; padding: 16px 32px; border: none;
                font-size: 18px; border-radius: 6px; cursor: pointer; width: 100%; margin-top: 24px; }}
        .name-box {{ background: #fff8e1; border: 1px solid #f59e0b; border-radius: 6px;
                     padding: 16px 20px; margin: 24px 0; }}
        .name-box p {{ margin: 0 0 12px 0; font-size: 14px; color: #444; }}
        .name-box strong {{ color: #0f2547; }}
        .name-box input {{ width: 100%; padding: 10px 12px; font-size: 16px; border: 1px solid #ccc;
                           border-radius: 4px; box-sizing: border-box; margin-top: 4px; }}
        .small {{ color: #666; font-size: 13px; margin-top: 20px; }}
      </style>
    </head>
    <body>
      {_logo()}
      <h1>Complete Your CPD</h1>
      <p>Hi {name}, you&apos;re one step away from your certificate for <strong>Course {course_id}</strong>.</p>
      <form method="POST" action="/complete/{token}">
        <div class="name-box">
          <p><strong>Your name for this certificate</strong></p>
          <p>This is the name that will appear on your CPD certificate. Please make sure it
          matches <strong>exactly</strong> the name registered with your accreditation body
          (e.g. Elmhurst, Quidos, ECMK, TrustMark). Your accreditation body will use this
          to verify your CPD record — a mismatch may mean they cannot accept it.</p>
          <input type="text" name="cert_name" value="{name}" required
                 placeholder="Your full name as registered with your accreditation body">
        </div>
        <label style="display:flex;align-items:center;gap:10px;margin:20px 0">
          <input type="checkbox" name="confirm" required style="width:20px;height:20px;flex-shrink:0">
          <span>I confirm I have read and understood the course material.</span>
        </label>
        <button type="submit" class="btn">Confirm Completion &amp; Get Certificate</button>
      </form>
      <p class="small">Your certificate will be sent to your registered email address
      and serves as evidence of CPD completion for your accreditation body.</p>
    </body>
    </html>
    """)


@app.post("/complete/{token}", response_class=HTMLResponse)
async def confirm_completion(token: str, request: Request):
    form = await request.form()
    if not form.get("confirm"):
        raise HTTPException(status_code=400, detail="Please confirm completion")

    result = supabase.table("completions").select(
        "*, members(name, email)"
    ).eq("completion_token", token).is_("completed_at", "null").execute()

    if not result.data:
        return HTMLResponse("<p>This link has already been used.</p>", status_code=400)

    refresh_catalogue()
    row = result.data[0]
    member_id = row["member_id"]
    course_id = row["course_id"]
    if course_id in UNDER_REVIEW:
        # No new certificates for an edition that has been withdrawn.
        return _under_review_page(course_id)
    member_email = row["members"]["email"]
    cert_name = str(form.get("cert_name", "")).strip()
    member_name = cert_name or row["members"]["name"] or "Assessor"

    # Mark completion
    supabase.table("completions").update({
        "completed_at": datetime.now(timezone.utc).isoformat(),
    }).eq("id", row["id"]).execute()

    # Find course details
    course = next(
        (c for c in COURSES.values() if c["course_id"] == course_id),
        {"title": course_id, "cpd_hours": 1.0}
    )

    # Generate certificate
    cert_number = next_cert_number()
    cert_pdf_bytes = generate_certificate(
        cert_number=cert_number,
        member_name=member_name,
        course_id=course_id,
        course_title=course["title"],
        cpd_hours=course["cpd_hours"],
        issued_date=datetime.now(timezone.utc).strftime("%-d %B %Y"),
    )

    # Log certificate
    supabase.table("certificates").insert({
        "cert_number": cert_number,
        "member_id": member_id,
        "member_name": member_name,
        "course_id": course_id,
        "course_title": course["title"],
        "cpd_hours": course["cpd_hours"],
        "issued_for_month": datetime.now(timezone.utc).strftime("%Y-%m"),
    }).execute()

    # Email certificate — catch errors so page always loads, log failure clearly
    email_sent = False
    try:
        await send_certificate_email(
            to_email=member_email,
            to_name=member_name,
            cert_number=cert_number,
            course_title=course["title"],
            cpd_hours=course["cpd_hours"],
            cert_pdf_bytes=cert_pdf_bytes,
        )
        email_sent = True
        print(f"Certificate email sent: {cert_number} → {member_email}")
    except Exception as e:
        print(f"ERROR sending certificate email {cert_number} to {member_email}: {e}")

    email_note = (
        f"Your certificate has been emailed to <strong>{member_email}</strong>."
        if email_sent else
        f"""<span style="color:#dc2626">We couldn't send the certificate email automatically —
        please contact <a href="mailto:hello@meridiancpd.co.uk">hello@meridiancpd.co.uk</a>
        quoting your certificate number above and we'll send it straight away.</span>"""
    )

    return HTMLResponse(f"""
    <html>
    <head>
      <title>Certificate Issued — Meridian CPD</title>
      <style>
        body {{ font-family: Arial, sans-serif; max-width: 600px; margin: 60px auto; padding: 0 20px; }}
        h1 {{ color: #0f2547; }}
        .cert-num {{ background: #f0f9ff; border: 2px solid #0891b2; padding: 16px;
                     border-radius: 6px; font-size: 20px; font-weight: bold;
                     text-align: center; color: #0891b2; margin: 24px 0; }}
      </style>
    </head>
    <body>
      {_logo()}
      <h1>CPD Completed</h1>
      <p>Well done, {member_name}. {email_note}</p>
      <div class="cert-num">{cert_number}</div>
      <p>Keep this certificate number — your accreditation body can verify it at
         <a href="{BASE_URL}/verify/{cert_number}">{BASE_URL.split("://", 1)[-1]}/verify/{cert_number}</a>
      </p>
      <p><a href="{BASE_URL}/my-cpd/dashboard">Back to my CPD dashboard →</a></p>
    </body>
    </html>
    """)


# ── Certificate verification ───────────────────────────────────────────────────

@app.get("/verify", response_class=HTMLResponse)
async def verify_landing():
    return HTMLResponse("""
    <html>
    <head>
      <title>Verify a Certificate — Meridian CPD</title>
      <meta name="viewport" content="width=device-width, initial-scale=1">
      <style>
        body { font-family: Arial, sans-serif; background: #f8fafc; margin: 0; padding: 0; }
        .wrap { max-width: 520px; margin: 80px auto; padding: 0 24px; }
        .logo { color: #0f2547; font-size: 22px; font-weight: 900; letter-spacing: -0.5px;
                margin-bottom: 40px; display: block; text-decoration: none; }
        .logo span { color: #0891b2; }
        h1 { color: #0f2547; font-size: 26px; margin: 0 0 8px; }
        p { color: #6b7280; font-size: 15px; margin: 0 0 28px; line-height: 1.5; }
        label { display: block; font-size: 13px; font-weight: bold; color: #374151; margin-bottom: 6px; }
        input { width: 100%; box-sizing: border-box; padding: 12px 14px; font-size: 15px;
                border: 1.5px solid #d1d5db; border-radius: 8px; outline: none;
                font-family: monospace; letter-spacing: 1px; }
        input:focus { border-color: #0891b2; box-shadow: 0 0 0 3px rgba(8,145,178,0.15); }
        button { margin-top: 14px; width: 100%; padding: 13px; background: #0f2547;
                 color: white; font-size: 15px; font-weight: bold; border: none;
                 border-radius: 8px; cursor: pointer; transition: background 0.15s; }
        button:hover { background: #0891b2; }
        .hint { margin-top: 14px; font-size: 13px; color: #9ca3af; text-align: center; }
        .hint strong { color: #6b7280; }
      </style>
    </head>
    <body>
      <div class="wrap">
        <a class="logo" href="https://meridiancpd.co.uk">MERIDIAN <span>CPD</span></a>
        <h1>Verify a Certificate</h1>
        <p>Enter a Meridian CPD certificate number below to confirm it is genuine and view the details.</p>
        <form method="get" action="" onsubmit="redirect(event)">
          <label for="cert">Certificate Number</label>
          <input id="cert" name="cert" type="text" placeholder="e.g. MER-2026-0001"
                 autocomplete="off" autocorrect="off" autocapitalize="characters" spellcheck="false" />
          <button type="submit">Verify Certificate</button>
        </form>
        <p class="hint">Format: <strong>MER-YYYY-NNNN</strong> — found on the certificate PDF</p>
      </div>
      <script>
        function redirect(e) {
          e.preventDefault();
          var val = document.getElementById('cert').value.trim().toUpperCase();
          if (!val) return;
          window.location.href = '/verify/' + encodeURIComponent(val);
        }
      </script>
    </body>
    </html>
    """)


@app.get("/verify/{cert_number}", response_class=HTMLResponse)
async def verify_certificate(cert_number: str):
    result = supabase.table("certificates").select(
        "*, members(name, email)"
    ).eq("cert_number", cert_number).execute()

    if not result.data:
        return HTMLResponse(f"""
        <html><body style="font-family:Arial;max-width:600px;margin:60px auto;padding:0 20px">
        <h2 style="color:#dc2626">Certificate Not Found</h2>
        <p>No certificate with number <strong>{cert_number}</strong> exists in our records.</p>
        <p>If you believe this is an error, contact
           <a href="mailto:hello@meridiancpd.co.uk">hello@meridiancpd.co.uk</a></p>
        </body></html>
        """, status_code=404)

    cert = result.data[0]
    issued_date = cert["issued_at"][:10]

    return HTMLResponse(f"""
    <html>
    <head>
      <title>Certificate Verified — Meridian CPD</title>
      <style>
        body {{ font-family: Arial, sans-serif; max-width: 600px; margin: 60px auto; padding: 0 20px; }}
        h1 {{ color: #0f2547; }}
        .verified {{ background: #f0fdf4; border: 2px solid #22c55e; border-radius: 8px;
                     padding: 24px; margin: 24px 0; }}
        .row {{ display: flex; justify-content: space-between; padding: 8px 0;
                border-bottom: 1px solid #e5e7eb; }}
        .label {{ color: #6b7280; font-size: 14px; }}
        .value {{ font-weight: bold; }}
        .badge {{ background: #22c55e; color: white; padding: 4px 12px; border-radius: 20px;
                  font-size: 14px; display: inline-block; margin-bottom: 16px; }}
      </style>
    </head>
    <body>
      {_logo()}
      <h1>Certificate Verification</h1>
      <div class="verified">
        <span class="badge">✓ Verified</span>
        <div class="row"><span class="label">Certificate Number</span>
             <span class="value">{cert["cert_number"]}</span></div>
        <div class="row"><span class="label">Issued To</span>
             <span class="value">{cert.get("member_name") or cert["members"]["name"]}</span></div>
        <div class="row"><span class="label">Course</span>
             <span class="value">{cert["course_title"]} ({cert["course_id"]})</span></div>
        <div class="row"><span class="label">CPD Hours</span>
             <span class="value">{cert["cpd_hours"]} hours</span></div>
        <div class="row"><span class="label">Date Issued</span>
             <span class="value">{issued_date}</span></div>
        <div class="row"><span class="label">Issued By</span>
             <span class="value">Meridian CPD (meridiancpd.co.uk)</span></div>
      </div>
      <p style="color:#6b7280;font-size:13px">
        Meridian CPD is an independent CPD provider. Acceptance of CPD hours is at the
        discretion of the subscriber's accreditation body.
      </p>
    </body>
    </html>
    """)


@app.get("/health")
def health():
    # Re-read the catalogue and the withdrawn list on the same ten-minute cycle as the
    # member routes, so the counts here reflect what members can actually download.
    refresh_catalogue()
    listed = [k for k in COURSES if k != "SUBSCRIPTION"]
    return {
        "status": "ok",
        "courses": len(listed),
        "available": len([k for k in listed if is_available(k)]),
        "under_review": len([k for k in listed if k in UNDER_REVIEW]),
    }


# ── Unsubscribe ────────────────────────────────────────────────────────────────

UNSUBSCRIBE_SECRET = os.environ.get("UNSUBSCRIBE_SECRET", "")

def _verify_unsubscribe_token(email: str, token: str) -> bool:
    if not UNSUBSCRIBE_SECRET:
        return False
    expected = hmac.new(
        UNSUBSCRIBE_SECRET.encode(),
        email.encode(),
        hashlib.sha256,
    ).hexdigest()[:16]
    return hmac.compare_digest(expected, token)


@app.post("/unsubscribe", response_class=HTMLResponse)
async def unsubscribe_one_click(email: str = "", token: str = ""):
    """Mail providers (Gmail, Yahoo, Outlook) offer an Unsubscribe button that POSTs to the
    List-Unsubscribe URL in the email's headers (RFC 8058). Same link, same check."""
    return await unsubscribe(email=email, token=token)


@app.get("/unsubscribe", response_class=HTMLResponse)
async def unsubscribe(email: str = "", token: str = ""):
    if not email or not token or not _verify_unsubscribe_token(email, token):
        return HTMLResponse(f"""<!DOCTYPE html>
<html><head><title>Unsubscribe — Meridian CPD</title>
<style>body{{font-family:Arial,sans-serif;max-width:520px;margin:80px auto;padding:0 24px;text-align:center}}
h2{{color:#dc2626}}p{{color:#64748b;line-height:1.6}}</style></head>
<body>
  <h2>Invalid link</h2>
  <p>This unsubscribe link is invalid or has already been used.<br>
  If you want to stop receiving emails, contact
  <a href="mailto:hello@meridiancpd.co.uk">hello@meridiancpd.co.uk</a> and we will remove you immediately.</p>
</body></html>""", status_code=400)

    # Mark suppressed in both tables
    supabase.table("outreach_contacts").update({
        "suppressed": True,
        "suppressed_reason": "unsubscribed",
    }).eq("email", email).execute()

    supabase.table("outreach_suppressed").upsert({
        "email": email,
        "reason": "unsubscribed",
    }).execute()

    print(f"Unsubscribed: {email}")

    try:
        await send_unsubscribe_goodbye_email(email)
    except Exception as e:
        print(f"Goodbye email failed for {email}: {e}")

    return HTMLResponse(f"""<!DOCTYPE html>
<html><head><title>Unsubscribed — Meridian CPD</title>
<meta name="viewport" content="width=device-width,initial-scale=1">
<style>
body{{font-family:Arial,sans-serif;max-width:520px;margin:80px auto;padding:0 24px;text-align:center}}
.logo{{font-size:20px;font-weight:900;color:#0f2547;margin-bottom:40px;display:block;text-decoration:none}}
.logo span{{color:#0891b2}}
h2{{color:#0f2547;font-size:22px;margin-bottom:12px}}
p{{color:#64748b;line-height:1.6;font-size:15px}}
</style></head>
<body>
  <a class="logo" href="https://meridiancpd.co.uk">MERIDIAN <span>CPD</span></a>
  <h2>You have been unsubscribed.</h2>
  <p>We have removed <strong>{email}</strong> from all future Meridian CPD marketing emails.<br>
  You will not hear from us again.</p>
  <p style="margin-top:24px;font-size:13px;color:#94a3b8">
  Changed your mind? Email <a href="mailto:hello@meridiancpd.co.uk" style="color:#0891b2">hello@meridiancpd.co.uk</a>
  and we will reinstate you.</p>
</body></html>""")


# ── Marketing consent ─────────────────────────────────────────────────────────

def _save_marketing_consent(email: str, consent: bool) -> bool:
    """Record the choice. Returns False (and logs) if it could not be saved.
    Requires members.marketing_consent — see migrations/2026-10-12_marketing_consent.sql."""
    try:
        supabase.table("members").update({"marketing_consent": consent}).eq(
            "email", email.strip().lower()
        ).execute()
        return True
    except Exception as e:
        print(f"ERROR saving marketing consent ({consent}) for {email}: {e}")
        return False


def _consent_not_saved_page() -> HTMLResponse:
    return HTMLResponse(f"""
    <html><head><title>Meridian CPD</title>
    <style>body{{font-family:Arial,sans-serif;max-width:520px;margin:80px auto;padding:0 24px;text-align:center}}
    h2{{color:#0f2547}}p{{color:#64748b;line-height:1.6}}
    .btn{{display:inline-block;margin-top:24px;background:#0f2547;color:white;padding:12px 24px;
          border-radius:8px;text-decoration:none;font-weight:bold}}</style></head>
    <body>
      <h2>Sorry — we couldn't save that just now.</h2>
      <p>Your subscription and course access are unaffected.<br>
      Reply to any Meridian CPD email, or write to
      <a href="mailto:hello@meridiancpd.co.uk">hello@meridiancpd.co.uk</a>, and we'll set your preference for you.</p>
      <a class="btn" href="{BASE_URL}/my-cpd/dashboard">Back to my dashboard →</a>
    </body></html>""", status_code=200)


def _consent_question_page(email: str, token: str, choice: str) -> HTMLResponse:
    """Mail link checkers open links in emails by themselves, so opening a consent link
    must never record a choice: the reader confirms with a button (a POST) instead."""
    if not email or not hmac.compare_digest(consent_token(email), token or ""):
        return HTMLResponse(f"""
    <html><head><title>Meridian CPD</title><meta name="viewport" content="width=device-width,initial-scale=1">
    <style>body{{font-family:Arial,sans-serif;max-width:520px;margin:80px auto;padding:0 24px;text-align:center}}
    h2{{color:#0f2547}}p{{color:#64748b;line-height:1.6}}</style></head>
    <body>
      <h2>This link has expired</h2>
      <p>To tell us whether you would like to hear about new courses and tools, reply to any
      Meridian CPD email or write to <a href="mailto:hello@meridiancpd.co.uk">hello@meridiancpd.co.uk</a>.
      Your subscription and course access are unaffected.</p>
    </body></html>""", status_code=400)
    yes_first = choice != "no"
    btn = lambda value, label, primary: (
        f'<form method="post" action="/my-cpd/consent/{value}" style="margin:12px 0">'
        f'<input type="hidden" name="email" value="{_esc(email)}"><input type="hidden" name="token" value="{_esc(token)}">'
        f'<button type="submit" style="width:100%;padding:13px;border-radius:8px;font-size:15px;font-weight:bold;'
        f'cursor:pointer;border:2px solid #0f2547;background:{"#0f2547" if primary else "white"};'
        f'color:{"white" if primary else "#0f2547"}">{label}</button></form>')
    buttons = (btn("yes", "Yes, keep me in the loop", yes_first) + btn("no", "No thanks, CPD only", not yes_first))
    return HTMLResponse(f"""
    <html><head><title>Meridian CPD</title><meta name="viewport" content="width=device-width,initial-scale=1">
    <style>body{{font-family:Arial,sans-serif;max-width:520px;margin:80px auto;padding:0 24px;text-align:center}}
    h2{{color:#0f2547}}p{{color:#64748b;line-height:1.6}}</style></head>
    <body>
      <h2>Hear about new courses and tools?</h2>
      <p>Now and then we develop new tools and resources for energy assessors and retrofit professionals.
      Would you like us to email <strong>{_esc(email)}</strong> about them? You can change your mind at any time.</p>
      {buttons}
    </body></html>""")


@app.get("/my-cpd/consent/yes", response_class=HTMLResponse)
async def consent_yes_page(email: str = "", token: str = ""):
    return _consent_question_page(email, token, "yes")


@app.get("/my-cpd/consent/no", response_class=HTMLResponse)
async def consent_no_page(email: str = "", token: str = ""):
    return _consent_question_page(email, token, "no")


async def _consent_form(request: Request):
    form = await request.form()
    email, token = str(form.get("email", "")), str(form.get("token", ""))
    ok = bool(email) and hmac.compare_digest(consent_token(email), token)
    return email, ok


@app.post("/my-cpd/consent/yes", response_class=HTMLResponse)
async def consent_yes(request: Request):
    email, ok = await _consent_form(request)
    if not ok:
        return _consent_question_page("", "", "yes")
    if not _save_marketing_consent(email, True):
        return _consent_not_saved_page()
    return HTMLResponse(f"""
    <html><head><title>Meridian CPD</title>
    <style>body{{font-family:Arial,sans-serif;max-width:520px;margin:80px auto;padding:0 24px;text-align:center}}
    h2{{color:#0f2547}}p{{color:#64748b;line-height:1.6}}
    .btn{{display:inline-block;margin-top:24px;background:#0f2547;color:white;padding:12px 24px;
          border-radius:8px;text-decoration:none;font-weight:bold}}</style></head>
    <body>
      <h2>Thanks — you're in the loop.</h2>
      <p>We'll only reach out when there's something genuinely useful for you.<br>
      No spam, no hard sell — ever.</p>
      <a class="btn" href="{BASE_URL}/my-cpd/dashboard">Back to my dashboard →</a>
    </body></html>""")


@app.post("/my-cpd/consent/no", response_class=HTMLResponse)
async def consent_no(request: Request):
    email, ok = await _consent_form(request)
    if not ok:
        return _consent_question_page("", "", "no")
    if not _save_marketing_consent(email, False):
        return _consent_not_saved_page()
    return HTMLResponse(f"""
    <html><head><title>Meridian CPD</title>
    <style>body{{font-family:Arial,sans-serif;max-width:520px;margin:80px auto;padding:0 24px;text-align:center}}
    h2{{color:#0f2547}}p{{color:#64748b;line-height:1.6}}
    .btn{{display:inline-block;margin-top:24px;background:#0f2547;color:white;padding:12px 24px;
          border-radius:8px;text-decoration:none;font-weight:bold}}</style></head>
    <body>
      <h2>No problem at all.</h2>
      <p>CPD only — we respect that. Your preference has been saved.<br>
      Your subscription and course access are completely unaffected.</p>
      <a class="btn" href="{BASE_URL}/my-cpd/dashboard">Back to my dashboard →</a>
    </body></html>""")


# ── Subscriber dashboard ──────────────────────────────────────────────────────

DASHBOARD_SECRET = os.environ.get("DASHBOARD_SECRET", secrets.token_hex(32))

_DASH_CSS = """
* { box-sizing: border-box; margin: 0; padding: 0; }
body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
       background: #f8fafc; color: #1e293b; font-size: 14px; min-height: 100vh; }
.topbar { background: #0f2547; padding: 0 28px; display: flex; align-items: center;
          justify-content: space-between; height: 56px; }
.topbar-brand { font-size: 18px; font-weight: 900; color: white; letter-spacing: -0.5px;
                text-decoration: none; }
.topbar-brand span { color: #0891b2; }
.topbar-right { display: flex; align-items: center; gap: 16px; }
.topbar-name { color: #94a3b8; font-size: 13px; }
.topbar-logout { color: #caf0f8; font-size: 13px; text-decoration: none;
                 border: 1px solid #1e3a5f; padding: 5px 12px; border-radius: 5px; }
.topbar-logout:hover { background: #1e3a5f; }
.wrap { max-width: 960px; margin: 0 auto; padding: 32px 24px; }
.hero { background: white; border-radius: 12px; padding: 28px 32px;
        border-left: 4px solid #0891b2; margin-bottom: 28px;
        box-shadow: 0 1px 3px rgba(0,0,0,0.06); }
.hero h1 { font-size: 22px; color: #0f2547; margin-bottom: 6px; }
.hero p { color: #64748b; font-size: 14px; }
.stats { display: grid; grid-template-columns: repeat(3, 1fr); gap: 16px; margin-bottom: 28px; }
.stat { background: white; border-radius: 10px; padding: 20px 24px;
        box-shadow: 0 1px 3px rgba(0,0,0,0.06); text-align: center; }
.stat .val { font-size: 36px; font-weight: 800; color: #0f2547; line-height: 1.1; }
.stat .lbl { color: #64748b; font-size: 12px; font-weight: 600;
             text-transform: uppercase; letter-spacing: 0.5px; margin-top: 6px; }
.card { background: white; border-radius: 10px; padding: 24px 28px;
        box-shadow: 0 1px 3px rgba(0,0,0,0.06); margin-bottom: 24px; }
.card-title { font-size: 13px; font-weight: 700; color: #0f2547; margin-bottom: 18px;
              text-transform: uppercase; letter-spacing: 0.5px; border-bottom: 2px solid #f1f5f9;
              padding-bottom: 12px; }
.course-row { display: flex; align-items: center; justify-content: space-between;
              padding: 14px 0; border-bottom: 1px solid #f1f5f9; gap: 12px; }
.course-row:last-child { border-bottom: none; }
.course-info { flex: 1; }
.course-id { font-size: 11px; color: #0891b2; font-weight: 700;
             letter-spacing: 0.5px; margin-bottom: 3px; }
.course-title { font-size: 14px; font-weight: 600; color: #1e293b; margin-bottom: 2px; }
.course-meta { font-size: 12px; color: #94a3b8; }
.course-actions { display: flex; align-items: center; gap: 10px; flex-shrink: 0; }
.pill { display: inline-flex; align-items: center; gap: 4px; padding: 4px 10px;
        border-radius: 20px; font-size: 11px; font-weight: 600; white-space: nowrap; }
.pill-complete { background: #dcfce7; color: #15803d; }
.pill-pending { background: #fef9c3; color: #854d0e; }
.pill-locked { background: #f1f5f9; color: #94a3b8; }
.btn { display: inline-block; padding: 8px 16px; border-radius: 6px; font-size: 13px;
       font-weight: 600; text-decoration: none; cursor: pointer; border: none; }
.btn-dl { background: #0891b2; color: white; }
.btn-dl:hover { background: #0f2547; }
.btn-read { background: #0f2547; color: white; }
.btn-read:hover { background: #0891b2; }
.empty { color: #94a3b8; text-align: center; padding: 32px; font-size: 14px; }
.cert-table { width: 100%; border-collapse: collapse; }
.cert-table th { text-align: left; font-size: 11px; font-weight: 700; color: #64748b;
                 text-transform: uppercase; letter-spacing: 0.5px; padding: 8px 12px;
                 border-bottom: 2px solid #e2e8f0; }
.cert-table td { padding: 10px 12px; border-bottom: 1px solid #f1f5f9; font-size: 13px; }
.cert-table tr:last-child td { border-bottom: none; }
.cert-num { font-family: monospace; color: #0891b2; font-weight: 700; font-size: 12px; }
.progress-bar { background: #e2e8f0; border-radius: 10px; height: 8px; margin-top: 8px; }
.progress-fill { background: linear-gradient(90deg, #0891b2, #0f2547);
                 border-radius: 10px; height: 8px; transition: width 0.3s; }
@media (max-width: 640px) {
  .stats { grid-template-columns: 1fr; }
  .course-row { flex-direction: column; align-items: flex-start; }
  .topbar { padding: 0 16px; }
  .wrap { padding: 20px 16px; }
}
"""

def _make_session_token(email: str) -> str:
    exp = int(time.time()) + 86400 * 30  # 30 days
    payload = f"{email}:{exp}"
    sig = hmac.new(DASHBOARD_SECRET.encode(), payload.encode(), hashlib.sha256).hexdigest()
    return f"{payload}:{sig}"

def _verify_session_token(token: str):
    """Returns email if valid, None if invalid/expired."""
    try:
        parts = token.rsplit(":", 2)
        if len(parts) != 3:
            return None
        email, exp_str, sig = parts
        exp = int(exp_str)
        if time.time() > exp:
            return None
        payload = f"{email}:{exp_str}"
        expected = hmac.new(DASHBOARD_SECRET.encode(), payload.encode(), hashlib.sha256).hexdigest()
        if not hmac.compare_digest(sig, expected):
            return None
        return email
    except Exception:
        return None

def _dash_header(name: str, email: str) -> str:
    return f"""
    <div class="topbar">
      <a class="topbar-brand" href="/my-cpd/dashboard">MERIDIAN <span>CPD</span></a>
      <div class="topbar-right">
        <span class="topbar-name">{name or email}</span>
        <a class="topbar-logout" href="/my-cpd/logout">Sign out</a>
      </div>
    </div>"""

def _get_dashboard_member(session_token: str = Cookie(default=None)):
    if not session_token:
        return None
    return _verify_session_token(session_token)


@app.get("/my-cpd", response_class=HTMLResponse)
async def dashboard_login_page(request: Request):
    # If already logged in, redirect to dashboard
    token = request.cookies.get("session_token")
    if token and _verify_session_token(token):
        return RedirectResponse("/my-cpd/dashboard", status_code=302)
    msg = request.query_params.get("msg", "")
    msg_html = ""
    if msg == "sent":
        msg_html = '<div class="msg-ok">Check your inbox — we\'ve sent you a login link.</div>'
    elif msg == "invalid":
        msg_html = '<div class="msg-err">That link has expired or is invalid. Please request a new one.</div>'
    elif msg == "notfound":
        msg_html = '<div class="msg-err">No account found for that email. Have you purchased a course?</div>'
    return HTMLResponse(f"""<!DOCTYPE html>
<html><head>
<title>My CPD — Meridian CPD</title>
<meta name="viewport" content="width=device-width,initial-scale=1">
<style>
* {{ box-sizing: border-box; margin: 0; padding: 0; }}
body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
       background: #f8fafc; display: flex; align-items: center;
       justify-content: center; min-height: 100vh; padding: 24px; }}
.card {{ background: white; border-radius: 14px; padding: 40px 36px; width: 100%;
         max-width: 420px; box-shadow: 0 4px 24px rgba(0,0,0,0.08); }}
.brand {{ font-size: 22px; font-weight: 900; color: #0f2547; letter-spacing: -0.5px;
          margin-bottom: 8px; }}
.brand span {{ color: #0891b2; }}
.sub {{ color: #64748b; font-size: 14px; margin-bottom: 32px; line-height: 1.5; }}
label {{ display: block; font-size: 13px; font-weight: 600; color: #374151; margin-bottom: 6px; }}
input {{ width: 100%; padding: 12px 14px; font-size: 15px; border: 1.5px solid #d1d5db;
         border-radius: 8px; outline: none; }}
input:focus {{ border-color: #0891b2; box-shadow: 0 0 0 3px rgba(8,145,178,0.12); }}
.btn {{ margin-top: 18px; width: 100%; padding: 13px; background: #0f2547; color: white;
        font-size: 15px; font-weight: 700; border: none; border-radius: 8px; cursor: pointer; }}
.btn:hover {{ background: #0891b2; }}
.hint {{ margin-top: 16px; font-size: 12px; color: #9ca3af; text-align: center; line-height: 1.5; }}
.msg-ok {{ background: #f0fdf4; border: 1px solid #86efac; color: #15803d; padding: 12px 16px;
           border-radius: 8px; font-size: 14px; margin-bottom: 20px; }}
.msg-err {{ background: #fef2f2; border: 1px solid #fca5a5; color: #dc2626; padding: 12px 16px;
            border-radius: 8px; font-size: 14px; margin-bottom: 20px; }}
</style>
</head><body>
<div class="card">
  <div class="brand">MERIDIAN <span>CPD</span></div>
  <p class="sub">Sign in to view your courses, track your CPD hours, and download your certificates.</p>
  {msg_html}
  <form method="POST" action="/my-cpd/send-link">
    <label for="email">Your email address</label>
    <input type="email" id="email" name="email" required placeholder="you@example.com" autocomplete="email">
    <button class="btn" type="submit">Send me a login link</button>
  </form>
  <p class="hint">We'll email you a secure one-click link. No password needed.</p>
</div>
</body></html>""")


@app.post("/my-cpd/send-link")
async def dashboard_send_link(request: Request):
    form = await request.form()
    email = str(form.get("email", "")).strip().lower()
    if not email:
        return RedirectResponse("/my-cpd?msg=invalid", status_code=302)

    # Check member exists
    result = supabase.table("members").select("id, name").eq("email", email).execute()
    if not result.data:
        return RedirectResponse("/my-cpd?msg=notfound", status_code=302)

    # Short-lived sign-in link (1 hour). It carries the member's record ID, not their email
    # address, so the link is short and does not expose the address to anything that
    # handles the URL. Opening it twice is fine: mail link checkers open links too.
    login_url = f"{BASE_URL}/my-cpd/login/{_login_token(result.data[0]['id'])}"

    # Send magic link email
    async with httpx.AsyncClient() as client:
        await client.post(
            "https://api.resend.com/emails",
            headers={"Authorization": f"Bearer {os.environ.get('RESEND_API_KEY', '')}"},
            json={
                "from": "Meridian CPD <hello@meridiancpd.co.uk>",
                "to": [email],
                "subject": "Your Meridian CPD login link",
                "text": (f"Your Meridian CPD login link\n\nOpen this link to sign in to My CPD. "
                         f"It works for 1 hour.\n\n{login_url}\n\nIf you didn't ask for this, ignore this "
                         f"email.\n\nMeridian CPD · meridiancpd.co.uk"),
                "html": f"""
                <div style="font-family:Arial,sans-serif;max-width:520px;margin:0 auto;padding:32px 24px">
                  <div style="font-size:20px;font-weight:900;color:#0f2547;margin-bottom:8px">
                    MERIDIAN <span style="color:#0891b2">CPD</span>
                  </div>
                  <h2 style="color:#0f2547;font-size:18px;margin:24px 0 8px">Your login link</h2>
                  <p style="color:#64748b;font-size:14px;line-height:1.6;margin-bottom:24px">
                    Click the button below to access your CPD dashboard. This link expires in 1 hour.
                  </p>
                  <a href="{login_url}"
                     style="display:inline-block;background:#0f2547;color:white;padding:14px 28px;
                            border-radius:8px;text-decoration:none;font-weight:700;font-size:15px">
                    Sign in to My CPD →
                  </a>
                  <p style="color:#64748b;font-size:12px;margin-top:20px;line-height:1.5">
                    If the button doesn't work, copy this link into your browser:<br>
                    <a href="{login_url}" style="color:#0891b2;word-break:break-all">{login_url}</a>
                  </p>
                  <p style="color:#94a3b8;font-size:12px;margin-top:32px;line-height:1.5">
                    If you didn't request this, ignore this email.<br>
                    Meridian CPD · meridiancpd.co.uk
                  </p>
                </div>""",
            },
        )

    return RedirectResponse("/my-cpd?msg=sent", status_code=302)


@app.get("/my-cpd/login/{encoded_token}", response_class=HTMLResponse)
async def dashboard_magic_login(encoded_token: str):
    if "." in encoded_token:  # current format: member-id.expiry.signature
        member_id = _check_login_token(encoded_token)
        member = _login_member(member_id) if member_id else None
        if not member:
            return RedirectResponse("/my-cpd?msg=invalid", status_code=302)
        return _signed_in(member["email"])
    # Older links (sent before the change) carry the email address itself.
    try:
        import base64
        magic_token = base64.urlsafe_b64decode(encoded_token.encode()).decode()
        parts = magic_token.rsplit(":", 2)
        if len(parts) != 3:
            raise ValueError
        email, exp_str, sig = parts
        exp = int(exp_str)
        if time.time() > exp:
            return RedirectResponse("/my-cpd?msg=invalid", status_code=302)
        payload = f"{email}:{exp_str}"
        expected = hmac.new(DASHBOARD_SECRET.encode(), payload.encode(), hashlib.sha256).hexdigest()
        if not hmac.compare_digest(sig, expected):
            return RedirectResponse("/my-cpd?msg=invalid", status_code=302)
    except Exception:
        return RedirectResponse("/my-cpd?msg=invalid", status_code=302)
    return _signed_in(email)


_LOGIN_LINK_SECONDS = 3600


def _login_sig(member_id: str, exp: int) -> str:
    return hmac.new(DASHBOARD_SECRET.encode(), f"login:{member_id}:{exp}".encode(),
                    hashlib.sha256).hexdigest()[:32]


def _login_token(member_id: str) -> str:
    exp = int(time.time()) + _LOGIN_LINK_SECONDS
    return f"{member_id}.{exp}.{_login_sig(member_id, exp)}"


def _check_login_token(token: str):
    """The member ID in a valid, unexpired sign-in token, else None."""
    parts = token.split(".")
    if len(parts) != 3 or not parts[1].isdigit():
        return None
    member_id, exp = parts[0], int(parts[1])
    if time.time() > exp or not hmac.compare_digest(parts[2], _login_sig(member_id, exp)):
        return None
    return member_id


def _login_member(member_id: str):
    try:
        res = supabase.table("members").select("id, email").eq("id", member_id).execute()
    except Exception as e:
        print(f"Sign-in lookup failed for member {member_id}: {e}")
        return None
    return res.data[0] if res.data else None


def _signed_in(email: str) -> RedirectResponse:
    # Issue a 30-day session cookie
    session_token = _make_session_token(email)
    response = RedirectResponse("/my-cpd/dashboard", status_code=302)
    response.set_cookie("session_token", session_token, max_age=86400 * 30,
                        httponly=True, samesite="lax", secure=True)
    return response


def _billing_help_page() -> HTMLResponse:
    return HTMLResponse("""<!DOCTYPE html>
<html><head><title>Manage your subscription — Meridian CPD</title>
<meta name="viewport" content="width=device-width,initial-scale=1"></head>
<body style="font-family:Arial,sans-serif;max-width:600px;margin:60px auto;padding:0 20px;color:#1e293b">
<h2 style="color:#0f2547">Manage your subscription</h2>
<p style="line-height:1.6">We could not open the subscription page just now. To cancel or change
your subscription, email <a style="color:#0891b2" href="mailto:hello@meridiancpd.co.uk">hello@meridiancpd.co.uk</a>
from the address you subscribed with and we will action it.</p>
<p><a style="color:#0891b2" href="/my-cpd/dashboard">Back to my courses</a></p>
</body></html>""")


@app.get("/my-cpd/billing")
async def billing_portal(request: Request):
    """Sends a signed-in member to Stripe's customer portal to cancel or manage their subscription."""
    session_token = request.cookies.get("session_token")
    email = _verify_session_token(session_token) if session_token else None
    if not email:
        return RedirectResponse("/my-cpd", status_code=302)
    res = supabase.table("members").select("*").eq("email", email).execute()
    member = res.data[0] if res.data else None
    customer_id = (member or {}).get("stripe_customer_id") or ""
    try:
        if not customer_id:
            found = stripe.Customer.list(email=email, limit=1)
            data = _g(found, "data", []) or []
            customer_id = _g(data[0], "id", "") if data else ""
        if not customer_id:
            return _billing_help_page()
        portal = stripe.billing_portal.Session.create(
            customer=customer_id, return_url=f"{BASE_URL}/my-cpd/dashboard")
        return RedirectResponse(_g(portal, "url"), status_code=303)
    except stripe.error.StripeError as e:
        print(f"ACTION NEEDED: customer portal failed for {email}: {e}")
        return _billing_help_page()


@app.get("/my-cpd/logout")
async def dashboard_logout():
    response = RedirectResponse("/my-cpd", status_code=302)
    response.delete_cookie("session_token")
    return response


@app.get("/my-cpd/dashboard", response_class=HTMLResponse)
async def subscriber_dashboard(request: Request):
    session_token = request.cookies.get("session_token")
    email = _verify_session_token(session_token) if session_token else None
    if not email:
        return RedirectResponse("/my-cpd", status_code=302)

    # Fetch member
    member_res = supabase.table("members").select("*").eq("email", email).execute()
    if not member_res.data:
        return RedirectResponse("/my-cpd", status_code=302)
    member = member_res.data[0]
    member_id = member["id"]
    member_name = member["name"] or email.split("@")[0].title()
    is_sub = subscription_active(member)
    sub_ended = member.get("plan") == "subscription" and not is_sub
    refresh_catalogue()

    # Fetch purchases
    purchases_res = supabase.table("purchases").select("course_id, purchased_at").eq(
        "member_id", member_id
    ).execute()
    purchased_ids = {p["course_id"] for p in (purchases_res.data or [])}

    # Fetch completions
    completions_res = supabase.table("completions").select(
        "course_id, completed_at, completion_token, downloaded_at"
    ).eq("member_id", member_id).execute()
    completed = {c["course_id"]: c for c in (completions_res.data or []) if c.get("completed_at")}
    pending_tokens = {c["course_id"]: c["completion_token"] for c in (completions_res.data or []) if not c.get("completed_at")}

    # For subscribers: ensure every course has a completion token so "Mark Complete" works.
    # Tokens are created lazily on first dashboard load — no email needed, just DB record.
    if is_sub:
        all_course_ids = [k for k in COURSES if is_available(k)]
        for cid in all_course_ids:
            if cid not in completed and cid not in pending_tokens:
                token = create_completion_token(member_id, cid)
                pending_tokens[cid] = token

    # Fetch certificates
    certs_res = supabase.table("certificates").select("*").eq("member_id", member_id).order(
        "issued_at", desc=True
    ).execute()
    certs = certs_res.data or []

    # CPD stats
    total_hours = sum(
        COURSES[cid]["cpd_hours"] for cid in completed if cid in COURSES
    )
    completed_count = len(completed)

    # Determine which courses to show — subscribers see full library, single buyers see only purchases
    if is_sub:
        show_courses = {k: v for k, v in COURSES.items() if k != "SUBSCRIPTION"}
    else:
        keep = set(purchased_ids)
        if sub_ended:
            # "PDFs and certs are yours to keep": courses downloaded or completed while subscribed stay listed.
            keep |= {c["course_id"] for c in (completions_res.data or [])
                     if c.get("completed_at") or c.get("downloaded_at")}
        show_courses = {k: COURSES[k] for k in keep if k in COURSES and k != "SUBSCRIPTION"}

    # Build course rows
    course_rows = ""
    for cid, course in show_courses.items():
        hours = course["cpd_hours"]
        title = course["title"]
        if cid in UNDER_REVIEW:
            # Withdrawn for revision: listed so the library does not silently shrink,
            # but with nothing to download or complete.
            done = '<span class="pill pill-complete">✓ Completed</span>' if cid in completed else ""
            status_pill = done + '<span class="pill pill-locked">Being updated</span>'
            action = ""
        elif cid in completed:
            status_pill = '<span class="pill pill-complete">✓ Completed</span>'
            action = f'<a class="btn btn-dl" href="/download/{cid}">Download PDF</a>'
        elif cid in pending_tokens:
            tok = pending_tokens[cid]
            status_pill = '<span class="pill pill-pending">⏳ Awaiting completion</span>'
            action = (f'<a class="btn btn-dl" href="/download/{cid}">Download PDF</a>'
                      f'<a class="btn btn-read" href="{BASE_URL}/complete/{tok}">Mark Complete</a>')
        else:
            status_pill = '<span class="pill pill-locked">Available</span>'
            action = f'<a class="btn btn-dl" href="/download/{cid}">Download PDF</a>'

        course_rows += f"""
        <div class="course-row">
          <div class="course-info">
            <div class="course-id">{cid}</div>
            <div class="course-title">{title}</div>
            <div class="course-meta">{hours:g} CPD hour{'s' if hours != 1 else ''}</div>
          </div>
          <div class="course-actions">
            {status_pill}
            {action}
          </div>
        </div>"""

    if not course_rows:
        course_rows = '<p class="empty">No courses yet. <a href="https://meridiancpd.co.uk">Browse the library →</a></p>'

    # Upsell banner — shown only to single-course buyers
    total_courses = len([k for k in COURSES if is_available(k)])
    courses_owned = len([k for k in show_courses if is_available(k)])
    upsell_html = ""
    if not is_sub:
        upsell_html = f"""
        <div style="background:linear-gradient(135deg,#0f2547,#0891b2);border-radius:12px;
                    padding:28px 32px;margin-bottom:28px;color:white;">
          <div style="font-size:11px;font-weight:700;letter-spacing:1px;
                      text-transform:uppercase;color:#caf0f8;margin-bottom:8px">
            Unlock the full library
          </div>
          <div style="font-size:20px;font-weight:800;margin-bottom:8px">
            You have access to {courses_owned} of {total_courses} courses.
          </div>
          <p style="font-size:14px;color:#caf0f8;margin-bottom:20px;line-height:1.6">
            An annual subscription gives you unlimited access to all {total_courses} courses —
            DEA, Retrofit Assessor, and cross-strand — plus every new course added throughout the year.
            At £79/year, it pays for itself after just 4 courses.
          </p>
          <a href="https://buy.stripe.com/fZufZgbse3BpcXE7TY73G01"
             style="display:inline-block;background:#d4ff00;color:#0f2547;padding:12px 24px;
                    border-radius:8px;text-decoration:none;font-weight:800;font-size:14px">
            Upgrade to Annual — £79/year →
          </a>
        </div>"""

    # Build certificates table
    cert_rows = ""
    for cert in certs:
        issued = cert["issued_at"][:10]
        cert_rows += f"""
        <tr>
          <td><span class="cert-num">{cert["cert_number"]}</span></td>
          <td>{cert["course_title"]}</td>
          <td>{cert["cpd_hours"]:g} hrs</td>
          <td>{issued}</td>
          <td><a href="{BASE_URL}/verify/{cert['cert_number']}" target="_blank"
                 style="color:#0891b2;font-size:12px;text-decoration:none">Verify ↗</a></td>
        </tr>"""

    if not cert_rows:
        cert_rows = '<tr><td colspan="5" style="text-align:center;color:#94a3b8;padding:24px">No certificates yet — complete a course to earn your first one.</td></tr>'

    # Progress bar (DEA requirement = 10 hours/year)
    target = 25 if is_sub and "RC" in str(purchased_ids) else 10
    pct = min(int((total_hours / target) * 100), 100)

    plan_badge = ("Annual Subscription" if is_sub else
                  "Subscription ended" if sub_ended else "Pay Per Course")
    manage_link = (' &nbsp;·&nbsp; <a href="/my-cpd/billing" style="color:#0891b2;text-decoration:none">'
                   'Manage or cancel subscription</a>') if member.get("plan") == "subscription" else ""

    return HTMLResponse(f"""<!DOCTYPE html>
<html><head>
<title>My CPD Dashboard — Meridian CPD</title>
<meta name="viewport" content="width=device-width,initial-scale=1">
<style>{_DASH_CSS}</style>
</head>
<body>
{_dash_header(member_name, email)}
<div class="wrap">

  <div class="hero">
    <h1>Welcome back, {member_name}</h1>
    <p>{email} &nbsp;·&nbsp; {plan_badge}{manage_link} &nbsp;·&nbsp;
       <a href="https://meridiancpd.co.uk" style="color:#0891b2;text-decoration:none">Browse all courses →</a></p>
  </div>

  <div class="stats">
    <div class="stat">
      <div class="val">{total_hours:g}</div>
      <div class="lbl">CPD Hours Earned</div>
    </div>
    <div class="stat">
      <div class="val">{completed_count}</div>
      <div class="lbl">Courses Completed</div>
    </div>
    <div class="stat">
      <div class="val">{len(certs)}</div>
      <div class="lbl">Certificates Issued</div>
    </div>
  </div>

  <div class="card">
    <div class="card-title">Annual CPD Progress — {total_hours:g} of {target} hours</div>
    <div class="progress-bar">
      <div class="progress-fill" style="width:{pct}%"></div>
    </div>
    <p style="font-size:12px;color:#94a3b8;margin-top:8px">
      Based on a {target}-hour annual CPD requirement. Check your accreditation body for your specific obligations.
    </p>
  </div>

  {upsell_html}

  <div class="card">
    <div class="card-title">My Courses</div>
    {course_rows}
  </div>

  <div class="card">
    <div class="card-title">Certificate Record</div>
    <table class="cert-table">
      <thead>
        <tr>
          <th>Certificate No.</th>
          <th>Course</th>
          <th>Hours</th>
          <th>Date Issued</th>
          <th>Verify</th>
        </tr>
      </thead>
      <tbody>{cert_rows}</tbody>
    </table>
  </div>

  <p style="text-align:center;font-size:12px;color:#cbd5e1;margin-top:8px">
    Meridian CPD · meridiancpd.co.uk · hello@meridiancpd.co.uk
  </p>

</div>
</body></html>""")


# ── Admin panel ────────────────────────────────────────────────────────────────

# No built-in fallback: this repository is public, so a default password in the code
# would be known to anyone. If ADMIN_PASSWORD is not set, the admin area stays shut.
ADMIN_PASSWORD = os.environ.get("ADMIN_PASSWORD", "").strip()
security = HTTPBasic()

_ADMIN_CSS = """
* { box-sizing: border-box; margin: 0; padding: 0; }
body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
       background: #f1f5f9; color: #1e293b; font-size: 14px; }
.topbar { background: #0f2547; color: white; padding: 14px 28px;
          display: flex; align-items: center; gap: 16px; }
.topbar h1 { font-size: 18px; font-weight: 700; letter-spacing: 0.3px; }
.topbar span { background: #0891b2; padding: 2px 10px; border-radius: 20px;
               font-size: 11px; font-weight: 600; letter-spacing: 0.5px; }
.nav { background: #1e3a5f; display: flex; gap: 2px; padding: 0 24px; }
.nav a { color: #94a3b8; text-decoration: none; padding: 10px 16px;
         font-size: 13px; font-weight: 500; border-bottom: 2px solid transparent; }
.nav a:hover, .nav a.active { color: white; border-bottom-color: #0891b2; }
.main { padding: 28px; max-width: 1200px; }
.stats { display: grid; grid-template-columns: repeat(4, 1fr); gap: 16px; margin-bottom: 28px; }
.stat { background: white; border-radius: 10px; padding: 20px 24px;
        box-shadow: 0 1px 3px rgba(0,0,0,0.08); border-top: 3px solid #0891b2; }
.stat .val { font-size: 32px; font-weight: 800; color: #0f2547; line-height: 1.1; }
.stat .lbl { color: #64748b; font-size: 12px; font-weight: 600;
             text-transform: uppercase; letter-spacing: 0.5px; margin-top: 4px; }
.stat .sub { color: #94a3b8; font-size: 11px; margin-top: 2px; }
.card { background: white; border-radius: 10px; padding: 20px 24px;
        box-shadow: 0 1px 3px rgba(0,0,0,0.08); margin-bottom: 24px; }
.card h2 { font-size: 14px; font-weight: 700; color: #0f2547; margin-bottom: 16px;
           text-transform: uppercase; letter-spacing: 0.5px; }
table { width: 100%; border-collapse: collapse; }
th { text-align: left; font-size: 11px; font-weight: 700; color: #64748b;
     text-transform: uppercase; letter-spacing: 0.5px; padding: 8px 12px;
     border-bottom: 2px solid #e2e8f0; }
td { padding: 10px 12px; border-bottom: 1px solid #f1f5f9; vertical-align: middle; }
tr:last-child td { border-bottom: none; }
tr:hover td { background: #f8fafc; }
.badge { display: inline-block; padding: 2px 8px; border-radius: 10px;
         font-size: 11px; font-weight: 600; white-space: nowrap; }
button { background: #0f2547; color: white; border: none; border-radius: 6px; padding: 7px 14px;
         font-size: 12px; font-weight: 600; cursor: pointer; }
button:hover { background: #0891b2; }
.badge-sub { background: #dcfce7; color: #15803d; }
.badge-single { background: #dbeafe; color: #1d4ed8; }
.badge-ok { background: #dcfce7; color: #15803d; }
.badge-warn { background: #fef9c3; color: #854d0e; }
.badge-off { background: #fee2e2; color: #dc2626; }
.empty { color: #94a3b8; text-align: center; padding: 32px; font-size: 13px; }
.section { margin-bottom: 32px; }
.course-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(280px, 1fr)); gap: 12px; }
.course-card { border: 1px solid #e2e8f0; border-radius: 8px; padding: 14px 16px; }
.course-card .cid { font-size: 11px; color: #0891b2; font-weight: 700;
                    letter-spacing: 0.5px; margin-bottom: 4px; }
.course-card .ctitle { font-size: 13px; font-weight: 600; color: #1e293b; margin-bottom: 6px; }
.course-card .cmeta { font-size: 11px; color: #64748b; }
.revenue { color: #15803d; font-weight: 700; }
.badge-test { background: #f1f5f9; color: #64748b; }
.badge-free { background: #ede9fe; color: #6d28d9; }
.badge-end { background: #f1f5f9; color: #475569; }
.filters { display: flex; flex-wrap: wrap; gap: 6px; margin: -4px 0 16px; }
.filters a { font-size: 12px; padding: 4px 10px; border-radius: 14px; background: #f1f5f9;
             color: #334155; text-decoration: none; }
.filters a.on { background: #0f2547; color: white; }
.note { color: #64748b; font-size: 12px; margin: -6px 0 14px; line-height: 1.5; }
@media (max-width: 900px) { .stats { grid-template-columns: repeat(2, 1fr); } .main { padding: 16px; } }
a.vlink { color: #0891b2; text-decoration: none; font-size: 12px; }
a.vlink:hover { text-decoration: underline; }
"""


def _check_admin(credentials: HTTPBasicCredentials = Depends(security)):
    if not ADMIN_PASSWORD:
        raise HTTPException(
            status_code=503,
            detail="Admin is switched off: set the ADMIN_PASSWORD variable on the hosting service.",
        )
    if not secrets.compare_digest(credentials.password.encode(), ADMIN_PASSWORD.encode()):
        raise HTTPException(
            status_code=401,
            detail="Incorrect password",
            headers={"WWW-Authenticate": "Basic realm='Meridian CPD Admin'"},
        )
    return credentials


# ── Test purchase endpoint (admin only) ────────────────────────────────────────

@app.get("/test-purchase", response_class=HTMLResponse)
async def test_purchase_form(credentials=Depends(_check_admin)):
    course_options = "".join(
        f'<option value="{cid}">{cid} — {c["title"]}</option>'
        for cid, c in COURSES.items() if cid != "SUBSCRIPTION"
    )
    return HTMLResponse(f"""
    <html><head><title>Test Purchase — Meridian CPD Admin</title>
    <style>body{{font-family:Arial;max-width:500px;margin:60px auto;padding:0 20px}}
    h2{{color:#0f2547}}label{{display:block;margin-top:16px;font-weight:bold;font-size:13px}}
    input,select{{width:100%;box-sizing:border-box;padding:10px;margin-top:6px;border:1px solid #d1d5db;border-radius:6px;font-size:14px}}
    button{{margin-top:24px;width:100%;padding:12px;background:#0f2547;color:white;font-size:15px;font-weight:bold;border:none;border-radius:6px;cursor:pointer}}
    button:hover{{background:#0891b2}}
    .warn{{background:#fef9c3;border:1px solid #d97706;padding:12px;border-radius:6px;font-size:13px;margin-bottom:20px}}</style>
    </head><body>
    <h2>Test Purchase</h2>
    <div class="warn">Fires a real email and logs a test record to Supabase. Use your own email.</div>
    <form method="POST" action="/test-purchase">
      <label>Email address (receives the course email)</label>
      <input type="email" name="email" required placeholder="hello@meridiancpd.co.uk">
      <label>Name</label>
      <input type="text" name="name" placeholder="Matt Test">
      <label>Course</label>
      <select name="course_id">{course_options}</select>
      <button type="submit">Fire Test Purchase</button>
    </form>
    <p style="margin-top:20px"><a style="color:#0891b2" href="/admin">← Back to admin</a></p>
    </body></html>
    """)


@app.post("/test-purchase", response_class=HTMLResponse)
async def test_purchase(request: Request, credentials=Depends(_check_admin)):
    form = await request.form()
    email = str(form.get("email", "")).strip()
    name = str(form.get("name", "")).strip() or email.split("@")[0].title()
    course_id = str(form.get("course_id", "MER-DEA-001")).strip()

    if not email:
        return HTMLResponse("<p>email is required</p>", status_code=400)

    course = COURSES.get(course_id)
    if not course:
        return HTMLResponse(f"<p>Unknown course_id: {course_id}</p>", status_code=400)
    if course_id in UNDER_REVIEW:
        return HTMLResponse(f"<p>{course_id} is withdrawn for revision and cannot be sent.</p>", status_code=400)

    fake_session_id = f"cs_test_{secrets.token_hex(8)}"
    member = get_or_create_member(email, name, "cus_test", "single")
    member_id = member["id"]
    log_purchase(member_id, course_id, fake_session_id, 0)  # tests are never revenue
    token = create_completion_token(member_id, course_id)
    completion_link = f"{BASE_URL}/complete/{token}"

    await send_course_email(
        to_email=email, to_name=name, course_title=str(course["title"]),
        course_id=course_id, pdf_url=_pdf_url(course_id),
        completion_link=completion_link, is_subscription=False,
    )

    return HTMLResponse(f"""
    <html><head><title>Test Purchase Fired — Meridian CPD</title>
    <style>body{{font-family:Arial;max-width:600px;margin:60px auto;padding:0 20px}}
    .ok{{background:#f0fdf4;border:2px solid #22c55e;border-radius:8px;padding:20px;margin:20px 0}}
    code{{background:#f1f5f9;padding:2px 6px;border-radius:4px}}a{{color:#0891b2}}</style></head>
    <body><h2 style="color:#0f2547">Test Purchase Fired</h2>
    <div class="ok">
      <p><strong>Email sent to:</strong> {email}</p>
      <p><strong>Course:</strong> {course['title']} ({course_id})</p>
      <p><strong>Completion link:</strong> <a href="{completion_link}">{completion_link}</a></p>
    </div>
    <p>Check {email} — PDF should arrive within 30 seconds. Click the completion link to test certificate generation.</p>
    <p><a href="/admin">← Back to admin</a></p>
    </body></html>
    """)


def _nav(active: str) -> str:
    tabs = [
        ("dashboard", "Dashboard"),
        ("members", "Members"),
        ("contacts", "Contacts"),
        ("outreach", "Outreach"),
        ("courses", "Courses"),
        ("certificates", "Certificates"),
        ("system", "System"),
    ]
    links = "".join(
        f'<a href="/admin/{t}" class="{"active" if t == active else ""}">{label}</a>'
        for t, label in tabs
    )
    return f"""
    <div class="topbar">
      <h1>MERIDIAN CPD</h1><span>ADMIN</span>
    </div>
    <nav class="nav">{links}</nav>
    """


def _page(title: str, nav_active: str, body: str) -> HTMLResponse:
    return HTMLResponse(f"""<!DOCTYPE html>
<html><head>
<title>{title} — Meridian CPD Admin</title>
<meta name="viewport" content="width=device-width,initial-scale=1">
<style>{_ADMIN_CSS}</style>
</head>
<body>
{_nav(nav_active)}
<div class="main">{body}</div>
</body></html>""")


# ── Back-office classification ─────────────────────────────────────────────────
# Test purchases (Admin → Test Purchase) use session ids starting "cs_test_" and the
# customer id "cus_test". Addresses on our own domain or example domains, and any listed
# in ADMIN_TEST_EMAILS (comma-separated, set in Railway), are also treated as tests.
# Tests are left out of every count and total, and can be shown with the Tests filter.
_TEST_DOMAINS = {"meridiancpd.co.uk", "example.com", "example.org"}

_MEMBER_STATUS = {  # key: (label, badge class, what it means)
    "subscriber":  ("Subscriber", "badge-sub", "Active subscription confirmed by Stripe"),
    "unconfirmed": ("Subscriber, unconfirmed", "badge-warn",
                    "Marked as a subscriber here but not yet matched to a Stripe subscription. "
                    "Run Sync from Stripe; any still listed have no subscription in Stripe"),
    "ended":       ("Subscription ended", "badge-end", "Stripe subscription has ended"),
    "buyer":       ("Course buyer", "badge-single", "Paid for one or more single courses"),
    "free":        ("Free course", "badge-free", "Took a free course (promo code), paid nothing"),
    "none":        ("No purchase", "badge-end", "Signed up but no purchase recorded"),
    "test":        ("Test", "badge-test", "Test account or test purchase"),
}


def _test_emails() -> set:
    return {e.strip().lower() for e in os.environ.get("ADMIN_TEST_EMAILS", "").split(",") if e.strip()}


def _is_test_purchase(p: dict) -> bool:
    return str(p.get("stripe_session_id") or "").startswith("cs_test_")


def _purchases_by_member() -> dict:
    res = supabase.table("purchases").select(
        "member_id, course_id, amount_gbp, stripe_session_id, purchased_at").execute()
    out: dict = {}
    for p in (res.data or []):
        out.setdefault(p.get("member_id"), []).append(p)
    return out


def classify_member(m: dict, purchases: list, test_emails: set | None = None) -> tuple[str, float]:
    """(status key, total paid in £ excluding tests) for one member."""
    test_emails = _test_emails() if test_emails is None else test_emails
    email = (m.get("email") or "").strip().lower()
    real = [p for p in purchases if not _is_test_purchase(p)]
    paid = round(sum(float(p.get("amount_gbp") or 0) for p in real), 2)
    if (m.get("stripe_customer_id") == "cus_test" or email in test_emails
            or email.split("@")[-1] in _TEST_DOMAINS or (purchases and not real)):
        return "test", paid
    if m.get("plan") == "subscription":
        if not subscription_active(m):
            return "ended", paid
        return ("subscriber" if m.get("subscription_expires_at") else "unconfirmed"), paid
    if paid > 0:
        return "buyer", paid
    return ("free" if real else "none"), paid


def _n(count: int, word: str, plural: str | None = None) -> str:
    return f"{count} {word if count == 1 else (plural or word + 's')}"


def _course_label(cid: str) -> str:
    if cid == "SUBSCRIPTION":
        return "Annual subscription"
    title = str(COURSES.get(cid, {}).get("title", ""))
    return f"{cid} · {title}" if title else (cid or "—")


def _status_badge(key: str) -> str:
    label, cls, meaning = _MEMBER_STATUS[key]
    return f'<span class="badge {cls}" title="{meaning}">{label}</span>'


def _classified_members():
    members = supabase.table("members").select("*").order("joined_at", desc=True).execute().data or []
    by_member = _purchases_by_member()
    tests = _test_emails()
    rows = []
    for m in members:
        key, paid = classify_member(m, by_member.get(m.get("id"), []), tests)
        rows.append((m, key, paid, by_member.get(m.get("id"), [])))
    return rows


@app.get("/admin", response_class=HTMLResponse)
@app.get("/admin/dashboard", response_class=HTMLResponse)
async def admin_dashboard(credentials=Depends(_check_admin)):
    rows = _classified_members()
    real = [r for r in rows if r[1] != "test"]
    count = lambda k: sum(1 for r in real if r[1] == k)
    test_ids = {r[0].get("id") for r in rows if r[1] == "test"}
    n_tests = len(test_ids)

    paid_purchases = [p for r in real for p in r[3] if not _is_test_purchase(p) and float(p.get("amount_gbp") or 0) > 0]
    revenue = sum(float(p.get("amount_gbp") or 0) for p in paid_purchases)

    certs = supabase.table("certificates").select("id, member_id").execute().data or []
    comps = supabase.table("completions").select("id, member_id").not_.is_("completed_at", "null").execute().data or []
    n_certs = sum(1 for c in certs if c.get("member_id") not in test_ids)
    n_comps = sum(1 for c in comps if c.get("member_id") not in test_ids)

    # Renewals coming up: promises (discounts, extra months) must be applied in Stripe before these dates
    now = datetime.now(timezone.utc)
    upcoming = []
    for m, key, paid, _ in real:
        if key != "subscriber":
            continue
        try:
            exp = datetime.fromisoformat(str(m["subscription_expires_at"]).replace("Z", "+00:00"))
        except (KeyError, ValueError):
            continue
        renew = exp - timedelta(days=SUB_GRACE_DAYS)
        if renew - now <= timedelta(days=60):
            upcoming.append((renew, m))
    upcoming.sort(key=lambda x: x[0])
    renew_rows = "".join(
        f"<tr><td>{d.strftime('%d %b %Y')}</td><td>{m.get('name') or '—'}</td><td>{m.get('email') or '—'}</td></tr>"
        for d, m in upcoming)

    # Recent purchases, tests left out
    recent = sorted(((p, r[0]) for r in real for p in r[3] if not _is_test_purchase(p)),
                    key=lambda x: x[0].get("purchased_at") or "", reverse=True)[:10]
    prow = ""
    for p, m in recent:
        amt = float(p.get("amount_gbp") or 0)
        amount = f'<span class="revenue">£{amt:.2f}</span>' if amt > 0 else _status_badge("free")
        course = _course_label(p.get("course_id") or "")
        prow += f"""<tr><td>{(p.get('purchased_at') or '')[:10]}</td><td>{m.get('name') or '—'}</td>
            <td>{m.get('email') or '—'}</td><td>{course}</td><td>{amount}</td></tr>"""

    unconf = count("unconfirmed")
    body = f"""
    <div class="stats">
      <div class="stat"><div class="val">{count("subscriber")}</div>
        <div class="lbl">Active subscribers</div>
        <div class="sub">{f"{unconf} more not yet confirmed in Stripe" if unconf else "All confirmed by Stripe"}</div></div>
      <div class="stat"><div class="val">{count("buyer")}</div>
        <div class="lbl">Course buyers</div>
        <div class="sub">{_n(count("free"), "took a free course only", "took a free course only")} · {_n(count("ended"), "subscription")} ended</div></div>
      <div class="stat"><div class="val">£{revenue:,.0f}</div>
        <div class="lbl">Revenue recorded</div>
        <div class="sub">{_n(len(paid_purchases), "paid purchase")}</div></div>
      <div class="stat"><div class="val">{n_certs}</div>
        <div class="lbl">Certificates issued</div>
        <div class="sub">{_n(n_comps, "course")} completed</div></div>
    </div>
    <p class="note">Test accounts and test purchases are left out of every figure on this page ({_n(n_tests, "test account")};
    see Members → Tests). Revenue is what the app recorded at checkout;
    Stripe is the record for money received and refunds.</p>
    {"" if not unconf else f'<div class="card"><h2>Needs attention</h2><p>{_n(unconf, "member is", "members are")} marked as {"a subscriber" if unconf == 1 else "subscribers"} but not yet matched to a subscription in Stripe. Go to <a class="vlink" href="/admin/members?show=unconfirmed">Members</a> and run <strong>Sync subscriptions from Stripe</strong>. Anyone still listed afterwards has no subscription in Stripe: check whether they paid.</p></div>'}
    <div class="card">
      <h2>Renewals in the next 60 days</h2>
      <p class="note">Any discount or extra time promised to these members must be set up in Stripe before the date shown.</p>
      <table><tr><th>Renews</th><th>Name</th><th>Email</th></tr>
      {renew_rows or '<tr><td colspan="3" class="empty">No renewals in the next 60 days</td></tr>'}</table>
    </div>
    <div class="card">
      <h2>Recent purchases</h2>
      <table><tr><th>Date</th><th>Name</th><th>Email</th><th>Course</th><th>Amount</th></tr>
      {prow or '<tr><td colspan="5" class="empty">No purchases yet</td></tr>'}</table>
    </div>"""
    return _page("Dashboard", "dashboard", body)


@app.get("/admin/members", response_class=HTMLResponse)
async def admin_members(request: Request, credentials=Depends(_check_admin)):
    show = request.query_params.get("show", "real")
    rows = _classified_members()
    groups = {
        "real": ("All members", lambda k: k != "test"),
        "subscriber": ("Subscribers", lambda k: k == "subscriber"),
        "unconfirmed": ("Unconfirmed", lambda k: k == "unconfirmed"),
        "buyer": ("Course buyers", lambda k: k == "buyer"),
        "free": ("Free course", lambda k: k == "free"),
        "ended": ("Ended", lambda k: k == "ended"),
        "none": ("No purchase", lambda k: k == "none"),
        "test": ("Tests", lambda k: k == "test"),
    }
    if show not in groups:
        show = "real"
    tabs = "".join(
        f'<a class="{"on" if g == show else ""}" href="/admin/members?show={g}">'
        f'{label} ({sum(1 for r in rows if fn(r[1]))})</a>'
        for g, (label, fn) in groups.items())
    shown = [r for r in rows if groups[show][1](r[1])]
    trs = ""
    for m, key, paid, purchases in shown:
        courses = sorted({p.get("course_id") for p in purchases
                          if p.get("course_id") and p.get("course_id") != "SUBSCRIPTION"})
        access = ((m.get("subscription_expires_at") or "")[:10] or "—") if m.get("plan") == "subscription" else "—"
        trs += f"""<tr>
            <td>{m.get('name') or '—'}</td>
            <td>{m.get('email') or '—'}<br><a class="vlink" style="font-size:11px"
                href="/admin/members/{m.get('id')}/email">Fix email</a></td>
            <td>{_status_badge(key)}</td>
            <td>{access}</td>
            <td>{f"£{paid:.2f}" if paid else "—"}</td>
            <td>{", ".join(courses) or "—"}</td>
            <td>{(m.get('joined_at') or '')[:10]}</td>
        </tr>"""
    body = f"""
    <div class="card">
      <h2>Members</h2>
      <div class="filters">{tabs}</div>
      <p class="note">Hover over a status for what it means. "Paid" is what the app recorded at checkout,
      tests excluded. "Access until" includes a 7-day grace period after the renewal date.</p>
      <form method="post" action="/admin/sync-subscriptions" style="margin:0 0 16px">
        <button type="submit">Sync subscriptions from Stripe</button>
        <span style="font-size:12px;color:#64748b;margin-left:8px">Reads every subscription in Stripe and
        updates each subscriber's access date. Changes nothing in Stripe.</span>
      </form>
      <table>
        <tr><th>Name</th><th>Email</th><th>Status</th><th>Access until</th><th>Paid</th><th>Courses</th><th>Joined</th></tr>
        {trs or '<tr><td colspan="7" class="empty">Nobody in this group</td></tr>'}
      </table>
    </div>"""
    return _page("Members", "members", body)


def _admin_fix_email_form(member: dict, purchases: list, notice: str = "", status_code: int = 200) -> HTMLResponse:
    orders = "".join(
        f"<tr><td>{_esc((p.get('purchased_at') or '')[:10])}</td><td>{_esc(_course_label(p.get('course_id') or ''))}</td>"
        f"<td>{'£%.2f' % float(p.get('amount_gbp') or 0)}</td></tr>"
        for p in sorted(purchases, key=lambda p: p.get("purchased_at") or "", reverse=True))
    n = len({p.get("course_id") for p in purchases if p.get("course_id")})
    body = f"""
    <div class="card">
      <h2>Fix email: {_esc(member.get('name') or '—')}</h2>
      {f'<p style="color:#b91c1c;margin-bottom:12px">{_esc(notice)}</p>' if notice else ''}
      <p>Current address: <strong>{_esc(member.get('email') or '—')}</strong></p>
      <table style="margin:12px 0"><tr><th>Bought</th><th>Course</th><th>Paid</th></tr>
      {orders or '<tr><td colspan="3" class="empty">No purchases</td></tr>'}</table>
      <form method="post" action="/admin/members/{_esc(str(member.get('id')))}/email">
        <p><label>Correct email address<br><input type="email" name="email" required style="width:100%;max-width:360px;padding:8px"></label></p>
        <p style="margin-top:8px"><label>Type it again<br><input type="email" name="email2" required style="width:100%;max-width:360px;padding:8px"></label></p>
        <p style="margin-top:10px"><label><input type="checkbox" name="resend" value="1" checked>
          Send the course emails again to the new address ({_n(n, "email")})</label></p>
        <p style="margin-top:12px"><button type="submit">Change the address</button></p>
      </form>
      <p class="note" style="margin-top:12px">Also changes the email on their Stripe customer record, so receipts and
      renewal notices go to the new address. If another member already has the new address, these purchases move to
      that member. Certificates already issued stay as they are. A course they have already completed is sent
      without a completion link, so it cannot earn a second certificate.</p>
      <p style="margin-top:12px"><a class="vlink" href="/admin/members">Back to members</a></p>
    </div>"""
    resp = _page("Fix email", "members", body)
    resp.status_code = status_code
    return resp


@app.get("/admin/members/{member_id}/email", response_class=HTMLResponse)
async def admin_fix_email_form(member_id: str, credentials=Depends(_check_admin)):
    member = _member(member_id)
    if not member:
        raise HTTPException(status_code=404, detail="Member not found")
    return _admin_fix_email_form(member, _member_purchases(member_id))


@app.post("/admin/members/{member_id}/email", response_class=HTMLResponse)
async def admin_fix_email(member_id: str, request: Request, credentials=Depends(_check_admin)):
    member = _member(member_id)
    if not member:
        raise HTTPException(status_code=404, detail="Member not found")
    form = await request.form()
    new_email, again = _clean_email(form.get("email")), _clean_email(form.get("email2"))
    purchases = _member_purchases(member_id)
    if not _valid_email(new_email):
        return _admin_fix_email_form(member, purchases, "That is not a valid email address.", 400)
    if new_email != again:
        return _admin_fix_email_form(member, purchases, "The two addresses do not match.", 400)
    old_email = member.get("email") or ""
    if new_email == old_email:
        return _admin_fix_email_form(member, purchases, "That is already their address.", 400)

    customer_id = member.get("stripe_customer_id") or ""
    holder = move_orders(member, purchases, new_email, rename_ok=True, customer_id=customer_id)
    _update_stripe_email(customer_id, new_email)
    if member.get("plan") == "subscription":
        _resync_customer(customer_id)
    print(f"Admin changed member {member_id}'s email from {old_email} to {new_email}")

    sent, error = 0, ""
    if form.get("resend") and purchases:
        try:
            sent = await resend_order_emails(holder, purchases)
        except Exception as e:
            error = str(e)
            print(f"ACTION NEEDED: resending to {new_email} failed: {e}")
    moved = holder.get("id") != member.get("id")
    body = f"""
    <div class="card">
      <h2>Email changed</h2>
      <p>{_esc(old_email)} → <strong>{_esc(new_email)}</strong>.
      {"Their purchases were moved to the existing member with that address." if moved else ""}</p>
      <p>{f"Sent {_n(sent, 'email')} to the new address." if sent else ("No emails sent." if not error else "")}
      {f'<span style="color:#b91c1c">Sending failed: {_esc(error)}. Send the course by hand.</span>' if error else ""}</p>
      <p style="margin-top:12px"><a class="vlink" href="/admin/members">Back to members</a></p>
    </div>"""
    return _page("Email changed", "members", body)


@app.post("/admin/sync-subscriptions", response_class=HTMLResponse)
async def admin_sync_subscriptions(credentials=Depends(_check_admin)):
    """Backfill and re-check every subscriber's access date from Stripe. Read-only on Stripe."""
    synced, unmatched, errors = 0, 0, []
    try:
        for sub in stripe.Subscription.list(status="all", limit=100).auto_paging_iter():
            try:
                if sync_subscription(sub):
                    synced += 1
                elif _g(sub, "status") != "incomplete":
                    unmatched += 1
            except Exception as e:
                errors.append(f"{_g(sub, 'id')}: {e}")
    except stripe.error.StripeError as e:
        errors.append(f"Stripe: {e}")
    still = [r[0] for r in _classified_members() if r[1] == "unconfirmed"]
    still_html = "".join(f"<li>{m.get('name') or '—'} ({m.get('email') or '—'})</li>" for m in still)
    body = f"""
    <div class="card">
      <h2>Subscription sync</h2>
      <p>Updated {synced} member(s). {unmatched} subscription(s) matched no member (see the app log for their IDs).</p>
      {f"<p style='margin-top:12px'><strong>Marked as subscribers here but with no subscription in Stripe:</strong></p><ul style='margin:6px 0 0 18px'>{still_html}</ul><p class='note' style='margin-top:6px'>Check whether each of these paid. If they did not, they are not subscribers.</p>" if still else "<p>Every subscriber here matches a subscription in Stripe.</p>"}
      {"<p>Errors:<br>" + "<br>".join(errors[:20]) + "</p>" if errors else ""}
      <p><a href="/admin/members">Back to members</a></p>
    </div>"""
    return _page("Subscription sync", "members", body)


@app.get("/admin/contacts", response_class=HTMLResponse)
async def admin_contacts(request: Request, credentials=Depends(_check_admin)):
    # Postcode area → region mapping
    POSTCODE_REGIONS = {
        "AB": "Scotland", "DD": "Scotland", "DG": "Scotland", "EH": "Scotland",
        "FK": "Scotland", "G": "Scotland", "HS": "Scotland", "IV": "Scotland",
        "KA": "Scotland", "KW": "Scotland", "KY": "Scotland", "ML": "Scotland",
        "PA": "Scotland", "PH": "Scotland", "TD": "Scotland", "ZE": "Scotland",
        "BT": "Northern Ireland",
        "CF": "Wales", "LD": "Wales", "LL": "Wales", "NP": "Wales",
        "SA": "Wales", "SY": "Wales",
        "TR": "South West", "PL": "South West", "TQ": "South West", "EX": "South West",
        "TA": "South West", "BA": "South West", "BS": "South West", "GL": "South West",
        "DT": "South West", "SP": "South West",
        "BH": "South East", "PO": "South East", "SO": "South East", "RG": "South East",
        "GU": "South East", "SL": "South East", "RH": "South East", "TN": "South East",
        "CT": "South East", "ME": "South East", "DA": "South East", "BR": "South East",
        "CR": "South East", "SM": "South East", "KT": "South East", "TW": "South East",
        "BN": "South East", "SN": "South West",
        "OX": "South East", "HP": "South East", "MK": "South East", "LU": "East of England",
        "SG": "East of England", "AL": "East of England", "WD": "East of England",
        "EN": "East of England", "CM": "East of England", "SS": "East of England",
        "CO": "East of England", "IP": "East of England", "NR": "East of England",
        "PE": "East of England", "CB": "East of England",
        "E": "London", "EC": "London", "N": "London", "NW": "London",
        "SE": "London", "SW": "London", "W": "London", "WC": "London",
        "IG": "London", "RM": "London", "UB": "London", "HA": "London",
        "B": "West Midlands", "CV": "West Midlands", "WS": "West Midlands",
        "WV": "West Midlands", "DY": "West Midlands", "ST": "West Midlands",
        "TF": "West Midlands", "HR": "West Midlands", "WR": "West Midlands",
        "NN": "East Midlands", "MK": "East Midlands", "LE": "East Midlands",
        "DE": "East Midlands", "NG": "East Midlands", "LN": "East Midlands",
        "S": "Yorkshire", "DN": "Yorkshire", "HU": "Yorkshire", "YO": "Yorkshire",
        "HG": "Yorkshire", "BD": "Yorkshire", "LS": "Yorkshire", "WF": "Yorkshire",
        "HD": "Yorkshire", "HX": "Yorkshire",
        "M": "North West", "WN": "North West", "WA": "North West", "SK": "North West",
        "CW": "North West", "CH": "North West", "L": "North West", "PR": "North West",
        "BB": "North West", "BL": "North West", "OL": "North West", "FY": "North West",
        "LA": "North West", "CA": "North West",
        "NE": "North East", "SR": "North East", "DH": "North East", "TS": "North East",
        "DL": "North East",
        "HG": "Yorkshire",
    }

    def get_region(postcode):
        if not postcode:
            return "Unknown"
        area = ''.join(c for c in postcode.split()[0] if c.isalpha()).upper()
        # Try longest match first
        for length in [3, 2, 1]:
            key = area[:length]
            if key in POSTCODE_REGIONS:
                return POSTCODE_REGIONS[key]
        return "Unknown"

    # Get filter params from query string
    search = request.query_params.get("search", "").strip().lower()
    scheme_filter = request.query_params.get("scheme", "").strip().lower()
    region_filter = request.query_params.get("region", "").strip().lower()
    postcode_filter = request.query_params.get("postcode", "").strip().upper()

    res = supabase.table("outreach_contacts").select(
        "full_name, email, accreditation_scheme, assessor_type, source_postcode, suppressed, created_at"
    ).order("created_at", desc=False).execute()

    all_contacts = res.data or []

    # Count by region and scheme for summary (unfiltered totals)
    region_counts = {}
    scheme_counts = {}
    for c in all_contacts:
        r = get_region(c.get("source_postcode", ""))
        region_counts[r] = region_counts.get(r, 0) + 1
        s = c.get("accreditation_scheme", "Unknown") or "Unknown"
        s_short = s.replace("Energy Systems Ltd", "").replace("Limited", "").replace("Ltd", "").strip()
        scheme_counts[s_short] = scheme_counts.get(s_short, 0) + 1

    # Apply filters
    contacts = all_contacts
    if search:
        contacts = [c for c in contacts if
            search in (c.get("full_name") or "").lower() or
            search in (c.get("email") or "").lower()]
    if scheme_filter:
        contacts = [c for c in contacts if scheme_filter in (c.get("accreditation_scheme") or "").lower()]
    if region_filter:
        contacts = [c for c in contacts if get_region(c.get("source_postcode", "")).lower() == region_filter]
    if postcode_filter:
        contacts = [c for c in contacts if (c.get("source_postcode") or "").upper().startswith(postcode_filter)]

    total_all = len(all_contacts)
    total_filtered = len(contacts)

    # Build unique scheme options for dropdown
    all_schemes = sorted(set(
        (c.get("accreditation_scheme") or "").replace("Energy Systems Ltd","").replace("Limited","").replace("Ltd","").strip()
        for c in all_contacts if c.get("accreditation_scheme")
    ))
    scheme_options = '<option value="">All Schemes</option>' + "".join(
        f'<option value="{s.lower()}" {"selected" if s.lower() == scheme_filter else ""}>{s}</option>'
        for s in all_schemes
    )

    all_regions = sorted(set(get_region(c.get("source_postcode","")) for c in all_contacts))
    region_options = '<option value="">All Regions</option>' + "".join(
        f'<option value="{r.lower()}" {"selected" if r.lower() == region_filter else ""}>{r}</option>'
        for r in all_regions
    )

    # Region summary pills
    region_pills = "".join(
        f'<a href="/admin/contacts?region={r.lower()}" style="display:inline-block;background:#e0f2fe;color:#0369a1;padding:3px 10px;border-radius:12px;font-size:12px;font-weight:600;margin:3px;text-decoration:none">{r}: {n}</a>'
        for r, n in sorted(region_counts.items(), key=lambda x: -x[1])
    )
    scheme_pills = "".join(
        f'<a href="/admin/contacts?scheme={s.lower()}" style="display:inline-block;background:#f0fdf4;color:#15803d;padding:3px 10px;border-radius:12px;font-size:12px;font-weight:600;margin:3px;text-decoration:none">{s}: {n}</a>'
        for s, n in sorted(scheme_counts.items(), key=lambda x: -x[1])
    )

    # Contact rows
    rows = ""
    for c in contacts[:500]:
        suppressed = c.get("suppressed", False)
        region = get_region(c.get("source_postcode", ""))
        scheme = (c.get("accreditation_scheme") or "—").replace("Energy Systems Ltd", "").replace("Limited", "").replace("Ltd", "").strip()
        status_badge = '<span class="badge" style="background:#fee2e2;color:#dc2626">Suppressed</span>' if suppressed else '<span class="badge badge-ok">Active</span>'
        rows += f"""<tr>
            <td>{c.get('full_name') or '—'}</td>
            <td style="font-size:12px">{c.get('email','—')}</td>
            <td>{scheme}</td>
            <td>{c.get('source_postcode','—')}</td>
            <td>{region}</td>
            <td>{status_badge}</td>
        </tr>"""

    showing = f"Showing {min(total_filtered,500):,} of {total_filtered:,} filtered" if (search or scheme_filter or region_filter or postcode_filter) else f"Showing first 500 of {total_all:,}"

    body = f"""
    <div class="card">
      <h2>DEA Contact Database — {total_all:,} total contacts</h2>
      <div style="margin-bottom:16px">
        <div style="font-size:12px;font-weight:700;color:#64748b;text-transform:uppercase;letter-spacing:0.5px;margin-bottom:8px">By Region (click to filter)</div>
        {region_pills}
      </div>
      <div style="margin-bottom:20px">
        <div style="font-size:12px;font-weight:700;color:#64748b;text-transform:uppercase;letter-spacing:0.5px;margin-bottom:8px">By Scheme (click to filter)</div>
        {scheme_pills}
      </div>
    </div>
    <div class="card">
      <form method="GET" action="/admin/contacts" style="display:flex;gap:12px;flex-wrap:wrap;align-items:flex-end;margin-bottom:20px">
        <div>
          <label style="display:block;font-size:11px;font-weight:700;color:#64748b;text-transform:uppercase;margin-bottom:4px">Search name / email</label>
          <input name="search" value="{search}" placeholder="e.g. John Smith" style="padding:8px 12px;border:1px solid #e2e8f0;border-radius:6px;font-size:13px;width:200px">
        </div>
        <div>
          <label style="display:block;font-size:11px;font-weight:700;color:#64748b;text-transform:uppercase;margin-bottom:4px">Postcode prefix</label>
          <input name="postcode" value="{postcode_filter}" placeholder="e.g. TR, SW, EX" style="padding:8px 12px;border:1px solid #e2e8f0;border-radius:6px;font-size:13px;width:120px">
        </div>
        <div>
          <label style="display:block;font-size:11px;font-weight:700;color:#64748b;text-transform:uppercase;margin-bottom:4px">Region</label>
          <select name="region" style="padding:8px 12px;border:1px solid #e2e8f0;border-radius:6px;font-size:13px">{region_options}</select>
        </div>
        <div>
          <label style="display:block;font-size:11px;font-weight:700;color:#64748b;text-transform:uppercase;margin-bottom:4px">Scheme</label>
          <select name="scheme" style="padding:8px 12px;border:1px solid #e2e8f0;border-radius:6px;font-size:13px">{scheme_options}</select>
        </div>
        <button type="submit" style="padding:8px 20px;background:#0f2547;color:white;border:none;border-radius:6px;font-size:13px;font-weight:600;cursor:pointer">Filter</button>
        <a href="/admin/contacts" style="padding:8px 16px;background:#f1f5f9;color:#64748b;border-radius:6px;font-size:13px;text-decoration:none">Clear</a>
      </form>
      <h2>Contacts — {showing}</h2>
      <table>
        <tr><th>Name</th><th>Email</th><th>Scheme</th><th>Postcode Area</th><th>Region</th><th>Status</th></tr>
        {rows or '<tr><td colspan="6" class="empty">No contacts match your filters</td></tr>'}
      </table>
    </div>"""
    return _page("Contacts", "contacts", body)


# ── Admin → Outreach ──────────────────────────────────────────────────────────

def _outreach_page(notice: str = "") -> HTMLResponse:
    campaign = outreach.get_campaign(supabase)
    notice_html = f'<div class="card" style="border-left:4px solid #0891b2">{notice}</div>' if notice else ""
    if not campaign:
        return _page("Outreach", "outreach", notice_html + """
    <div class="card"><h2>Outreach</h2>
      <p class="note">No campaign is set up yet. Run <code>webhook/migrations/2026-10-22_outreach_queue.sql</code>
      in Supabase → SQL Editor to create the first one (it starts paused).</p></div>""")
    s = outreach.summary(supabase, campaign)
    now = outreach.uk_now()
    paused = campaign["status"] != outreach.STATUS_ACTIVE
    limit = outreach.daily_limit()
    today = outreach.sent_today(supabase, campaign["id"], now)
    nxt = ("in the next few minutes" if outreach.in_send_window(now) and not paused
           else outreach.next_send_time(now).strftime("%a %d %b, %H:%M"))
    every = max(1, round(outreach.window_minutes() / limit)) if limit else 0
    status_badge = ('<span class="badge" style="background:#fef3c7;color:#b45309">Paused</span>' if paused
                    else '<span class="badge badge-ok">Sending</span>')
    toggle = (f'<form method="post" action="/admin/outreach/resume" style="display:inline"><button>Resume sending</button></form>'
              if paused else
              f'<form method="post" action="/admin/outreach/pause" style="display:inline"><button style="background:#b45309">Pause</button></form>')
    run_rows = "".join(
        f"<tr><td>{_esc(str(r.get('started_at') or '')[:16].replace('T', ' '))}</td><td>{_esc(r.get('trigger') or '')}</td>"
        f"<td>{r.get('sent') or 0}</td><td>{r.get('skipped') or 0}</td><td>{r.get('failed') or 0}</td>"
        f"<td>{r.get('bounced') or 0}</td><td>{r.get('complained') or 0}</td><td class=\"note\">{_esc(r.get('note') or '')}</td></tr>"
        for r in s["runs"]
    ) or '<tr><td colspan="8" class="empty">Nothing sent yet</td></tr>'
    subject, text, _html = outreach.render("there", f"{BASE_URL}/unsubscribe?email=…&token=…")
    body = f"""
    {notice_html}
    <div class="card">
      <h2>{_esc(campaign['name'])} {status_badge}</h2>
      <p class="note">One email per contact, never a second. Up to {limit} a day, sent one at a time between
      {outreach.SEND_FROM[0]:02d}:{outreach.SEND_FROM[1]:02d} and {outreach.SEND_UNTIL[0]:02d}:{outreach.SEND_UNTIL[1]:02d} UK time,
      Monday to Friday (about one every {every} minutes, so it never looks like a burst).
      Sent today: {today} of {limit}. Next send: {nxt}.
      Anyone who bounces, complains or unsubscribes goes on the do-not-email list before the next send.</p>
      <div style="display:flex;gap:10px;flex-wrap:wrap;align-items:center">
        {toggle}
        <form method="post" action="/admin/outreach/run" style="display:inline"
              onsubmit="return confirm('Send the rest of today\\'s allowance now, in one go, instead of spread through the day?')">
          <button style="background:#0891b2" {'disabled' if paused else ''}>Send the rest of today's batch now</button></form>
        <form method="post" action="/admin/outreach/test" style="display:inline-flex;gap:6px;align-items:center">
          <input name="email" type="email" required placeholder="your address"
                 style="padding:8px 12px;border:1px solid #e2e8f0;border-radius:6px;font-size:13px;width:220px">
          <button style="background:#64748b">Send me a test copy</button></form>
      </div>
    </div>
    <div class="stats">
      <div class="stat"><div class="lbl">Waiting to send</div><div class="val">{s['queued']:,}</div></div>
      <div class="stat"><div class="lbl">Sent</div><div class="val">{s['sent']:,}</div></div>
      <div class="stat"><div class="lbl">Delivered</div><div class="val">{s['delivered']:,}</div></div>
      <div class="stat"><div class="lbl">Bounced</div><div class="val">{s['bounced']:,}</div></div>
      <div class="stat"><div class="lbl">Complaints</div><div class="val">{s['complained']:,}</div></div>
      <div class="stat"><div class="lbl">Unsubscribed</div><div class="val">{s['unsubscribed']:,}</div></div>
      <div class="stat"><div class="lbl">Skipped</div><div class="val">{s['skipped']:,}</div></div>
      <div class="stat"><div class="lbl">Failed</div><div class="val">{s['failed']:,}</div></div>
    </div>
    <div class="card">
      <h2>Runs</h2>
      <table><tr><th>Started</th><th>By</th><th>Sent</th><th>Skipped</th><th>Failed</th><th>Bounced</th><th>Complaints</th><th>Note</th></tr>{run_rows}</table>
    </div>
    <div class="card">
      <h2>The email</h2>
      <p class="note">Subject: <strong>{_esc(subject)}</strong>. Wording lives in <code>webhook/outreach.py</code> (render).</p>
      <pre style="white-space:pre-wrap;font-family:Arial,sans-serif;font-size:14px;line-height:1.5;background:#f8fafc;padding:16px;border-radius:8px">{_esc(text)}</pre>
    </div>"""
    return _page("Outreach", "outreach", body)


@app.get("/admin/outreach", response_class=HTMLResponse)
async def admin_outreach(credentials=Depends(_check_admin)):
    return _outreach_page()


@app.post("/admin/outreach/pause", response_class=HTMLResponse)
async def admin_outreach_pause(credentials=Depends(_check_admin)):
    campaign = outreach.get_campaign(supabase)
    if campaign:
        outreach.set_paused(supabase, campaign["id"], True)
    return _outreach_page("Paused. Nothing will be sent until you resume.")


@app.post("/admin/outreach/resume", response_class=HTMLResponse)
async def admin_outreach_resume(credentials=Depends(_check_admin)):
    campaign = outreach.get_campaign(supabase)
    if campaign:
        outreach.set_paused(supabase, campaign["id"], False)
    return _outreach_page("Sending resumed. The next batch goes at the next scheduled time, or press Send now.")


@app.post("/admin/outreach/run", response_class=HTMLResponse)
async def admin_outreach_run(credentials=Depends(_check_admin)):
    r = await outreach.run_batch(supabase, trigger="admin")
    return _outreach_page(f"Batch finished: {r['sent']} sent, {r['skipped']} skipped, {r['failed']} failed"
                          + (f" ({_esc(r['note'])})" if r.get("note") else "") + ".")


@app.post("/admin/outreach/test", response_class=HTMLResponse)
async def admin_outreach_test(request: Request, credentials=Depends(_check_admin)):
    form = await request.form()
    email = str(form.get("email", "")).strip()
    if not outreach._EMAIL_RE.match(email):
        return _outreach_page("That address does not look right.")
    try:
        await outreach.send_to(email, "Matt", "test")
    except Exception as e:
        return _outreach_page(f"Could not send: {_esc(str(e)[:200])}")
    return _outreach_page(f"Test copy sent to {_esc(email)}. Its unsubscribe link is live: if you press it, "
                          "that address goes on the do-not-email list (remove it in Supabase if you need to).")


@app.get("/admin/courses", response_class=HTMLResponse)
async def admin_courses(credentials=Depends(_check_admin)):
    from datetime import date, timedelta
    refresh_catalogue(force=True)
    today = date.today()
    new_threshold = today - timedelta(days=14)

    new_courses = []
    cards = ""
    for cid, course in COURSES.items():
        if cid == "SUBSCRIPTION":
            continue
        pdf_link = _pdf_url(cid)
        pub_str = str(course.get("published", ""))
        try:
            pub_date = date.fromisoformat(pub_str)
            is_new = pub_date >= new_threshold
        except ValueError:
            is_new = False

        new_badge = '<span class="badge" style="background:#7c3aed;color:white">NEW</span> ' if is_new else ""
        if cid in UNDER_REVIEW:
            new_badge += '<span class="badge" style="background:#b45309;color:white">WITHDRAWN FOR REVISION</span> '
        if is_new:
            new_courses.append(course)

        hours = course['cpd_hours']
        cards += f"""
        <div class="course-card{' course-new' if is_new else ''}">
          <div class="cid">{new_badge}{course['course_id']}</div>
          <div class="ctitle">{course['title']}</div>
          <div class="cmeta">{hours:g} CPD Hour{'s' if hours != 1 else ''} &nbsp;•&nbsp;
            <a href="{pdf_link}" target="_blank" class="badge badge-ok" style="text-decoration:none">View PDF ↗</a>
          </div>
        </div>"""

    # New course alert banner
    alert = ""
    if new_courses:
        names = ", ".join(str(c['course_id']) for c in new_courses)
        alert = f"""
        <div style="background:#f5f3ff;border:2px solid #7c3aed;border-radius:8px;padding:16px 20px;margin-bottom:20px;display:flex;align-items:center;gap:12px">
          <span style="font-size:24px">🆕</span>
          <div>
            <strong style="color:#5b21b6">{len(new_courses)} new course{'s' if len(new_courses)!=1 else ''} published in the last 14 days</strong><br>
            <span style="font-size:13px;color:#6b7280">{names}</span>
          </div>
        </div>"""

    body = f"""
    {alert}
    <div class="card">
      <h2>Course Library ({len([k for k in COURSES if is_available(k)])} available, {len([k for k in COURSES if k in UNDER_REVIEW])} withdrawn for revision)</h2>
      <div class="course-grid">{cards}</div>
    </div>"""
    return _page("Courses", "courses", body)


@app.get("/admin/certificates", response_class=HTMLResponse)
async def admin_certificates(credentials=Depends(_check_admin)):
    res = supabase.table("certificates").select(
        "*, members(name, email)"
    ).order("issued_at", desc=True).limit(100).execute()

    test_ids = {r[0].get("id") for r in _classified_members() if r[1] == "test"}
    n_test = sum(1 for c in (res.data or []) if c.get("member_id") in test_ids)
    rows = ""
    for cert in (res.data or []):
        m = cert.get("members") or {}
        issued = (cert.get("issued_at") or "")[:10]
        if cert.get("member_id") in test_ids:
            m = dict(m, name=f"{m.get('name') or '—'} {_status_badge('test')}")
        verify_link = f'<a class="vlink" href="/verify/{cert["cert_number"]}" target="_blank">{cert["cert_number"]}</a>'
        rows += f"""<tr>
            <td>{verify_link}</td>
            <td>{m.get('name','—')}</td>
            <td>{cert.get('course_id','—')}</td>
            <td>{cert.get('cpd_hours',0):g}h</td>
            <td>{issued}</td>
        </tr>"""

    body = f"""
    <div class="card">
      <h2>Certificates issued ({len(res.data or []) - n_test} to members{f", {n_test} test" if n_test else ""})</h2>
      <table>
        <tr><th>Certificate #</th><th>Member</th><th>Course</th><th>CPD</th><th>Issued</th></tr>
        {rows or '<tr><td colspan="5" class="empty">No certificates issued yet</td></tr>'}
      </table>
    </div>"""
    return _page("Certificates", "certificates", body)


@app.get("/admin/system", response_class=HTMLResponse)
async def admin_system(credentials=Depends(_check_admin)):
    def var_status(key: str, required: bool = True) -> str:
        val = os.environ.get(key, "")
        if val and not val.startswith("placeholder"):
            return '<span class="badge badge-ok">Set</span>'
        return '<span class="badge badge-off">Not set</span>' if required else '<span class="badge badge-warn">Not set</span>'

    check_vars = [
        ("STRIPE_SECRET_KEY", "Stripe secret key", True, ""),
        ("STRIPE_WEBHOOK_SECRET", "Stripe webhook signing secret", True, ""),
        ("STRIPE_PRICE_SINGLE", "Stripe price, single course", True, ""),
        ("STRIPE_PRICE_SUBSCRIPTION", "Stripe price, annual subscription", True, ""),
        ("RESEND_API_KEY", "Resend (sends course and certificate emails)", True, ""),
        ("SUPABASE_URL", "Supabase project", True, ""),
        ("SUPABASE_SERVICE_ROLE_KEY", "Supabase service key", True, ""),
        ("ADMIN_PASSWORD", "This admin area", True, ""),
        ("DASHBOARD_SECRET", "Member login sessions", True,
         "If not set, every member is signed out whenever the app restarts or redeploys."),
        ("UNSUBSCRIBE_SECRET", "Unsubscribe links", True,
         "If not set, unsubscribe links in emails cannot be verified."),
        ("APP_URL", "This app's public address", False, "Defaults to app.meridiancpd.co.uk."),
        ("ADMIN_TEST_EMAILS", "Addresses treated as test accounts", False,
         "Optional, comma-separated. Our own domain and example.com are always treated as tests."),
        ("OUTREACH_DAILY_LIMIT", "Outreach emails a day", False,
         f"Optional. Default {outreach.DEFAULT_LIMIT}, ceiling {outreach.HARD_CEILING}. See Admin → Outreach."),
        ("OUTREACH_SCHEDULER", "Outreach scheduler", False,
         "Optional. Set to off to stop the daily batch without a deploy (pausing in Admin → Outreach does the same)."),
    ]
    vars_rows = "".join(
        f"<tr><td>{label}</td><td><code>{key}</code></td><td>{var_status(key, req)}</td>"
        f"<td style='font-size:12px;color:#64748b'>{note}</td></tr>"
        for key, label, req, note in check_vars)

    # Course PDFs: check each one on sale can actually be downloaded
    live = [k for k in COURSES if k != "SUBSCRIPTION" and is_available(k)]
    async def _check(cid):
        try:
            async with httpx.AsyncClient(timeout=6) as client:
                r = await client.head(_pdf_url(cid))
            return cid, r.status_code
        except Exception:
            return cid, None
    import asyncio
    results = dict(await asyncio.gather(*[_check(c) for c in live]))
    missing = [c for c in live if results.get(c) != 200]
    pdf_rows = "".join(
        f"<tr><td>{c}</td><td>{COURSES[c]['title']}</td><td>"
        + ('<span class="badge badge-ok">Downloadable</span>' if results.get(c) == 200
           else f'<span class="badge badge-off">Problem ({results.get(c) or "no response"})</span>')
        + "</td></tr>" for c in live)

    try:
        suppressed = supabase.table("outreach_suppressed").select("email", count="exact").execute().count or 0
    except Exception:
        suppressed = "unknown"

    body = f"""
    <div class="card section">
      <h2>Settings</h2>
      <table><tr><th>What it's for</th><th>Setting</th><th>Status</th><th></th></tr>{vars_rows}</table>
    </div>
    <div class="card section">
      <h2>Course PDFs on sale ({len(live) - len(missing)} of {len(live)} downloadable)</h2>
      <table><tr><th>Course</th><th>Title</th><th>PDF</th></tr>{pdf_rows}</table>
    </div>
    <div class="card section">
      <h2>Outreach</h2>
      <table>
        <tr><td>Marketing emails</td><td><span class="badge badge-warn">Paused</span></td></tr>
        <tr><td>Addresses on the permanent do-not-email list</td><td>{suppressed}</td></tr>
      </table>
      <p class="note" style="margin-top:10px">Outreach stays paused until it has a lawful contact list,
      per-contact and daily limits, and working unsubscribe links.</p>
    </div>
    <div class="card section">
      <h2>App</h2>
      <table>
        <tr><td>Health check</td><td><a class="vlink" href="/health">/health</a></td></tr>
        <tr><td>Stripe webhook address</td><td><code>{BASE_URL}/stripe-webhook</code></td></tr>
        <tr><td>Stripe events it needs</td><td style="font-size:12px">checkout.session.completed,
          customer.subscription.created, customer.subscription.updated, customer.subscription.deleted,
          invoice.paid, invoice.payment_failed</td></tr>
      </table>
    </div>"""
    return _page("System", "system", body)
