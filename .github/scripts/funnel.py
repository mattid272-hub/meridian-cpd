"""The daily funnel report: the numbers and the red lines, with no network or database.

health_report.py fetches the rows (Supabase, Stripe, the app's /health) and hands them
here; everything that decides what the email says is in this file, so it can be tested
with plain lists (webhook/tests/test_funnel_report.py).

Days are UK days (Europe/London). "Yesterday" is the whole of yesterday; "7 days" is the
seven whole days ending with yesterday. Test orders (cs_test_ sessions) and test members
(stripe_customer_id cus_test) never count.
"""
from __future__ import annotations

from datetime import datetime, timedelta, timezone
from html import escape
from zoneinfo import ZoneInfo

UK = ZoneInfo("Europe/London")
RECORD_GRACE = timedelta(minutes=30)   # a paid checkout younger than this may still be recording
MAX_LISTED = 3                         # session ids listed in a red line before "and N more"


# ── Time ──────────────────────────────────────────────────────────────────────

def windows(now: datetime) -> dict:
    """UTC bounds of yesterday, the two days before today and the last seven days."""
    today = now.astimezone(UK).replace(hour=0, minute=0, second=0, microsecond=0)

    def day(n):  # midnight UK n days before today, as UTC (handles the clock change)
        d = (today - timedelta(days=n)).replace(tzinfo=None)
        return d.replace(tzinfo=UK).astimezone(timezone.utc)

    end = day(0)
    return {"yday": (day(1), end), "two": (day(2), end), "week": (day(7), end),
            "yday_label": (today - timedelta(days=1)).strftime("%a %d %b"),
            "today_label": today.strftime("%a %d %b %Y")}


def ts(value) -> datetime | None:
    """A Supabase timestamp string, a Stripe unix time or a datetime, as aware UTC."""
    if value in (None, ""):
        return None
    if isinstance(value, (int, float)):
        return datetime.fromtimestamp(value, timezone.utc)
    if isinstance(value, datetime):
        return value if value.tzinfo else value.replace(tzinfo=timezone.utc)
    s = str(value).replace("Z", "+00:00")
    if "." in s:  # Supabase can send 1 to 6 fractional digits; fromisoformat wants 3 or 6
        head, _, tail = s.partition(".")
        digits = "".join(ch for ch in tail if ch.isdigit())
        s = head + "." + (digits + "000000")[:6] + tail[len(digits):]
    try:
        d = datetime.fromisoformat(s)
    except ValueError:
        return None
    return d if d.tzinfo else d.replace(tzinfo=timezone.utc)


def inside(value, bounds) -> bool:
    t = ts(value)
    return t is not None and bounds[0] <= t < bounds[1]


# ── Orders ────────────────────────────────────────────────────────────────────

def is_test(p: dict) -> bool:
    return str(p.get("stripe_session_id") or "").startswith("cs_test_")


def product(rows: list) -> str:
    """free | single | series | annual, for the purchase rows of one checkout."""
    total = sum(float(r.get("amount_gbp") or 0) for r in rows)
    if any(r.get("course_id") == "SUBSCRIPTION" for r in rows):
        return "annual"
    if any(r.get("series_id") or r.get("course_id") == "SERIES" for r in rows):
        return "series"
    return "free" if total == 0 else "single"


def orders(purchases: list) -> list:
    """One entry per live checkout: {session, product, gbp, at}. A series is three
    purchase rows with one session id; it is one order."""
    by_session: dict = {}
    for p in purchases:
        sid = p.get("stripe_session_id")
        if not sid or is_test(p):
            continue
        by_session.setdefault(sid, []).append(p)
    out = []
    for sid, rows in by_session.items():
        times = [t for t in (ts(r.get("purchased_at")) for r in rows) if t]
        out.append({"session": sid, "product": product(rows),
                    "gbp": round(sum(float(r.get("amount_gbp") or 0) for r in rows), 2),
                    "at": min(times) if times else None})
    return out


# ── The numbers ───────────────────────────────────────────────────────────────

