"""
Meridian CPD — Certificate Generator (v2)

Generates polished, tamper-resistant PDF certificates with:
- Logo drawn via ReportLab primitives (no file dependency)
- Unique certificate number + QR verification
- Subtle diagonal watermark
- Shadow effects for depth
- Seren Surveying / RetroTrack imprint
- © Meridian CPD branding
"""
import io
import os
from datetime import datetime

import qrcode
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.pdfgen import canvas
from reportlab.lib.utils import ImageReader


# ── Brand palette ──────────────────────────────────────────────────────────────
NAVY      = (15/255,  37/255,  71/255)   # #0f2547
CYAN      = (8/255,  145/255, 178/255)   # #0891b2
CYAN_DARK = (6/255,  110/255, 140/255)   # deeper cyan for shadow
WHITE     = (1.0, 1.0, 1.0)
CREAM     = (0.98, 0.985, 0.995)         # near-white background
LIGHT_BG  = (0.94, 0.96, 0.98)          # detail-band fill
MID_GREY  = (0.50, 0.50, 0.50)
SOFT_GREY = (0.60, 0.62, 0.65)          # subtle text
SHADOW    = (0.75, 0.78, 0.82)          # shadow colour

BASE_URL = os.environ.get("BASE_URL", "https://meridiancpd.co.uk")


# ── Logo drawing (all primitives — no file dependency) ─────────────────────────

def _draw_meridian_logo(c, x, y, icon_r: float, on_dark: bool = True):
    """
    Draw the Meridian CPD logo.
    x, y  — centre of the compass icon
    icon_r — radius of the compass circle in points
    on_dark — True = white wordmark (for header), False = navy wordmark
    """
    text_colour = WHITE if on_dark else NAVY

    # ── Compass circle ──────────────────────────────────────────────────────
    c.setStrokeColorRGB(*WHITE if on_dark else NAVY)
    c.setLineWidth(2.2)
    c.setFillColorRGB(0, 0, 0)  # dummy — no fill
    c.circle(x, y, icon_r, fill=0, stroke=1)

    # Meridian vertical line
    c.setLineWidth(1.8)
    c.line(x, y + icon_r, x, y - icon_r)

    # Faint horizontal axis
    c.setStrokeColorRGB(*(0.85, 0.90, 0.95) if on_dark else (0.55, 0.60, 0.68))
    c.setLineWidth(0.9)
    c.line(x - icon_r, y, x + icon_r, y)

    # Cyan arc (the meridian curve) — quadratic Q(cx+0.65r, cy) -> endpoint
    p0x, p0y = x, y + icon_r
    endx, endy = x, y - icon_r
    qx = x + icon_r * 0.68
    qy = y
    # Quad → cubic conversion
    c1x = p0x + 2/3 * (qx - p0x)
    c1y = p0y + 2/3 * (qy - p0y)
    c2x = endx + 2/3 * (qx - endx)
    c2y = endy + 2/3 * (qy - endy)
    c.setStrokeColorRGB(*CYAN)
    c.setLineWidth(2.2)
    path = c.beginPath()
    path.moveTo(p0x, p0y)
    path.curveTo(c1x, c1y, c2x, c2y, endx, endy)
    c.drawPath(path, stroke=1, fill=0)

    # North/south terminal dots
    c.setFillColorRGB(*WHITE if on_dark else NAVY)
    c.circle(x, y + icon_r, 2.5, fill=1, stroke=0)
    c.circle(x, y - icon_r, 2.5, fill=1, stroke=0)

    # Centre dot (cyan)
    c.setFillColorRGB(*CYAN)
    c.circle(x, y, 3.5, fill=1, stroke=0)

    # ── Wordmark ────────────────────────────────────────────────────────────
    word_x = x + icon_r + 7
    word_y_top = y + icon_r * 0.42

    c.setFillColorRGB(*text_colour)
    c.setFont("Helvetica-Bold", 22)
    c.drawString(word_x, word_y_top, "MERIDIAN")

    # CPD badge
    badge_w = 36
    badge_h = 14
    badge_x = word_x
    badge_y = word_y_top - 19

    # Shadow behind badge
    c.setFillColorRGB(*CYAN_DARK)
    c.roundRect(badge_x + 1.5, badge_y - 1.5, badge_w, badge_h, 2.5, fill=1, stroke=0)

    c.setFillColorRGB(*CYAN)
    c.roundRect(badge_x, badge_y, badge_w, badge_h, 2.5, fill=1, stroke=0)
    c.setFillColorRGB(*WHITE)
    c.setFont("Helvetica-Bold", 10)
    c.drawCentredString(badge_x + badge_w / 2, badge_y + 3.5, "CPD")


