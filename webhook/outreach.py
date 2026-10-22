"""Daily outreach to the corporate contact list: one email per contact, a few dozen a day.

Why this lives in the app: the June campaign ran on a separate service that sent some
people the same email more than twenty times, logged every send as a success, and
linked to an unsubscribe page that did not exist. This sender deploys with the app, uses
the app's working /unsubscribe route, can be paused from Admin → Outreach, and is tested
(tests/test_outreach.py).

Rules enforced in code on every send:
  - one email per contact per campaign, ever (outreach_queue is unique per contact)
  - never to anyone suppressed, on the suppression list, or a member
  - at most OUTREACH_DAILY_LIMIT a day (default 50, ceiling 100), sent one at a time,
    spread across working hours (08:00-18:00 UK, Monday to Friday), never in a burst
  - every email carries a working unsubscribe link and List-Unsubscribe headers
  - bounces and complaints reported by Resend suppress the address before the next run

Campaign rows for this sender use the statuses app_active / app_paused. They must never
be set to 'active': that is the trigger word for the old Node service, which is still
deployed (idle) and would start sending its own emails to the whole list.
"""
import asyncio
import hashlib
import hmac
import os
import random
import re
from datetime import datetime, timedelta
from html import escape
from urllib.parse import quote
from zoneinfo import ZoneInfo

import httpx

from settings import APP_URL, SITE_URL

UK = ZoneInfo("Europe/London")
RESEND_API = "https://api.resend.com"
FROM_ADDRESS = "hello@meridiancpd.co.uk"
FROM_NAME = "Matt Davies, Meridian CPD"
DEFAULT_LIMIT = 50
HARD_CEILING = 100
SEND_FROM = (8, 0)    # working hours, UK time: the scheduler only sends between these ...
SEND_UNTIL = (18, 0)  # ... so nobody's phone pings at night
MAX_PER_TICK = 2      # catching up after a restart never dumps a burst
STATUS_ACTIVE = "app_active"
STATUS_PAUSED = "app_paused"
POLL_DAYS = 3         # how long to keep asking Resend what happened to a sent email
PACE_SECONDS = 0.6    # Resend allows two requests a second
TEST_DOMAINS = {"meridiancpd.co.uk", "example.com", "example.org"}
_EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[A-Za-z]{2,}$")
_NAME_RE = re.compile(r"^[A-Za-z][A-Za-z'\-]{1,19}$")

_run_lock = asyncio.Lock()


# ── The email ─────────────────────────────────────────────────────────────────

SUBJECT = "Renewal's coming and the CPD hours aren't there yet?"
OFFER_DEADLINE = "31 December"   # the £79 price holds until then; raise it in January


# The hello@ signature Matt set up in Gmail (22 October): same fonts, colours and logo, so
# an outreach email and a reply from the inbox look like the same sender.
INK = "#0d1f0e"        # text
MUTED = "#5b6660"      # tagline
SMALL = "#8a918c"      # legal line and footer
RULE = "#d9d5c9"       # hairline
LOGO_URL = "https://serensurveying.co.uk/assets/img/email/meridian-cpd-lockup.png"
TAGLINE = "Practitioner-written CPD for domestic energy assessors, retrofit assessors and retrofit coordinators. Stay sharp. Stay certified."
TRADING_LINE = "Meridian CPD is a trading name of FistralAI Ltd, registered in England and Wales, company number 17091704."

SIGNATURE_TEXT = f"""Matt Davies
Meridian CPD
hello@meridiancpd.co.uk  ·  meridiancpd.co.uk

{TAGLINE}
{TRADING_LINE}"""

