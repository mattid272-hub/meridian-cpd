"""
Meridian CPD — Course Publisher

Takes a course ID, converts the markdown to a branded PDF,
uploads it to Supabase Storage, and emails all active subscribers.

Usage: python3 course_publisher.py MER-ALL-100
"""
import os
import re
import sys
from pathlib import Path

import httpx
from supabase import create_client

ROOT = Path(__file__).parent.parent
COURSES_DIR = ROOT / "courses"

supabase = create_client(
    os.environ["SUPABASE_URL"],
    os.environ["SUPABASE_SERVICE_ROLE_KEY"],
)


# ── PDF builder ───────────────────────────────────────────────────────────────

def build_pdf(course_id: str) -> bytes:
    """Convert course markdown to a branded PDF using the v2 builder."""
    md_path = COURSES_DIR / course_id / f"{course_id}.md"
    if not md_path.exists():
        raise FileNotFoundError(f"Markdown not found: {md_path}")

    content = md_path.read_text(encoding="utf-8")

    # Delegate entirely to the v2 branded builder
    import sys
    sys.path.insert(0, str(COURSES_DIR))
    from build_pdfs_v2 import build_pdf as _build_pdf_v2
    return _build_pdf_v2(course_id, content)


# ── Supabase upload ───────────────────────────────────────────────────────────

def upload_pdf(course_id: str, pdf_bytes: bytes) -> str:
    """Upload PDF to Supabase Storage and return public URL."""
    filename = f"{course_id}.pdf"
    bucket = "courses"

    # Upload (upsert)
    supabase.storage.from_(bucket).upload(
        filename,
        pdf_bytes,
        file_options={"content-type": "application/pdf", "upsert": "true"},
    )

    # Return public URL
    url_result = supabase.storage.from_(bucket).get_public_url(filename)
    return url_result


# ── Subscriber notification ───────────────────────────────────────────────────

def notify_subscribers(course_id: str, title: str, cpd_hours: float):
    """Email all active subscribers to let them know a new course is available."""
    # Get all subscription members
    result = supabase.table("members").select("email, name").eq(
        "plan", "subscription"
    ).execute()

    if not result.data:
        print("  No subscribers to notify.")
        return

    print(f"  Notifying {len(result.data)} subscribers...")

    # Send via Gmail API
    import asyncio
    import sys
    sys.path.insert(0, str(ROOT / "webhook"))
    from email_sender import send_new_course_notification, send_admin_new_course_alert

    async def send_all():
        # Notify subscribers
        for member in result.data:
            try:
                await send_new_course_notification(
                    to_email=member["email"],
                    to_name=member["name"] or "there",
                    course_id=course_id,
                    course_title=title,
                    cpd_hours=cpd_hours,
                )
            except Exception as e:
                print(f"    Failed to notify {member['email']}: {e}")

        # Alert admins (Matt + Ceri)
        try:
            await send_admin_new_course_alert(
                course_id=course_id,
                course_title=title,
                cpd_hours=cpd_hours,
                subscriber_count=len(result.data),
            )
            print("  Admin alert sent to Matt and Ceri.")
        except Exception as e:
            print(f"  Admin alert failed: {e}")

    asyncio.run(send_all())
    print(f"  Notifications sent.")


# ── Main ─────────────────────────────────────────────────────────────────────

def main():
    if len(sys.argv) < 2:
        print("Usage: python3 course_publisher.py <COURSE_ID>")
        sys.exit(1)

    course_id = sys.argv[1]
    print(f"\nPublishing {course_id}...")

    # Build PDF
    print("  Building PDF...")
    pdf_bytes = build_pdf(course_id)
    print(f"  PDF built: {len(pdf_bytes):,} bytes")

    # Save locally too
    local_pdf = COURSES_DIR / course_id / f"{course_id}.pdf"
    local_pdf.write_bytes(pdf_bytes)
    print(f"  Saved locally: {local_pdf}")

    # Upload to Supabase Storage
    print("  Uploading to Supabase Storage...")
    pdf_url = upload_pdf(course_id, pdf_bytes)
    print(f"  Public URL: {pdf_url}")

    # Read course title from markdown
    md_path = COURSES_DIR / course_id / f"{course_id}.md"
    content = md_path.read_text(encoding="utf-8")
    title = content.split("\n")[0].lstrip("# ").strip()
    cpd_hours = 1.0
    for line in content.split("\n")[:5]:
        match = re.search(r"CPD Hours:\*\*\s*([\d.]+)", line)
        if match:
            cpd_hours = float(match.group(1))

    # Notify subscribers
    notify_subscribers(course_id, title, cpd_hours)

    print(f"\n  {course_id} published successfully.")


if __name__ == "__main__":
    main()
