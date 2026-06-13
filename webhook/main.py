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
import os
import secrets
import uuid
import hmac
import hashlib
import time
from datetime import datetime, timezone

import stripe
from fastapi import FastAPI, HTTPException, Request, Response, Depends, Cookie
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.security import HTTPBasic, HTTPBasicCredentials
import httpx
from supabase import create_client

from email_sender import send_course_email, send_certificate_email, send_unsubscribe_goodbye_email
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
    "MER-DEA-014": {"course_id": "MER-DEA-014", "title": "EPC Audit Preparation: How to Pass Your Annual Audit", "cpd_hours": 1.0, "published": "2026-03-01"},
    "MER-DEA-021": {"course_id": "MER-DEA-021", "title": "Airtightness Testing in RdSAP 10", "cpd_hours": 1.0, "published": "2026-03-01"},
    "MER-RA-001":  {"course_id": "MER-RA-001",  "title": "PAS 2035:2023 Overview for Retrofit Assessors", "cpd_hours": 2.0, "published": "2026-03-01"},
    "MER-RA-002":  {"course_id": "MER-RA-002",  "title": "Moisture Risk Assessment in PAS 2035:2023: The Updated Framework", "cpd_hours": 1.0, "published": "2026-03-01"},
    "MER-RA-003":  {"course_id": "MER-RA-003",  "title": "Dwelling Data Collection: PAS 2035:2023 Annex A Requirements", "cpd_hours": 1.0, "published": "2026-03-01"},
    "MER-RA-004":  {"course_id": "MER-RA-004",  "title": "Cavity Wall Insulation: Risk Factors and the Retrofit Assessor's Role", "cpd_hours": 1.0, "published": "2026-03-01"},
    "MER-RA-005":  {"course_id": "MER-RA-005",  "title": "Solid Wall Insulation: IWI vs EWI — Risks, Evidence and Assessment", "cpd_hours": 1.0, "published": "2026-03-01"},
    "MER-RA-006":  {"course_id": "MER-RA-006",  "title": "EPR Variation: Managing the RdSAP 10 Transition in PAS 2035 Projects", "cpd_hours": 1.0, "published": "2026-03-01"},
    "MER-RA-007":  {"course_id": "MER-RA-007",  "title": "Heating System Assessment for Retrofit: What the Retrofit Assessor Must Record", "cpd_hours": 1.0, "published": "2026-03-01"},
    "MER-RA-008":  {"course_id": "MER-RA-008",  "title": "Ventilation Assessment in Retrofit: Background Ventilation to MVHR", "cpd_hours": 1.0, "published": "2026-03-01"},
    "MER-RA-009":  {"course_id": "MER-RA-009",  "title": "External Wall Insulation: Planning Permission and Fire Risk", "cpd_hours": 1.0, "published": "2026-03-01"},
    "MER-RA-010":  {"course_id": "MER-RA-010",  "title": "Thermal Bridging in Retrofit Assessment: What Assessors Must Record", "cpd_hours": 1.0, "published": "2026-03-01"},
    "MER-RA-011":  {"course_id": "MER-RA-011",  "title": "Occupancy Assessment: Health Conditions, Vulnerability and Overheating Risk", "cpd_hours": 1.0, "published": "2026-03-01"},
    "MER-RA-012":  {"course_id": "MER-RA-012",  "title": "TrustMark Data Requirements: What Retrofit Assessors Must Submit", "cpd_hours": 1.0, "published": "2026-03-01"},
    "MER-ALL-001": {"course_id": "MER-ALL-001", "title": "UK Energy Policy 2026: What Assessors Need to Know", "cpd_hours": 1.0, "published": "2026-03-01"},
    "MER-ALL-004": {"course_id": "MER-ALL-004", "title": "Fire Safety in Retrofit: What Every Assessor Must Know", "cpd_hours": 1.0, "published": "2026-03-01"},
    "MER-ALL-005": {"course_id": "MER-ALL-005", "title": "Future Homes Standard 2025: What Energy Assessors Need to Know", "cpd_hours": 1.0, "published": "2026-04-15"},
    # Subscription — welcome email only; library access granted via plan field
    "SUBSCRIPTION": {"course_id": "SUBSCRIPTION", "title": "Annual Subscription — All Courses", "cpd_hours": 0, "published": "2026-03-01"},
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

    if event["type"] == "checkout.session.completed":
        session = event["data"]["object"]
        await handle_checkout(session)

    return {"status": "ok"}


async def handle_checkout(session):
    customer_details = getattr(session, "customer_details", None) or {}
    email = ((getattr(customer_details, "email", None) or customer_details.get("email", "")) if customer_details else "").strip().lower()
    name = (getattr(customer_details, "name", None) or customer_details.get("name", "")) if customer_details else ""
    name = name or (email.split("@")[0].title() if email else "")
    stripe_customer_id = getattr(session, "customer", "") or ""
    session_id = getattr(session, "id", None) or session["id"]
    amount = getattr(session, "amount_total", 0) or 0

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

    print(f"Handled checkout for {email}: {course_keys}")


