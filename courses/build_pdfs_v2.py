"""
Meridian CPD — Branded PDF Builder v2 (ReportLab)
Produces professional, fully branded course PDFs.

Usage:
    python3 build_pdfs_v2.py           # build all missing PDFs
    python3 build_pdfs_v2.py --force   # rebuild all (overwrite)
    python3 build_pdfs_v2.py MER-DEA-002  # build one course
"""

import io
import os
import re
import sys
import urllib.request
import urllib.error
from pathlib import Path
from typing import Optional

try:
    from reportlab.lib import colors
    from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY, TA_LEFT
    from reportlab.lib.pagesizes import A4
    from reportlab.lib.styles import ParagraphStyle
    from reportlab.lib.units import mm
    from reportlab.platypus import (
        BaseDocTemplate, Frame, Image, NextPageTemplate,
        PageBreak, PageTemplate, Paragraph, Spacer, Table, TableStyle,
        HRFlowable, KeepTogether,
    )
    from reportlab.platypus.flowables import Flowable
    from reportlab.lib.utils import ImageReader
except ImportError:
    print("Install reportlab: pip3 install reportlab")
    sys.exit(1)

ROOT = Path(__file__).parent
IMG_CACHE = ROOT / ".img-cache"
IMG_CACHE.mkdir(exist_ok=True)

# ── Brand colours ─────────────────────────────────────────────────────────────
DARK    = colors.HexColor("#0D1F0E")
ACCENT  = colors.HexColor("#D4FF00")
GREEN   = colors.HexColor("#22c55e")
LIGHT   = colors.HexColor("#F5F5F0")
BORDER  = colors.HexColor("#d4e8d4")
GREY    = colors.HexColor("#6b7280")
LTGREY  = colors.HexColor("#f3f4f6")
WHITE   = colors.white
BLACK   = colors.HexColor("#1a1a1a")

STRAND_COLOURS = {
    "MER-DEA": colors.HexColor("#1d4ed8"),
    "MER-RA":  colors.HexColor("#7c3aed"),
    "MER-ALL": colors.HexColor("#059669"),
}
STRAND_LABELS = {
    "MER-DEA": "Domestic Energy Assessor",
    "MER-RA":  "Retrofit Assessor",
    "MER-ALL": "All Strands",
}

# Season cover image — one consistent image across ALL courses.
# To change for a new season, update SEASON_IMAGE only.
# Season 1 (2026): clean modern residential exterior — works at 38% opacity on dark green.
SEASON = "1"
SEASON_IMAGE = "https://images.unsplash.com/photo-1570129477492-45c003edd2be?w=1200&h=500&fit=crop"


def fetch_image(url: str, cache_key: str) -> Optional[str]:
    """Download image to cache, return local path or None."""
    safe = re.sub(r'[^a-z0-9]', '_', cache_key.lower())
    cache_path = IMG_CACHE / f"{safe}.jpg"
    if cache_path.exists():
        return str(cache_path)
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=10) as resp:
            cache_path.write_bytes(resp.read())
        return str(cache_path)
    except Exception as e:
        print(f"    [img] Could not fetch cover image: {e}")
        return None


