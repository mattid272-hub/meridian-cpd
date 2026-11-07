"""Follow-up emails for people who took a free course (MERIDIAN10) and have paid nothing.

The sequence Matt approved on 6 November 2026:
  1. nudge    finish the free course: 14 days after taking it, only if not completed
  2. next     what's next (a Field Work series at £39.99, or the year at the annual price
              checkout charges): 7 days after completing the free course, or after the nudge
              if it was never completed; while FREE_FOLLOWUP_PRICE_RISE is on, the £79
              version carries a heads-up (£99 from 1 January; subscribe before and keep £79)
  3. price    the annual price rises to £99 on 1 January 2027: once, between 1 and 23
              December 2026, and only while checkout still charges £79 and
              FREE_FOLLOWUP_PRICE_RISE is on (Matt sets it once the £99 line is live on the
              site); it covers what 'next' says, so 'next' is not sent after it
  4. monthly  then at most one email a month: each edition is its own dated entry in
              MONTHLY_EDITIONS and needs Matt's approval of its text; the list is empty, so
              nothing beyond step 3 is sent until he adds one

The switch is the FREE_FOLLOWUP environment variable and it defaults to off:
  off      nothing runs (the default)
  dry_run  works out who would get what, prints it once a day and shows it in
           Admin -> Follow-up; sends nothing and writes nothing
  on       sends, at most FREE_FOLLOWUP_DAILY_LIMIT a day (default 10), one or two at a
           time, weekdays 09:00 to 17:00 UK

Rules enforced on every send (the contact rule in Matt's HQ, 5 November 2026):
  - each step goes to a person once, ever (free_course_followup_sends is unique per
    member and step), and a failed send is not retried, as it may have gone
  - the sequence stops for anyone who buys anything, starts a subscription, is on the
    suppression list (unsubscribed, bounced, complained, the 12 June 2026 unsubscribers),
    or said no to marketing (members.marketing_consent = false)
  - at least FREE_FOLLOWUP_MIN_GAP_DAYS (default 30) since the last email from this
    sequence or from the outreach sender to the same address
  - at most FREE_FOLLOWUP_MAX_EMAILS (default 4) from this sequence to a person, ever
  - the marketing steps (next, price, monthly) go only to people who said yes to hearing
    from us, unless FREE_FOLLOWUP_CONSENT is set to not_no (see the PR for why)
  - every email carries the app's working unsubscribe link and List-Unsubscribe headers
  - the annual price in an email is the price checkout charges, read from the Stripe price
    in STRIPE_PRICE_SUBSCRIPTION (a read, never a change), not the calendar; if it cannot be
    read, or is not £79 or £99 (the two prices the approved texts are written for), no email
    that names the annual price goes
  - bounces and complaints reported by Resend suppress the address before the next send

The wording is in the templates below. It was drafted for Matt's approval; a changed word
needs his approval again before the switch is turned on.
"""
import asyncio
import os
import random
import re
from datetime import datetime, timedelta
from html import escape

import httpx

import outreach
from settings import APP_URL, SITE_URL

UK = outreach.UK
RESEND_API = outreach.RESEND_API
FROM_ADDRESS = outreach.FROM_ADDRESS
FROM_NAME = outreach.FROM_NAME
TAG = "free-course-followup"
TABLE = "free_course_followup_sends"

MODES = ("off", "dry_run", "on")
DEFAULT_LIMIT = 10
HARD_CEILING = 50
DEFAULT_GAP_DAYS = 30
DEFAULT_MAX_EMAILS = 4
SEND_FROM = (9, 0)
SEND_UNTIL = (17, 0)
MAX_PER_TICK = 2
PACE_SECONDS = 0.6
POLL_DAYS = 3

NUDGE_AFTER_DAYS = 14
NEXT_AFTER_COMPLETION_DAYS = 7
PRICE_NOTICE_FROM = datetime(2026, 12, 1, tzinfo=UK)
PRICE_NOTICE_UNTIL = datetime(2026, 12, 24, tzinfo=UK)   # exclusive: the last day is 23 December

ANNUAL_PRICES = (79, 99)   # the annual prices the approved texts are written for
PRICE_CACHE_HOURS = 6

STEPS = ("nudge", "next", "price")
MARKETING_STEPS = {"next", "price"}   # and every monthly edition

