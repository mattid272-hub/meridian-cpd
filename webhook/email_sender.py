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
        subject = "Welcome to Meridian CPD — your subscription is active"
        body = f"""Hi {to_name},

Your Meridian CPD annual subscription is now active.

You have unlimited access to our full course library. Browse all available courses and start logging your CPD hours today.

Visit your library: https://meridiancpd.co.uk/library

When you complete each course, you'll receive a CPD certificate immediately — just click the completion link at the end of each course.

Any questions? Reply to this email.

Matt
Meridian CPD | Stay Sharp. Stay Certified.
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

Access it now: https://meridiancpd.co.uk/library

Once you've read the course, use the completion link to receive your CPD certificate immediately.

Matt
Meridian CPD | Stay Sharp. Stay Certified.
hello@meridiancpd.co.uk
"""
    await _send(to_email, to_name, subject, body)