# ── Page drawing callbacks ────────────────────────────────────────────────────
def draw_cover(canvas, doc, meta: dict):
    """Draw the full cover page."""
    W, H = A4
    canvas.saveState()

    # Dark green background
    canvas.setFillColor(DARK)
    canvas.rect(0, 0, W, H, fill=1, stroke=0)

    # Cover photo (top 42% of page, relevant to course topic)
    img_path = meta.get('img_path')
    if img_path:
        try:
            ih = H * 0.42
            canvas.saveState()
            canvas.setFillAlpha(0.38)
            canvas.drawImage(img_path, 0, H - ih, W, ih, preserveAspectRatio=False, mask='auto')
            canvas.restoreState()
        except Exception:
            pass

    # Accent bar (horizontal stripe)
    bar_y = H * 0.42
    canvas.setFillColor(ACCENT)
    canvas.rect(0, bar_y - 3*mm, W, 3*mm, fill=1, stroke=0)

    # Strand badge (pill) — positioned below accent bar with breathing room
    strand_col = meta['strand_colour']
    badge_text = meta['strand_label']
    badge_x = 22*mm
    badge_y = bar_y - 18*mm  # 18mm below accent bar
    canvas.setFillColor(strand_col)
    canvas.roundRect(badge_x, badge_y, len(badge_text)*5.2 + 14, 16, 8, fill=1, stroke=0)
    canvas.setFillColor(WHITE)
    canvas.setFont("Helvetica-Bold", 8)
    canvas.drawString(badge_x + 7, badge_y + 4.5, badge_text.upper())

    # Title — word-wrapped white text
    title = meta['title']
    max_w = W - 44*mm
    words = title.split()
    lines_t, line = [], []
    canvas.setFont("Helvetica-Bold", 26)
    for word in words:
        test = ' '.join(line + [word])
        if canvas.stringWidth(test, "Helvetica-Bold", 26) > max_w and line:
            lines_t.append(' '.join(line))
            line = [word]
        else:
            line.append(word)
    if line:
        lines_t.append(' '.join(line))

    title_y = badge_y - 26  # gap below badge
    canvas.setFillColor(WHITE)
    for i, ln in enumerate(lines_t):
        canvas.drawString(22*mm, title_y - i*33, ln)

    # Accent underline below title
    last_line_y = title_y - (len(lines_t) - 1) * 33
    ul_y = last_line_y - 10
    canvas.setFillColor(ACCENT)
    canvas.rect(22*mm, ul_y, 28*mm, 2.5, fill=1, stroke=0)

    # Meta info bar — solid dark panel with ACCENT values + white labels
    meta_y = ul_y - 14  # top of the text, box drawn below
    box_h = 34
    box_y = meta_y - box_h + 16

    # Solid slightly-lighter dark background using setFillAlpha
    canvas.saveState()
    canvas.setFillColor(colors.HexColor("#1a3320"))
    canvas.rect(22*mm, box_y, W - 44*mm, box_h, fill=1, stroke=0)
    canvas.restoreState()

    items = [
        (meta['hours_str'], "CPD HOURS"),
        (meta['course_id'], "COURSE ID"),
        (meta['published'], "PUBLISHED"),
    ]
    col_w = (W - 44*mm) / len(items)
    for i, (val, label) in enumerate(items):
        cx = 22*mm + col_w * i + col_w / 2
        canvas.setFillColor(ACCENT)
        canvas.setFont("Helvetica-Bold", 16)
        canvas.drawCentredString(cx, box_y + 14, val)
        canvas.setFillColor(WHITE)
        canvas.setFont("Helvetica", 7)
        canvas.drawCentredString(cx, box_y + 4, label)

    # Subtle vertical dividers between items
    canvas.setStrokeColor(DARK)
    canvas.setLineWidth(0.5)
    for i in range(1, len(items)):
        dx = 22*mm + col_w * i
        canvas.line(dx, box_y + 4, dx, box_y + box_h - 4)

    # Footer
    canvas.setFillColor(GREY)
    canvas.setFont("Helvetica", 7.5)
    canvas.drawCentredString(W/2, 14*mm, "meridiancpd.co.uk  ·  Stay Sharp. Stay Certified.  ·  © Meridian CPD 2026")

    canvas.restoreState()


def draw_header(canvas, doc):
    """Running header on content pages."""
    W, H = A4
    canvas.saveState()
    canvas.setStrokeColor(DARK)
    canvas.setLineWidth(0.5)
    canvas.line(20*mm, H - 14*mm, W - 20*mm, H - 14*mm)
    canvas.setFillColor(DARK)
    canvas.setFont("Helvetica-Bold", 7)
    canvas.drawString(20*mm, H - 12*mm, "MERIDIAN CPD")
    canvas.setFillColor(GREY)
    canvas.setFont("Helvetica", 7)
    canvas.drawRightString(W - 20*mm, H - 12*mm, doc.course_id)
    canvas.restoreState()