COURSES_URL = f"{SITE_URL}/courses.html"
PRIVACY_URL = f"{SITE_URL}/privacy.html"
TEST_DOMAINS = outreach.TEST_DOMAINS

# Monthly editions, each approved by Matt before it is added. Shape:
#   {"key": "2027-02", "send_from": datetime(2027, 2, 1, tzinfo=UK),
#    "send_until": datetime(2027, 3, 1, tzinfo=UK), "subject": "...", "paragraphs": ["...", ...]}
# A paragraph may use {name}. Each edition goes to a person at most once.
MONTHLY_EDITIONS: list[dict] = []


# ── Settings ──────────────────────────────────────────────────────────────────

def mode() -> str:
    m = os.environ.get("FREE_FOLLOWUP", "off").strip().lower()
    return m if m in MODES else "off"


def _int_env(key: str, default: int, low: int, high: int) -> int:
    try:
        n = int(os.environ.get(key, default))
    except ValueError:
        n = default
    return max(low, min(n, high))


def daily_limit() -> int:
    return _int_env("FREE_FOLLOWUP_DAILY_LIMIT", DEFAULT_LIMIT, 0, HARD_CEILING)


def min_gap_days() -> int:
    return _int_env("FREE_FOLLOWUP_MIN_GAP_DAYS", DEFAULT_GAP_DAYS, 7, 365)


def max_emails() -> int:
    return _int_env("FREE_FOLLOWUP_MAX_EMAILS", DEFAULT_MAX_EMAILS, 0, 12)


def consent_mode() -> str:
    """yes_only: marketing steps only to members who said yes (members.marketing_consent
    true). not_no: also to those who never answered. A 'no' always stops everything."""
    m = os.environ.get("FREE_FOLLOWUP_CONSENT", "yes_only").strip().lower()
    return m if m in ("yes_only", "not_no") else "yes_only"


def price_rise_notice_on() -> bool:
    """FREE_FOLLOWUP_PRICE_RISE=on lets the price-rise email go (1 to 23 December, while
    checkout still charges £79). Default off: Matt turns it on once the £99 line is live
    on meridiancpd.co.uk, so the email never says something the site does not."""
    return os.environ.get("FREE_FOLLOWUP_PRICE_RISE", "off").strip().lower() == "on"


def _fetch_annual_pence() -> int | None:
    """Unit amount, in pence, of the Stripe price the webhook treats as the annual
    subscription (STRIPE_PRICE_SUBSCRIPTION). Reads only."""
    price_id = os.environ.get("STRIPE_PRICE_SUBSCRIPTION", "").strip()
    if not price_id:
        return None
    import stripe   # main sets stripe.api_key at start-up
    price = stripe.Price.retrieve(price_id)
    amount = price.get("unit_amount") if hasattr(price, "get") else getattr(price, "unit_amount", None)
    return int(amount) if amount is not None else None


_price_cache: dict = {"at": None, "gbp": None}


def annual_price_gbp(now: datetime | None = None) -> int | None:
    """The annual price checkout charges, in whole pounds, if it is one the approved texts
    are written for (£79 or £99); else None. Cached for PRICE_CACHE_HOURS."""
    now = now or datetime.now(UK)
    at = _price_cache["at"]
    if at is not None and timedelta(0) <= now - at < timedelta(hours=PRICE_CACHE_HOURS):
        return _price_cache["gbp"]
    try:
        pence = _fetch_annual_pence()
    except Exception as e:
        print(f"Free-course follow-up: could not read the annual price from Stripe ({type(e).__name__})")
        pence = None
    gbp = pence // 100 if pence is not None and pence % 100 == 0 and pence // 100 in ANNUAL_PRICES else None
    _price_cache.update(at=now, gbp=gbp)
    return gbp


def in_send_window(now: datetime) -> bool:
    now = now.astimezone(UK)
    if now.weekday() >= 5:
        return False
    return SEND_FROM <= (now.hour, now.minute) < SEND_UNTIL


def start_of_day(now: datetime) -> datetime:
    return now.astimezone(UK).replace(hour=0, minute=0, second=0, microsecond=0)


