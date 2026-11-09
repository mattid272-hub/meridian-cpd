"""The member area's look: the dark green streaming layout with lime accents Matt chose
on 6 November 2026 (HQ mock 2026-11-06-series-packaging), and the one SVG poster
template every series and course cover is drawn with. Pure functions, no
database: main.py builds the pages from these.

The same poster template lives in landing-page/courses.html (JavaScript) for the public
site, which GitHub Pages serves without this app. Keep the two in step."""
import os
import re
from html import escape as _esc

WHERE_LABEL = {
    "EWS": "England, Wales and Scotland",
    "EW": "England and Wales",
    "E": "England",
    "S": "Scotland",
    "UK": "UK-wide",
}

FONTS = ('<link rel="preconnect" href="https://fonts.googleapis.com">'
         '<link href="https://fonts.googleapis.com/css2?family=Bebas+Neue&family=DM+Sans:opsz,wght@9..40,400;9..40,500;9..40,600;9..40,700&display=swap" rel="stylesheet">')

CSS = """
*, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }
:root { --dark: #0D1F0E; --dark2: #162818; --card: #1A2E1C; --line: #2A4229; --accent: #D4FF00;
        --white: #FFFFFF; --muted: #8A9E8B; --light: #F5F5F0;
        --display: 'Bebas Neue', sans-serif; --body: 'DM Sans', Arial, sans-serif; }
body { background: var(--dark); color: var(--white); font-family: var(--body); font-size: 15px; line-height: 1.5; min-height: 100vh; }
a { color: inherit; text-decoration: none; }
button, input, select { font-family: inherit; }
.topbar { display: flex; align-items: center; gap: 28px; padding: 0 40px; height: 64px; background: rgba(13,31,14,.96);
          border-bottom: 1px solid var(--line); position: sticky; top: 0; z-index: 5; }
.brand { font-family: var(--display); font-size: 28px; letter-spacing: .06em; line-height: 1; white-space: nowrap; }
.brand span { background: var(--accent); color: var(--dark); padding: 0 5px; border-radius: 2px; }
.nav { display: flex; gap: 22px; font-size: 14px; font-weight: 500; color: var(--muted); }
.nav a.on { color: var(--white); box-shadow: inset 0 -2px 0 var(--accent); padding-bottom: 4px; }
.topbar .grow { flex: 1; }
.who { font-size: 13px; color: var(--muted); white-space: nowrap; }
.signout { font-size: 13px; color: var(--accent); border: 1px solid var(--line); padding: 5px 12px; border-radius: 5px; white-space: nowrap; }
.btn { display: inline-flex; align-items: center; justify-content: center; gap: 8px; border-radius: 6px; padding: 10px 18px;
       font-weight: 700; font-size: 14px; border: 0; cursor: pointer; white-space: nowrap; text-align: center; }
.btn-p { background: var(--accent); color: var(--dark); }
.btn-s { background: rgba(255,255,255,.08); color: var(--white); border: 1px solid rgba(255,255,255,.18); }
.btn-sm { padding: 7px 12px; font-size: 13px; }
.btn[disabled] { opacity: .45; cursor: not-allowed; }
.wrap { padding: 28px 40px 60px; max-width: 1400px; margin: 0 auto; }
.kicker { font-size: 12px; font-weight: 700; letter-spacing: .12em; text-transform: uppercase; color: var(--accent); }
h1, h2, h3 { font-weight: 700; }
.h-display { font-family: var(--display); font-weight: 400; letter-spacing: .02em; line-height: .95; }
.muted { color: var(--muted); }
.notice { background: var(--dark2); border: 1px solid var(--accent); border-radius: 8px; padding: 12px 16px; margin-bottom: 20px; font-size: 14px; }
.hero { position: relative; display: grid; grid-template-columns: 1.05fr 1fr; gap: 40px; align-items: center; padding: 36px 40px;
        background: linear-gradient(90deg, #0D1F0E 0%, #13291A 100%); border-bottom: 1px solid var(--line); }
.hero h1 { font-family: var(--display); font-weight: 400; font-size: 64px; line-height: .95; margin: 10px 0 8px; }
.hero .sub { color: #cfd8cf; font-size: 16px; max-width: 560px; }
.hero .actions { display: flex; gap: 12px; margin-top: 22px; flex-wrap: wrap; }
.hero .poster, .page-head .poster { border-radius: 10px; overflow: hidden; box-shadow: 0 20px 60px rgba(0,0,0,.45); }
.poster svg, .cover svg, .thumb svg { display: block; width: 100%; height: auto; }
.progress { margin-top: 18px; max-width: 420px; }
.progress .bar { height: 6px; background: rgba(255,255,255,.12); border-radius: 6px; overflow: hidden; }
.progress .fill { height: 100%; background: var(--accent); }
.progress .lbl { font-size: 13px; color: var(--muted); margin-top: 6px; }
.tally { display: flex; align-items: center; gap: 32px; padding: 18px 22px; background: var(--dark2); border: 1px solid var(--line);
         border-radius: 10px; margin-bottom: 26px; flex-wrap: wrap; }
.tally .num { font-family: var(--display); font-size: 40px; line-height: 1; color: var(--accent); }
.tally .lab { font-size: 13px; color: var(--muted); }
.tally .note { font-size: 13px; color: var(--muted); flex: 1; min-width: 220px; }
.row { margin-bottom: 30px; }
.row-head { display: flex; align-items: baseline; justify-content: space-between; margin-bottom: 12px; }
.row-head h2 { font-size: 19px; }
.row-head a { font-size: 13px; color: var(--muted); }
.rail { display: flex; gap: 16px; overflow-x: auto; padding-bottom: 6px; scrollbar-width: thin; }
.card { flex: 0 0 290px; background: var(--card); border: 1px solid var(--line); border-radius: 10px; overflow: hidden; display: flex; flex-direction: column; }
.card .cover { position: relative; aspect-ratio: 16/9; }
.card .body { padding: 12px 14px 14px; display: flex; flex-direction: column; gap: 8px; flex: 1; }
.card .title { font-weight: 700; font-size: 14.5px; line-height: 1.3; }
.meta { display: flex; gap: 8px; align-items: center; flex-wrap: wrap; font-size: 12px; color: #cfd8cf; }
.meta .dot { width: 3px; height: 3px; background: var(--muted); border-radius: 50%; }
.status { font-size: 11px; font-weight: 700; padding: 3px 8px; border-radius: 4px; letter-spacing: .02em; white-space: nowrap; }
.status.done { background: var(--accent); color: var(--dark); }
.status.prog { background: rgba(212,255,0,.14); color: var(--accent); }
.status.none { background: rgba(255,255,255,.08); color: #cfd8cf; }
.status.held { background: rgba(255,255,255,.08); color: var(--muted); }
.card .acts { display: flex; gap: 8px; align-items: center; margin-top: auto; padding-top: 4px; flex-wrap: wrap; }
.card .acts .btn-p { flex: 1; }
.card .files { font-size: 12px; color: var(--muted); display: flex; gap: 10px; flex-wrap: wrap; }
.card .files a { color: #cfd8cf; text-decoration: underline; text-underline-offset: 2px; }
.card.series { flex-basis: 340px; }
.series-parts { font-size: 12.5px; color: #cfd8cf; list-style: none; display: grid; gap: 3px; }
.series-parts li::before { content: ''; display: inline-block; width: 8px; height: 8px; border-radius: 50%; border: 1.5px solid var(--muted); margin-right: 8px; }
.series-parts li.done::before { background: var(--accent); border-color: var(--accent); }
.series-parts li.prog::before { border-color: var(--accent); }
.page-head { display: grid; grid-template-columns: 520px 1fr; gap: 36px; align-items: start; padding: 32px 40px; border-bottom: 1px solid var(--line);
             background: linear-gradient(180deg, #13291A, #0D1F0E); }
.page-head h1 { font-family: var(--display); font-weight: 400; font-size: 54px; line-height: .95; margin: 8px 0 12px; }
.page-head .intro { color: #cfd8cf; max-width: 640px; }
.crumb { font-size: 13px; color: var(--muted); margin-bottom: 4px; }
.crumb a:hover { color: var(--white); }
.facts { display: flex; gap: 10px; flex-wrap: wrap; margin: 14px 0 6px; }
.fact { font-size: 13px; padding: 5px 10px; border-radius: 4px; background: rgba(255,255,255,.07); color: #e3eae3; }
.section-title { font-size: 19px; margin: 0 0 14px; }
.part { display: grid; grid-template-columns: 240px 1fr 220px; gap: 20px; align-items: center; background: var(--card); border: 1px solid var(--line);
        border-radius: 10px; padding: 14px; margin-bottom: 12px; }
.part .cover { border-radius: 6px; overflow: hidden; aspect-ratio: 16/9; }
.part h3 { font-size: 16px; margin: 2px 0 6px; }
.part p { font-size: 13.5px; color: var(--muted); }
.part .side { display: flex; flex-direction: column; gap: 8px; align-items: stretch; }
.part .side .status { align-self: flex-start; }
.certno { font-family: ui-monospace, Menlo, monospace; font-size: 12px; color: var(--accent); }
.two-col { display: grid; grid-template-columns: 1fr 420px; gap: 32px; align-items: start; }
.panel { background: var(--card); border: 1px solid var(--line); border-radius: 10px; padding: 20px; }
.panel h2 { font-size: 18px; margin-bottom: 10px; }
.panel ul { padding-left: 18px; color: #cfd8cf; font-size: 14px; display: grid; gap: 6px; }
.materials { display: grid; grid-template-columns: 1fr 1fr; gap: 12px; margin-bottom: 20px; }
.material { background: var(--dark2); border: 1px solid var(--line); border-radius: 8px; padding: 16px; display: flex; gap: 14px; align-items: center; }
.material:hover { border-color: var(--accent); }
.material svg { width: 34px; height: 34px; color: var(--accent); flex: 0 0 auto; }
.material b { display: block; font-size: 15px; }
.material span { font-size: 13px; color: var(--muted); }
.complete { background: #F5F5F0; color: var(--dark); border-radius: 10px; padding: 22px; position: sticky; top: 84px; }
.complete h2 { font-size: 20px; margin-bottom: 4px; }
.complete .step { display: flex; gap: 10px; align-items: flex-start; font-size: 14px; margin: 12px 0; }
.complete .step b.n { flex: 0 0 24px; height: 24px; border-radius: 50%; background: var(--dark); color: var(--accent); font-size: 12px;
                      display: inline-flex; align-items: center; justify-content: center; }
.complete .step.ok b.n { background: #4d7c0f; color: #fff; }
.complete label.name { display: block; font-size: 13px; font-weight: 700; margin: 14px 0 4px; }
.complete input[type=text] { width: 100%; padding: 10px 12px; border: 1px solid #c9cdbf; border-radius: 6px; font: inherit; font-size: 15px; background: #fff; }
.complete .hint { font-size: 12.5px; color: #5C6B5D; margin-top: 4px; }
.declare { display: flex; gap: 10px; align-items: flex-start; margin: 16px 0; padding: 12px; border: 1px solid #c9cdbf; border-radius: 6px; background: #fff; font-size: 14px; cursor: pointer; }
.declare input { width: 20px; height: 20px; flex: 0 0 20px; accent-color: #0D1F0E; margin-top: 1px; }
.complete .btn-p { width: 100%; background: var(--dark); color: var(--accent); padding: 14px; font-size: 15px; white-space: normal; line-height: 1.3; }
.complete .small { font-size: 12.5px; color: #5C6B5D; margin-top: 12px; }
.complete .locked { font-size: 13px; color: #5C6B5D; background: #e9ebe0; border-radius: 6px; padding: 10px 12px; margin-top: 10px; }
.complete .err { font-size: 13px; color: #b91c1c; background: #fef2f2; border: 1px solid #fca5a5; border-radius: 6px; padding: 10px 12px; margin-top: 10px; }
.issued { border-top: 1px solid #d8dccd; margin-top: 16px; padding-top: 16px; }
.issued .certno { font-family: ui-monospace, Menlo, monospace; font-weight: 700; color: #4d7c0f; font-size: 16px; }
.issued .acts { display: flex; gap: 8px; margin-top: 12px; }
.issued .acts .btn { flex: 1; }
.issued a.u { text-decoration: underline; }
.btn-dark { background: var(--dark); color: var(--white); }
.btn-line { background: transparent; color: var(--dark); border: 1px solid var(--dark); }
.cert-table { width: 100%; border-collapse: collapse; background: var(--card); border: 1px solid var(--line); border-radius: 10px; overflow: hidden; }
.cert-table th { text-align: left; font-size: 11px; font-weight: 700; color: var(--muted); text-transform: uppercase; letter-spacing: .08em;
                 padding: 12px 14px; border-bottom: 1px solid var(--line); background: var(--dark2); }
.cert-table td { padding: 12px 14px; border-bottom: 1px solid var(--line); font-size: 14px; vertical-align: middle; }
.cert-table tr:last-child td { border-bottom: 0; }
.cert-table .certno { font-size: 13px; }
.cert-table .t { display: flex; gap: 12px; align-items: center; }
.cert-table .t .thumb { width: 96px; flex: 0 0 96px; border-radius: 4px; overflow: hidden; aspect-ratio: 16/9; }
.cert-table a.lnk { color: var(--accent); font-weight: 600; font-size: 13px; white-space: nowrap; margin-right: 18px; }
.toolbar { display: flex; gap: 12px; align-items: center; justify-content: space-between; margin-bottom: 16px; flex-wrap: wrap; }
.select { background: var(--dark2); border: 1px solid var(--line); border-radius: 6px; padding: 8px 12px; font-size: 14px; color: #cfd8cf; }
.upsell { background: linear-gradient(135deg,#0D1F0E,#1a2f1b); border: 1px solid var(--line); border-radius: 12px; padding: 28px 32px; margin-bottom: 28px; }
.foot { text-align: center; font-size: 12px; color: var(--muted); padding: 20px 16px 30px; }
.empty { color: var(--muted); padding: 20px 0; font-size: 14px; }
@media (max-width: 700px) {
  .topbar { padding: 0 16px; gap: 12px; height: 56px; }
  .topbar .nav { display: none; }
  .who { display: none; }
  .brand { font-size: 24px; }
  .tabbar { display: flex !important; }
  .wrap { padding: 18px 16px 90px; }
  .hero { grid-template-columns: 1fr; gap: 18px; padding: 18px 16px 22px; }
  .hero .poster { order: -1; }
  .hero h1 { font-size: 42px; }
  .hero .sub { font-size: 14.5px; }
  .card { flex-basis: 236px; }
  .card.series { flex-basis: 270px; }
  .tally { gap: 18px; padding: 14px 16px; }
  .tally .num { font-size: 32px; }
  .page-head { grid-template-columns: 1fr; padding: 16px; gap: 16px; }
  .page-head h1 { font-size: 40px; }
  .part { grid-template-columns: 110px 1fr; gap: 12px; }
  .part .side { grid-column: 1 / -1; flex-direction: row; flex-wrap: wrap; }
  .part .side .btn { flex: 1; }
  .two-col { grid-template-columns: 1fr; }
  .materials { grid-template-columns: 1fr; }
  .complete { position: static; }
  .cert-table thead { display: none; }
  .cert-table, .cert-table tbody, .cert-table tr, .cert-table td { display: block; width: 100%; }
  .cert-table tr { border-bottom: 1px solid var(--line); padding: 8px 0; }
  .cert-table td { border: 0; padding: 4px 14px; }
  .cert-table td.acts { display: flex; gap: 16px; padding-bottom: 12px; }
  .foot { padding-bottom: 90px; }
}
.tabbar { display: none; position: fixed; left: 0; right: 0; bottom: 0; height: 64px; background: #0A180B; border-top: 1px solid var(--line);
          justify-content: space-around; align-items: center; font-size: 11px; color: var(--muted); z-index: 6; }
.tabbar a { display: flex; flex-direction: column; align-items: center; gap: 3px; }
.tabbar a.on { color: var(--accent); }
.tabbar svg { width: 20px; height: 20px; }
"""

