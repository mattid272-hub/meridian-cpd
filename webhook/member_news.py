"""Member news: the thank-you and what's-new emails to paying members.

Matt approved the customer care plan and the first email, both versions, on 13 November
2026 (HQ board row mer-customer-care; the text passed the independent check on
12 November). The plan:
  - who: paying members only. Version A goes to active annual subscribers. Version B goes
    to people who bought a course or a Field Work series and have no active subscription.
    Never to free-course-only members (they have their own follow-up), lapsed subscribers
    (a win-back is a separate email), test accounts, anyone who said no to marketing
    (members.marketing_consent = false) or anyone on the suppression list.
  - how often: each edition goes to a member once, ever (member_news_sends is unique per
    member and edition), and never within MEMBER_NEWS_MIN_GAP_DAYS (30, and never less) of
    the last member-news email, free-course follow-up or outreach email to that address.
  - what: each edition is its own entry in EDITIONS, with the exact approved text. A
    changed word needs a fresh check and Matt's yes before it goes in.

The switch is the MEMBER_NEWS environment variable and it defaults to off:
  off      nothing runs (the default)
  dry_run  works out who would get which version, prints the counts once a day and shows
           them in Admin -> Member news; sends nothing and writes nothing
  on       sends, at most MEMBER_NEWS_DAILY_LIMIT a day (default 10), one or two at a
           time, weekdays 09:00 to 17:00 UK

Also on every send:
  - the app's working unsubscribe link in the footer and the List-Unsubscribe and
    one-click headers (RFC 8058); unsubscribing puts the address on outreach_suppressed
  - the prices in the text are the prices checkout charges: the annual price read from
    STRIPE_PRICE_SUBSCRIPTION must be £79, and for version B the series price read from
    STRIPE_PRICE_SERIES must be £39.99 (reads only, never a change); otherwise that version
    does not go
  - an address can be held for an edition from Admin (for one the HQ send guard blocked);
    a held member is never sent that edition
  - bounces and complaints reported by Resend suppress the address before the next send
"""
import asyncio
import os
import random
import re
from datetime import datetime, timedelta
from html import escape

import httpx

import followup
import outreach

UK = outreach.UK
RESEND_API = outreach.RESEND_API
FROM_ADDRESS = outreach.FROM_ADDRESS
FROM_NAME = outreach.FROM_NAME
TAG = "member-news"
TABLE = "member_news_sends"
PRIVACY_URL = "https://meridiancpd.co.uk/privacy.html"

MODES = ("off", "dry_run", "on")
DEFAULT_LIMIT = 10
HARD_CEILING = 50
MIN_GAP_FLOOR = 30          # never more than one email in 30 days (Matt's plan)
SEND_FROM = (9, 0)
SEND_UNTIL = (17, 0)
MAX_PER_TICK = 2
PACE_SECONDS = 0.6
POLL_DAYS = 3
PRICE_CACHE_HOURS = 6

SERIES_PENCE = 3999         # £39.99, the price version B names
SERIES_ORDER = ("FW-INSULATION", "FW-HEATING", "FW-VENTILATION", "FW-MOISTURE")


# ── Settings ──────────────────────────────────────────────────────────────────

def mode() -> str:
    m = os.environ.get("MEMBER_NEWS", "off").strip().lower()
    return m if m in MODES else "off"


def _int_env(key: str, default: int, low: int, high: int) -> int:
    try:
        n = int(os.environ.get(key, default))
    except ValueError:
        n = default
    return max(low, min(n, high))


def daily_limit() -> int:
    return _int_env("MEMBER_NEWS_DAILY_LIMIT", DEFAULT_LIMIT, 0, HARD_CEILING)


def min_gap_days() -> int:
    return _int_env("MEMBER_NEWS_MIN_GAP_DAYS", MIN_GAP_FLOOR, MIN_GAP_FLOOR, 365)


def in_send_window(now: datetime) -> bool:
    now = now.astimezone(UK)
    if now.weekday() >= 5:
        return False
    return SEND_FROM <= (now.hour, now.minute) < SEND_UNTIL


def start_of_day(now: datetime) -> datetime:
    return now.astimezone(UK).replace(hour=0, minute=0, second=0, microsecond=0)


_parse = followup._parse


def annual_price_gbp(now: datetime | None = None) -> int | None:
    """The annual price checkout charges (£79 or £99), read from Stripe; None if unknown."""
    return followup.annual_price_gbp(now)


