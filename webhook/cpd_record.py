"""The member's CPD record for one calendar year as a PDF: one page (or more) listing
every certificate of completion issued to them that year, for the member to hand to
their scheme. Drawn with reportlab like the certificates; pure function, no database:
main.py passes in the member's own certificates, already filtered to the year."""
import io
from datetime import datetime

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import mm
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle

from settings import APP_URL

DARK = colors.HexColor("#0D1F0E")
LIME = colors.HexColor("#D4FF00")
DEEP_LIME = colors.HexColor("#6A8C00")
GREY = colors.HexColor("#5C6B5D")
LINE = colors.HexColor("#D8DCCD")
BAND = colors.HexColor("#F5F5F0")

SCHEME_LINE = "Check your own scheme's CPD rules."


def _date(iso: str) -> str:
    s = str(iso or "")[:10]
    try:
        return datetime.strptime(s, "%Y-%m-%d").strftime("%-d %B %Y")
    except ValueError:
        return s


def _hours(h) -> str:
    return f"{float(h or 0):g}"


def generate_cpd_record(member_name: str, year: int, certificates: list[dict]) -> bytes:
    """certificates: the member's own rows for `year`, each with course_title, course_id,
    issued_at, cpd_hours and cert_number. Returns the PDF bytes."""
    buf = io.BytesIO()
    doc = SimpleDocTemplate(buf, pagesize=A4, leftMargin=16 * mm, rightMargin=16 * mm, topMargin=34 * mm,
                            bottomMargin=20 * mm, title=f"CPD record {year}", author="Meridian CPD")
    body = ParagraphStyle("b", fontName="Helvetica", fontSize=9, leading=12, textColor=DARK)
    small = ParagraphStyle("s", parent=body, fontSize=7.5, leading=10, textColor=GREY)
    head = ParagraphStyle("h", parent=body, fontName="Helvetica-Bold", fontSize=8, textColor=colors.white)
    title = ParagraphStyle("t", parent=body, fontName="Helvetica-Bold", fontSize=18, leading=22)
    sub = ParagraphStyle("u", parent=body, fontSize=10.5, leading=15)

    rows = sorted(certificates, key=lambda c: str(c.get("issued_at") or ""))
    total = sum(float(c.get("cpd_hours") or 0) for c in rows)
    esc = lambda s: str(s or "").replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")

    story = [
        Paragraph(f"CPD record {year}", title),
        Spacer(1, 4),
        Paragraph(f"<b>{esc(member_name)}</b>", sub),
        Paragraph(f"Certificates of completion issued by Meridian CPD between 1 January and 31 December {year}.", sub),
        Spacer(1, 10),
    ]
    data = [[Paragraph(h, head) for h in ("Course", "Completed", "CPD hours", "Certificate number", "Verify")]]
    for c in rows:
        number = str(c.get("cert_number") or "")
        url = f"{APP_URL}/verify/{number}"
        data.append([
            Paragraph(f"{esc(c.get('course_title'))}<br/><font color='#5C6B5D' size='7.5'>{esc(c.get('course_id'))}</font>", body),
            Paragraph(esc(_date(c.get("issued_at"))), body),
            Paragraph(_hours(c.get("cpd_hours")), body),
            Paragraph(f"<font name='Courier-Bold'>{esc(number)}</font>", body),
            Paragraph(f"<link href='{esc(url)}' color='#6A8C00'>{esc(url.split('://', 1)[-1])}</link>", small),
        ])
    if not rows:
        data.append([Paragraph(f"No certificates of completion in {year}.", body), "", "", "", ""])
    data.append([Paragraph("<b>Total</b>", body), "", Paragraph(f"<b>{_hours(total)}</b>", body), "", ""])

    table = Table(data, colWidths=[64 * mm, 26 * mm, 18 * mm, 32 * mm, 38 * mm], repeatRows=1)
    style = [
        ("BACKGROUND", (0, 0), (-1, 0), DARK),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("TOPPADDING", (0, 0), (-1, -1), 6),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
        ("LINEBELOW", (0, 1), (-1, -2), 0.5, LINE),
        ("BACKGROUND", (0, -1), (-1, -1), BAND),
        ("LINEABOVE", (0, -1), (-1, -1), 1, DEEP_LIME),
    ]
    if not rows:
        style.append(("SPAN", (0, 1), (-1, 1)))
    table.setStyle(TableStyle(style))
    story += [table, Spacer(1, 14),
              Paragraph("Each certificate carries its own number. Anyone can check one at the verify address beside it.", body),
              Spacer(1, 6), Paragraph(f"<b>{SCHEME_LINE}</b>", body)]

    def frame(c, d):
        w, h = A4
        c.saveState()
        c.setFillColor(DARK)
        c.rect(0, h - 24 * mm, w, 24 * mm, fill=1, stroke=0)
        c.setFillColor(LIME)
        c.rect(0, h - 25.2 * mm, w, 1.2 * mm, fill=1, stroke=0)
        c.setFillColor(colors.white)
        c.setFont("Helvetica-Bold", 17)
        c.drawString(16 * mm, h - 15 * mm, "MERIDIAN")
        x = 16 * mm + c.stringWidth("MERIDIAN ", "Helvetica-Bold", 17)
        c.setFillColor(LIME)
        c.rect(x - 1, h - 16.6 * mm, c.stringWidth("CPD", "Helvetica-Bold", 17) + 4, 6.4 * mm, fill=1, stroke=0)
        c.setFillColor(DARK)
        c.drawString(x + 1, h - 15 * mm, "CPD")
        c.setFillColor(colors.white)
        c.setFont("Helvetica", 9)
        c.drawRightString(w - 16 * mm, h - 15 * mm, f"CPD record {year}")
        c.setFillColor(GREY)
        c.setFont("Helvetica", 7.5)
        c.drawString(16 * mm, 10 * mm, "Meridian CPD · meridiancpd.co.uk · hello@meridiancpd.co.uk · "
                     "FistralAI Ltd (company no. 17091704) trading as Meridian CPD")
        c.drawRightString(w - 16 * mm, 10 * mm, f"Page {d.page}")
        c.restoreState()

    doc.build(story, onFirstPage=frame, onLaterPages=frame)
    return buf.getvalue()