def count_in(rows, field, bounds, where=None):
    """How many rows have `field` inside `bounds`; None when the rows could not be read."""
    if rows is None:
        return None
    return sum(1 for r in rows if inside(r.get(field), bounds) and (where is None or where(r)))


def figures(data: dict, bounds) -> dict:
    """Every number in one column of the table, for one window."""
    f: dict = {}
    sessions = data.get("stripe_sessions")
    if sessions is None:
        f["started"] = f["completed"] = f["not_finished"] = None
    else:
        mine = [s for s in sessions if inside(s.get("created"), bounds)]
        f["started"] = len(mine)
        f["completed"] = sum(1 for s in mine if s.get("status") == "complete")
        f["not_finished"] = f["started"] - f["completed"]

    if data.get("purchases") is None:  # could not be read: n/a, never a false 0
        for kind in ("free", "single", "series", "annual"):
            f[kind] = f[kind + "_gbp"] = None
        f["paid_gbp"] = None
    else:
        placed = [o for o in orders(data["purchases"]) if o["at"] and bounds[0] <= o["at"] < bounds[1]]
        for kind in ("free", "single", "series", "annual"):
            mine = [o for o in placed if o["product"] == kind]
            f[kind] = len(mine)
            f[kind + "_gbp"] = round(sum(o["gbp"] for o in mine), 2)
        f["paid_gbp"] = round(f["single_gbp"] + f["series_gbp"] + f["annual_gbp"], 2)

    real_member = lambda m: m.get("stripe_customer_id") != "cus_test"
    f["members"] = count_in(data.get("members"), "joined_at", bounds, real_member)
    f["signins"] = count_in(data.get("signins"), "signed_in_at", bounds)
    f["opened"] = count_in(data.get("opened"), "downloaded_at", bounds)
    f["completions"] = count_in(data.get("completed"), "completed_at", bounds)
    f["certificates"] = count_in(data.get("certificates"), "issued_at", bounds)
    f["followups"] = count_in(data.get("followups"), "sent_at", bounds,
                              lambda r: r.get("status") != "failed")
    f["outreach"] = count_in(data.get("outreach_sends"), "sent_at", bounds)
    f["unsubscribes"] = count_in(data.get("suppressed"), "suppressed_at", bounds,
                                 lambda r: r.get("reason") == "unsubscribed")
    return f


def pool(members: list | None, purchases: list | None) -> dict | None:
    """Who we can still sell to: members whose only order is a free course, and how many
    non-subscribers said yes to emails. None when either table could not be read."""
    if members is None or purchases is None:
        return None
    by_member: dict = {}
    for p in purchases or []:
        if not is_test(p):
            by_member.setdefault(p.get("member_id"), []).append(p)
    real = [m for m in members if m.get("stripe_customer_id") != "cus_test"]
    subs = [m for m in real if m.get("plan") == "subscription"]
    others = [m for m in real if m.get("plan") != "subscription"]
    free_only = [m for m in others
                 if by_member.get(m.get("id"))
                 and all(float(p.get("amount_gbp") or 0) == 0 for p in by_member[m.get("id")])]
    return {"members": len(real), "subscribers": len(subs), "free_only": len(free_only),
            "non_subscribers": len(others),
            "said_yes": sum(1 for m in others if m.get("marketing_consent") is True)}


# ── Red lines ─────────────────────────────────────────────────────────────────

def _ids(ids: list) -> str:
    shown = ", ".join(ids[:MAX_LISTED])
    return shown + (f" and {len(ids) - MAX_LISTED} more" if len(ids) > MAX_LISTED else "")


def _gbp(pence) -> str:
    return f"£{(pence or 0) / 100:.2f}"


def uk_date(value) -> str:
    """A timestamp as its London date, 'Sat 07 Nov'; 'none' passes through."""
    if value is None:
        return "not read"
    if value == "none":
        return "none"
    t = ts(value)
    return t.astimezone(UK).strftime("%a %d %b") if t else str(value)