SIGNATURE_HTML = f"""<table cellpadding="0" cellspacing="0" border="0" style="font-family:Helvetica,Arial,sans-serif;font-size:14px;line-height:20px;color:{INK};border-collapse:collapse">
<tr><td style="padding:0 0 10px;line-height:20px"><strong>Matt Davies</strong><br>Meridian CPD<br><a href="mailto:hello@meridiancpd.co.uk" style="color:{INK};text-decoration:none">hello@meridiancpd.co.uk</a>&nbsp;&nbsp;·&nbsp;&nbsp;<a href="{SITE_URL}/" style="color:{INK};text-decoration:none">meridiancpd.co.uk</a></td></tr>
<tr><td style="padding:12px 0 0;border-top:1px solid {RULE}"><a href="{SITE_URL}/" style="text-decoration:none"><img src="{LOGO_URL}" width="140" height="36" alt="Meridian CPD" style="max-width:100%;height:36px;display:block;border:0;width:140px"></a></td></tr>
<tr><td style="padding:8px 0 0;font-size:12px;line-height:18px;color:{MUTED}">{TAGLINE}</td></tr>
<tr><td style="padding:8px 0 0;font-size:11px;line-height:16px;color:{SMALL}">{TRADING_LINE}</td></tr>
</table>"""


def greeting_name(first_name: str | None) -> str:
    """The scraped first names are mostly fine, but some are initials, company names or
    shouted in capitals. Anything that does not look like a first name becomes 'there'."""
    name = (first_name or "").strip()
    if not _NAME_RE.match(name):
        return "there"
    return name if name[1:] != name[1:].upper() else name.capitalize()


def render(first_name: str | None, unsubscribe_url: str) -> tuple[str, str, str]:
    """Returns (subject, text, html). The wording is approved by Matt; change it here."""
    name = greeting_name(first_name)
    verify = f"{APP_URL}/verify"
    privacy = f"{SITE_URL}/privacy.html"
    text = f"""Hello {name},

Every assessor knows the feeling. The renewal reminder lands, you open your CPD record, and the year that was meant to be full of webinars and reading has somehow got away from you. Six weeks left, or four, or two, and the hours still have to be real, evidenced and ready to show your scheme.

I'm a practising assessor and I built Meridian CPD because I was that person. I wanted CPD I could actually use on the job, written by people who do the job, that I could get through in an evening and have the certificate in my hand the same night. It didn't exist, so I made it. I love doing it, and I'd like you to try it.

Start with the free one. "RdSAP 10: What's Changed and Why" is two CPD hours, certificate included, free with the code MERIDIAN10 at meridiancpd.co.uk. Read it when it suits you, confirm you've completed it, and your certificate arrives straight away, with a number anyone, including your scheme, can check at meridiancpd.co.uk/verify.

If it works for you, the annual subscription is every course in the library, plus every new one we add, for £79 a year if you join before {OFFER_DEADLINE}.

If this isn't for you, the unsubscribe link below works, and that's the end of it.

{SIGNATURE_TEXT}

We found your work address on the public assessor register. If you'd rather not hear from us: {unsubscribe_url}
Privacy: meridiancpd.co.uk/privacy.html
"""
    p = "margin:0 0 16px"
    link = f'style="color:{INK};text-decoration:underline"'
    html = f"""<!DOCTYPE html><html><body style="margin:0;padding:0;background:#ffffff">
<div style="font-family:Helvetica,Arial,sans-serif;font-size:14px;line-height:20px;color:{INK};max-width:600px;margin:0 auto;padding:24px">
<p style="{p}">Hello {escape(name)},</p>
<p style="{p}">Every assessor knows the feeling. The renewal reminder lands, you open your CPD record, and the year that was meant to be full of webinars and reading has somehow got away from you. Six weeks left, or four, or two, and the hours still have to be real, evidenced and ready to show your scheme.</p>
<p style="{p}">I'm a practising assessor and I built Meridian CPD because I was that person. I wanted CPD I could actually use on the job, written by people who do the job, that I could get through in an evening and have the certificate in my hand the same night. It didn't exist, so I made it. I love doing it, and I'd like you to try it.</p>
<p style="{p}"><strong>Start with the free one.</strong> &ldquo;RdSAP 10: What's Changed and Why&rdquo; is two CPD hours, certificate included, free with the code <strong>MERIDIAN10</strong> at <a href="{SITE_URL}" {link}>meridiancpd.co.uk</a>. Read it when it suits you, confirm you've completed it, and your certificate arrives straight away, with a number anyone, including your scheme, can check at <a href="{verify}" {link}>meridiancpd.co.uk/verify</a>.</p>
<p style="{p}">If it works for you, the annual subscription is every course in the library, plus every new one we add, for <strong>£79 a year</strong> if you join before {OFFER_DEADLINE}.</p>
<p style="margin:0 0 24px">If this isn't for you, the unsubscribe link below works, and that's the end of it.</p>
{SIGNATURE_HTML}
<p style="margin:24px 0 0;font-size:11px;line-height:16px;color:{SMALL}">We found your work address on the public assessor register. If you'd rather not hear from us: <a href="{unsubscribe_url}" style="color:{SMALL}">unsubscribe</a>. Privacy: <a href="{privacy}" style="color:{SMALL}">meridiancpd.co.uk/privacy.html</a></p>
</div></body></html>"""
    return SUBJECT, text, html