def _parse(ts) -> datetime | None:
    if not ts:
        return None
    if isinstance(ts, datetime):
        return ts if ts.tzinfo else ts.replace(tzinfo=UK)
    s = str(ts).strip().replace("Z", "+00:00")
    if " " in s and "T" not in s:
        s = s.replace(" ", "T", 1)
    # Postgres can return fractions of a second with other than 3 or 6 digits
    s = re.sub(r"\.(\d+)", lambda m: "." + (m.group(1) + "000000")[:6], s)
    try:
        d = datetime.fromisoformat(s)
    except ValueError:
        return None
    return d if d.tzinfo else d.replace(tzinfo=UK)


# ── The emails ────────────────────────────────────────────────────────────────

_NUMBERS = {1: "one", 2: "two", 3: "three", 4: "four", 5: "five", 6: "six"}


def _hours(h) -> str:
    try:
        f = float(h)
    except (TypeError, ValueError):
        return ""
    word = _NUMBERS.get(int(f)) if f == int(f) else None
    n = word or f"{f:g}"
    return f"{n} CPD hour" + ("" if f == 1 else "s")


def first_name(full_name: str | None) -> str:
    return outreach.greeting_name((full_name or "").strip().split(" ")[0] if full_name else "")


def _footer_text(unsub: str) -> str:
    return (f"You're getting this because you took a free course with Meridian CPD. "
            f"If you'd rather not hear from us: {unsub}\nPrivacy: meridiancpd.co.uk/privacy.html")


def _compose(subject: str, paragraphs: list[str], unsub: str) -> tuple[str, str, str]:
    """Plain text and HTML from the same paragraphs. A paragraph that is only a URL
    becomes a link in the HTML. The body ends at 'Kind regards,' and the hello@
    signature follows, as in the outreach email."""
    text = "\n\n".join(paragraphs) + "\n\n" + outreach.SIGNATURE_TEXT + "\n\n" + _footer_text(unsub) + "\n"
    ink, small = outreach.INK, outreach.SMALL
    link = f'style="color:{ink};text-decoration:underline"'
    parts = []
    for p in paragraphs:
        if re.fullmatch(r"https?://\S+", p):
            label = p.split("://", 1)[1]
            parts.append(f'<p style="margin:0 0 16px"><a href="{escape(p)}" {link}>{escape(label)}</a></p>')
        else:
            parts.append(f'<p style="margin:0 0 16px">{escape(p)}</p>')
    html = f"""<!DOCTYPE html><html><body style="margin:0;padding:0;background:#ffffff">
<div style="font-family:Helvetica,Arial,sans-serif;font-size:14px;line-height:20px;color:{ink};max-width:600px;margin:0 auto;padding:24px">
{"".join(parts)}
{outreach.SIGNATURE_HTML}
<p style="margin:24px 0 0;font-size:11px;line-height:16px;color:{small}">You're getting this because you took a free course with Meridian CPD. If you'd rather not hear from us: <a href="{escape(unsub)}" style="color:{small}">unsubscribe</a>. Privacy: <a href="{PRIVACY_URL}" style="color:{small}">meridiancpd.co.uk/privacy.html</a></p>
</div></body></html>"""
    return subject, text, html


def render_nudge(name: str, course_title: str, cpd_hours, unsub: str):
    """Points at My CPD, not the completion link: a download needs a signed-in session,
    and the completion page sends anyone who has not downloaded there back to My CPD."""
    hours = _hours(cpd_hours)
    paragraphs = [
        f"Hello {name},",
        f"You took {course_title} with us and it isn't marked as complete yet. "
        + (f"It is {hours}, and it is there whenever you have the time." if hours else "It is there whenever you have the time."),
        "Sign in at the link below with this email address and the course is on your page, ready to download.",
        f"{APP_URL}/my-cpd",
        "When you've read it, press Mark Complete next to the course and your certificate of completion comes by email.",
        "Kind regards,",
    ]
    return _compose("Your free course is still open", paragraphs, unsub)


RISE_HEADS_UP = ("One thing to know before you decide: it is £79 a year until 31 December and £99 a year "
                 "from 1 January 2027. Subscribe before then and you keep £79 for as long as you stay.")


