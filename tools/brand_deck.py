"""
Meridian CPD — Add the Meridian footer band to a NotebookLM slide-deck PDF.

Takes the PDF that NotebookLM exports (More → Download PDF Document) and stamps every page
with a dark-green band along the bottom carrying the course ID, version, date, the copyright
line and a disclosure that the visuals were generated with NotebookLM from Meridian's checked
course text. The band sits on the left; the small "Gemini Notebook" badge in the bottom-right
corner is left visible by default, because Google's Terms of Service say not to remove, obscure
or alter Google's branding or legal notices, and not to mislead others into thinking generative
AI content was created by a human. Pass --cover-badge only if Matt has decided otherwise.

Usage:
    python3 tools/brand_deck.py "Insulation Part 1.pdf" MER-ALL-019 --version v4 \
        --out courses/MER-ALL-019/MER-ALL-019-deck.pdf
    python3 tools/brand_deck.py deck.pdf MER-ALL-019 --version v4 --date "October 2026"

The output is what tools/upload_deck.py sends to Supabase as {id}-deck.pdf.
"""
import argparse
import io
import re
from datetime import date
from pathlib import Path

from pypdf import PdfReader, PdfWriter, Transformation
from reportlab.lib.colors import HexColor
from reportlab.pdfgen import canvas

DARK = HexColor("#0D1F0E")
LIME = HexColor("#D4FF00")
WHITE = HexColor("#FFFFFF")
MUTED = HexColor("#8A9E8B")
COURSE_ID_RE = re.compile(r"^MER-[A-Z]{2,4}-\d{3}$")

COPYRIGHT = "© Meridian CPD {year}. All rights reserved."
DISCLOSURE = "Visuals generated with Google NotebookLM from Meridian's checked course text; checked slide by slide."


def band_overlay(width: float, height: float, course_id: str, version: str, when: str,
                 cover_badge: bool) -> bytes:
    """One page of overlay, sized to the slide, with the footer band drawn on it."""
    buf = io.BytesIO()
    c = canvas.Canvas(buf, pagesize=(width, height))
    band_h = (height * 0.052) if cover_badge else (height / 1.052 * 0.052)  # the strip added below
    band_w = width  # full width: in extend mode nothing on the slide is covered
    c.setFillColor(DARK)
    c.rect(0, 0, band_w, band_h, stroke=0, fill=1)
    c.setFillColor(LIME)
    c.rect(0, band_h, band_w, 1.2, stroke=0, fill=1)  # lime hairline on top of the band

    pad = width * 0.018
    big = band_h * 0.40
    small = band_h * 0.26
    c.setFillColor(WHITE)
    c.setFont("Helvetica-Bold", big)
    c.drawString(pad, band_h * 0.50, f"MERIDIAN CPD  ·  {course_id}  ·  {version}  ·  {when}")
    c.setFillColor(MUTED)
    c.setFont("Helvetica", small)
    c.drawString(pad, band_h * 0.17, COPYRIGHT.format(year=date.today().year) + "   " + DISCLOSURE)
    c.showPage()
    c.save()
    return buf.getvalue()


def brand(src: Path, out: Path, course_id: str, version: str, when: str, cover_badge: bool) -> int:
    """The band is added below the slide, not over it: the page grows by the band's height, so
    no slide content is ever hidden. With --cover-badge the band also runs full width over the
    slide's bottom edge, which is the only mode that hides anything."""
    reader = PdfReader(str(src))
    writer = PdfWriter()
    for page in reader.pages:
        w = float(page.mediabox.width)
        h = float(page.mediabox.height)
        band_h = h * 0.052
        if cover_badge:
            overlay = PdfReader(io.BytesIO(band_overlay(w, h, course_id, version, when, True)))
            page.merge_page(overlay.pages[0])
            writer.add_page(page)
            continue
        new_h = h + band_h
        base = writer.add_blank_page(width=w, height=new_h)
        base.merge_transformed_page(page, Transformation().translate(0, band_h))
        overlay = PdfReader(io.BytesIO(band_overlay(w, new_h, course_id, version, when, False)))
        base.merge_page(overlay.pages[0])
    writer.add_metadata({
        "/Title": f"{course_id} {version}",
        "/Author": "Meridian CPD",
        "/Producer": "Meridian CPD",
    })
    out.parent.mkdir(parents=True, exist_ok=True)
    with out.open("wb") as fh:
        writer.write(fh)
    return len(reader.pages)


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("pdf", help="the NotebookLM PDF export")
    ap.add_argument("course_id", help="for example MER-ALL-019")
    ap.add_argument("--version", default="v1", help="deck version as checked, for example v4")
    ap.add_argument("--date", default=date.today().strftime("%B %Y"), help='for example "October 2026"')
    ap.add_argument("--out", help="output path (default courses/<id>/<id>-deck.pdf)")
    ap.add_argument("--cover-badge", action="store_true",
                    help="run the band the full width, covering the Gemini badge (Matt's decision)")
    args = ap.parse_args()

    if not COURSE_ID_RE.match(args.course_id):
        raise SystemExit(f"Course ID should look like MER-ALL-019, not {args.course_id}")
    src = Path(args.pdf)
    if not src.is_file() or not src.read_bytes().startswith(b"%PDF"):
        raise SystemExit(f"Not a PDF: {src}")
    out = Path(args.out) if args.out else Path("courses") / args.course_id / f"{args.course_id}-deck.pdf"
    n = brand(src, out, args.course_id, args.version, args.date, args.cover_badge)
    print(f"{n} pages → {out}")


if __name__ == "__main__":
    main()
