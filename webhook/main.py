"""
Meridian CPD — Stripe Webhook + Course Delivery + Admin Panel
Deployed on Railway. Handles:
  - checkout.session.completed → deliver course PDF + log member
  - GET /complete/[token]      → show completion confirmation page
  - POST /complete/[token]     → record completion + issue certificate
  - GET /verify/[cert-number]  → certificate verification page
  - GET /admin                 → admin dashboard (password protected)
"""
import os
import secrets
import uuid
from datetime import datetime, timezone

import stripe
from fastapi import FastAPI, HTTPException, Request, Response, Depends
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.security import HTTPBasic, HTTPBasicCredentials
import httpx
from supabase import create_client

from email_sender import send_course_email, send_certificate_email
from certificate_generator import generate_certificate

app = FastAPI()

# ── Clients ───────────────────────────────────────────────────────────────────
stripe.api_key = os.environ["STRIPE_SECRET_KEY"]
WEBHOOK_SECRET = os.environ["STRIPE_WEBHOOK_SECRET"]

supabase = create_client(
    os.environ["SUPABASE_URL"],
    os.environ["SUPABASE_SERVICE_ROLE_KEY"],
)

BASE_URL = os.environ.get("BASE_URL", "https://meridiancpd.co.uk")
LOGO_URL = os.environ.get("LOGO_URL", "")  # Set this env var when new logo is ready

def _logo() -> str:
    """Returns logo HTML — image if LOGO_URL is set, otherwise styled text fallback."""
    if LOGO_URL:
        return f'<img src="{LOGO_URL}" height="50" alt="Meridian CPD" style="margin-bottom:16px;display:block">'
    return '<div style="font-size:22px;font-weight:900;color:#0f2547;letter-spacing:-0.5px;margin-bottom:16px">MERIDIAN <span style="color:#0891b2">CPD</span></div>'

# ── Course catalogue ───────────────────────────────────────────────────────────
# Each entry: course_id, title, cpd_hours, pdf_url (Supabase Storage public URL)
COURSES = {
    "MER-DEA-001": {
        "course_id": "MER-DEA-001",
        "title": "RdSAP 10: What's Changed and Why",
        "cpd_hours": 2.0,
        "pdf_url": os.environ.get("PDF_MER_DEA_001", ""),
    },
    "MER-DEA-002": {
        "course_id": "MER-DEA-002",
        "title": "Measuring Windows in RdSAP 10",
        "cpd_hours": 1.0,
        "pdf_url": os.environ.get("PDF_MER_DEA_002", ""),
    },
    "MER-DEA-003": {
        "course_id": "MER-DEA-003",
        "title": "Ventilation in RdSAP 10: PIV, MVHR, Natural",
        "cpd_hours": 1.0,
        "pdf_url": os.environ.get("PDF_MER_DEA_003", ""),
    },
    "MER-DEA-004": {
        "course_id": "MER-DEA-004",
        "title": "Room in Roof: Type 1 and Type 2",
        "cpd_hours": 1.0,
        "pdf_url": os.environ.get("PDF_MER_DEA_004", ""),
    },
    "MER-DEA-010": {
        "course_id": "MER-DEA-010",
        "title": "Lighting and Renewables in RdSAP 10",
        "cpd_hours": 1.0,
        "pdf_url": os.environ.get("PDF_MER_DEA_010", ""),
    },
    "MER-DEA-011": {
        "course_id": "MER-DEA-011",
        "title": "Solar PV, Battery Storage and PV Diverters in RdSAP 10",
        "cpd_hours": 1.0,
        "pdf_url": os.environ.get("PDF_MER_DEA_011", ""),
    },
    "MER-DEA-021": {
        "course_id": "MER-DEA-021",
        "title": "Airtightness Testing in RdSAP 10",
        "cpd_hours": 1.0,
        "pdf_url": os.environ.get("PDF_MER_DEA_021", ""),
    },
    "MER-RA-001": {
        "course_id": "MER-RA-001",
        "title": "PAS 2035:2023 Overview for Retrofit Assessors",
        "cpd_hours": 2.0,
        "pdf_url": os.environ.get("PDF_MER_RA_001", ""),
    },
    "MER-RA-006": {
        "course_id": "MER-RA-006",
        "title": "EPR Variation: Managing the RdSAP 10 Transition in PAS 2035 Projects",
        "cpd_hours": 1.0,
        "pdf_url": os.environ.get("PDF_MER_RA_006", ""),
    },
    "MER-RA-009": {
        "course_id": "MER-RA-009",
        "title": "External Wall Insulation: Planning Permission and Fire Risk",
        "cpd_hours": 1.0,
        "pdf_url": os.environ.get("PDF_MER_RA_009", ""),
    },
    "MER-ALL-001": {
        "course_id": "MER-ALL-001",
        "title": "UK Energy Policy 2026: What Assessors Need to Know",
        "cpd_hours": 1.0,
        "pdf_url": os.environ.get("PDF_MER_ALL_001", ""),
    },
    "MER-ALL-004": {
        "course_id": "MER-ALL-004",
        "title": "Fire Safety in Retrofit: What Every Assessor Must Know",
        "cpd_hours": 1.0,
        "pdf_url": os.environ.get("PDF_MER_ALL_004", ""),
    },
    # Subscription — welcome email only; library access granted via plan field
    "SUBSCRIPTION": {
        "course_id": "SUBSCRIPTION",
        "title": "Annual Subscription — All Courses",
        "cpd_hours": 0,
        "pdf_url": "",
    },
}

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
        # Update plan if upgrading to subscription
        if plan == "subscription" and member["plan"] != "subscription":
            supabase.table("members").update({
                "plan": "subscription",
                "stripe_customer_id": stripe_customer_id,
            }).eq("id", member["id"]).execute()
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

    if event["type"] == "checkout.session.completed":
        session = event["data"]["object"]
        await handle_checkout(session)

    return {"status": "ok"}