def draw_footer(canvas, doc):
    """Running footer with page number."""
    W, H = A4
    canvas.saveState()
    canvas.setStrokeColor(BORDER)
    canvas.setLineWidth(0.5)
    canvas.line(20*mm, 14*mm, W - 20*mm, 14*mm)
    canvas.setFillColor(GREY)
    canvas.setFont("Helvetica", 7.5)
    canvas.drawCentredString(W/2, 10*mm, str(canvas.getPageNumber()))
    canvas.setFont("Helvetica", 6.5)
    canvas.drawString(20*mm, 10*mm, "© Meridian CPD 2026 · Unauthorised reproduction prohibited")
    canvas.restoreState()


# ── Styles ────────────────────────────────────────────────────────────────────
def make_styles():
    H2 = ParagraphStyle("H2",
        fontSize=13, fontName="Helvetica-Bold", textColor=DARK,
        spaceBefore=8*mm, spaceAfter=2*mm, keepWithNext=1)
    H3 = ParagraphStyle("H3",
        fontSize=10.5, fontName="Helvetica-Bold", textColor=DARK,
        spaceBefore=4*mm, spaceAfter=1*mm, keepWithNext=1)
    BODY = ParagraphStyle("Body",
        fontSize=10, fontName="Helvetica", leading=15.5,
        spaceAfter=3*mm, alignment=TA_JUSTIFY, textColor=BLACK)
    BULLET = ParagraphStyle("Bullet",
        fontSize=10, fontName="Helvetica", leading=14.5,
        spaceAfter=1.5*mm, leftIndent=6*mm, bulletIndent=0,
        textColor=BLACK)
    BULLET_DARK = ParagraphStyle("BulletDark",
        fontSize=10, fontName="Helvetica", leading=14.5,
        spaceAfter=1.5*mm, leftIndent=6*mm,
        textColor=WHITE)
    META = ParagraphStyle("Meta",
        fontSize=8.5, fontName="Helvetica-Oblique",
        textColor=GREY, spaceAfter=2*mm)
    QUIZ_Q = ParagraphStyle("QuizQ",
        fontSize=10, fontName="Helvetica-Bold", textColor=DARK,
        spaceBefore=3*mm, spaceAfter=1*mm)
    QUIZ_OPT = ParagraphStyle("QuizOpt",
        fontSize=9.5, fontName="Helvetica", textColor=BLACK,
        leftIndent=4*mm, spaceAfter=0.5*mm)
    QUIZ_ANS = ParagraphStyle("QuizAns",
        fontSize=9.5, fontName="Helvetica-Bold", textColor=DARK,
        spaceBefore=1.5*mm, spaceAfter=0.5*mm)
    QUIZ_EXP = ParagraphStyle("QuizExp",
        fontSize=9, fontName="Helvetica-Oblique", textColor=GREY,
        leftIndent=4*mm, spaceAfter=2*mm)
    FOOTER_TEXT = ParagraphStyle("FooterText",
        fontSize=7.5, fontName="Helvetica", textColor=GREY,
        alignment=TA_CENTER, spaceBefore=3*mm)
    return dict(h2=H2, h3=H3, body=BODY, bullet=BULLET, bullet_dark=BULLET_DARK,
                meta=META, quiz_q=QUIZ_Q, quiz_opt=QUIZ_OPT, quiz_ans=QUIZ_ANS,
                quiz_exp=QUIZ_EXP, footer=FOOTER_TEXT)


def inline_fmt(text: str) -> str:
    # Remove em/en dashes — strip surrounding whitespace and replace with comma
    text = re.sub(r'\s*\u2014\s*', ', ', text)  # — em dash
    text = re.sub(r'\s*\u2013\s*', ', ', text)  # – en dash
    text = text.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
    # Handle bold-italic (***...***) first to avoid crossed tags
    text = re.sub(r'\*\*\*(.+?)\*\*\*', r'<b><i>\1</i></b>', text)
    text = re.sub(r'\*\*(.+?)\*\*', r'<b>\1</b>', text)
    text = re.sub(r'\*([^*]+?)\*', r'<i>\1</i>', text)
    text = re.sub(r'\[([^\]]+)\]\([^\)]+\)', r'\1', text)
    return text