def _fetch_series_pence() -> int | None:
    price_id = os.environ.get("STRIPE_PRICE_SERIES", "").strip()
    if not price_id:
        return None
    import stripe   # main sets stripe.api_key at start-up
    price = stripe.Price.retrieve(price_id)
    amount = price.get("unit_amount") if hasattr(price, "get") else getattr(price, "unit_amount", None)
    return int(amount) if amount is not None else None


_series_cache: dict = {"at": None, "pence": None}


def series_price_pence(now: datetime | None = None) -> int | None:
    """Unit amount of the series price checkout charges. Reads only; cached."""
    now = now or datetime.now(UK)
    at = _series_cache["at"]
    if at is not None and timedelta(0) <= now - at < timedelta(hours=PRICE_CACHE_HOURS):
        return _series_cache["pence"]
    try:
        pence = _fetch_series_pence()
    except Exception as e:
        print(f"Member news: could not read the series price from Stripe ({type(e).__name__})")
        pence = None
    _series_cache.update(at=now, pence=pence)
    return pence


# ── The emails (approved text, word for word) ────────────────────────────────

first_name = followup.first_name


def _greeting(name: str) -> str:
    return f"Hello {name}," if name else "Hello,"


FOOTER_LEAD = "You're getting this because you are a Meridian CPD member. If you'd rather not hear from us:"


def _compose(subject: str, paragraphs: list[str], unsub: str) -> tuple[str, str, str]:
    """Plain text and HTML from the same paragraphs; a URL becomes a link in the HTML. The
    body ends at 'Kind regards,' and the hello@ signature follows, then the footer."""
    text = ("\n\n".join(paragraphs) + "\n\n" + outreach.SIGNATURE_TEXT + "\n\n"
            + f"{FOOTER_LEAD} {unsub}\nPrivacy: meridiancpd.co.uk/privacy.html\n")
    ink, small = outreach.INK, outreach.SMALL
    link = f'style="color:{ink};text-decoration:underline"'
    parts = []
    for p in paragraphs:
        body = re.sub(r"https?://[^\s<]+",
                      lambda m: f'<a href="{m.group(0)}" {link}>{m.group(0).split("://", 1)[1]}</a>',
                      escape(p))
        parts.append(f'<p style="margin:0 0 16px">{body}</p>')
    html = f"""<!DOCTYPE html><html><body style="margin:0;padding:0;background:#ffffff">
<div style="font-family:Helvetica,Arial,sans-serif;font-size:14px;line-height:20px;color:{ink};max-width:600px;margin:0 auto;padding:24px">
{"".join(parts)}
{outreach.SIGNATURE_HTML}
<p style="margin:24px 0 0;font-size:11px;line-height:16px;color:{small}">{escape(FOOTER_LEAD)} <a href="{escape(unsub)}" style="color:{small}">unsubscribe</a>. Privacy: <a href="{PRIVACY_URL}" style="color:{small}">meridiancpd.co.uk/privacy.html</a></p>
</div></body></html>"""
    return subject, text, html


MY_CPD = "https://app.meridiancpd.co.uk/my-cpd"
ANNUAL_79 = "https://buy.stripe.com/fZufZgbse3BpcXE7TY73G01"
SERIES_LINE = {
    "FW-INSULATION": "Insulation: https://meridiancpd.co.uk/courses.html#fw-insulation",
    "FW-HEATING": "Heating: https://meridiancpd.co.uk/courses.html#fw-heating",
    "FW-VENTILATION": "Ventilation: https://meridiancpd.co.uk/courses.html#fw-ventilation",
    "FW-MOISTURE": "Moisture: https://meridiancpd.co.uk/courses.html#fw-moisture",
}


def render_thank_you_subscriber(name: str, unsub: str):
    """Edition 2026-11-thank-you, version A (HQ audit 2026-11-12-0849, A PASS round 1).
    The optional referral paragraph is not here: it goes in only once the refer-a-colleague
    scheme (PR #67) is merged and REFERRAL_COUPON_ID is set, with a fresh check."""
    paragraphs = [
        _greeting(name),
        f"Thank you for being a Meridian member. Your library is here: {MY_CPD}",
        "We have rebuilt it so things are quicker to find. Courses sit in rows by topic, with Continue where you "
        "left off first and a search box at the top. Mark a course as a favourite or save it to read later and it "
        "gets its own row.",
        "The four Field Work series are in your library under Your series: Insulation, Heating, Ventilation and "
        "Moisture. Each is three linked courses on one subject, written for England and Wales, with a certificate "
        "of completion for each part. They are included in your membership.",
        "My certificates holds every certificate you have earned with us. Download CPD record (PDF) gives you a "
        "year's record in one file.",
        "The annual price goes up to £99 on 1 January 2027. Yours stays at £79 for as long as you stay.",
        "If anything is not where you expect it, reply to this email.",
        f"Your library: {MY_CPD}",
        "Kind regards,",
    ]
    return _compose("Thank you, and what's new in your library", paragraphs, unsub)


