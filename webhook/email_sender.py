"""Resend email sender for Meridian CPD."""
import hashlib
import hmac
import os
from urllib.parse import quote

import httpx

from settings import APP_URL, APP_HOST

RESEND_API = "https://api.resend.com/emails"
FROM_EMAIL = "hello@meridiancpd.co.uk"
FROM_NAME = "Meridian CPD"
# Until domain is verified in Resend, use onboarding@resend.dev for testing
# After domain verification, switch back to hello@meridiancpd.co.uk


def consent_token(email: str) -> str:
    """Signs the marketing-consent links in our emails, so a choice can only be made from
    the link we sent to that address."""
    key = os.environ.get("DASHBOARD_SECRET", "").encode()
    return hmac.new(key, f"consent:{email.strip().lower()}".encode(), hashlib.sha256).hexdigest()[:24]


async def _send(to_email: str, to_name: str, subject: str, body: str, attachments: list[dict] | None = None):
    """Send email via Resend API."""
    api_key = os.environ["RESEND_API_KEY"]

    payload: dict = {
        "from": f"{FROM_NAME} <{FROM_EMAIL}>",
        "to": [f"{to_name} <{to_email}>"],
        "subject": subject,
        "text": body,
    }

    if attachments:
        payload["attachments"] = attachments

    async with httpx.AsyncClient() as client:
        r = await client.post(
            RESEND_API,
            headers={"Authorization": f"Bearer {api_key}"},
            json=payload,
            timeout=30,
        )
        r.raise_for_status()


async def _fetch_pdf(url: str) -> bytes | None:
    async with httpx.AsyncClient() as client:
        r = await client.get(url, timeout=30)
    return r.content if r.status_code == 200 else None


async def send_course_email(
    to_email: str,
    to_name: str,
    course_title: str,
    course_id: str,
    pdf_url: str | None,
    completion_link: str | None,
    is_subscription: bool = False,
    notes_url: str | None = None,
    series_title: str | None = None,
    part: int | None = None,
    parts_total: int | None = None,
    held_parts: list[str] | None = None,
):
    """The course email. pdf_url is the file that is the course: the written PDF, or the
    slide deck for a deck course, in which case notes_url is the written PDF that goes
    with it and both are attached. series_title, part and parts_total say where the
    course sits in a Field Work series; held_parts lists the titles of parts of that
    series that were bought but are being updated and will follow."""
    if is_subscription:
        subject = "Welcome to Meridian CPD — a few things worth knowing"
        base_url = APP_URL
        consent_query = f"email={quote(to_email)}&token={consent_token(to_email)}"
        body = f"""Hi {to_name},

⚠ QUICK NOTE: This email may have landed in your junk or spam folder. If it did, please mark it as safe and add hello@meridiancpd.co.uk to your contacts — this ensures your CPD certificates reach you without any issues.

─────────────────────────────

Welcome to Meridian CPD. Your annual subscription is active and the full course library is ready and waiting.

Before you dive in, a few things worth knowing from people who've been in the industry a while:

─────────────────────────────
SPREAD YOUR CPD THROUGH THE YEAR — IT MATTERS MORE THAN YOU THINK
─────────────────────────────
Accreditation bodies don't just count hours — some look at when you completed them. A portfolio showing steady engagement across the year looks far more credible than 10 hours logged in a single weekend.

We'd suggest one course every few weeks, whenever you have a quiet hour. By the end of the year your CPD record tells a story of a professional who takes their development seriously.

─────────────────────────────
DON'T RUSH TO COMPLETE EVERYTHING AT ONCE
─────────────────────────────
Each course is designed to be read properly — not skimmed. Download it, read it, mark it complete, get your certificate. Then move on. The library isn't going anywhere.

─────────────────────────────
YOUR CERTIFICATES ARRIVE INSTANTLY
─────────────────────────────
No waiting, no monthly batch. As soon as you click Mark Complete and confirm, your certificate lands in your inbox. Keep them somewhere safe — a dedicated folder works well. Your dashboard also holds a permanent record.

─────────────────────────────
START WITH WHAT'S MOST RELEVANT RIGHT NOW
─────────────────────────────
If you're actively doing retrofit assessments, start with the PAS 2035 courses. If you're a DEA dealing with the RdSAP 10 transition, start there. Use the library in the order that makes sense for your practice.

Your dashboard is always at:
{base_url}/my-cpd/dashboard

─────────────────────────────

One last thing — we occasionally develop new tools, resources, and products for energy assessors and retrofit professionals. If you'd be happy to hear about those from time to time, just let us know with one click:

Yes, keep me in the loop → {base_url}/my-cpd/consent/yes?{consent_query}

No thanks, CPD only → {base_url}/my-cpd/consent/no?{consent_query}

No hard sell, ever. Just the occasional heads-up when something genuinely useful comes along.

Welcome aboard.

Matt Davies
Meridian CPD
Stay Sharp. Stay Certified.
hello@meridiancpd.co.uk
"""
        await _send(to_email, to_name, subject, body)
        return

    subject = f"Your course is ready — {course_title}"
    consent_query = f"email={quote(to_email)}&token={consent_token(to_email)}"
    completion_section = f"""
─────────────────────────────
Once you've read the course:

→ Click here to confirm completion and receive your certificate:
{completion_link}

Your certificate will be emailed to you immediately.
─────────────────────────────""" if completion_link else """
─────────────────────────────
You already hold the certificate for this course, so this email carries no completion link.
─────────────────────────────"""

    if notes_url:
        files_section = f"""Two PDFs are attached:

• {course_id}-slides.pdf — the course. Read the slides in full.
• {course_id}-notes.pdf — the written notes that go with them, for reference and for the self-assessment questions, sources and further reading.

Save both for your records."""
    else:
        files_section = "Your course PDF is attached to this email. Download and save it for your records."

    series_section = ""
    if series_title and part and parts_total:
        series_section = f"""
This is Part {part} of {parts_total} of {series_title}. Each part is its own course with its own completion link and certificate; the other parts come in their own emails.
"""
        if held_parts:
            held = "\n".join(f"• {t}" for t in held_parts)
            one = len(held_parts) == 1
            series_section += f"""
{"One part" if one else f"{len(held_parts)} parts"} of your series {"is" if one else "are"} being updated and {"has" if one else "have"} not been sent yet:
{held}

{"It" if one else "They"} will follow by email as soon as the updated edition has been checked. Nothing more to do on your side.
"""

    body = f"""Hi {to_name},

Thank you for purchasing {course_title} (Course {course_id}).

{files_section}
{series_section}{completion_section}

Certificate details:
• CPD Hours: see course cover page
• Your certificate will be a PDF you can upload to your accreditation body
• Accreditation bodies can verify any Meridian CPD certificate at {APP_HOST}/verify

─────────────────────────────
Would you like to hear about new courses and tools from Meridian CPD? Only if you say yes:

Yes, keep me posted → {APP_URL}/my-cpd/consent/yes?{consent_query}

No thanks, just this course → {APP_URL}/my-cpd/consent/no?{consent_query}
─────────────────────────────

Questions? Reply to this email.

Matt
Meridian CPD | Stay Sharp. Stay Certified.
hello@meridiancpd.co.uk
"""

    import base64
    attachments = []
    # A deck course is two files (slides about 1.9 MB plus the notes); a PDF course is one.
    wanted = [(f"{course_id}-slides.pdf", pdf_url), (f"{course_id}-notes.pdf", notes_url)] if notes_url \
        else [(f"{course_id}.pdf", pdf_url)]
    for filename, url in wanted:
        if not url:
            continue
        content = await _fetch_pdf(url)
        if content is not None:
            attachments.append({"filename": filename, "content": base64.b64encode(content).decode()})

    await _send(to_email, to_name, subject, body, attachments or None)