# ── Download gate — marks course as downloaded before serving PDF ──────────────

@app.get("/download/{course_id}")
async def download_course(course_id: str, request: Request):
    """Records that subscriber has downloaded the PDF, then redirects to it.
    Requires active session. Sets downloaded_at on the completion record."""
    session_token = request.cookies.get("session_token")
    email = _verify_session_token(session_token) if session_token else None
    if not email:
        return RedirectResponse("/my-cpd", status_code=302)

    if course_id not in COURSES:
        raise HTTPException(status_code=404, detail="Course not found")

    # Mark downloaded_at on the completion record if not already set
    member_res = supabase.table("members").select("id").eq("email", email).execute()
    if member_res.data:
        member_id = member_res.data[0]["id"]
        supabase.table("completions").update({
            "downloaded_at": datetime.now(timezone.utc).isoformat(),
        }).eq("member_id", member_id).eq("course_id", course_id).is_(
            "downloaded_at", "null"
        ).execute()
        print(f"Download recorded: {email} → {course_id}")

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

    row = result.data[0]
    course_id = row["course_id"]
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

    row = result.data[0]
    member_id = row["member_id"]
    course_id = row["course_id"]
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
    return {"status": "ok"}


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

@app.get("/my-cpd/consent/yes", response_class=HTMLResponse)
async def consent_yes(email: str):
    supabase.table("members").update({"marketing_consent": True}).eq("email", email).execute()
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


@app.get("/my-cpd/consent/no", response_class=HTMLResponse)
async def consent_no(email: str):
    supabase.table("members").update({"marketing_consent": False}).eq("email", email).execute()
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

    # Create a short-lived magic link token (1 hour)
    exp = int(time.time()) + 3600
    payload = f"{email}:{exp}"
    sig = hmac.new(DASHBOARD_SECRET.encode(), payload.encode(), hashlib.sha256).hexdigest()
    magic_token = f"{payload}:{sig}"
    import base64
    encoded = base64.urlsafe_b64encode(magic_token.encode()).decode()

    login_url = f"{BASE_URL}/my-cpd/login/{encoded}"

    # Send magic link email
    async with httpx.AsyncClient() as client:
        await client.post(
            "https://api.resend.com/emails",
            headers={"Authorization": f"Bearer {os.environ.get('RESEND_API_KEY', '')}"},
            json={
                "from": "Meridian CPD <hello@meridiancpd.co.uk>",
                "to": [email],
                "subject": "Your Meridian CPD login link",
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

    # Issue a 30-day session cookie
    session_token = _make_session_token(email)
    response = RedirectResponse("/my-cpd/dashboard", status_code=302)
    response.set_cookie("session_token", session_token, max_age=86400 * 30,
                        httponly=True, samesite="lax", secure=True)
    return response


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
    is_sub = member["plan"] == "subscription"

    # Fetch purchases
    purchases_res = supabase.table("purchases").select("course_id, purchased_at").eq(
        "member_id", member_id
    ).execute()
    purchased_ids = {p["course_id"] for p in (purchases_res.data or [])}

    # Fetch completions
    completions_res = supabase.table("completions").select(
        "course_id, completed_at, completion_token"
    ).eq("member_id", member_id).execute()
    completed = {c["course_id"]: c for c in (completions_res.data or []) if c.get("completed_at")}
    pending_tokens = {c["course_id"]: c["completion_token"] for c in (completions_res.data or []) if not c.get("completed_at")}

    # For subscribers: ensure every course has a completion token so "Mark Complete" works.
    # Tokens are created lazily on first dashboard load — no email needed, just DB record.
    if is_sub:
        all_course_ids = [k for k in COURSES if k != "SUBSCRIPTION"]
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
        show_courses = {k: COURSES[k] for k in purchased_ids if k in COURSES and k != "SUBSCRIPTION"}

    # Build course rows
    course_rows = ""
    for cid, course in show_courses.items():
        hours = course["cpd_hours"]
        title = course["title"]
        if cid in completed:
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
    total_courses = len([k for k in COURSES if k != "SUBSCRIPTION"])
    courses_owned = len(show_courses)
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

    plan_badge = "Annual Subscription" if is_sub else "Pay Per Course"

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
    <p>{email} &nbsp;·&nbsp; {plan_badge} &nbsp;·&nbsp;
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


@app.get("/admin/courses", response_class=HTMLResponse)
async def admin_courses(credentials=Depends(_check_admin)):
    from datetime import date, timedelta
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