def render_next(name: str, course_title: str, unsub: str, annual: int, rise_notice: bool | None = None):
    """annual is the price checkout charges (annual_price_gbp), 79 or 99. rise_notice adds
    the January heads-up to the £79 version; by default it follows FREE_FOLLOWUP_PRICE_RISE,
    so the email never says something the site does not."""
    if annual not in ANNUAL_PRICES:
        raise ValueError(f"no approved text for an annual price of {annual!r}")
    if rise_notice is None:
        rise_notice = price_rise_notice_on()
    paragraphs = [
        f"Hello {name},",
        f"Thanks for taking {course_title}. If it was useful, there are two ways to carry on.",
        "A Field Work series is three linked courses on one subject for £39.99, written for England and Wales. "
        "There are series on insulation, heating, ventilation and moisture. "
        "Each part has its own certificate of completion as you finish it.",
        f"The annual membership is every course in the library, plus every new one we add, for £{annual} a year.",
    ]
    if annual == 79 and rise_notice:
        paragraphs.append(RISE_HEADS_UP)
    paragraphs += [
        "Both are here:",
        COURSES_URL,
        "Whichever you choose, check your own scheme's CPD rules for what counts towards your hours.",
        "Kind regards,",
    ]
    return _compose("What comes after the free course", paragraphs, unsub)


def render_price(name: str, unsub: str):
    paragraphs = [
        f"Hello {name},",
        "A short note on price. Annual membership at Meridian CPD is £79 a year until 31 December 2026. "
        "From 1 January 2027 it will be £99 a year.",
        "Membership is every course in the library, plus every new one we add, with a certificate of completion "
        "for each course you finish. Join before 1 January and you keep £79 at every renewal for as long as you "
        "stay subscribed.",
        COURSES_URL,
        "If a whole year is more than you need, a Field Work series is three courses on one subject for £39.99, "
        "written for England and Wales.",
        "Check your own scheme's CPD rules for what counts towards your hours.",
        "Kind regards,",
    ]
    return _compose("The annual membership goes up to £99 on 1 January", paragraphs, unsub)


def render_monthly(edition: dict, name: str, unsub: str):
    paragraphs = [p.format(name=name) for p in edition["paragraphs"]]
    return _compose(edition["subject"], paragraphs, unsub)


def render(step: str, member: dict, info: dict, unsub: str, now: datetime):
    name = first_name(member.get("name"))
    if step == "nudge":
        return render_nudge(name, info["course_title"], info.get("cpd_hours"), unsub)
    if step == "next":
        return render_next(name, info["course_title"], unsub, info["annual"])
    if step == "price":
        return render_price(name, unsub)
    if step.startswith("monthly:"):
        edition = next(e for e in MONTHLY_EDITIONS if e["key"] == step.split(":", 1)[1])
        return render_monthly(edition, name, unsub)
    raise ValueError(step)


SAMPLE_COURSE = ("RdSAP 10: What's Changed and Why", 2.0)


def versions(name: str, unsub: str) -> list[tuple[str, str, str, str]]:
    """(label, subject, text, html) for every email, including both annual-price versions
    of 'next' and every monthly edition, with the sample course. For Admin's previews and
    test copies, and for review."""
    title, hours = SAMPLE_COURSE
    out = [
        ("nudge", *render_nudge(name, title, hours, unsub)),
        ("next (annual £79)", *render_next(name, title, unsub, 79)),
        ("next (annual £99)", *render_next(name, title, unsub, 99)),
        ("price", *render_price(name, unsub)),
    ]
    for e in MONTHLY_EDITIONS:
        out.append((f"monthly:{e['key']}", *render_monthly(e, name, unsub)))
    return out


def previews(now: datetime | None = None) -> list[tuple[str, str, str]]:
    """(label, subject, text) for every email, with the sample name Jo."""
    unsub = f"{APP_URL}/unsubscribe?email=…&token=…"
    return [(label, subject, text) for label, subject, text, _html in versions("Jo", unsub)]


# ── Who is due what ───────────────────────────────────────────────────────────

def _is_test_session(p: dict) -> bool:
    return str(p.get("stripe_session_id") or "").startswith("cs_test_")


def _test_emails() -> set:
    return {e.strip().lower() for e in os.environ.get("ADMIN_TEST_EMAILS", "").split(",") if e.strip()}