def render_thank_you_buyer(name: str, purchase_title: str, held_series: set, unsub: str):
    """Edition 2026-11-thank-you, version B (HQ audit 2026-11-12-0849, B PASS round 2).
    As the approved text says, the line for any series the member already holds is left
    out; a member holding all four also loses the sentence that introduces them (a
    condition of the pass)."""
    lines = [SERIES_LINE[s] for s in SERIES_ORDER if s not in held_series]
    paragraphs = [
        _greeting(name),
        f"Thank you for buying {purchase_title}. The annual membership covers all four Field Work series and every "
        f"other course in the library, for £79 a year: {ANNUAL_79}",
        "It goes up to £99 a year on 1 January 2027. Subscribe before then and you keep £79 for as long as you stay.",
    ]
    if lines:
        paragraphs.append("A Field Work series is three linked courses on one subject for £39.99, written for "
                          "England and Wales, with a certificate of completion for each part.")
        paragraphs += lines
    paragraphs += [
        "We have also rebuilt My CPD. Your courses sit in rows by topic with a search box at the top, and My "
        f"certificates holds every certificate you have earned, with a year's CPD record as one PDF: {MY_CPD}",
        "Check your own scheme's CPD rules for what counts towards your hours.",
        f"Annual membership, £79 a year: {ANNUAL_79}",
        "Kind regards,",
    ]
    return _compose("Thank you, and what's new at Meridian", paragraphs, unsub)


# Each edition: its key, the HQ send-guard purpose it is recorded under, when it may go,
# and its two versions. The 2026-11 edition names £79 and £99 from 1 January 2027, so it
# stops at the end of 2026.
EDITIONS = [
    {
        "key": "2026-11-thank-you",
        "hq_purpose": "announcement",
        "send_from": datetime(2026, 11, 16, tzinfo=UK),
        "send_until": datetime(2027, 1, 1, tzinfo=UK),
        "annual": 79,
        "subscriber": render_thank_you_subscriber,
        "buyer": render_thank_you_buyer,
    },
]


def current_edition(now: datetime) -> dict | None:
    open_now = [e for e in EDITIONS if e["send_from"] <= now < e["send_until"]]
    return open_now[-1] if open_now else None


def render(edition: dict, item: dict, unsub: str):
    name = first_name(item["member"].get("name"))
    if item["version"] == "A":
        return edition["subscriber"](name, unsub)
    return edition["buyer"](name, item["purchase_title"], set(item.get("held_series") or ()), unsub)


def previews() -> list[tuple[str, str, str, str]]:
    """(label, subject, text, html) for each version of each edition, with sample details,
    for Admin's previews and test copies. Version B is shown as for a buyer of one course,
    so every series line is in."""
    unsub = "https://app.meridiancpd.co.uk/unsubscribe?email=…&token=…"
    out = []
    for e in EDITIONS:
        out.append((f"{e['key']} A (subscribers)", *e["subscriber"]("Jo", unsub)))
        out.append((f"{e['key']} B (buyers)", *e["buyer"]("Jo", "Field Work: Insulation", {"FW-INSULATION"}, unsub)))
    return out


# ── Who gets what ─────────────────────────────────────────────────────────────

def _is_test_session(p: dict) -> bool:
    return str(p.get("stripe_session_id") or "").startswith("cs_test_")


def _subscription_active(member: dict, now: datetime) -> bool:
    """The same test as main.subscription_active: plan subscription and the expiry, if
    recorded, still ahead."""
    if member.get("plan") != "subscription":
        return False
    exp = _parse(member.get("subscription_expires_at"))
    return exp is None or exp > now


def _held_series(purchases: list, series: dict) -> set:
    held = set()
    ids = {p.get("course_id") for p in purchases}
    for sid, s in series.items():
        if any(p.get("series_id") == sid for p in purchases) or all(c in ids for c in s.get("courses", [])):
            held.add(sid)
    return held


def _purchase_title(p: dict, courses: dict, series: dict) -> str | None:
    sid = p.get("series_id")
    if sid and sid in series:
        return series[sid]["title"]
    cid = p.get("course_id")
    if cid in ("SERIES", "SUBSCRIPTION", None):
        return None
    title = (courses.get(cid) or {}).get("title")
    return str(title) if title else None


