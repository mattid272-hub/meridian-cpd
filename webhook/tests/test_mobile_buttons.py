"""Buttons on a phone (board row mer-app-mobile-buttons, Matt's iPhone, 10 Nov 2026):
'Buy the series, £39.99' spilled out of its button and 'See the course' ran into Info,
because the card's main button was allowed to shrink below its label (min-width: 0 with
white-space: nowrap). This checks the rules that stop it, in the member area and on the
public courses page, and that Sign out shows once on a phone (the bottom bar).
Run: python3 tests/test_mobile_buttons.py (or python -m pytest -q from webhook/)."""
import re, sys
from pathlib import Path
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent))
import member_ui

fails = 0
def check(name, cond):
    global fails
    print(("PASS " if cond else "FAIL ") + name)
    fails += 0 if cond else 1

css = member_ui.CSS
phone = css.split("@media (max-width: 700px) {", 1)[1].split("\n}\n", 1)[0]
check("a card's main button never shrinks below its label", "min-width: 0" not in css.split(".card .acts .btn-p, .card .acts .btn-s.main", 1)[1].split("}", 1)[0])
check("on a phone a button's label wraps inside it", re.search(r"\.btn \{[^}]*white-space: normal", phone))
check("on a phone every button is at least 44px high", re.search(r"\.btn \{[^}]*min-height: 44px", phone))
check("on a phone the icon buttons are 44px square", re.search(r"\.icon-btn \{[^}]*width: 44px; height: 44px", phone))
check("on a phone the card's main action has its own line", ".card .acts .btn-p, .card .acts .btn-s.main { flex: 1 1 100%; }" in phone)
check("on a phone Sign out is in the bottom bar only", ".topbar .signout { display: none; }" in phone and ".tabbar { display: flex !important; }" in phone)
bar = member_ui.topbar("A Member", "Home")
check("both Sign out links are still in the page (top bar for desktop, bottom bar for phones)", bar.count('href="/my-cpd/logout"') == 2)

page = (HERE.parent.parent / "landing-page" / "courses.html").read_text()
pub = page.split("/* ── RESPONSIVE ── */", 1)[1].split("</style>", 1)[0]
check("public courses page: card buttons wrap their label and are 44px on a phone",
      ".card-acts, .series-acts { flex-wrap: wrap; }" in pub and re.search(r"\.card-btn-buy, \.card-btn-detail \{[^}]*min-height: 44px;[^}]*white-space: normal", pub))

# Every other tap target on a phone (13 Nov 2026 check after PR #78 and #80 went live): the
# topic chips, the bottom bar's links and the brand link in the member area; the topic and
# nation chips, the code's Apply button and the course window's close button on courses.html.
check("on a phone the member area's topic chips are 44px", re.search(r"\.chip \{[^}]*min-height: 44px;[^}]*min-width: 44px", phone))
check("on a phone the bottom bar's links are 44px", re.search(r"\.tabbar a \{[^}]*min-width: 44px; min-height: 44px", phone))
check("on a phone the brand link is 44px high", re.search(r"\.brand \{[^}]*min-height: 44px", phone))
check("public courses page: chips and Apply are 44px on a phone", ".filter-tab, .nation-chip, .promo-apply-btn { min-height: 44px; }" in pub)
check("public courses page: the window's close button is 44px square on a phone", re.search(r"\.modal-close \{ min-width: 44px; min-height: 44px", pub))

if fails:
    raise SystemExit(f"{fails} check(s) failed")
print("all passed")