ICON = {
    "home": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M3 11l9-7 9 7v9h-6v-6H9v6H3z"/></svg>',
    "stack": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="3" y="4" width="18" height="12" rx="2"/><path d="M6 20h12"/></svg>',
    "cert": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="3" y="4" width="18" height="13" rx="1"/><circle cx="12" cy="19" r="2.5"/><path d="M7 9h10M7 12h6"/></svg>',
    "deck": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8"><rect x="2" y="4" width="20" height="13" rx="1.5"/><path d="M8 21h8M12 17v4M6 8h7M6 11h10"/></svg>',
    "notes": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8"><path d="M6 2h9l5 5v15H6z"/><path d="M15 2v5h5M9 12h8M9 16h8M9 8h3"/></svg>',
    "out": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M10 4H5v16h5M14 8l5 4-5 4M19 12H9"/></svg>',
}


# ── The poster template ─────────────────────────────────────────────────────
# One line-drawing poster for every cover: a kicker, a short title, an optional part
# label and a line motif chosen from the title. It carries no claims. The JavaScript
# version in landing-page/courses.html draws the same picture for the public site.

def short_title(title: str) -> str:
    t = re.sub(r"^.*Series, Part \d+:\s*", "", title)
    if ":" in t:
        t = t.split(":")[0]
    return t