# ── Links ─────────────────────────────────────────────────────────────────────

def unsubscribe_token(email: str) -> str:
    """Same scheme as main._verify_unsubscribe_token: HMAC of the address as stored."""
    secret = os.environ.get("UNSUBSCRIBE_SECRET", "").encode()
    return hmac.new(secret, email.encode(), hashlib.sha256).hexdigest()[:16]


def unsubscribe_url(email: str) -> str:
    return f"{APP_URL}/unsubscribe?email={quote(email)}&token={unsubscribe_token(email)}"


# ── Limits and timing ─────────────────────────────────────────────────────────

def daily_limit() -> int:
    try:
        n = int(os.environ.get("OUTREACH_DAILY_LIMIT", DEFAULT_LIMIT))
    except ValueError:
        n = DEFAULT_LIMIT
    return max(0, min(n, HARD_CEILING))


def uk_now() -> datetime:
    return datetime.now(UK)


def start_of_day(now: datetime) -> datetime:
    return now.astimezone(UK).replace(hour=0, minute=0, second=0, microsecond=0)


def in_send_window(now: datetime) -> bool:
    now = now.astimezone(UK)
    if now.weekday() >= 5:
        return False
    t = (now.hour, now.minute)
    return SEND_FROM <= t < SEND_UNTIL


def next_send_time(now: datetime) -> datetime:
    """The next moment the scheduler would send, for showing in Admin."""
    now = now.astimezone(UK)
    candidate = now.replace(hour=SEND_FROM[0], minute=SEND_FROM[1], second=0, microsecond=0)
    if candidate <= now:
        candidate += timedelta(days=1)
    while candidate.weekday() >= 5:
        candidate += timedelta(days=1)
    return candidate


# ── Database helpers ──────────────────────────────────────────────────────────

def get_campaign(db) -> dict | None:
    """The one campaign this sender runs (statuses app_active / app_paused)."""
    res = db.table("outreach_campaigns").select("*").in_("status", [STATUS_ACTIVE, STATUS_PAUSED]) \
        .order("created_at", desc=True).limit(1).execute()
    return (res.data or [None])[0]


def set_paused(db, campaign_id: str, paused: bool) -> None:
    db.table("outreach_campaigns").update({"status": STATUS_PAUSED if paused else STATUS_ACTIVE}) \
        .eq("id", campaign_id).execute()


def sent_today(db, campaign_id: str, now: datetime) -> int:
    res = db.table("outreach_sends").select("id", count="exact").eq("campaign_id", campaign_id) \
        .gte("sent_at", start_of_day(now).isoformat()).execute()
    return res.count or 0


def ran_today(db, campaign_id: str, now: datetime, trigger: str = "scheduler") -> bool:
    res = db.table("outreach_runs").select("id").eq("campaign_id", campaign_id).eq("trigger", trigger) \
        .gte("started_at", start_of_day(now).isoformat()).limit(1).execute()
    return bool(res.data)