def section_box(heading: str, items: list, bg: colors.Color, fg: colors.Color,
                accent: colors.Color, S: dict, bullet_style) -> list:
    """Render a full-width callout box: heading bar + bulleted items."""
    W_box = 170*mm
    head_para = Paragraph(
        f'<font color="#{accent.hexval()[2:] if hasattr(accent,"hexval") else "D4FF00"}">{heading}</font>',
        ParagraphStyle("BoxHead", fontSize=11, fontName="Helvetica-Bold",
                       textColor=accent, spaceBefore=0, spaceAfter=0)
    )
    head_row = [[head_para]]
    head_table = Table(head_row, colWidths=[W_box])
    head_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), bg),
        ('TOPPADDING', (0,0), (-1,-1), 6),
        ('BOTTOMPADDING', (0,0), (-1,-1), 6),
        ('LEFTPADDING', (0,0), (-1,-1), 8),
        ('RIGHTPADDING', (0,0), (-1,-1), 8),
        ('ROUNDEDCORNERS', [4]),
    ]))

    # Inline bullet + text in single column — avoids separate bullet cell with its own background
    rows = []
    for item in items:
        text_p = Paragraph(
            f'<font color="#D4FF00"><b>\u2022</b></font>\u2002{inline_fmt(item)}',
            ParagraphStyle("BoxBullet", fontSize=10, fontName="Helvetica", leading=15,
                           textColor=WHITE if bg == DARK else BLACK,
                           leftIndent=4*mm, firstLineIndent=-4*mm, spaceAfter=0),
        )
        rows.append([text_p])

    body_table = Table(rows, colWidths=[W_box])
    body_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), bg),
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
        ('TOPPADDING', (0,0), (-1,-1), 2),
        ('BOTTOMPADDING', (0,0), (-1,-1), 2),
        ('LEFTPADDING', (0,0), (-1,-1), 8),
        ('RIGHTPADDING', (0,0), (-1,-1), 8),
    ]))

    # Extra bottom padding on last bullet row — no separate foot_table needed
    body_table.setStyle(TableStyle([
        ('BOTTOMPADDING', (0,-1), (-1,-1), 10),
    ]))

    return [KeepTogether([head_table, body_table]), Spacer(1, 4*mm)]


def reading_box(heading: str, items: list, S: dict) -> list:
    """Further reading box in light green."""
    W_box = 170*mm
    rows = [[Paragraph(f'<b>{heading}</b>',
        ParagraphStyle("RH", fontSize=11, fontName="Helvetica-Bold",
                       textColor=DARK, spaceBefore=0, spaceAfter=0))]]
    for item in items:
        rows.append([Paragraph(f'\u2022 {inline_fmt(item)}',
            ParagraphStyle("RI", fontSize=9.5, fontName="Helvetica",
                           textColor=colors.HexColor("#1a3d1a"), spaceAfter=1*mm))])
    t = Table(rows, colWidths=[W_box])
    t.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor("#f0faf2")),
        ('TOPPADDING', (0,0), (-1,-1), 5),
        ('BOTTOMPADDING', (0,0), (-1,-1), 5),
        ('LEFTPADDING', (0,0), (-1,-1), 9),
        ('RIGHTPADDING', (0,0), (-1,-1), 9),
        ('BOX', (0,0), (-1,-1), 0.75, BORDER),
        ('LINEBELOW', (0,0), (0,0), 1.5, DARK),
        ('ROUNDEDCORNERS', [4]),
    ]))
    return [KeepTogether([t]), Spacer(1, 4*mm)]