def free_course_of(member: dict, purchases: list) -> dict | None:
    """The member's free course purchase if they are a free-course taker who has paid
    nothing (the same test as Admin's 'Free course' badge), else None."""
    email = (member.get("email") or "").strip().lower()
    if not outreach._EMAIL_RE.match(email) or email.split("@")[1] in TEST_DOMAINS or email in _test_emails():
        return None
    if member.get("stripe_customer_id") == "cus_test" or member.get("plan") == "subscription":
        return None
    real = [p for p in purchases if not _is_test_session(p)]
    if not real or any(float(p.get("amount_gbp") or 0) > 0 for p in real):
        return None
    free = [p for p in real if float(p.get("amount_gbp") or 0) == 0 and p.get("course_id") not in ("SUBSCRIPTION", "SERIES")]
    if not free:
        return None
    return sorted(free, key=lambda p: str(p.get("purchased_at") or ""))[0]


def _last_outreach_send(db, email: str) -> datetime | None:
    contacts = db.table("outreach_contacts").select("id").eq("email", email).execute().data or []
    latest = None
    for c in contacts:
        rows = db.table("outreach_sends").select("sent_at").eq("contact_id", c["id"]) \
            .order("sent_at", desc=True).limit(1).execute().data or []
        for r in rows:
            d = _parse(r.get("sent_at"))
            if d and (latest is None or d > latest):
                latest = d
    return latest


def _consent_ok(member: dict, step: str) -> bool:
    consent = member.get("marketing_consent")
    if consent is False:
        return False
    if step in MARKETING_STEPS or step.startswith("monthly:"):
        return consent is True or consent_mode() == "not_no"
    return True


def due_step(member: dict, free: dict, completion: dict | None, sends: list, now: datetime,
             annual: int | None = None) -> tuple[str | None, str]:
    """(step, why) for one free-course taker, ignoring suppression and gap (checked after).
    step is None when nothing is due, and why says why. annual is the price checkout
    charges (annual_price_gbp); without it no email that names the annual price is due."""
    done = {s.get("step") for s in sends}
    if len(sends) >= max_emails():
        return None, "lifetime cap reached"
    taken = _parse(free.get("purchased_at")) or now
    completed = _parse((completion or {}).get("completed_at"))
    candidates = []
    priced_out = False   # an email that names the annual price is due, but the price is not known
    if PRICE_NOTICE_FROM <= now < PRICE_NOTICE_UNTIL and "price" not in done and price_rise_notice_on():
        if annual == 79:
            candidates.append("price")
        elif annual is None:
            priced_out = True
    if "next" not in done and "price" not in done:
        if (completed and now >= completed + timedelta(days=NEXT_AFTER_COMPLETION_DAYS)) or (not completed and "nudge" in done):
            if annual in ANNUAL_PRICES:
                candidates.append("next")
            else:
                priced_out = True
    if not completed and "nudge" not in done and now >= taken + timedelta(days=NUDGE_AFTER_DAYS):
        candidates.append("nudge")
    if done & {"next", "price"}:
        for e in MONTHLY_EDITIONS:
            key = f"monthly:{e['key']}"
            if key not in done and e["send_from"] <= now < e["send_until"]:
                candidates.append(key)
    if not candidates:
        return None, "annual price not known" if priced_out else "nothing due yet"
    for step in candidates:
        if _consent_ok(member, step):
            return step, "due"
    return None, "no marketing consent" if member.get("marketing_consent") is not False else "said no to marketing"