def is_suppressed(db, email: str) -> bool:
    res = db.table("outreach_suppressed").select("id").eq("email", email).limit(1).execute()
    if res.data:
        return True
    low = email.lower()
    if low != email:
        res = db.table("outreach_suppressed").select("id").eq("email", low).limit(1).execute()
        if res.data:
            return True
    return False


def is_member(db, email: str) -> bool:
    res = db.table("members").select("id").eq("email", email.lower()).limit(1).execute()
    return bool(res.data)


def suppress(db, email: str, reason: str) -> None:
    db.table("outreach_suppressed").upsert({"email": email, "reason": reason}).execute()
    db.table("outreach_contacts").update({"suppressed": True, "suppressed_reason": reason}).eq("email", email).execute()


def why_not(db, contact: dict | None) -> str | None:
    """Reason not to email this contact right now, or None if it is fine to send."""
    if not contact:
        return "contact missing"
    email = (contact.get("email") or "").strip()
    if not _EMAIL_RE.match(email):
        return "address not valid"
    if email.split("@")[1].lower() in TEST_DOMAINS:
        return "test domain"
    if contact.get("suppressed"):
        return "contact suppressed"
    if is_suppressed(db, email):
        return "on suppression list"
    if is_member(db, email):
        return "already a member"
    return None


# ── Sending ───────────────────────────────────────────────────────────────────

async def send_to(email: str, first_name: str | None, tag: str) -> str:
    """Sends one email through Resend and returns Resend's id. Raises on failure."""
    api_key = os.environ["RESEND_API_KEY"]
    unsub = unsubscribe_url(email)
    subject, text, html = render(first_name, unsub)
    payload = {
        "from": f"{FROM_NAME} <{FROM_ADDRESS}>",
        "to": [email],
        "reply_to": FROM_ADDRESS,
        "subject": subject,
        "text": text,
        "html": html,
        "headers": {
            "List-Unsubscribe": f"<mailto:{FROM_ADDRESS}?subject=unsubscribe>, <{unsub}>",
            "List-Unsubscribe-Post": "List-Unsubscribe=One-Click",
        },
        # Resend only allows letters, numbers, underscores and dashes in a tag
        "tags": [{"name": "campaign", "value": re.sub(r"[^A-Za-z0-9_-]+", "-", tag).strip("-")[:64] or "outreach"}],
    }
    async with httpx.AsyncClient() as client:
        r = await client.post(f"{RESEND_API}/emails", headers={"Authorization": f"Bearer {api_key}"},
                              json=payload, timeout=30)
        r.raise_for_status()
        return (r.json() or {}).get("id", "")


def _run_row(db, campaign_id: str, trigger: str, now: datetime) -> dict:
    """The scheduler's many small sends in a day share one row; an admin press gets its own."""
    if trigger == "scheduler":
        res = db.table("outreach_runs").select("*").eq("campaign_id", campaign_id).eq("trigger", trigger) \
            .gte("started_at", start_of_day(now).isoformat()).limit(1).execute()
        if res.data:
            return res.data[0]
    return db.table("outreach_runs").insert({
        "campaign_id": campaign_id, "trigger": trigger, "started_at": now.isoformat(),
    }).execute().data[0]