def not_finished_yesterday(data: dict, now: datetime):
    """'£79.00, £39.99 and 1 more' for checkouts started yesterday and not completed;
    None when there were none or Stripe was not read."""
    sessions = data.get("stripe_sessions")
    if sessions is None:
        return None
    left = [s for s in sessions if inside(s.get("created"), windows(now)["yday"]) and s.get("status") != "complete"]
    if not left:
        return None
    more = f" and {len(left) - MAX_LISTED} more" if len(left) > MAX_LISTED else ""
    return ", ".join(_gbp(s.get("amount_total")) for s in left[:MAX_LISTED]) + more


def red_lines(data: dict, now: datetime) -> list:
    """What needs Matt today, most urgent first. Empty when nothing does."""
    w = windows(now)
    lines = []
    health = data.get("health")

    if health is None:
        lines.append("The app did not answer. Check Railway.")
    else:
        code = str(health.get("free_code") or "")
        if code.startswith("invalid"):
            lines.append(f"Free course code MERIDIAN10 refused by Stripe ({code[len('invalid'):].lstrip(': ') or 'no reason given'}). "
                         "Fix it in Stripe > Product catalogue > Coupons.")
        if health.get("series_price") == "missing":
            lines.append("Field Work series cannot be bought: STRIPE_PRICE_SERIES is not set in Railway.")

    purchases = data.get("purchases")
    if purchases is None:
        lines.append("Orders could not be read from Supabase. Check Supabase > Logs.")

    sessions = data.get("stripe_sessions")
    if sessions is None and data.get("stripe_error"):
        lines.append("Stripe did not answer with STRIPE_REPORT_KEY. Check the key in the GitHub repo secrets.")
    elif sessions is None:
        lines.append("Checkout figures are missing: add the STRIPE_REPORT_KEY secret in "
                     "GitHub > Settings > Secrets and variables > Actions.")
    elif purchases is not None:
        recorded = {o["session"] for o in orders(purchases)}
        unrecorded = [s["id"] for s in sessions
                      if s.get("status") == "complete" and s.get("id") not in recorded
                      and inside(s.get("created"), (w["week"][0], now - RECORD_GRACE))]
        if unrecorded:
            lines.append(f"Stripe took {len(unrecorded)} order{'s' if len(unrecorded) != 1 else ''} "
                         f"the app has not recorded: {_ids(unrecorded)}. "
                         "Resend them from Stripe > Developers > Webhooks.")

    if purchases is not None:
        free_two = [o for o in orders(purchases)
                    if o["product"] == "free" and o["at"] and w["two"][0] <= o["at"] < w["two"][1]]
        if not free_two:
            lines.append(f"No free-course orders for 2 days (last one {uk_date(data.get('last_free_order'))}). "
                         "Try the free course checkout yourself on meridiancpd.co.uk with MERIDIAN10.")
    return lines


# ── The email ─────────────────────────────────────────────────────────────────

ROWS = [  # (label, key, money key or None)
    ("Checkouts started", "started", None),
    ("Checkouts completed", "completed", None),
    ("Checkouts not finished", "not_finished", None),
    ("Free-course orders", "free", None),
    ("Single courses", "single", "single_gbp"),
    ("Field Work series", "series", "series_gbp"),
    ("Annual", "annual", "annual_gbp"),
    ("Paid in", "paid_gbp", "money"),
    ("New members", "members", None),
    ("My CPD sign-ins", "signins", None),
    ("Courses downloaded", "opened", None),
    ("Courses completed", "completions", None),
    ("Certificates issued", "certificates", None),
    ("Follow-up emails sent", "followups", None),
    ("Outreach emails sent", "outreach", None),
    ("Unsubscribes", "unsubscribes", None),
]


def cell(f: dict, key: str, money: str | None) -> str:
    v = f.get(key)
    if v is None:
        return "n/a"
    if money == "money":
        return f"£{v:,.2f}"
    if money and v:
        return f"{v} (£{f.get(money, 0):,.2f})"
    return str(v)