def classify(member: dict, purchases: list, now: datetime, courses: dict, series: dict) -> tuple[str | None, str, dict]:
    """(version, why, extra) for one member: version 'A' (subscriber), 'B' (buyer) or None
    with the reason. Ignores suppression, the gap and prices (checked after)."""
    email = (member.get("email") or "").strip().lower()
    if not outreach._EMAIL_RE.match(email) or email.split("@")[1] in outreach.TEST_DOMAINS \
            or email in followup._test_emails() or member.get("stripe_customer_id") == "cus_test":
        return None, "test account", {}
    real = [p for p in purchases if not _is_test_session(p)]
    if purchases and not real:
        return None, "test account", {}
    if member.get("marketing_consent") is False:
        return None, "said no to marketing", {}
    if _subscription_active(member, now):
        if not member.get("stripe_customer_id"):
            return None, "subscriber with no Stripe customer (not a paying member)", {}
        return "A", "due", {}
    if member.get("plan") == "subscription" or any(p.get("course_id") == "SUBSCRIPTION" for p in real):
        return None, "lapsed subscriber (win-back, not this email)", {}
    paid = [p for p in real if float(p.get("amount_gbp") or 0) > 0 and p.get("course_id") != "SUBSCRIPTION"]
    if not paid:
        return None, "free courses only (has its own follow-up)", {}
    latest = sorted(paid, key=lambda p: str(p.get("purchased_at") or ""))[-1]
    title = _purchase_title(latest, courses, series)
    if not title:
        return None, "latest purchase has no title (check in Admin)", {}
    return "B", "due", {"purchase_title": title, "held_series": sorted(_held_series(real, series))}


def _last_other_send(db, member_id, email: str) -> datetime | None:
    """The latest email to this person from the free-course follow-up or the outreach sender."""
    latest = followup._last_outreach_send(db, email)
    try:
        rows = db.table(followup.TABLE).select("sent_at").eq("member_id", member_id).execute().data or []
    except Exception:
        rows = []
    for r in rows:
        d = _parse(r.get("sent_at"))
        if d and (latest is None or d > latest):
            latest = d
    return latest


def plan(db, now: datetime, courses: dict | None = None, series: dict | None = None) -> dict:
    """Everyone due the current edition right now, and counts of why the others are not.
    Reads only."""
    courses, series = courses or {}, series or {}
    edition = current_edition(now)
    out = {"edition": edition["key"] if edition else None, "due": [], "skipped": {}, "paying": 0,
           "annual": None, "series_pence": None}
    if not edition:
        return out

    def skip(why):
        out["skipped"][why] = out["skipped"].get(why, 0) + 1

    members = db.table("members").select(
        "id, email, name, plan, marketing_consent, stripe_customer_id, subscription_expires_at").execute().data or []
    purchases = db.table("purchases").select(
        "member_id, course_id, series_id, amount_gbp, stripe_session_id, purchased_at").execute().data or []
    by_member: dict = {}
    for p in purchases:
        by_member.setdefault(p.get("member_id"), []).append(p)
    sends = db.table(TABLE).select("member_id, edition, status, sent_at").execute().data or []
    sends_by: dict = {}
    for s in sends:
        sends_by.setdefault(s.get("member_id"), []).append(s)

    gap = timedelta(days=min_gap_days())
    prices_read = False
    for m in members:
        version, why, extra = classify(m, by_member.get(m["id"], []), now, courses, series)
        if not version:
            if why not in ("test account", "free courses only (has its own follow-up)"):
                skip(why)
            continue
        out["paying"] += 1
        mine = sends_by.get(m["id"], [])
        if any(s.get("edition") == edition["key"] for s in mine):
            skip("already has this edition (or held)")
            continue
        email = m["email"].strip()
        if outreach.is_suppressed(db, email):
            skip("on suppression list")
            continue
        last = max([d for d in (_parse(s.get("sent_at")) for s in mine if s.get("status") != "held") if d]
                   + [d for d in [_last_other_send(db, m["id"], email)] if d], default=None)
        if last and now - last < gap:
            skip("too soon after the last email")
            continue
        if not prices_read:
            out["annual"], out["series_pence"] = annual_price_gbp(now), series_price_pence(now)
            prices_read = True
        if out["annual"] != edition["annual"]:
            skip(f"annual price at checkout is not £{edition['annual']}")
            continue
        if version == "B" and len(extra.get("held_series") or []) < len(SERIES_ORDER) and out["series_pence"] != SERIES_PENCE:
            skip("series price at checkout is not £39.99")
            continue
        out["due"].append({"member": m, "version": version, "edition": edition["key"], **extra})
    out["due"].sort(key=lambda d: (d["version"], str(d["member"].get("id"))))
    return out


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
    rows = db.table(TABLE).select("status, sent_at").gte("sent_at", start_of_day(now).isoformat()).execute().data or []
    return sum(1 for r in rows if r.get("status") != "held")


