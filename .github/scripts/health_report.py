"""
Meridian CPD — Daily Health Report

Runs at 07:20 UTC via GitHub Actions.
Emails mattid272@gmail.com with a one-glance system status.

Checks:
- Active subscribers (Supabase members table)
- New sign-ups in last 24 hrs
- Outreach campaign status
- Emails sent yesterday (outreach_sends)
- Backend health (app.meridiancpd.co.uk)
- Course library count
"""
import os
import httpx
from datetime import datetime, timezone, timedelta
from supabase import create_client
import resend

SUPABASE_URL = os.environ["SUPABASE_URL"]
SUPABASE_KEY = os.environ["SUPABASE_SERVICE_ROLE_KEY"]
REPORT_TO    = os.environ.get("REPORT_TO_EMAIL", "mattid272@gmail.com")

resend.api_key = os.environ["RESEND_API_KEY"]

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

now = datetime.now(timezone.utc)
yesterday = (now - timedelta(hours=24)).isoformat()


def q(label, fn):
    try:
        return fn()
    except Exception as e:
        print(f"  Warning — {label}: {e}")
        return None


def check_backend():
    try:
        r = httpx.get("https://app.meridiancpd.co.uk/health", timeout=8)
        return "UP" if r.status_code < 400 else f"DOWN ({r.status_code})"
    except Exception:
        return "UNREACHABLE"


def get_subscriber_count():
    res = supabase.table("members").select("id", count="exact").eq("plan", "subscription").execute()
    return res.count or 0


def get_new_signups():
    res = supabase.table("members").select("email, name, joined_at").gte("joined_at", yesterday).order("joined_at", desc=True).execute()
    return res.data or []


def get_campaign_status():
    res = supabase.table("outreach_campaigns").select("name, status").execute()
    campaigns = res.data or []
    if not campaigns:
        return "No campaigns"
    return "; ".join(f"{c['name']} ({c['status']})" for c in campaigns)


def get_emails_sent_yesterday():
    res = supabase.table("outreach_sends").select("id", count="exact").gte("sent_at", yesterday).execute()
    return res.count or 0


def get_suppressions_today():
    res = supabase.table("outreach_suppressed").select("email").gte("suppressed_at", yesterday).execute()
    return res.data or []


def get_course_count():
    from pathlib import Path
    courses_dir = Path(__file__).parent.parent.parent / "courses"
    if courses_dir.exists():
        return len([d for d in courses_dir.iterdir() if d.is_dir() and not d.name.startswith(".")])
    return "?"


# ── Gather ────────────────────────────────────────────────────────────────────
print("Gathering health data...")

backend_status   = q("backend",      check_backend)
subscriber_count = q("subscribers",  get_subscriber_count)
new_signups      = q("new signups",  get_new_signups)
campaign_status  = q("campaigns",    get_campaign_status)
emails_yesterday = q("emails sent",  get_emails_sent_yesterday)
suppressions     = q("suppressions", get_suppressions_today)
course_count     = q("courses",      get_course_count)

today_str = now.strftime("%a %d %b %Y")

# ── Format email ──────────────────────────────────────────────────────────────
status_icon = "✅" if backend_status == "UP" else "🔴"

signup_lines = ""
if new_signups:
    signup_lines = "\n".join(f"  + {s.get('name', 'Unknown')} ({s.get('email', '?')}) — {s.get('joined_at', '')[:10]}" for s in new_signups)
else:
    signup_lines = "  None in last 24 hrs"

suppression_lines = ""
if suppressions:
    suppression_lines = "Unsubscribes (last 24 hrs):\n" + "\n".join(f"  - {s.get('email', '?')}" for s in suppressions) + "\n\n"

subject = f"Meridian CPD — Daily report {today_str} | {subscriber_count} subscribers | Backend {backend_status}"

body_text = f"""Meridian CPD — Daily Health Report
{today_str}

SYSTEM STATUS
─────────────
Backend (app.meridiancpd.co.uk): {status_icon} {backend_status}
Courses in library: {course_count}
Campaign status: {campaign_status}

SUBSCRIBERS
──────────────
Active subscribers: {subscriber_count}

New signups (last 24 hrs):
{signup_lines}

OUTREACH
────────
Emails sent yesterday: {emails_yesterday}
{suppression_lines}
NOTES
─────
• Admin panel: https://meridiancpd.co.uk/admin/
• Subscriber dashboard: https://app.meridiancpd.co.uk/admin/
• Content engine runs on the 1st and 15th automatically.

—
This report is sent daily at 07:20 UTC.
Meridian CPD | hello@meridiancpd.co.uk
"""

