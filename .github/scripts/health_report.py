"""
Meridian CPD: daily funnel report

Runs at 07:20 UTC via GitHub Actions and emails REPORT_TO_EMAIL one screen: yesterday and
the last 7 days from checkout to certificate, with red lines at the top for anything that
needs Matt. This file only fetches; what the email says is decided in funnel.py.

Reads:
- Supabase (service key): members, purchases, completions, certificates, member_signins,
  free_course_followup_sends, outreach_sends, outreach_suppressed
- Stripe (STRIPE_REPORT_KEY, a restricted key with Checkout Sessions: Read and nothing
  else): checkout sessions of the last 8 days. Without it the report says so in a red line.
- The app's /health: up or down, courses on sale, the free code, the series price
"""
import os
import sys
from datetime import datetime, timezone, timedelta

import httpx
from supabase import create_client

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import funnel  # noqa: E402


def fail(reason: str):
    """Stop with a reason that shows on the GitHub Actions run page (not just in the log)."""
    print(f"::error title=Health report not sent::{reason}")
    sys.exit(1)


SUPABASE_URL   = os.environ.get("SUPABASE_URL", "").strip()
SUPABASE_KEY   = os.environ.get("SUPABASE_SERVICE_ROLE_KEY", "").strip()
RESEND_API_KEY = os.environ.get("RESEND_API_KEY", "").strip()
STRIPE_KEY     = os.environ.get("STRIPE_REPORT_KEY", "").strip()
REPORT_TO      = os.environ.get("REPORT_TO_EMAIL", "mattid272@gmail.com")
APP_URL        = os.environ.get("APP_URL", "https://app.meridiancpd.co.uk").rstrip("/")
PAGE = 1000

missing = [name for name, val in [
    ("SUPABASE_URL", SUPABASE_URL),
    ("SUPABASE_SERVICE_ROLE_KEY", SUPABASE_KEY),
    ("RESEND_API_KEY", RESEND_API_KEY),
] if not val]
if missing:
    fail("Missing GitHub repository secret(s): " + ", ".join(missing)
         + ". Add them under Settings > Secrets and variables > Actions.")

try:
    supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
except Exception as e:
    fail(f"Could not connect to Supabase: {type(e).__name__}: {str(e)[:200]}")

now = datetime.now(timezone.utc)
since = (funnel.windows(now)["week"][0] - timedelta(days=1)).isoformat()


def q(label, fn):
    """The result, or None (shown as n/a) when this one read fails."""
    try:
        return fn()
    except Exception as e:
        print(f"  Warning: {label}: {type(e).__name__}: {str(e)[:200]}")
        return None


def rows(table, cols, since_field=None):
    """Every row (paged, Supabase returns at most 1000 at a time), or only those since
    the start of the report's first day."""
    out, start = [], 0
    while True:
        query = supabase.table(table).select(cols)
        if since_field:
            query = query.gte(since_field, since)
        page = query.range(start, start + PAGE - 1).execute().data or []
        out += page
        if len(page) < PAGE:
            return out
        start += PAGE


def purchases():
    try:
        return rows("purchases", "member_id, course_id, amount_gbp, stripe_session_id, purchased_at, series_id")
    except Exception:  # before the series migration there is no series_id column
        return rows("purchases", "member_id, course_id, amount_gbp, stripe_session_id, purchased_at")


def last_free_order():
    res = (supabase.table("purchases").select("purchased_at").eq("amount_gbp", 0)
           .like("stripe_session_id", "cs_live%").order("purchased_at", desc=True).limit(1).execute())
    found = res.data or []
    return found[0]["purchased_at"] if found else "none"  # funnel.py shows it as a London date


def health():
    r = httpx.get(f"{APP_URL}/health", timeout=20)
    r.raise_for_status()
    return r.json()


def stripe_sessions():
    """Checkout sessions created since the report's first day: id, created, status, amount."""
    if not STRIPE_KEY:
        return None
    out, after = [], None
    created = int(datetime.fromisoformat(since).timestamp())
    while True:
        params = {"limit": 100, "created[gte]": created}
        if after:
            params["starting_after"] = after
        r = httpx.get("https://api.stripe.com/v1/checkout/sessions", params=params,
                      auth=(STRIPE_KEY, ""), timeout=30)
        r.raise_for_status()
        body = r.json()
        out += [{"id": s.get("id"), "created": s.get("created"), "status": s.get("status"),
                 "amount_total": s.get("amount_total")} for s in body.get("data", [])]
        if not body.get("has_more") or not body.get("data"):
            return out
        after = body["data"][-1]["id"]


# ── Gather ────────────────────────────────────────────────────────────────────
print("Gathering report data...")
data = {
    "health":          q("app /health", health),
    "stripe_sessions": q("Stripe checkout sessions", stripe_sessions),
    "members":         q("members", lambda: rows("members", "id, plan, stripe_customer_id, joined_at, marketing_consent")),
    "purchases":       q("purchases", purchases),
    "last_free_order": q("last free order", last_free_order),
    "opened":          q("courses opened", lambda: rows("completions", "downloaded_at", "downloaded_at")),
    "completed":       q("completions", lambda: rows("completions", "completed_at", "completed_at")),
    "certificates":    q("certificates", lambda: rows("certificates", "issued_at", "issued_at")),
    "signins":         q("sign-ins", lambda: rows("member_signins", "signed_in_at", "signed_in_at")),
    "followups":       q("follow-up emails", lambda: rows("free_course_followup_sends", "sent_at, status", "sent_at")),
    "outreach_sends":  q("outreach emails", lambda: rows("outreach_sends", "sent_at", "sent_at")),
    "suppressed":      q("unsubscribes", lambda: rows("outreach_suppressed", "suppressed_at, reason", "suppressed_at")),
}
# Key set but Stripe would not answer: a different red line from "no key".
data["stripe_error"] = bool(STRIPE_KEY) and data["stripe_sessions"] is None

report = funnel.build(data, now)

# ── Send ──────────────────────────────────────────────────────────────────────
# The repo is public and so is this run's log: nothing from the report is printed.
print(f"Sending report ({len(report['red'])} red line(s))...")

try:
    resp = httpx.post(
        "https://api.resend.com/emails",
        headers={"Authorization": f"Bearer {RESEND_API_KEY}"},
        json={
            "from": "Meridian CPD <hello@meridiancpd.co.uk>",
            "to": [REPORT_TO],
            "subject": report["subject"],
            "text": report["text"],
            "html": report["html"],
        },
        timeout=30,
    )
except Exception as e:
    fail(f"Could not reach the email service (Resend): {type(e).__name__}: {str(e)[:200]}")

if resp.status_code >= 400:
    fail(f"Resend rejected the email (HTTP {resp.status_code}): {resp.text[:300]}. "
         "The same key sends new-course emails from this repo, so those are failing too.")

print("Report sent.")