def kicker_for(course: dict, text: dict) -> str:
    if course.get("series"):
        return "Field Work"
    if text.get("where") == "S":
        return "Scotland"
    return {"DEA": "For DEAs", "RA": "Retrofit", "ALL": "All assessors"}.get(text.get("strand", ""), "")


def motif_for(text: str) -> str:
    t = text.lower()
    if re.search(r"insulation|wall", t):
        return "layers"
    if re.search(r"heat pump|heating|boiler|hot water|heat loss", t):
        return "fan"
    if re.search(r"ventilat|airtight|breathe", t):
        return "flow"
    if re.search(r"damp|moisture|condensation|mould|floors|roofs and lofts", t):
        return "drop"
    if "window" in t:
        return "window"
    if "roof" in t:
        return "roof"
    if re.search(r"solar|renewable|lighting|pv", t):
        return "sun"
    if "scotland" in t:
        return "contour"
    return "meridian"


MOTIFS = {
    "layers": "<g>" + "".join(f'<rect x="{300 + i * 26}" y="40" width="18" height="190" rx="2"/>' for i in range(5))
              + '<path d="M290 80h150M290 135h150M290 190h150" opacity=".5"/></g>',
    "fan": '<g><circle cx="370" cy="135" r="92"/><circle cx="370" cy="135" r="14"/>'
           + "".join(f'<path transform="rotate({a} 370 135)" d="M370 121c10-40 40-62 58-50 10 18-20 42-58 50z"/>' for a in (0, 72, 144, 216, 288))
           + "</g>",
    "flow": "<g>" + "".join(f'<path d="M280 {60 + i * 38}c40-26 80 26 120 0s60-12 70 0"/>' for i in range(5))
            + '<path d="M455 50l15 10-15 10M455 202l15 10-15 10"/></g>',
    "drop": '<g><path d="M370 40c38 58 70 96 70 132a70 70 0 0 1-140 0c0-36 32-74 70-132z"/><path d="M335 175a36 36 0 0 0 30 34" opacity=".6"/><path d="M290 250h160" opacity=".5"/></g>',
    "window": '<g><rect x="300" y="40" width="140" height="190" rx="3"/><path d="M370 40v190M300 135h140"/><path d="M285 245h170" opacity=".5"/></g>',
    "roof": '<g><path d="M270 170l100-110 100 110"/><path d="M300 170v70h140v-70"/><path d="M330 128h80" opacity=".6"/></g>',
    "sun": '<g><circle cx="370" cy="120" r="40"/>'
           + "".join(f'<path transform="rotate({a} 370 120)" d="M370 60v-24"/>' for a in (0, 45, 90, 135, 180, 225, 270, 315))
           + '<path d="M290 230l40-50h120l-40 50z" opacity=".7"/></g>',
    "contour": "<g>" + "".join(f'<ellipse cx="380" cy="140" rx="{30 + i * 22}" ry="{18 + i * 16}" transform="rotate(-18 380 140)"/>' for i in range(5)) + "</g>",
    "meridian": '<g><circle cx="370" cy="135" r="90"/><path d="M370 45v180"/><path d="M370 45q60 90 0 180"/><path d="M280 135h180" opacity=".4"/><circle cx="370" cy="135" r="6" fill="#D4FF00"/></g>',
}