# ── Watermark ──────────────────────────────────────────────────────────────────

def _draw_watermark(c, width, height):
    c.saveState()
    c.setFont("Helvetica", 8)
    c.setFillColorRGB(0.91, 0.935, 0.955)
    c.rotate(45)
    text = "MERIDIAN CPD  •  STAY SHARP. STAY CERTIFIED.  •  "
    for x in range(-int(height), int(width + height), 130):
        for y in range(-int(width), int(height + width), 28):
            c.drawString(x, y, text)
    c.restoreState()


# ── Decorative border ──────────────────────────────────────────────────────────

def _draw_border(c, width, height):
    c.setStrokeColorRGB(*NAVY)
    c.setLineWidth(2.5)
    c.rect(10*mm, 10*mm, width - 20*mm, height - 20*mm)
    c.setStrokeColorRGB(*CYAN)
    c.setLineWidth(0.6)
    c.rect(12.5*mm, 12.5*mm, width - 25*mm, height - 25*mm)


# ── QR code ────────────────────────────────────────────────────────────────────

def _generate_qr(cert_number: str) -> io.BytesIO:
    url = f"{BASE_URL}/verify/{cert_number}"
    qr = qrcode.QRCode(version=1, box_size=6, border=2,
                       error_correction=qrcode.constants.ERROR_CORRECT_H)
    qr.add_data(url)
    qr.make(fit=True)
    img = qr.make_image(fill_color="#0f2547", back_color="white")
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    buf.seek(0)
    return buf


# ── Shadow helpers ─────────────────────────────────────────────────────────────

def _shadow_rect(c, x, y, w, h, radius=0, offset=2.5):
    """Draw a soft shadow, then the white card on top."""
    c.setFillColorRGB(*SHADOW)
    if radius:
        c.roundRect(x + offset, y - offset, w, h, radius, fill=1, stroke=0)
    else:
        c.rect(x + offset, y - offset, w, h, fill=1, stroke=0)


# ── Main generator ─────────────────────────────────────────────────────────────

