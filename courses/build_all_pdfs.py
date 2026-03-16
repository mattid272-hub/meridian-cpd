"""
Build PDFs for all courses in the courses/ directory.
Run once to generate PDFs from the existing markdown files.

Usage:  python3 build_all_pdfs.py
"""
import re
import sys
import io
from pathlib import Path

ROOT = Path(__file__).parent

try:
    from reportlab.lib.pagesizes import A4
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.units import mm
    from reportlab.platypus import (
        SimpleDocTemplate, Paragraph, Spacer, HRFlowable,
    )
    from reportlab.lib import colors
    from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_JUSTIFY
except ImportError:
    print("Install reportlab: pip3 install reportlab")
    sys.exit(1)

NAVY = colors.HexColor("#0f2547")
CYAN = colors.HexColor("#0891b2")


def build_pdf(course_id: str, md_content: str) -> bytes:
    lines = md_content.split("\n")
    title = lines[0].lstrip("# ").strip()

    cpd_hours = 1.0
    for line in lines[:5]:
        m = re.search(r"CPD Hours:\*\*\s*([\d.]+)", line)
        if m:
            cpd_hours = float(m.group(1))
            break

    buf = io.BytesIO()
    doc = SimpleDocTemplate(
        buf, pagesize=A4,
        leftMargin=22*mm, rightMargin=22*mm,
        topMargin=22*mm, bottomMargin=20*mm,
        title=f"Meridian CPD — {title}",
        author="Meridian CPD",
    )

    style_h1 = ParagraphStyle("H1", fontSize=18, fontName="Helvetica-Bold",
        textColor=NAVY, spaceAfter=6)
    style_h2 = ParagraphStyle("H2", fontSize=13, fontName="Helvetica-Bold",
        textColor=NAVY, spaceBefore=10, spaceAfter=3)
    style_h3 = ParagraphStyle("H3", fontSize=11, fontName="Helvetica-Bold",
        textColor=NAVY, spaceBefore=6, spaceAfter=2)
    style_body = ParagraphStyle("Body", fontSize=10, fontName="Helvetica",
        leading=15, spaceAfter=5, alignment=TA_JUSTIFY)
    style_bullet = ParagraphStyle("Bullet", fontSize=10, fontName="Helvetica",
        leading=14, spaceAfter=2, leftIndent=10)
    style_meta = ParagraphStyle("Meta", fontSize=8.5, fontName="Helvetica",
        textColor=colors.HexColor("#777777"), spaceAfter=10)
    style_footer = ParagraphStyle("Footer", fontSize=7, fontName="Helvetica",
        textColor=colors.HexColor("#999999"), alignment=TA_CENTER)

    story = []

    for i, line in enumerate(lines):
        stripped = line.strip()
        if i == 0:
            story.append(Paragraph(stripped.lstrip("# "), style_h1))
            story.append(HRFlowable(width="100%", thickness=2,
                                     color=CYAN, spaceAfter=6))
        elif stripped.startswith("## "):
            story.append(Spacer(1, 2))
            story.append(Paragraph(stripped[3:], style_h2))
            story.append(HRFlowable(width="100%", thickness=0.8,
                                     color=CYAN, spaceAfter=2))
        elif stripped.startswith("### "):
            story.append(Paragraph(stripped[4:], style_h3))
        elif stripped.startswith("- ") or stripped.startswith("• "):
            text = stripped[2:].strip()
            text = re.sub(r"\*\*(.+?)\*\*", r"<b>\1</b>", text)
            story.append(Paragraph(f"• &nbsp;{text}", style_bullet))
        elif stripped.startswith("---"):
            story.append(HRFlowable(width="100%", thickness=0.4,
                                     color=colors.HexColor("#cccccc"),
                                     spaceAfter=4, spaceBefore=4))
        elif stripped == "":
            story.append(Spacer(1, 3))
        elif stripped.startswith("*") and stripped.endswith("*"):
            inner = stripped.strip("*")
            formatted = re.sub(r"\*\*(.+?)\*\*", r"<b>\1</b>", inner)
            story.append(Paragraph(f"<i>{formatted}</i>", style_meta))
        else:
            formatted = re.sub(r"\*\*(.+?)\*\*", r"<b>\1</b>", stripped)
            formatted = re.sub(r"\*(.+?)\*", r"<i>\1</i>", formatted)
            story.append(Paragraph(formatted, style_body))

    story.append(Spacer(1, 8))
    story.append(HRFlowable(width="100%", thickness=0.5,
                             color=colors.HexColor("#cccccc")))
    story.append(Paragraph(
        f"© Meridian CPD 2026  •  meridiancpd.co.uk  •  {course_id}  •  "
        f"{cpd_hours:g} CPD Hour{'s' if cpd_hours != 1 else ''}",
        style_footer,
    ))

    doc.build(story)
    buf.seek(0)
    return buf.read()


def main():
    course_dirs = sorted(ROOT.iterdir())
    built = 0
    skipped = 0

    for d in course_dirs:
        if not d.is_dir() or d.name.startswith("."):
            continue
        md_files = list(d.glob("*.md"))
        if not md_files:
            continue
        course_id = d.name
        md_path = md_files[0]
        pdf_path = d / f"{course_id}.pdf"

        if pdf_path.exists():
            print(f"  Skip (exists): {course_id}.pdf")
            skipped += 1
            continue

        print(f"  Building: {course_id}.pdf ...")
        content = md_path.read_text(encoding="utf-8")
        pdf_bytes = build_pdf(course_id, content)
        pdf_path.write_bytes(pdf_bytes)
        print(f"    → {len(pdf_bytes):,} bytes")
        built += 1

    print(f"\nDone. Built {built} PDFs, skipped {skipped} (already existed).")


if __name__ == "__main__":
    main()