async def run_batch(db, trigger: str, now: datetime | None = None, limit: int | None = None,
                    max_send: int | None = None, poll: bool = True) -> dict:
    """Sends for the campaign: up to today's remaining limit, or max_send if smaller. Safe to
    call any number of times a day: the limit counts every send made today, whoever triggered it."""
    now = now or uk_now()
    campaign = get_campaign(db)
    result = {"sent": 0, "skipped": 0, "failed": 0, "bounced": 0, "complained": 0, "note": ""}
    if not campaign:
        result["note"] = "no campaign"
        return result
    if campaign["status"] != STATUS_ACTIVE and trigger != "test":
        result["note"] = "paused"
        return result
    async with _run_lock:
        run = _run_row(db, campaign["id"], trigger, now)
        try:
            if poll:
                bounced, complained = await poll_delivery(db, campaign["id"], now)
                result["bounced"], result["complained"] = bounced, complained
            cap = daily_limit() if limit is None else min(limit, HARD_CEILING)
            room = cap - sent_today(db, campaign["id"], now)
            if max_send is not None:
                room = min(room, max_send)
            if room <= 0:
                result["note"] = "daily limit already reached"
            failures_in_a_row = 0
            stopped = False
            while result["sent"] < room and not stopped:
                # Skipped rows change status, so each pass fetches the next unprocessed ones.
                queued = db.table("outreach_queue").select("*").eq("campaign_id", campaign["id"]) \
                    .eq("status", "queued").order("position").limit(room - result["sent"]).execute().data or []
                if not queued:
                    if not result["sent"]:
                        result["note"] = "queue empty"
                    break
                for row in queued:
                    contact = (db.table("outreach_contacts").select("*").eq("id", row["contact_id"])
                               .limit(1).execute().data or [None])[0]
                    reason = why_not(db, contact)
                    if reason:
                        db.table("outreach_queue").update({"status": "skipped", "note": reason}).eq("id", row["id"]).execute()
                        result["skipped"] += 1
                        continue
                    try:
                        msg_id = await send_to(contact["email"], contact.get("first_name"), campaign["name"])
                    except Exception as e:  # Resend refused or is down
                        failures_in_a_row += 1
                        result["failed"] += 1
                        db.table("outreach_queue").update({"status": "failed", "note": str(e)[:200]}).eq("id", row["id"]).execute()
                        if failures_in_a_row >= 3:
                            result["note"] = "stopped: three failures in a row"
                            stopped = True
                            break
                        continue
                    failures_in_a_row = 0
                    stamp = now.isoformat()
                    db.table("outreach_sends").insert({
                        "contact_id": contact["id"], "campaign_id": campaign["id"], "step_number": 1,
                        "status": "sent", "sendgrid_message_id": f"resend:{msg_id}", "sent_at": stamp,
                    }).execute()
                    db.table("outreach_queue").update({"status": "sent", "sent_at": stamp}).eq("id", row["id"]).execute()
                    result["sent"] += 1
                    await asyncio.sleep(PACE_SECONDS)
        finally:
            db.table("outreach_runs").update({
                "finished_at": now.isoformat(),
                **{k: (run.get(k) or 0) + result[k] for k in ("sent", "skipped", "failed", "bounced", "complained")},
                "note": result["note"] or run.get("note") or "",
            }).eq("id", run["id"]).execute()
    return result


# ── Bounces and complaints ────────────────────────────────────────────────────

async def poll_delivery(db, campaign_id: str, now: datetime | None = None) -> tuple[int, int]:
    """Asks Resend what happened to each recent send still marked 'sent'. Bounced and
    complained addresses go on the suppression list; delivered ones stop being polled."""
    now = now or uk_now()
    since = (now - timedelta(days=POLL_DAYS)).isoformat()
    rows = db.table("outreach_sends").select("id, contact_id, sendgrid_message_id").eq("campaign_id", campaign_id) \
        .eq("status", "sent").gte("sent_at", since).execute().data or []
    api_key = os.environ.get("RESEND_API_KEY", "")
    bounced = complained = 0
    async with httpx.AsyncClient() as client:
        for row in rows:
            ref = row.get("sendgrid_message_id") or ""
            if not ref.startswith("resend:"):
                continue
            try:
                r = await client.get(f"{RESEND_API}/emails/{ref[7:]}", headers={"Authorization": f"Bearer {api_key}"}, timeout=20)
                if r.status_code != 200:
                    continue
                event = (r.json() or {}).get("last_event") or ""
            except Exception:
                continue
            if event in ("bounced", "complained"):
                contact = (db.table("outreach_contacts").select("email").eq("id", row["contact_id"]).limit(1).execute().data or [None])[0]
                if contact:
                    suppress(db, contact["email"], event)
                db.table("outreach_sends").update({"status": event}).eq("id", row["id"]).execute()
                if event == "bounced":
                    bounced += 1
                else:
                    complained += 1
            elif event == "delivered":
                db.table("outreach_sends").update({"status": "delivered"}).eq("id", row["id"]).execute()
            await asyncio.sleep(PACE_SECONDS)
    return bounced, complained