def hold(db, emails: list[str], now: datetime | None = None, reason: str = "held from Admin") -> tuple[int, int]:
    """Holds the current edition for these addresses (for example ones the HQ send guard
    blocked): a 'held' row means the member never gets this edition. (held, not found)."""
    now = now or datetime.now(UK)
    edition = current_edition(now)
    if not edition:
        return 0, len(emails)
    held = missing = 0
    for raw in emails:
        email = raw.strip().lower()
        if not email:
            continue
        found = db.table("members").select("id, email").eq("email", email).limit(1).execute().data or []
        if not found:
            missing += 1
            continue
        mid = found[0]["id"]
        have = db.table(TABLE).select("id").eq("member_id", mid).eq("edition", edition["key"]).execute().data or []
        if not have:
            db.table(TABLE).insert({"member_id": mid, "email": found[0]["email"], "edition": edition["key"],
                                    "version": "", "status": "held", "note": reason[:200],
                                    "sent_at": now.isoformat()}).execute()
        held += 1
    return held, missing


_run_lock = asyncio.Lock()


async def run(db, now: datetime | None = None, courses: dict | None = None, series: dict | None = None,
              max_send: int | None = None, dry_run: bool | None = None) -> dict:
    """One pass. In dry-run it returns what it would send and touches nothing."""
    now = now or datetime.now(UK)
    dry = (mode() != "on") if dry_run is None else dry_run
    result = {"mode": "dry_run" if dry else "on", "sent": 0, "failed": 0, "would_send": [], "note": ""}
    if not dry and mode() != "on":
        result["note"] = "switched off"
        return result
    async with _run_lock:
        p = plan(db, now, courses, series)
        result.update(edition=p["edition"], paying=p["paying"], skipped=p["skipped"])
        if not p["edition"]:
            result["note"] = "no edition open"
            return result
        edition = current_edition(now)
        room = daily_limit() - (0 if dry else sent_today(db, now))
        if max_send is not None:
            room = min(room, max_send)
        if room <= 0:
            result["note"] = "daily limit reached"
        for item in p["due"][:max(room, 0)]:
            m = item["member"]
            if dry:
                result["would_send"].append({"member_id": m["id"], "version": item["version"]})
                continue
            email = m["email"].strip()
            unsub = outreach.unsubscribe_url(email)
            subject, text, html = render(edition, item, unsub)
            row = {"member_id": m["id"], "email": email, "edition": item["edition"], "version": item["version"],
                   "sent_at": now.isoformat()}
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
    """Bounced and complained addresses go on the suppression list."""
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


async def scheduler_loop(get_db, get_courses=lambda: {}, get_series=lambda: {},
                         get_now=lambda: datetime.now(UK), tick_seconds=(240, 600)) -> None:
    """Runs inside the web process when MEMBER_NEWS is dry_run or on."""
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
                        res = await run(db, now, get_courses(), get_series(), dry_run=True)
                        versions: dict = {}
                        for w in res["would_send"]:
                            versions[w["version"]] = versions.get(w["version"], 0) + 1
                        print(f"Member news (dry run): edition={res.get('edition')} paying={res.get('paying')} "
                              f"would_send={versions} skipped={res.get('skipped')}")
                else:
                    if first_of_day:
                        await poll_delivery(db, now)
                    res = await run(db, now, get_courses(), get_series(), max_send=MAX_PER_TICK, dry_run=False)
                    if res["sent"] or res["failed"]:
                        print(f"Member news: sent={res['sent']} failed={res['failed']} {res['note']}")
                last_day = now.date()
        except Exception as e:
            print(f"Member news error: {e}")
        await asyncio.sleep(random.uniform(*tick_seconds))


def summary(db) -> dict:
    """Sends by edition, version and status."""
    rows = db.table(TABLE).select("edition, version, status").execute().data or []
    out: dict = {}
    for r in rows:
        key = f"{r.get('edition')} {r.get('version') or '-'}"
        st = out.setdefault(key, {"sent": 0, "delivered": 0, "bounced": 0, "complained": 0, "failed": 0, "held": 0})
        status = r.get("status") or "sent"
        if status not in ("failed", "held"):
            st["sent"] += 1
        if status in st and status != "sent":
            st[status] += 1
    return out