async def handle_checkout(session):
    email = session.get("customer_details", {}).get("email", "")
    name = session.get("customer_details", {}).get("name", "") or email.split("@")[0].title()
    stripe_customer_id = session.get("customer", "") or ""
    session_id = session["id"]
    amount = session.get("amount_total", 0)

    # Determine what was purchased
    line_items = stripe.checkout.Session.list_line_items(session_id, limit=5)
    course_keys = []
    plan = "single"
    for item in line_items.data:
        price_id = item.price.id
        course_key = PRICE_TO_COURSE.get(price_id, "")
        if course_key:
            course_keys.append(course_key)
            if course_key == "subscription":
                plan = "subscription"

    if not email:
        print(f"No email in session {session_id} — skipping")
        return

    member = get_or_create_member(email, name, stripe_customer_id, plan)
    member_id = member["id"]

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
        else:
            token = create_completion_token(member_id, course["course_id"])
            completion_link = f"{BASE_URL}/complete/{token}"
            await send_course_email(
                to_email=email,
                to_name=name,
                course_title=course["title"],
                course_id=course["course_id"],
                pdf_url=course["pdf_url"],
                completion_link=completion_link,
                is_subscription=False,
            )
            log_purchase(member_id, course["course_id"], session_id, amount)

    print(f"Handled checkout for {email}: {course_keys}")


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

    row = result.data[0]
    course_id = row["course_id"]
    name = row["members"]["name"] or "there"

    return HTMLResponse(f"""
    <html>
    <head>
      <title>Complete Your CPD — Meridian CPD</title>
      <style>
        body {{ font-family: Arial, sans-serif; max-width: 600px; margin: 60px auto; padding: 0 20px; }}
        h1 {{ color: #0f2547; }}
        .btn {{ background: #0891b2; color: white; padding: 16px 32px; border: none;
                font-size: 18px; border-radius: 6px; cursor: pointer; text-decoration: none;
                display: inline-block; margin-top: 24px; }}
        .small {{ color: #666; font-size: 13px; margin-top: 20px; }}
      </style>
    </head>
    <body>
      {_logo()}
      <h1>Complete Your CPD</h1>
      <p>Hi {name},</p>
      <p>Please confirm you have read and understood <strong>Course {course_id}</strong>.</p>
      <p>Once confirmed, your CPD certificate will be generated and emailed to you immediately.</p>
      <form method="POST" action="/complete/{token}">
        <label style="display:flex;align-items:center;gap:10px;margin:20px 0">
          <input type="checkbox" name="confirm" required style="width:20px;height:20px">
          <span>I confirm I have read and understood the course material.</span>
        </label>
        <button type="submit" class="btn">Confirm Completion &amp; Get Certificate</button>
      </form>
      <p class="small">Your certificate will be sent to your registered email address.
      It serves as evidence of CPD completion for your accreditation body.</p>
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

    row = result.data[0]
    member_id = row["member_id"]
    course_id = row["course_id"]
    member_name = row["members"]["name"] or "Assessor"
    member_email = row["members"]["email"]

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
        "course_id": course_id,
        "course_title": course["title"],
        "cpd_hours": course["cpd_hours"],
        "issued_for_month": datetime.now(timezone.utc).strftime("%Y-%m"),
    }).execute()

    # Email certificate
    await send_certificate_email(
        to_email=member_email,
        to_name=member_name,
        cert_number=cert_number,
        course_title=course["title"],
        cpd_hours=course["cpd_hours"],
        cert_pdf_bytes=cert_pdf_bytes,
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
      <p>Well done, {member_name}. Your certificate has been emailed to <strong>{member_email}</strong>.</p>
      <div class="cert-num">{cert_number}</div>
      <p>Keep this certificate number — your accreditation body can verify it at
         <a href="https://meridiancpd.co.uk/verify/{cert_number}">meridiancpd.co.uk/verify/{cert_number}</a>
      </p>
      <p><a href="https://meridiancpd.co.uk/library">Browse more courses →</a></p>
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
             <span class="value">{cert["members"]["name"]}</span></div>
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
    return {"status": "ok"}


# ── Admin panel ────────────────────────────────────────────────────────────────

ADMIN_PASSWORD = os.environ.get("ADMIN_PASSWORD", "meridian-admin")
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
         font-size: 11px; font-weight: 600; }
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
a.vlink { color: #0891b2; text-decoration: none; font-size: 12px; }
a.vlink:hover { text-decoration: underline; }
"""


def _check_admin(credentials: HTTPBasicCredentials = Depends(security)):
    if credentials.password != ADMIN_PASSWORD:
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

    fake_session_id = f"cs_test_{secrets.token_hex(8)}"
    member = get_or_create_member(email, name, "cus_test", "single")
    member_id = member["id"]
    log_purchase(member_id, course_id, fake_session_id, int(course.get("cpd_hours", 1) * 100))
    token = create_completion_token(member_id, course_id)
    completion_link = f"{BASE_URL}/complete/{token}"

    await send_course_email(
        to_email=email, to_name=name, course_title=course["title"],
        course_id=course_id, pdf_url=course["pdf_url"],
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


@app.get("/admin", response_class=HTMLResponse)
@app.get("/admin/dashboard", response_class=HTMLResponse)
async def admin_dashboard(credentials=Depends(_check_admin)):
    # Fetch counts
    members_res = supabase.table("members").select("id, plan, joined_at", count="exact").execute()
    purchases_res = supabase.table("purchases").select("id, amount_gbp, purchased_at", count="exact").execute()
    completions_res = supabase.table("completions").select("id", count="exact").not_.is_("completed_at", "null").execute()
    certs_res = supabase.table("certificates").select("id", count="exact").execute()

    total_members = members_res.count or 0
    total_purchases = purchases_res.count or 0
    total_completions = completions_res.count or 0
    total_certs = certs_res.count or 0

    sub_count = sum(1 for m in (members_res.data or []) if m.get("plan") == "subscription")
    revenue = sum(float(p.get("amount_gbp") or 0) for p in (purchases_res.data or []))

    # Recent purchases
    recent_p = supabase.table("purchases").select(
        "*, members(name, email)"
    ).order("purchased_at", desc=True).limit(8).execute()

    rows = ""
    for p in (recent_p.data or []):
        m = p.get("members") or {}
        date = (p.get("purchased_at") or "")[:10]
        amt = f"£{float(p.get('amount_gbp') or 0):.2f}"
        rows += f"""<tr>
            <td>{date}</td>
            <td>{m.get('name','—')}</td>
            <td>{m.get('email','—')}</td>
            <td>{p.get('course_id','—')}</td>
            <td class="revenue">{amt}</td>
        </tr>"""

    recent_table = f"""
    <table>
      <tr><th>Date</th><th>Name</th><th>Email</th><th>Course</th><th>Amount</th></tr>
      {rows or '<tr><td colspan="5" class="empty">No purchases yet — campaigns not fired yet</td></tr>'}
    </table>"""

    body = f"""
    <div class="stats">
      <div class="stat"><div class="val">{total_members}</div>
        <div class="lbl">Total Members</div>
        <div class="sub">{sub_count} on annual subscription</div></div>
      <div class="stat"><div class="val">£{revenue:.0f}</div>
        <div class="lbl">Total Revenue</div>
        <div class="sub">{total_purchases} purchases</div></div>
      <div class="stat"><div class="val">{total_completions}</div>
        <div class="lbl">Completions</div>
        <div class="sub">Courses confirmed read</div></div>
      <div class="stat"><div class="val">{total_certs}</div>
        <div class="lbl">Certificates Issued</div>
        <div class="sub">All time</div></div>
    </div>
    <div class="card">
      <h2>Recent Purchases</h2>
      {recent_table}
    </div>"""

    return _page("Dashboard", "dashboard", body)


@app.get("/admin/members", response_class=HTMLResponse)
async def admin_members(credentials=Depends(_check_admin)):
    res = supabase.table("members").select("*").order("joined_at", desc=True).execute()
    rows = ""
    for m in (res.data or []):
        plan = m.get("plan", "single")
        badge = "badge-sub" if plan == "subscription" else "badge-single"
        label = "Annual Sub" if plan == "subscription" else "Single"
        joined = (m.get("joined_at") or "")[:10]
        courses = ", ".join(m.get("courses_purchased") or []) or "—"
        rows += f"""<tr>
            <td>{m.get('name','—')}</td>
            <td>{m.get('email','—')}</td>
            <td><span class="badge {badge}">{label}</span></td>
            <td>{joined}</td>
            <td>{courses}</td>
        </tr>"""

    body = f"""
    <div class="card">
      <h2>All Members ({len(res.data or [])})</h2>
      <table>
        <tr><th>Name</th><th>Email</th><th>Plan</th><th>Joined</th><th>Courses</th></tr>
        {rows or '<tr><td colspan="5" class="empty">No members yet</td></tr>'}
      </table>
    </div>"""
    return _page("Members", "members", body)


@app.get("/admin/courses", response_class=HTMLResponse)
async def admin_courses(credentials=Depends(_check_admin)):
    cards = ""
    for cid, course in COURSES.items():
        if cid == "SUBSCRIPTION":
            continue
        has_pdf = bool(course.get("pdf_url"))
        status_badge = '<span class="badge badge-ok">PDF Ready</span>' if has_pdf else '<span class="badge badge-warn">Awaiting Upload</span>'
        cards += f"""
        <div class="course-card">
          <div class="cid">{course['course_id']}</div>
          <div class="ctitle">{course['title']}</div>
          <div class="cmeta">{course['cpd_hours']:g} CPD Hour{'s' if course['cpd_hours'] != 1 else ''} &nbsp;•&nbsp; {status_badge}</div>
        </div>"""

    body = f"""
    <div class="card">
      <h2>Course Library ({len(COURSES) - 1} courses)</h2>
      <div class="course-grid">{cards}</div>
    </div>"""
    return _page("Courses", "courses", body)


@app.get("/admin/certificates", response_class=HTMLResponse)
async def admin_certificates(credentials=Depends(_check_admin)):
    res = supabase.table("certificates").select(
        "*, members(name, email)"
    ).order("issued_at", desc=True).limit(100).execute()

    rows = ""
    for cert in (res.data or []):
        m = cert.get("members") or {}
        issued = (cert.get("issued_at") or "")[:10]
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
      <h2>Certificates Issued ({len(res.data or [])})</h2>
      <table>
        <tr><th>Certificate #</th><th>Member</th><th>Course</th><th>CPD</th><th>Issued</th></tr>
        {rows or '<tr><td colspan="5" class="empty">No certificates issued yet</td></tr>'}
      </table>
    </div>"""
    return _page("Certificates", "certificates", body)


@app.get("/admin/system", response_class=HTMLResponse)
async def admin_system(credentials=Depends(_check_admin)):
    # Check which env vars are set vs placeholder
    def var_status(key: str) -> str:
        val = os.environ.get(key, "")
        if not val or val.startswith("placeholder"):
            return '<span class="badge badge-off">Not Set</span>'
        return '<span class="badge badge-ok">Configured</span>'

    vars_rows = ""
    check_vars = [
        ("STRIPE_SECRET_KEY", "Stripe Secret Key"),
        ("STRIPE_WEBHOOK_SECRET", "Stripe Webhook Secret"),
        ("STRIPE_PRICE_SINGLE", "Stripe Price — Single Course"),
        ("STRIPE_PRICE_SUBSCRIPTION", "Stripe Price — Subscription"),
        ("RESEND_API_KEY", "Resend API Key (email)"),
        ("SUPABASE_URL", "Supabase URL"),
        ("SUPABASE_SERVICE_ROLE_KEY", "Supabase Service Role Key"),
        ("BASE_URL", "Base URL"),
    ]
    for key, label in check_vars:
        vars_rows += f"<tr><td>{label}</td><td><code>{key}</code></td><td>{var_status(key)}</td></tr>"

    # Course PDF status
    pdf_rows = ""
    for cid, course in COURSES.items():
        if cid == "SUBSCRIPTION":
            continue
        env_key = f"PDF_{cid.replace('-', '_')}"
        val = os.environ.get(env_key, "")
        status = '<span class="badge badge-ok">Set</span>' if val and not val.startswith("placeholder") else '<span class="badge badge-warn">Missing</span>'
        pdf_rows += f"<tr><td>{cid}</td><td><code>{env_key}</code></td><td>{status}</td></tr>"

    # Email optimizer status
    optimizer_status = '<span class="badge badge-warn">Schedule disabled — manual trigger only</span>'

    body = f"""
    <div class="card section">
      <h2>Environment Variables</h2>
      <table>
        <tr><th>Service</th><th>Variable</th><th>Status</th></tr>
        {vars_rows}
      </table>
    </div>
    <div class="card section">
      <h2>Course PDF Storage URLs</h2>
      <table>
        <tr><th>Course</th><th>Env Var</th><th>Status</th></tr>
        {pdf_rows}
      </table>
    </div>
    <div class="card section">
      <h2>Email Optimizer</h2>
      <table>
        <tr><th>Component</th><th>Status</th></tr>
        <tr><td>GitHub Actions Schedule</td><td>{optimizer_status}</td></tr>
        <tr><td>Warm-up Score Required</td><td>≥ 80 before enabling</td></tr>
        <tr><td>Repo</td><td><code>mattid272-hub/meridian-email-optimizer</code></td></tr>
      </table>
    </div>
    <div class="card section">
      <h2>Webhook Health</h2>
      <table>
        <tr><th>Endpoint</th><th>URL</th></tr>
        <tr><td>Health</td><td><a class="vlink" href="/health">/health</a></td></tr>
        <tr><td>Stripe Webhook</td><td><code>/stripe-webhook</code></td></tr>
        <tr><td>Railway URL</td><td><code>https://laudable-eagerness-production-4f04.up.railway.app</code></td></tr>
      </table>
    </div>"""
    return _page("System", "system", body)