def build(data: dict, now: datetime) -> dict:
    """{'subject', 'text', 'html', 'red'} for the morning email."""
    w = windows(now)
    yday, week = figures(data, w["yday"]), figures(data, w["week"])
    red = red_lines(data, now)
    p = pool(data.get("members"), data.get("purchases"))
    health = data.get("health") or {}

    if yday["paid_gbp"] is None:
        subject = f"Meridian {w['yday_label']}: orders not read"
    else:
        paid_n = yday["single"] + yday["series"] + yday["annual"]
        subject = (f"Meridian {w['yday_label']}: {yday['free']} free, {paid_n} paid (£{yday['paid_gbp']:,.2f})")
    left = not_finished_yesterday(data, now)
    left_line = f"Not finished yesterday: {left}." if left else ""
    if red:
        subject = f"{len(red)} need{'s' if len(red) == 1 else ''} you | " + subject

    if p:
        pool_line = (f"Members {p['members']}: {p['subscribers']} subscribers, "
                     f"{p['free_only']} free-course only. "
                     f"{p['said_yes']} of {p['non_subscribers']} non-subscribers said yes to emails.")
    else:
        pool_line = "Members: not read."
    if health:
        app_line = (f"App up, {health.get('available', '?')} courses on sale, "
                    f"free code {health.get('free_code', 'not checked')}.")
    else:
        app_line = "App not answering."

    width = max(len(r[0]) for r in ROWS)
    table = "\n".join(f"{label:<{width}}  {cell(yday, k, m):>12}  {cell(week, k, m):>14}"
                      for label, k, m in ROWS)
    text = "\n".join([
        f"Meridian CPD, {w['yday_label']} and the last 7 days",
        "",
        *(["NEEDS YOU", *(f"- {r}" for r in red), ""] if red else ["Nothing needs you today.", ""]),
        f"{'':<{width}}  {'Yesterday':>12}  {'7 days':>14}",
        table,
        *([left_line] if left_line else []),
        "",
        pool_line,
        app_line,
        "",
        "Admin: https://app.meridiancpd.co.uk/admin",
    ]) + "\n"

    red_html = ("".join(f'<div style="background:#fee2e2;color:#991b1b;border-left:4px solid #dc2626;'
                        f'padding:8px 10px;margin:0 0 6px;font-weight:600">{escape(r)}</div>' for r in red)
                if red else '<div style="color:#166534;margin:0 0 6px">Nothing needs you today.</div>')
    rows_html = "".join(
        f'<tr><td style="padding:3px 6px 3px 0">{escape(label)}</td>'
        f'<td style="padding:3px 6px;text-align:right">{escape(cell(yday, k, m))}</td>'
        f'<td style="padding:3px 0 3px 6px;text-align:right;color:#4b5563">{escape(cell(week, k, m))}</td></tr>'
        for label, k, m in ROWS)
    html = f"""<!DOCTYPE html><html><head><meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1"></head>
<body style="font-family:Arial,sans-serif;max-width:480px;margin:0 auto;padding:12px;color:#1a1a1a;font-size:14px;line-height:1.4">
<div style="font-weight:700;color:#0D1F0E;margin-bottom:8px">Meridian CPD, {escape(w['yday_label'])} and the last 7 days</div>
{red_html}
<table style="width:100%;border-collapse:collapse;margin-top:8px;font-size:14px">
<tr style="color:#6b7280;font-size:12px"><td></td><td style="text-align:right;padding:0 6px">Yesterday</td><td style="text-align:right">7 days</td></tr>
{rows_html}
</table>
{f'<p style="font-size:13px;margin:6px 0 0">{escape(left_line)}</p>' if left_line else ''}
<p style="font-size:13px;margin:10px 0 2px">{escape(pool_line)}</p>
<p style="font-size:13px;margin:0 0 8px;color:#4b5563">{escape(app_line)}</p>
<p style="font-size:13px;margin:0"><a style="color:#0D1F0E" href="https://app.meridiancpd.co.uk/admin">Admin</a></p>
</body></html>"""
    return {"subject": subject, "text": text, "html": html, "red": red}