def plan(db, now: datetime, courses: dict | None = None) -> dict:
    """Everyone due an email right now, and counts of why the others are not. Reads only."""
    courses = courses or {}
    members = db.table("members").select("id, email, name, plan, marketing_consent, stripe_customer_id").execute().data or []
    purchases = db.table("purchases").select("member_id, course_id, amount_gbp, stripe_session_id, purchased_at").execute().data or []
    by_member: dict = {}
    for p in purchases:
        by_member.setdefault(p.get("member_id"), []).append(p)
    sends_all = db.table(TABLE).select("member_id, step, status, sent_at").execute().data or []
    sends_by: dict = {}
    for s in sends_all:
        sends_by.setdefault(s.get("member_id"), []).append(s)

    due, skipped, takers = [], {}, 0
    def skip(why):
        skipped[why] = skipped.get(why, 0) + 1
    gap = timedelta(days=min_gap_days())
    annual = None
    for m in members:
        free = free_course_of(m, by_member.get(m["id"], []))
        if not free:
            continue
        takers += 1
        cid = free.get("course_id")
        comps = db.table("completions").select("course_id, completed_at, completion_token") \
            .eq("member_id", m["id"]).eq("course_id", cid).execute().data or []
        completion = next((c for c in comps if c.get("completed_at")), None)
        sends = sends_by.get(m["id"], [])
        if annual is None:
            annual = annual_price_gbp(now)
        step, why = due_step(m, free, completion, sends, now, annual)
        if not step:
            skip(why)
            continue
        email = m["email"].strip()
        if outreach.is_suppressed(db, email):
            skip("on suppression list")
            continue
        last = max([d for d in (_parse(s.get("sent_at")) for s in sends) if d] + [d for d in [_last_outreach_send(db, email)] if d],
                   default=None)
        if last and now - last < gap:
            skip("too soon after the last email")
            continue
        course = courses.get(cid) or {}
        due.append({
            "member": m, "step": step, "course_id": cid,
            "course_title": str(course.get("title") or cid),
            "cpd_hours": course.get("cpd_hours"),
            "annual": annual,
        })
    order = {"price": 0, "nudge": 1, "next": 2}
    due.sort(key=lambda d: (order.get(d["step"], 3), str(d["member"].get("id"))))
    return {"takers": takers, "due": due, "skipped": skipped, "annual": annual}


# ── Sending ───────────────────────────────────────────────────────────────────

async def send_one(email: str, subject: str, text: str, html: str, unsub: str) -> str:
    api_key = os.environ["RESEND_API_KEY"]
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
        "tags": [{"name": "campaign", "value": TAG}],
    }
    async with httpx.AsyncClient() as client:
        r = await client.post(f"{RESEND_API}/emails", headers={"Authorization": f"Bearer {api_key}"},
                              json=payload, timeout=30)
        r.raise_for_status()
        return (r.json() or {}).get("id", "")


def sent_today(db, now: datetime) -> int:
    res = db.table(TABLE).select("id", count="exact").gte("sent_at", start_of_day(now).isoformat()).execute()
    return res.count or 0


_run_lock = asyncio.Lock()


async def run(db, now: datetime | None = None, courses: dict | None = None,
              max_send: int | None = None, dry_run: bool | None = None) -> dict:
    """One pass. In dry-run it returns what it would send and touches nothing."""
    now = now or datetime.now(UK)
    dry = (mode() != "on") if dry_run is None else dry_run
    result = {"mode": "dry_run" if dry else "on", "sent": 0, "failed": 0, "would_send": [], "note": ""}
    if not dry and mode() != "on":
        result["note"] = "switched off"
        return result
    async with _run_lock:
        p = plan(db, now, courses)
        result["takers"], result["skipped"] = p["takers"], p["skipped"]
        room = daily_limit() - (0 if dry else sent_today(db, now))
        if max_send is not None:
            room = min(room, max_send)
        if room <= 0:
            result["note"] = "daily limit reached"
        for item in p["due"][:max(room, 0)]:
            m = item["member"]
            if dry:
                result["would_send"].append({"member_id": m["id"], "step": item["step"]})
                continue
            email = m["email"].strip()
            unsub = outreach.unsubscribe_url(email)
            subject, text, html = render(item["step"], m, item, unsub, now)
            row = {"member_id": m["id"], "email": email, "step": item["step"], "sent_at": now.isoformat()}
            try:
                msg_id = await send_one(email, subject, text, html, unsub)
            except Exception as e:
                note = f"{type(e).__name__}: {e}" if str(e) else type(e).__name__
                db.table(TABLE).insert({**row, "status": "failed", "note": note[:200]}).execute()
                result["failed"] += 1
                if result["failed"] >= 3:
                    result["note"] = "stopped: three failures"
                    break
                continue
            db.table(TABLE).insert({**row, "status": "sent", "resend_id": msg_id}).execute()
            result["sent"] += 1
            await asyncio.sleep(PACE_SECONDS)
    return result


