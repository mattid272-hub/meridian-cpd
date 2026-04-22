"""Resend email sender for Meridian CPD."""
import os

import httpx

RESEND_API = "https://api.resend.com/emails"
FROM_EMAIL = "hello@meridiancpd.co.uk"
FROM_NAME = "Meridian CPD"
# Until domain is verified in Resend, use onboarding@resend.dev for testing
# After domain verification, switch back to hello@meridiancpd.co.uk


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


async def send_course_email(
    to_email: str,
    to_name: str,
    course_title: str,
    course_id: str,
    pdf_url: str | None,
    completion_link: str | None,
    is_subscription: bool = False,
):
    if is_subscription:
        subject = "Welcome to Meridian CPD — a few things worth knowing"
        base_url = os.environ.get("BASE_URL", "https://app.meridiancpd.co.uk")
        body = f"""Hi {to_name},

⚠ QUICK NOTE: This email may have landed in your junk or spam folder. If it did, please mark it as safe and add hello@meridiancpd.co.uk to your contacts — this ensures your CPD certificates reach you without any issues.

─────────────────────────────

Welcome to Meridian CPD. Your annual subscription is active and your full library of 26 courses is ready and waiting.

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

Yes, keep me in the loop → {base_url}/my-cpd/consent/yes?email={to_email}

No thanks, CPD only → {base_url}/my-cpd/consent/no?email={to_email}

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
    completion_section = f"""
─────────────────────────────
Once you've read the course:

→ Click here to confirm completion and receive your certificate:
{completion_link}

Your certificate will be emailed to you immediately.
─────────────────────────────""" if completion_link else ""

    body = f"""Hi {to_name},

Thank you for purchasing {course_title} (Course {course_id}).

Your course PDF is attached to this email. Download and save it for your records.
{completion_section}

Certificate details:
• CPD Hours: see course cover page
• Your certificate will be a PDF you can upload to your accreditation body
• Accreditation bodies can verify any Meridian CPD certificate at meridiancpd.co.uk/verify

Questions? Reply to this email.

Matt
Meridian CPD | Stay Sharp. Stay Certified.
hello@meridiancpd.co.uk
"""

    attachments = []
    if pdf_url:
        async with httpx.AsyncClient() as client:
            r = await client.get(pdf_url, timeout=30)
            if r.status_code == 200:
                import base64
                attachments.append({
                    "filename": f"{course_id}.pdf",
                    "content": base64.b64encode(r.content).decode(),
                })

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
Verified at: https://meridiancpd.co.uk/verify/{cert_number}

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

Access it now: https://app.meridiancpd.co.uk/my-cpd

Once you've read the course, use the completion link to receive your CPD certificate immediately.

Matt
Meridian CPD | Stay Sharp. Stay Certified.
hello@meridiancpd.co.uk
"""
    await _send(to_email, to_name, subject, body)


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

View in admin: https://app.meridiancpd.co.uk/admin
Course PDF:   https://app.meridiancpd.co.uk/courses/{course_id}

— Meridian CPD Content Engine
"""
    admin_recipients = [
        ("mattid272@gmail.com", "Matt"),
        ("ceri@docsurveying.co.uk", "Ceri"),
    ]
    for email, name in admin_recipients:
        await _send(email, name, subject, body)