async def send_certificate_email(
    to_email: str,
    to_name: str,
    cert_number: str,
    course_title: str,
    cpd_hours: float,
    cert_pdf_bytes: bytes,
):
    import base64

    subject = f"Your CPD Certificate — {cert_number}"
    body = f"""Hi {to_name},

Your CPD certificate for {course_title} is attached.

Certificate number: {cert_number}
CPD hours: {cpd_hours}
Verified at: {APP_URL}/verify/{cert_number}

Keep this certificate — you can upload it to your accreditation body as evidence of CPD completion. Your accreditation body can independently verify the certificate number at the link above.

Matt
Meridian CPD | Stay Sharp. Stay Certified.
"""

    attachments = [{
        "filename": f"Meridian-CPD-Certificate-{cert_number}.pdf",
        "content": base64.b64encode(cert_pdf_bytes).decode(),
    }]

    await _send(to_email, to_name, subject, body, attachments)


async def send_new_course_notification(
    to_email: str,
    to_name: str,
    course_id: str,
    course_title: str,
    cpd_hours: float,
):
    """Notify a subscriber that a new course has been added to the library."""
    subject = f"New CPD course available — {course_title}"
    body = f"""Hi {to_name},

A new course has just been added to your Meridian CPD library.

{course_title}
{cpd_hours:g} CPD Hour{'s' if cpd_hours != 1 else ''} | Course {course_id}

As a subscriber, this course is included in your plan at no extra cost.

Access it now: {APP_URL}/my-cpd

Once you've read the course, use the completion link to receive your CPD certificate immediately.

Matt
Meridian CPD | Stay Sharp. Stay Certified.
hello@meridiancpd.co.uk
"""
    await _send(to_email, to_name, subject, body)


async def send_unsubscribe_goodbye_email(to_email: str):
    """Confirmation email after a successful unsubscribe."""
    subject = "Removed from Meridian CPD emails"
    body = """Hi,

As requested, we've removed your address from all future Meridian CPD marketing emails.

You won't hear from us again.

If you change your mind at any point, you're always welcome back at meridiancpd.co.uk.

Matt Davies
Meridian CPD
hello@meridiancpd.co.uk
"""
    await _send(to_email, "", subject, body)


async def send_admin_new_course_alert(
    course_id: str,
    course_title: str,
    cpd_hours: float,
    subscriber_count: int,
):
    """Alert Matt and Ceri that a new course has been published."""
    subject = f"[Meridian CPD] New course published — {course_id}"
    body = f"""New course published automatically by the content engine.

Course ID:    {course_id}
Title:        {course_title}
CPD Hours:    {cpd_hours:g}
Notified:     {subscriber_count} subscriber{'s' if subscriber_count != 1 else ''}

View in admin: {APP_URL}/admin

— Meridian CPD Content Engine
"""
    admin_recipients = [
        ("mattid272@gmail.com", "Matt"),
        ("ceri@docsurveying.co.uk", "Ceri"),
    ]
    for email, name in admin_recipients:
        await _send(email, name, subject, body)