def _wrap_words(text: str, max_len: int) -> list[str]:
    lines, cur = [], ""
    for w in text.split():
        if len((cur + " " + w).strip()) > max_len and cur:
            lines.append(cur)
            cur = w
        else:
            cur = (cur + " " + w).strip()
    if cur:
        lines.append(cur)
    return lines


def _fmt(n: float) -> str:
    return f"{n:g}"


def poster(kicker: str, title: str, part: str = "", motif: str = "meridian") -> str:
    """Inline SVG, 480 by 270, so the page's own fonts are used."""
    max_len, size = 13, 48
    lines = _wrap_words(title.upper(), max_len)
    if len(lines) > 3:
        max_len, size = 17, 38
        lines = _wrap_words(title.upper(), max_len)
    if len(lines) > 3:
        lines = lines[:3]
        lines[2] += "…"
    y0 = 230 - (len(lines) - 1) * size * 0.95 - (34 if part else 0)
    text_lines = "".join(
        f'<text x="24" y="{_fmt(y0 + i * size * 0.95)}" fill="#FFFFFF" font-family="Bebas Neue, Impact, sans-serif" font-size="{size}" letter-spacing="1">{_esc(l)}</text>'
        for i, l in enumerate(lines))
    part_label = ""
    if part:
        part_label = (f'<rect x="24" y="214" width="{_fmt(len(part) * 8.4 + 20)}" height="26" rx="3" fill="#D4FF00"/>'
                      f'<text x="34" y="232" fill="#0D1F0E" font-family="DM Sans, Arial" font-weight="700" font-size="12.5" letter-spacing="1.5">{_esc(part.upper())}</text>')
    return (f'<svg viewBox="0 0 480 270" xmlns="http://www.w3.org/2000/svg" role="img" aria-label="{_esc(title)}">'
            '<defs><linearGradient id="g" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#16301A"/><stop offset="1" stop-color="#0A170B"/></linearGradient></defs>'
            '<rect width="480" height="270" fill="url(#g)"/>'
            f'<g fill="none" stroke="#D4FF00" stroke-width="2.4" stroke-linecap="round" stroke-linejoin="round" opacity=".35">{MOTIFS.get(motif, MOTIFS["meridian"])}</g>'
            '<rect x="24" y="24" width="4" height="18" fill="#D4FF00"/>'
            f'<text x="36" y="39" fill="#D4FF00" font-family="DM Sans, Arial" font-weight="700" font-size="13" letter-spacing="2">{_esc(kicker.upper())}</text>'
            f"{text_lines}{part_label}"
            '<text x="456" y="250" text-anchor="end" fill="#FFFFFF" opacity=".55" font-family="Bebas Neue, Impact, sans-serif" font-size="17" letter-spacing="2">MERIDIAN CPD</text>'
            "</svg>")


