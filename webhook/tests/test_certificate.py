"""The certificate PDF (certificate_generator.py). Run: python3 tests/test_certificate.py

What must hold: the certificate names Meridian CPD only (no other company); the number,
date, course and verify link are on it; the QR code is drawn; the watermark copies sit
end to end and never print over each other; the outreach email logo is hosted on the
Meridian site and the file exists in landing-page/."""
import os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, ".."))
import certificate_generator as cg
from reportlab.pdfgen import canvas as rl_canvas

drawn, images = [], []

class Recording(rl_canvas.Canvas):
    def drawString(self, x, y, text, *a, **k):
        drawn.append(("l", x, y, text, self._fontname, self._fontsize)); return super().drawString(x, y, text, *a, **k)
    def drawRightString(self, x, y, text, *a, **k):
        drawn.append(("r", x, y, text, self._fontname, self._fontsize)); return super().drawRightString(x, y, text, *a, **k)
    def drawCentredString(self, x, y, text, *a, **k):
        drawn.append(("c", x, y, text, self._fontname, self._fontsize)); return super().drawCentredString(x, y, text, *a, **k)
    def drawImage(self, *a, **k):
        images.append(a); return super().drawImage(*a, **k)

cg.canvas.Canvas = Recording
pdf = cg.generate_certificate(cert_number="MER-2026-0001", member_name="Test Assessor",
                              course_id="MER-DEA-001", course_title="RdSAP 10: What's Changed and Why",
                              cpd_hours=2.0, issued_date="14 March 2026")
assert pdf.startswith(b"%PDF"), "not a PDF"
text = " ".join(d[3] for d in drawn)

# Meridian CPD only
for name in ("Seren", "RetroTrack", "Curriculum by", "Managed by"):
    assert name not in text, f"certificate still names {name!r}"
assert "Meridian CPD" in text

# Number, date, course, verify link unchanged
for must in ("MER-2026-0001", "14 March 2026", "MER-DEA-001", "Test Assessor",
             "/verify/MER-2026-0001", "certificate of completion"):
    assert must in text, f"missing {must!r}"
assert images, "QR code not drawn"

# Watermark: copies in one row must not overlap
mark = "MERIDIAN CPD  •  STAY SHARP. STAY CERTIFIED.  •  "
rows = {}
for kind, x, y, t, font, size in drawn:
    if t == mark:
        rows.setdefault(y, []).append(x)
assert rows, "watermark not drawn"
w = cg.canvas.Canvas(os.devnull).stringWidth(mark, "Helvetica", 8)
for y, xs in rows.items():
    xs.sort()
    for a, b in zip(xs, xs[1:]):
        assert b - a >= w, f"watermark copies overlap: step {b - a} < text width {w}"

# Outreach logo on the Meridian domain, and the file is in the site
src = open(os.path.join(HERE, "..", "outreach.py")).read()
line = next(l for l in src.splitlines() if l.startswith("LOGO_URL"))
url = line.split('"')[1]
assert url.startswith("https://meridiancpd.co.uk/"), url
assert "serensurveying" not in src
path = os.path.join(HERE, "..", "..", "landing-page", url.split("meridiancpd.co.uk/", 1)[1])
assert os.path.isfile(path), f"logo file missing from landing-page: {path}"

print("certificate: all checks passed")