def quiz_box(heading: str, qa_blocks: list, S: dict) -> list:
    """Self-assessment questions box.
    Questions and options are shown first; answers collected into a key at the bottom.
    """
    W_box = 170*mm
    TABLE_STYLE = TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor("#f8faf8")),
        ('LEFTPADDING', (0,0), (-1,-1), 9),
        ('RIGHTPADDING', (0,0), (-1,-1), 9),
        ('TOPPADDING', (0,0), (-1,-1), 1),
        ('BOTTOMPADDING', (0,0), (-1,-1), 1),
        ('BOX', (0,0), (-1,-1), 0.75, BORDER),
        ('LINEBEFORE', (0,0), (0,-1), 3, DARK),
    ])

    def make_head(label):
        t = Table([[Paragraph(f'<b>{label}</b>',
            ParagraphStyle("QH", fontSize=11, fontName="Helvetica-Bold",
                           textColor=DARK, spaceBefore=0, spaceAfter=0))]],
            colWidths=[W_box])
        t.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,-1), colors.HexColor("#f8faf8")),
            ('TOPPADDING', (0,0), (-1,-1), 6),
            ('BOTTOMPADDING', (0,0), (-1,-1), 6),
            ('LEFTPADDING', (0,0), (-1,-1), 9),
            ('RIGHTPADDING', (0,0), (-1,-1), 9),
            ('LINEBELOW', (0,0), (-1,-1), 2, DARK),
        ]))
        return t

    # ── Questions (no answers shown) ──────────────────────────────────────────
    q_rows = []
    for q_text, opts, _ans, _exp in qa_blocks:
        q_rows.append([Paragraph(inline_fmt(q_text), S['quiz_q'])])
        for opt in opts:
            q_rows.append([Paragraph(inline_fmt(opt), S['quiz_opt'])])
        q_rows.append([Spacer(1, 3*mm)])

    t_q_body = Table(q_rows, colWidths=[W_box])
    t_q_body.setStyle(TABLE_STYLE)

    # ── Answer key ────────────────────────────────────────────────────────────
    QUIZ_KEY = ParagraphStyle("QuizKey", fontSize=9, fontName="Helvetica",
                               leading=13, leftIndent=0, spaceAfter=2*mm,
                               textColor=colors.HexColor("#1a3a1a"))
    key_rows = []
    for i, (q_text, _opts, ans_text, exp_text) in enumerate(qa_blocks, 1):
        # Extract just the letter: "Correct answer: C" → "C"
        letter = ans_text.replace('Correct answer:', '').replace('*', '').strip()
        line = f'<b>Q{i}: {letter}</b>'
        if exp_text:
            line += f' — {inline_fmt(exp_text)}'
        key_rows.append([Paragraph(line, QUIZ_KEY)])

    t_key_body = Table(key_rows, colWidths=[W_box])
    t_key_body.setStyle(TABLE_STYLE)

    return [
        # Keep heading with question body start, but allow question table to split across pages
        make_head(heading),
        t_q_body,
        Spacer(1, 3*mm),
        KeepTogether([make_head("Answer Key"), t_key_body]),
        Spacer(1, 4*mm),
    ]


# ── Markdown parser ───────────────────────────────────────────────────────────
def parse_md(md: str) -> dict:
    """Extract metadata and structured sections from markdown."""
    lines = md.strip().split('\n')
    title, cpd_hours, published = '', 1.0, 'March 2026'
    for line in lines[:6]:
        if line.startswith('# '):
            title = line[2:].strip()
        m = re.search(r'CPD Hours:\*\*\s*([\d.]+)', line)
        if m:
            cpd_hours = float(m.group(1))
        m2 = re.search(r'Published:\*\*\s*(.+)', line)
        if m2:
            published = m2.group(1).strip()

    # Parse into sections
    sections = []  # each: {'type': str, 'heading': str, 'content': [lines]}
    current = None
    content_started = False

    for line in lines:
        stripped = line.strip()
        if not content_started:
            if stripped.startswith('## '):
                content_started = True
            else:
                continue

        if stripped.startswith('## '):
            current = {'type': 'section', 'heading': stripped[3:], 'content': []}
            sections.append(current)
        elif current is not None:
            current['content'].append(stripped)

    return dict(title=title, cpd_hours=cpd_hours, published=published, sections=sections)