def generate_certificate(
    cert_number: str,
    member_name: str,
    course_id: str,
    course_title: str,
    cpd_hours: float,
    issued_date: str,
) -> bytes:
    """Return a tamper-resistant certificate as PDF bytes."""
    buf = io.BytesIO()
    width, height = A4   # 595.27 × 841.89 pts

    c = canvas.Canvas(buf, pagesize=A4)
    c.setTitle(f"Meridian CPD Certificate — {cert_number}")
    c.setAuthor("Meridian CPD")
    c.setSubject(f"CPD Certificate: {course_title}")

    # ── Page background ─────────────────────────────────────────────────────
    c.setFillColorRGB(*CREAM)
    c.rect(0, 0, width, height, fill=1, stroke=0)

    _draw_watermark(c, width, height)

    # ── Header band ─────────────────────────────────────────────────────────
    HEADER_H = 62 * mm

    # Shadow strip behind header
    c.setFillColorRGB(0.06, 0.12, 0.26)
    c.rect(0, height - HEADER_H - 2.5, width, HEADER_H + 2.5, fill=1, stroke=0)

    # Main header fill
    c.setFillColorRGB(*NAVY)
    c.rect(0, height - HEADER_H, width, HEADER_H, fill=1, stroke=0)

    # Fine white top edge (gives a "framed" quality)
    c.setFillColorRGB(*WHITE)
    c.rect(0, height - 1, width, 1, fill=1, stroke=0)

    # Cyan accent bar (bottom of header)
    c.setFillColorRGB(*CYAN)
    c.rect(0, height - HEADER_H - 2*mm, width, 2*mm, fill=1, stroke=0)

    # Draw logo — icon centred at 35mm from left, vertically centred in header
    icon_centre_x = 38 * mm
    icon_centre_y = height - HEADER_H / 2
    icon_r = 14 * mm
    _draw_meridian_logo(c, icon_centre_x, icon_centre_y, icon_r, on_dark=True)

    # Tagline (right-aligned, italic-feel via spacing)
    c.setFillColorRGB(0.75, 0.85, 0.93)
    c.setFont("Helvetica", 9.5)
    c.drawRightString(width - 18*mm, icon_centre_y - 3, "Stay Sharp. Stay Certified.")

    # ── Certificate title ───────────────────────────────────────────────────
    title_y = height - HEADER_H - 22*mm

    # Subtle shadow on title text (draw offset first)
    c.setFillColorRGB(*SHADOW)
    c.setFont("Helvetica-Bold", 21)
    c.drawCentredString(width / 2 + 1, title_y - 1, "CERTIFICATE OF CPD COMPLETION")

    c.setFillColorRGB(*NAVY)
    c.setFont("Helvetica-Bold", 21)
    c.drawCentredString(width / 2, title_y, "CERTIFICATE OF CPD COMPLETION")

    # Cyan rule with tapered ends (simulated by overlapping rects)
    rule_y = title_y - 7*mm
    c.setFillColorRGB(*CYAN)
    c.rect(35*mm, rule_y, width - 70*mm, 1.2, fill=1, stroke=0)

    # ── "This is to certify that" ────────────────────────────────────────────
    certify_y = rule_y - 14*mm
    c.setFillColorRGB(*SOFT_GREY)
    c.setFont("Helvetica", 11.5)
    c.drawCentredString(width / 2, certify_y, "This is to certify that")

    # ── Recipient name ───────────────────────────────────────────────────────
    name_y = certify_y - 16*mm

    # Shadow layer
    c.setFillColorRGB(*SHADOW)
    c.setFont("Helvetica-Bold", 30)
    c.drawCentredString(width / 2 + 1, name_y - 1, member_name)

    c.setFillColorRGB(*NAVY)
    c.setFont("Helvetica-Bold", 30)
    c.drawCentredString(width / 2, name_y, member_name)

    # Name underline (cyan, tapers to width of name)
    name_w = c.stringWidth(member_name, "Helvetica-Bold", 30)
    ul_y = name_y - 4*mm
    c.setFillColorRGB(*CYAN)
    c.rect(width/2 - name_w/2, ul_y, name_w, 1.5, fill=1, stroke=0)

    # ── "has successfully completed" ─────────────────────────────────────────
    completed_y = ul_y - 13*mm
    c.setFillColorRGB(*SOFT_GREY)
    c.setFont("Helvetica", 11.5)
    c.drawCentredString(width / 2, completed_y, "has successfully completed")

    # ── Course title ──────────────────────────────────────────────────────────
    course_y = completed_y - 14*mm
    c.setFillColorRGB(*NAVY)
    c.setFont("Helvetica-Bold", 15)
    max_w = width - 60*mm
    if c.stringWidth(course_title, "Helvetica-Bold", 15) > max_w:
        words = course_title.split()
        mid = len(words) // 2
        line1 = " ".join(words[:mid])
        line2 = " ".join(words[mid:])
        c.drawCentredString(width / 2, course_y, line1)
        c.drawCentredString(width / 2, course_y - 9*mm, line2)
        after_title_y = course_y - 18*mm
    else:
        c.drawCentredString(width / 2, course_y, course_title)
        after_title_y = course_y - 10*mm

    # Course ID
    c.setFillColorRGB(*SOFT_GREY)
    c.setFont("Helvetica", 9)
    c.drawCentredString(width / 2, after_title_y, f"Course {course_id}")

    # ── CPD hours pill ────────────────────────────────────────────────────────
    pill_y = after_title_y - 22*mm
    pill_w = 52*mm
    pill_h = 17*mm
    pill_x = width/2 - pill_w/2

    # Shadow
    c.setFillColorRGB(*CYAN_DARK)
    c.roundRect(pill_x + 2, pill_y - 2, pill_w, pill_h, 3*mm, fill=1, stroke=0)

    c.setFillColorRGB(*CYAN)
    c.roundRect(pill_x, pill_y, pill_w, pill_h, 3*mm, fill=1, stroke=0)

    c.setFillColorRGB(*WHITE)
    c.setFont("Helvetica-Bold", 16)
    hours_text = f"{cpd_hours:g} CPD Hour{'s' if cpd_hours != 1 else ''}"
    c.drawCentredString(width / 2, pill_y + 5*mm, hours_text)

    # ── Details band ─────────────────────────────────────────────────────────
    details_y = pill_y - 24*mm
    details_h = 17*mm
    details_w = width - 36*mm

    _shadow_rect(c, 18*mm, details_y, details_w, details_h, radius=2*mm)
    c.setFillColorRGB(*LIGHT_BG)
    c.roundRect(18*mm, details_y, details_w, details_h, 2*mm, fill=1, stroke=0)

    c.setFillColorRGB(*NAVY)
    c.setFont("Helvetica-Bold", 7.5)
    c.drawString(24*mm, details_y + 10*mm, "CERTIFICATE NUMBER")
    c.drawCentredString(width/2, details_y + 10*mm, "DATE ISSUED")
    c.drawRightString(width - 24*mm, details_y + 10*mm, "ISSUED BY")

    c.setFont("Helvetica", 9.5)
    c.drawString(24*mm, details_y + 3.5*mm, cert_number)
    c.drawCentredString(width/2, details_y + 3.5*mm, issued_date)
    c.drawRightString(width - 24*mm, details_y + 3.5*mm, "Meridian CPD")

    # ── QR code ───────────────────────────────────────────────────────────────
    qr_size = 26*mm
    qr_x = width/2 - qr_size/2
    qr_y = details_y - 34*mm

    # White card behind QR with shadow
    card_pad = 3*mm
    c.setFillColorRGB(*SHADOW)
    c.roundRect(qr_x - card_pad + 2, qr_y - card_pad - 2,
                qr_size + card_pad*2, qr_size + card_pad*2, 2*mm, fill=1, stroke=0)
    c.setFillColorRGB(*WHITE)
    c.roundRect(qr_x - card_pad, qr_y - card_pad,
                qr_size + card_pad*2, qr_size + card_pad*2, 2*mm, fill=1, stroke=0)

    qr_buf = _generate_qr(cert_number)
    c.drawImage(ImageReader(qr_buf), qr_x, qr_y, width=qr_size, height=qr_size,
                preserveAspectRatio=True)

    c.setFillColorRGB(*SOFT_GREY)
    c.setFont("Helvetica", 7)
    c.drawCentredString(width/2, qr_y - 6*mm,
                        f"Scan to verify: meridiancpd.co.uk/verify/{cert_number}")

    # ── Disclaimer ────────────────────────────────────────────────────────────
    disclaimer_y = qr_y - 18*mm
    c.setFillColorRGB(0.62, 0.62, 0.62)
    c.setFont("Helvetica", 6.5)
    disclaimer = (
        "Meridian CPD is an independent CPD provider. This certificate is not issued by or on "
        "behalf of any accreditation scheme. Acceptance of CPD hours is at the discretion of the "
        "subscriber's accreditation body. Subscribers are responsible for verifying their scheme's "
        "CPD acceptance criteria."
    )
    words = disclaimer.split()
    lines, current = [], ""
    for word in words:
        test = (current + " " + word).strip()
        if c.stringWidth(test, "Helvetica", 6.5) < (width - 44*mm):
            current = test
        else:
            lines.append(current)
            current = word
    if current:
        lines.append(current)
    for i, line in enumerate(lines):
        c.drawCentredString(width/2, disclaimer_y - i * 8.5, line)

    # ── Imprint bar (Seren Surveying + RetroTrack only) ───────────────────────
    imprint_y = 14*mm
    c.setFillColorRGB(0.92, 0.945, 0.965)
    c.roundRect(18*mm, imprint_y, width - 36*mm, 7.5*mm, 1.5*mm, fill=1, stroke=0)
    c.setFillColorRGB(*SOFT_GREY)
    c.setFont("Helvetica", 6.5)
    c.drawString(22*mm, imprint_y + 2.5*mm, "Curriculum by Seren Surveying Limited")
    c.drawRightString(width - 22*mm, imprint_y + 2.5*mm, "Managed by RetroTrack")

    # ── Navy footer ────────────────────────────────────────────────────────────
    c.setFillColorRGB(*NAVY)
    c.rect(0, 0, width, 12*mm, fill=1, stroke=0)
    c.setFillColorRGB(*WHITE)
    c.setFont("Helvetica", 7.5)
    c.drawCentredString(width/2, 4.2*mm,
        f"© Meridian CPD 2026  •  meridiancpd.co.uk  •  hello@meridiancpd.co.uk  •  {cert_number}")

    # ── Border (drawn last so it sits on top) ──────────────────────────────────
    _draw_border(c, width, height)

    c.save()
    buf.seek(0)
    return buf.read()


if __name__ == "__main__":
    pdf_bytes = generate_certificate(
        cert_number="MER-2026-0001",
        member_name="John Smith",
        course_id="MER-DEA-001",
        course_title="RdSAP 10: What's Changed and Why",
        cpd_hours=2.0,
        issued_date="14 March 2026",
    )
    out = os.path.join(os.path.dirname(__file__), "test_certificate.pdf")
    with open(out, "wb") as f:
        f.write(pdf_bytes)
    print(f"Certificate generated: {out}")