# ── Scheduler ─────────────────────────────────────────────────────────────────

def window_minutes() -> int:
    return (SEND_UNTIL[0] * 60 + SEND_UNTIL[1]) - (SEND_FROM[0] * 60 + SEND_FROM[1])


def expected_by_now(now: datetime, limit: int) -> int:
    """How many of today's emails should have gone out by this time, if the day's limit is
    spread evenly across the send window (50 a day is one every 12 minutes)."""
    if not in_send_window(now) or limit <= 0:
        return 0
    now = now.astimezone(UK)
    elapsed = (now.hour * 60 + now.minute) - (SEND_FROM[0] * 60 + SEND_FROM[1])
    return min(limit, int(elapsed * limit / window_minutes()))


def drip_size(db, now: datetime) -> int:
    """How many to send on this tick: enough to keep pace with the day, at most MAX_PER_TICK."""
    campaign = get_campaign(db)
    if not campaign or campaign["status"] != STATUS_ACTIVE:
        return 0
    behind = expected_by_now(now, daily_limit()) - sent_today(db, campaign["id"], now)
    return max(0, min(MAX_PER_TICK, behind))


async def scheduler_loop(get_db, get_now=uk_now, tick_seconds=(45, 120)) -> None:
    """Runs inside the web process. Through each weekday's working hours it sends one or
    two emails at a time, keeping pace with the daily limit, on a jittered timer. Delivery
    results from Resend are checked on the day's first tick. If the process restarts, the
    send log stops it exceeding the day's limit."""
    while True:
        try:
            now = get_now()
            db = get_db()
            n = drip_size(db, now)
            if n:
                campaign = get_campaign(db)
                first_of_day = not ran_today(db, campaign["id"], now, "scheduler")
                result = await run_batch(db, trigger="scheduler", now=now, max_send=n, poll=first_of_day)
                if result["sent"] or result["failed"] or result["bounced"] or result["complained"]:
                    print(f"Outreach: {result}")
        except Exception as e:
            print(f"Outreach scheduler error: {e}")
        await asyncio.sleep(random.uniform(*tick_seconds))


# ── Figures for Admin ─────────────────────────────────────────────────────────

def summary(db, campaign: dict) -> dict:
    cid = campaign["id"]
    def count(table, **eq):
        q = db.table(table).select("id", count="exact")
        for k, v in eq.items():
            q = q.eq(k, v)
        return q.execute().count or 0
    sends = db.table("outreach_sends").select("status").eq("campaign_id", cid).execute().data or []
    by_status = {}
    for s in sends:
        by_status[s["status"]] = by_status.get(s["status"], 0) + 1
    unsubscribed = db.table("outreach_suppressed").select("id", count="exact").eq("reason", "unsubscribed") \
        .gte("suppressed_at", campaign["created_at"]).execute().count or 0
    runs = db.table("outreach_runs").select("*").eq("campaign_id", cid).order("started_at", desc=True).limit(10).execute().data or []
    return {
        "queued": count("outreach_queue", campaign_id=cid, status="queued"),
        "sent": len(sends),
        "delivered": by_status.get("delivered", 0),
        "bounced": by_status.get("bounced", 0),
        "complained": by_status.get("complained", 0),
        "skipped": count("outreach_queue", campaign_id=cid, status="skipped"),
        "failed": count("outreach_queue", campaign_id=cid, status="failed"),
        "unsubscribed": unsubscribed,
        "runs": runs,
    }