def build_story(parsed: dict, S: dict) -> list:
    story = []
    W_inner = 170*mm

    def add_h2(text):
        story.append(Spacer(1, 1*mm))
        story.append(Paragraph(inline_fmt(text), S['h2']))
        story.append(HRFlowable(width=W_inner, thickness=2, color=ACCENT, spaceAfter=2*mm))

    for sec in parsed['sections']:
        heading = sec['heading']
        lines = sec['content']

        is_objectives = 'Learning Objective' in heading
        is_takeaways = 'Takeaway' in heading
        is_quiz = 'Self-Assessment' in heading or 'Assessment Question' in heading
        is_reading = 'Further Reading' in heading

        # Collect bullet items for box sections
        if is_objectives or is_takeaways or is_reading:
            bullets = []
            for ln in lines:
                if ln.startswith('- ') or ln.startswith('• '):
                    bullets.append(ln[2:].strip())
                # Also collect plain text as bullets if in objectives
                elif ln and not ln.startswith('#') and not ln.startswith('---') and is_objectives:
                    bullets.append(ln)

            if is_objectives and bullets:
                bg_c = DARK
                fg_c = WHITE
                acc = ACCENT
                bl_style = S['bullet_dark']
                story += section_box(heading, bullets, bg_c, fg_c, acc, S, bl_style)
            elif is_takeaways and bullets:
                story += section_box(heading, bullets, DARK, WHITE, ACCENT, S, S['bullet_dark'])
            elif is_reading and bullets:
                story += reading_box(heading, bullets, S)
            continue

        if is_quiz:
            # Parse Q&A blocks
            qa_blocks = []
            q_text = opts = ans = exp = None
            opts_buf = []

            def flush_qa():
                if q_text:
                    qa_blocks.append((q_text, list(opts_buf), ans or '', exp or ''))

            for ln in lines:
                if re.match(r'^\*\*Q\d+\.', ln):
                    flush_qa()
                    q_text = re.sub(r'\*\*(.+?)\*\*', r'\1', ln)
                    opts_buf, ans, exp = [], None, None
                elif re.match(r'^[ABCD]\)', ln):
                    opts_buf.append(ln)
                elif ln.startswith('**Correct answer:'):
                    ans = re.sub(r'\*\*(.+?)\*\*', r'\1', ln)
                elif ln.startswith('*') and ln.endswith('*') and not ln.startswith('**'):
                    exp = ln.strip('*')
            flush_qa()

            if qa_blocks:
                story += quiz_box(heading, qa_blocks, S)
            continue

        # Regular section
        add_h2(heading)
        in_list = False
        bullets_buf = []

        def flush_bullets():
            nonlocal in_list, bullets_buf
            if bullets_buf:
                for b in bullets_buf:
                    p = Paragraph(
                        f'<font color="#D4FF00"><b>\u2022</b></font>\u2002{inline_fmt(b)}',
                        ParagraphStyle("BulletInline", fontSize=10, fontName="Helvetica",
                                       leading=15, leftIndent=4*mm, firstLineIndent=-4*mm,
                                       spaceAfter=2*mm, textColor=BLACK),
                    )
                    story.append(p)
                bullets_buf = []
            in_list = False

        for ln in lines:
            if not ln or ln == '---':
                flush_bullets()
                if ln == '---':
                    story.append(HRFlowable(width=W_inner, thickness=0.5,
                                           color=BORDER, spaceAfter=2*mm, spaceBefore=2*mm))
                continue

            if ln.startswith('### '):
                flush_bullets()
                story.append(Paragraph(inline_fmt(ln[4:]), S['h3']))
                continue

            if ln.startswith('- ') or ln.startswith('• '):
                bullets_buf.append(ln[2:].strip())
                in_list = True
                continue

            if in_list:
                flush_bullets()

            if ln.startswith('*') and ln.endswith('*') and not ln.startswith('**') and len(ln) < 150:
                story.append(Paragraph(f'<i>{inline_fmt(ln.strip("*"))}</i>', S['meta']))
            else:
                story.append(Paragraph(inline_fmt(ln), S['body']))

        flush_bullets()

    return story