body_html = f"""<!DOCTYPE html>
<html><head><meta charset="UTF-8">
<style>
  body{{font-family:Arial,sans-serif;max-width:600px;margin:0 auto;padding:28px 24px;color:#1a1a1a;font-size:15px;line-height:1.6;background:#f5f5f5}}
  .card{{background:#fff;border-radius:8px;padding:24px;margin-bottom:16px;border:1px solid #e5e7eb}}
  h1{{font-size:18px;font-weight:700;color:#0D1F0E;margin:0 0 4px}}
  .date{{font-size:13px;color:#6b7280;margin-bottom:20px}}
  h2{{font-size:13px;font-weight:700;letter-spacing:.08em;text-transform:uppercase;color:#6b7280;margin:0 0 12px;border-bottom:1px solid #e5e7eb;padding-bottom:8px}}
  .stat{{display:inline-block;margin-right:24px;margin-bottom:12px}}
  .stat-num{{font-size:28px;font-weight:700;color:#0D1F0E;line-height:1}}
  .stat-lbl{{font-size:12px;color:#6b7280;margin-top:2px}}
  .status-ok{{color:#16a34a;font-weight:700}}
  .status-err{{color:#dc2626;font-weight:700}}
  .signup-list{{font-size:13px;color:#374151}}
  .signup-item{{padding:6px 0;border-bottom:1px solid #f3f4f6}}
  .empty{{color:#9ca3af;font-style:italic;font-size:13px}}
  .links a{{color:#0D1F0E;font-size:13px;margin-right:16px}}
  .footer{{font-size:12px;color:#9ca3af;margin-top:20px;padding-top:16px;border-top:1px solid #e5e7eb}}
  .pill{{display:inline-block;padding:2px 8px;border-radius:100px;font-size:12px;font-weight:600}}
  .pill-paused{{background:#fef3c7;color:#92400e}}
  .pill-active{{background:#dcfce7;color:#166534}}
</style></head><body>
<div class="card">
  <h1>Meridian CPD</h1>
  <div class="date">Daily Report — {today_str}</div>

  <h2>System Status</h2>
  <p>Backend: <span class="{'status-ok' if backend_status == 'UP' else 'status-err'}">{status_icon} {backend_status}</span>
  &nbsp;&nbsp; Courses in library: <strong>{course_count}</strong></p>
  <p style="margin-top:8px;font-size:13px;color:#374151">Campaign: {campaign_status}</p>
</div>

<div class="card">
  <h2>Subscribers</h2>
  <div class="stat">
    <div class="stat-num">{subscriber_count}</div>
    <div class="stat-lbl">Active subscribers</div>
  </div>
  <div style="margin-top:12px">
    <strong style="font-size:13px">New signups (last 24 hrs)</strong>
    {"".join(f'<div class="signup-item">{s.get("name","?")} &bull; {s.get("email","?")} &bull; {s.get("joined_at","")[:10]}</div>' for s in new_signups) if new_signups else '<p class="empty">None</p>'}
  </div>
</div>

<div class="card">
  <h2>Outreach</h2>
  <p style="font-size:14px">Emails sent (last 24 hrs): <strong>{emails_yesterday}</strong></p>
  {"<p style='font-size:13px;margin-top:8px'><strong>Unsubscribes:</strong> " + ", ".join(s.get("email","?") for s in suppressions) + "</p>" if suppressions else ""}
</div>

<div class="links card">
  <h2>Quick Links</h2>
  <a href="https://meridiancpd.co.uk/admin/">Course Admin</a>
  <a href="https://app.meridiancpd.co.uk/admin/">Subscriber Admin</a>
  <a href="https://dashboard.stripe.com">Stripe</a>
  <a href="https://railway.app">Railway</a>
</div>

<div class="footer">
  Daily health report sent by GitHub Actions at 07:20 UTC.<br>
  Meridian CPD | hello@meridiancpd.co.uk
</div>
</body></html>"""

# ── Send ──────────────────────────────────────────────────────────────────────
print(f"Sending report to {REPORT_TO}...")

resend.Emails.send({
    "from": "Meridian CPD <hello@meridiancpd.co.uk>",
    "to": [REPORT_TO],
    "subject": subject,
    "text": body_text,
    "html": body_html,
})

print("Report sent.")
print(f"  Backend: {backend_status}")
print(f"  Subscribers: {subscriber_count}")
print(f"  New signups: {len(new_signups or [])}")
print(f"  Emails sent yesterday: {emails_yesterday}")
print(f"  Courses: {course_count}")
