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
    """Convert course markdown to a branded PDF using ReportLab."""
    md_path = COURSES_DIR / course_id / f"{course_id}.md"
    if not md_path.exists():
        raise FileNotFoundError(f"Markdown not found: {md_path}")

    content = md_path.read_text(encoding="utf-8")

    # Parse title and metadata from first lines
    lines = content.split("\n")
    title = lines[0].lstrip("# ").strip()

    # Extract CPD hours
    cpd_hours = 1.0
    for line in lines[:5]:
        match = re.search(r"CPD Hours:\*\*\s*([\d.]+)", line)
        if match:
            cpd_hours = float(match.group(1))
            break

    # Build PDF using ReportLab
    import io
    from reportlab.lib.pagesizes import A4
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.units import mm
    from reportlab.platypus import (
        SimpleDocTemplate, Paragraph, Spacer, HRFlowable, PageBreak
    )
    from reportlab.lib import colors
    from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_JUSTIFY

    NAVY = colors.HexColor("#0f2547")
    CYAN = colors.HexColor("#0891b2")
    LIGHT_BG = colors.HexColor("#f8fafc")

    buf = io.BytesIO()
    doc = SimpleDocTemplate(
        buf,
        pagesize=A4,
        leftMargin=20*mm,
        rightMargin=20*mm,
        topMargin=25*mm,
        bottomMargin=20*mm,
        title=f"Meridian CPD — {title}",
        author="Meridian CPD",
    )

    styles = getSampleStyleSheet()

    style_h1 = ParagraphStyle(
        "H1", fontSize=20, fontName="Helvetica-Bold",
        textColor=NAVY, spaceAfter=6, alignment=TA_LEFT,
    )
    style_h2 = ParagraphStyle(
        "H2", fontSize=14, fontName="Helvetica-Bold",
        textColor=NAVY, spaceBefore=12, spaceAfter=4, alignment=TA_LEFT,
    )
    style_h3 = ParagraphStyle(
        "H3", fontSize=11, fontName="Helvetica-Bold",
        textColor=NAVY, spaceBefore=8, spaceAfter=3,
    )
    style_body = ParagraphStyle(
        "Body", fontSize=10, fontName="Helvetica",
        leading=15, spaceAfter=6, alignment=TA_JUSTIFY,
    )
    style_bullet = ParagraphStyle(
        "Bullet", fontSize=10, fontName="Helvetica",
        leading=14, spaceAfter=3, leftIndent=12,
        bulletIndent=0,
    )
    style_meta = ParagraphStyle(
        "Meta", fontSize=9, fontName="Helvetica",
        textColor=colors.HexColor("#666666"), spaceAfter=12,
    )
    style_footer = ParagraphStyle(
        "Footer", fontSize=7, fontName="Helvetica",
        textColor=colors.HexColor("#999999"), alignment=TA_CENTER,
    )

    story = []

    # Header block
    story.append(Paragraph(title, style_h1))

    # Parse and flow content
    in_list = False
    for line in lines[1:]:
        stripped = line.strip()

        if stripped.startswith("# "):
            story.append(Paragraph(stripped[2:], style_h1))
        elif stripped.startswith("## "):
            story.append(HRFlowable(width="100%", thickness=1, color=CYAN, spaceAfter=4))
            story.append(Paragraph(stripped[3:], style_h2))
        elif stripped.startswith("### "):
            story.append(Paragraph(stripped[4:], style_h3))
        elif stripped.startswith("- ") or stripped.startswith("• "):
            text = stripped[2:].strip()
            story.append(Paragraph(f"• {text}", style_bullet))
        elif stripped.startswith("**") and stripped.endswith("**"):
            story.append(Paragraph(
                f"<b>{stripped[2:-2]}</b>", style_body
            ))
        elif stripped.startswith("*") and stripped.endswith("*") and len(stripped) > 2:
            story.append(Paragraph(
                f"<i>{stripped[1:-1]}</i>", style_meta
            ))
        elif stripped.startswith("---"):
            story.append(HRFlowable(width="100%", thickness=0.5,
                                     color=colors.HexColor("#cccccc"), spaceAfter=6))
        elif stripped == "":
            story.append(Spacer(1, 4))
        else:
            # Convert inline markdown bold
            formatted = re.sub(r"\*\*(.+?)\*\*", r"<b>\1</b>", stripped)
            formatted = re.sub(r"\*(.+?)\*", r"<i>\1</i>", formatted)
            story.append(Paragraph(formatted, style_body))

    # Footer
    story.append(Spacer(1, 10))
    story.append(HRFlowable(width="100%", thickness=0.5,
                             color=colors.HexColor("#cccccc")))
    story.append(Paragraph(
        f"© Meridian CPD 2026  •  meridiancpd.co.uk  •  {course_id}  •  {cpd_hours:g} CPD Hour{'s' if cpd_hours != 1 else ''}",
        style_footer,
    ))

    doc.build(story)
    buf.seek(0)
    return buf.read()


# ── Supabase upload ───────────────────────────────────────────────────────────

def upload_pdf(course_id: str, pdf_bytes: bytes) -> str:
    """Upload PDF to Supabase Storage and return public URL."""
    filename = f"{course_id}.pdf"
    bucket = "courses"

    # Upload (upsert)
    result = supabase.storage.from_(bucket).upload(
        filename,
        pdf_bytes,
        file_options={"content-type": "application/pdf", "upsert": "true"},
    )

    # Return public URL
    url_result = supabase.storage.from_(bucket).get_public_url(filename)
    return url_result


# ── Subscriber notification ───────────────────────────────────────────────────

def notify_subscribers(course_id: str, title: str, cpd_hours: float, pdf_url: str):
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
    from email_sender import send_new_course_notification

    async def send_all():
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
    notify_subscribers(course_id, title, cpd_hours, pdf_url)

    print(f"\n  {course_id} published successfully.")


if __name__ == "__main__":
    main()