async def poll_delivery(db, now: datetime | None = None) -> tuple[int, int]:
    """Bounced and complained addresses go on the suppression list, which stops the sequence."""
    now = now or datetime.now(UK)
    since = (now - timedelta(days=POLL_DAYS)).isoformat()
    rows = db.table(TABLE).select("id, email, resend_id").eq("status", "sent").gte("sent_at", since).execute().data or []
    api_key = os.environ.get("RESEND_API_KEY", "")
    bounced = complained = 0
    async with httpx.AsyncClient() as client:
        for row in rows:
            if not row.get("resend_id"):
                continue
            try:
                r = await client.get(f"{RESEND_API}/emails/{row['resend_id']}",
                                     headers={"Authorization": f"Bearer {api_key}"}, timeout=20)
                if r.status_code != 200:
                    continue
                event = (r.json() or {}).get("last_event") or ""
            except Exception:
                continue
            if event in ("bounced", "complained"):
                outreach.suppress(db, row["email"], event)
                db.table(TABLE).update({"status": event}).eq("id", row["id"]).execute()
                bounced += event == "bounced"
                complained += event == "complained"
            elif event == "delivered":
                db.table(TABLE).update({"status": "delivered"}).eq("id", row["id"]).execute()
            await asyncio.sleep(PACE_SECONDS)
    return bounced, complained


async def scheduler_loop(get_db, get_courses=lambda: {}, get_now=lambda: datetime.now(UK),
                         tick_seconds=(240, 600)) -> None:
    """Runs inside the web process when FREE_FOLLOWUP is dry_run or on. Dry-run prints the
    day's plan once; on sends one or two at a time through the weekday window."""
    last_day = None
    while True:
        try:
            now = get_now()
            m = mode()
            if m != "off" and in_send_window(now):
                db = get_db()
                first_of_day = last_day != now.date()
                if m == "dry_run":
                    if first_of_day:
                        res = await run(db, now, get_courses(), dry_run=True)
                        steps: dict = {}
                        for w in res["would_send"]:
                            steps[w["step"]] = steps.get(w["step"], 0) + 1
                        print(f"Free-course follow-up (dry run): takers={res.get('takers')} would_send={steps} skipped={res.get('skipped')}")
                else:
                    if first_of_day:
                        await poll_delivery(db, now)
                    res = await run(db, now, get_courses(), max_send=MAX_PER_TICK, dry_run=False)
                    if res["sent"] or res["failed"]:
                        print(f"Free-course follow-up: sent={res['sent']} failed={res['failed']} {res['note']}")
                last_day = now.date()
        except Exception as e:
            print(f"Free-course follow-up error: {e}")
        await asyncio.sleep(random.uniform(*tick_seconds))


# ── Figures for Admin and the Friday review ───────────────────────────────────

def summary(db) -> dict:
    """Sends by step and status, and how many people who got a follow-up paid for
    something afterwards (and how much). The SQL view free_course_followup_stats gives
    the same by week for the Friday review."""
    sends = db.table(TABLE).select("member_id, step, status, sent_at").execute().data or []
    steps: dict = {}
    first_send: dict = {}
    for s in sends:
        st = steps.setdefault(s["step"], {"sent": 0, "delivered": 0, "bounced": 0, "complained": 0, "failed": 0})
        status = s.get("status") or "sent"
        if status != "failed":
            st["sent"] += 1
        if status in st and status != "sent":
            st[status] += 1
        d = _parse(s.get("sent_at"))
        if status != "failed" and d and (s["member_id"] not in first_send or d < first_send[s["member_id"]]):
            first_send[s["member_id"]] = d
    buyers, revenue = 0, 0.0
    if first_send:
        purchases = db.table("purchases").select("member_id, amount_gbp, stripe_session_id, purchased_at").execute().data or []
        paid_by: dict = {}
        for p in purchases:
            if p.get("member_id") in first_send and not _is_test_session(p) and float(p.get("amount_gbp") or 0) > 0:
                d = _parse(p.get("purchased_at"))
                if d and d > first_send[p["member_id"]]:
                    paid_by[p["member_id"]] = paid_by.get(p["member_id"], 0) + float(p["amount_gbp"])
        buyers, revenue = len(paid_by), round(sum(paid_by.values()), 2)
    return {"steps": steps, "people": len(first_send), "buyers_after": buyers, "revenue_after": revenue}