def course_poster(course: dict, text: dict, parts_total: int = 0) -> str:
    title = str(course.get("title", ""))
    part = f"Part {course['part']} of {parts_total}" if course.get("series") and parts_total else ""
    return poster(kicker_for(course, text), short_title(title), part, motif_for(title))


def series_poster(series_title: str) -> str:
    return poster("Field Work series", series_title.replace("Field Work: ", ""), "Three parts", motif_for(series_title))


# ── Small helpers for the pages ───────────────────────────────────────────────

def hours_label(h) -> str:
    h = float(h or 0)
    return f"{h:g} CPD hour{'' if h == 1 else 's'}"


_MONTHS = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]


def fmt_date(iso: str) -> str:
    """'2026-11-06T12:00:00+00:00' -> '6 Nov 2026'."""
    s = str(iso or "")[:10]
    try:
        y, m, d = s.split("-")
        return f"{int(d)} {_MONTHS[int(m) - 1]} {y}"
    except (ValueError, IndexError):
        return s


def topbar(name: str, on: str) -> str:
    items = [("Home", "/my-cpd/dashboard"), ("Series", "/my-cpd/series"), ("My certificates", "/my-cpd/certificates")]
    refer = bool(os.environ.get("REFERRAL_COUPON_ID", "").strip())  # refer a colleague is on (referrals.py)
    if refer:
        items.append(("Refer a colleague", "/my-cpd/refer"))
    nav = "".join(f'<a href="{h}" class="{"on" if t == on else ""}">{t}</a>' for t, h in items)
    return f"""<header class="topbar"><a class="brand" href="/my-cpd/dashboard">MERIDIAN <span>CPD</span></a>
  <nav class="nav">{nav}</nav><div class="grow"></div>
  <span class="who">{_esc(name)}</span><a class="signout" href="/my-cpd/logout">Sign out</a></header>
<nav class="tabbar">
  <a href="/my-cpd/dashboard" class="{'on' if on == 'Home' else ''}">{ICON['home']}Home</a>
  <a href="/my-cpd/series" class="{'on' if on == 'Series' else ''}">{ICON['stack']}Series</a>
  <a href="/my-cpd/certificates" class="{'on' if on == 'My certificates' else ''}">{ICON['cert']}Certificates</a>
  {f'<a href="/my-cpd/refer" class="{"on" if on == "Refer a colleague" else ""}">{ICON["stack"]}Refer</a>' if refer else ""}
  <a href="/my-cpd/logout">{ICON['out']}Sign out</a>
</nav>"""


def page(title: str, body: str) -> str:
    return f"""<!DOCTYPE html>
<html lang="en-GB"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
{FONTS}<title>{_esc(title)} | Meridian CPD</title><style>{CSS}</style></head>
<body>{body}
<p class="foot">Meridian CPD · meridiancpd.co.uk · hello@meridiancpd.co.uk · Check your own scheme's CPD rules.</p>
</body></html>"""