# ── Main PDF builder ──────────────────────────────────────────────────────────
class MeridianDoc(BaseDocTemplate):
    def __init__(self, filename, course_id, on_cover_page=None, **kwargs):
        super().__init__(filename, **kwargs)
        self.course_id = course_id
        W, H = A4
        content_frame = Frame(20*mm, 20*mm, W - 40*mm, H - 42*mm,
                              leftPadding=0, rightPadding=0,
                              topPadding=0, bottomPadding=0, id='content')
        cover_frame = Frame(20*mm, H/2, W - 40*mm, 1, id='cover')  # near-zero height — nothing flows in
        cover_cb = on_cover_page if on_cover_page else lambda c, d: None
        self.addPageTemplates([
            PageTemplate(id='Cover', frames=[cover_frame], onPage=cover_cb),
            PageTemplate(id='Content', frames=[content_frame],
                        onPage=lambda c, d: (draw_header(c, d), draw_footer(c, d))),
        ])


def build_pdf(course_id: str, md_content: str) -> bytes:
    parsed = parse_md(md_content)
    S = make_styles()

    strand_prefix = '-'.join(course_id.split('-')[:2])
    strand_colour = STRAND_COLOURS.get(strand_prefix, GREEN)
    strand_label = STRAND_LABELS.get(strand_prefix, 'All Strands')
    hours_str = f"{parsed['cpd_hours']:g}"
    img_path = fetch_image(SEASON_IMAGE, f"season_{SEASON}_cover")

    meta = dict(
        title=parsed['title'],
        course_id=course_id,
        hours_str=hours_str,
        published=parsed['published'],
        strand_colour=strand_colour,
        strand_label=strand_label,
        img_path=img_path or "",
    )

    buf = io.BytesIO()
    # Attach meta to a mutable container so onPage callbacks can access it
    meta_box = [meta]

    def on_cover_page(canvas, document):
        draw_cover(canvas, document, meta_box[0])

    doc = MeridianDoc(buf, course_id=course_id, pagesize=A4,
                      title=f"Meridian CPD — {parsed['title']}",
                      author="Meridian CPD",
                      on_cover_page=on_cover_page)

    story = []
    # Page 1 = Cover (automatically uses the first PageTemplate = 'Cover')
    # The onPage callback draws the full cover art.
    # Switch to Content template and break to page 2 before any content flows.
    story.append(NextPageTemplate('Content'))
    story.append(PageBreak())

    # Content starts on page 2
    story += build_story(parsed, S)

    # Copyright footer
    W_inner = 170*mm
    story.append(Spacer(1, 8*mm))
    story.append(HRFlowable(width=W_inner, thickness=0.5, color=BORDER))
    story.append(Paragraph(
        f'© Meridian CPD 2026 &nbsp;·&nbsp; meridiancpd.co.uk &nbsp;·&nbsp;'
        f' {course_id} &nbsp;·&nbsp; {hours_str} CPD Hour{"s" if parsed["cpd_hours"] != 1 else ""}'
        f' &nbsp;·&nbsp; Unauthorised reproduction prohibited.'
        f' This course material is licensed to individual subscribers only.',
        S['footer']
    ))

    doc.build(story)
    buf.seek(0)
    return buf.read()


def main():
    args = sys.argv[1:]
    force = '--force' in args
    specific = [a for a in args if not a.startswith('--')]

    course_dirs = sorted(ROOT.iterdir())
    built = skipped = 0

    for d in course_dirs:
        if not d.is_dir() or d.name.startswith('.') or d.name in ('__pycache__',):
            continue
        md_files = list(d.glob('*.md'))
        if not md_files:
            continue
        course_id = d.name
        if specific and course_id not in specific:
            continue

        pdf_path = d / f'{course_id}.pdf'
        if pdf_path.exists() and not force:
            print(f'  Skip: {course_id}')
            skipped += 1
            continue

        print(f'  Building {course_id} ...', end=' ', flush=True)
        try:
            content = md_files[0].read_text(encoding='utf-8')
            pdf_bytes = build_pdf(course_id, content)
            pdf_path.write_bytes(pdf_bytes)
            print(f'{len(pdf_bytes)//1024} KB ✓')
            built += 1
        except Exception as e:
            print(f'ERROR: {e}')
            import traceback; traceback.print_exc()

    print(f'\nDone. Built: {built}  Skipped: {skipped}')


if __name__ == '__main__':
    main()
