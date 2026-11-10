"""Platform Phase 2: favourites and read later, the CPD record PDF, the streaming
dashboard (rows from tags, newest-series hero, search and chips, full cards), and the
public pages (no course counts, PR #56's line, the new home hero and How certificates work).
Run: python3 tests/test_platform_phase2.py (or python -m pytest -q from webhook/)."""
import os, re, sys, types
from datetime import date, datetime, timezone
from pathlib import Path
os.environ.update(STRIPE_SECRET_KEY="sk_test_x", STRIPE_WEBHOOK_SECRET="whsec_x", SUPABASE_URL="https://example.supabase.co",
                  SUPABASE_SERVICE_ROLE_KEY="eyJhbGciOiJIUzI1NiJ9.eyJyb2xlIjoic2VydmljZV9yb2xlIn0.x", SESSION_SECRET="s",
                  ADMIN_PASSWORD="test-admin", DASHBOARD_SECRET="dash-secret-for-tests", UNSUBSCRIBE_SECRET="u",
                  STRIPE_PRICE_SINGLE="price_single", STRIPE_PRICE_SUBSCRIPTION="price_sub", STRIPE_PRICE_SERIES="price_series")
HERE = Path(__file__).resolve().parent
ROOT = HERE.parent.parent
sys.path.insert(0, str(HERE.parent))
import main, member_ui, cpd_record
from fastapi.testclient import TestClient

YEAR = datetime.now(timezone.utc).year


class Res:
    def __init__(self, data): self.data, self.count = data, len(data)
class Q:
    def __init__(s, db, t): s.db, s.t, s.f, s.op, s.pl, s.o = db, t, [], "select", None, None
    def _gone(s):
        if s.t == "member_marks" and s.db.get("_no_marks"):
            raise RuntimeError('relation "public.member_marks" does not exist (test)')
    def select(s, *a, **k): return s
    def eq(s, c, v): s.f.append(lambda r, c=c, v=v: r.get(c) == v); return s
    def in_(s, c, v): s.f.append(lambda r, c=c, v=v: r.get(c) in v); return s
    def order(s, c, desc=False, **k): s.o = (c, desc); return s
    def limit(s, *a): return s
    @property
    def not_(s): s._neg = True; return s
    def is_(s, c, _n):
        neg = getattr(s, "_neg", False); s._neg = False
        s.f.append((lambda r, c=c: r.get(c) is not None) if neg else (lambda r, c=c: r.get(c) is None)); return s
    def insert(s, row): s.op, s.pl = "insert", row; return s
    def update(s, row): s.op, s.pl = "update", row; return s
    def delete(s): s.op = "delete"; return s
    def execute(s):
        s._gone()
        rows = s.db.setdefault(s.t, [])
        if s.op == "insert":
            if s.t == "member_marks" and s.db.get("_race"):
                s.db["_race"] = False  # the other click's row lands first, then ours hits the unique index
                rows.append(dict(s.pl, id="race"))
                raise RuntimeError("{'code': '23505', 'message': 'duplicate key value violates unique constraint \"member_marks_member_id_course_id_kind_key\"'}")
            row = dict(s.pl); row.setdefault("id", f"{s.t}-{len(rows) + 1}")
            row.setdefault("created_at", datetime.now(timezone.utc).isoformat()); rows.append(row); return Res([row])
        hit = [r for r in rows if all(f(r) for f in s.f)]
        if s.op == "delete":
            s.db[s.t] = [r for r in rows if r not in hit]; return Res(hit)
        if s.op == "select" and s.t == "member_marks" and s.db.get("_race"):
            return Res([])  # the existence check runs before the other click's row lands
        if s.op == "update":
            [r.update(s.pl) for r in hit]
        if s.o: hit = sorted(hit, key=lambda r: str(r.get(s.o[0]) or ""), reverse=s.o[1])
        return Res(hit)


db = {
    "members": [
        {"id": "bea", "email": "bea@example.com", "name": "Bea Buyer", "plan": "single", "joined_at": f"{YEAR}-01-05T10:00:00+00:00"},
        {"id": "sue", "email": "sue@example.com", "name": "Sue Sub", "plan": "subscription", "stripe_customer_id": "cus_s",
         "subscription_status": "active", "subscription_period_end": f"{YEAR + 1}-01-01T00:00:00+00:00", "joined_at": f"{YEAR}-01-05T10:00:00+00:00"},
        {"id": "empty", "email": "empty@example.com", "name": "Ed Empty", "plan": "single", "joined_at": f"{YEAR}-01-05T10:00:00+00:00"},
    ],
    "purchases": [
        {"id": "p1", "member_id": "bea", "course_id": "MER-DEA-001", "amount_gbp": 0},
        {"id": "p2", "member_id": "bea", "course_id": "MER-ALL-019", "amount_gbp": 19.99},
    ],
    "completions": [
        {"id": "c1", "member_id": "bea", "course_id": "MER-DEA-001", "completion_token": "t1", "completed_at": f"{YEAR}-03-01T09:00:00+00:00", "downloaded_at": f"{YEAR}-03-01T08:00:00+00:00"},
        {"id": "c2", "member_id": "bea", "course_id": "MER-ALL-019", "completion_token": "t2", "completed_at": None, "downloaded_at": f"{YEAR}-11-01T08:00:00+00:00"},
    ],
    "certificates": [
        {"id": "z1", "member_id": "bea", "cert_number": f"MER-{YEAR}-0101", "course_id": "MER-DEA-001", "member_name": "Bea B. Buyer",
         "course_title": main.COURSES["MER-DEA-001"]["title"], "cpd_hours": 2.0, "issued_at": f"{YEAR}-03-01T09:00:00+00:00"},
        {"id": "z2", "member_id": "bea", "cert_number": f"MER-{YEAR - 1}-0042", "course_id": "MER-DEA-004", "member_name": "Bea Buyer",
         "course_title": main.COURSES["MER-DEA-004"]["title"], "cpd_hours": 1.0, "issued_at": f"{YEAR - 1}-06-02T09:00:00+00:00"},
        {"id": "z3", "member_id": "sue", "cert_number": f"MER-{YEAR}-0102", "course_id": "MER-DEA-003", "member_name": "Sue Sub",
         "course_title": main.COURSES["MER-DEA-003"]["title"], "cpd_hours": 1.0, "issued_at": f"{YEAR}-04-02T09:00:00+00:00"},
    ],
    "member_marks": [
        {"id": "m0", "member_id": "sue", "course_id": "MER-RA-001", "kind": "favourite", "created_at": f"{YEAR}-10-01T00:00:00+00:00"},
    ],
}
main.supabase = types.SimpleNamespace(table=lambda t: Q(db, t),
    storage=types.SimpleNamespace(from_=lambda b: types.SimpleNamespace(download=lambda f: (_ for _ in ()).throw(RuntimeError("no catalogue")))))
main._refresh_under_review = lambda: None
main.UNDER_REVIEW.clear()
main.subscription_active = lambda m: m.get("plan") == "subscription"

c = TestClient(main.app, follow_redirects=False)
fails = 0
def check(name, cond):
    global fails
    print(("PASS " if cond else "FAIL ") + name)
    fails += 0 if cond else 1
cookie = lambda email: {"session_token": main._make_session_token(email)}
BEA, SUE, ED = cookie("bea@example.com"), cookie("sue@example.com"), cookie("empty@example.com")
JSON = {"Accept": "application/json"}
marks = lambda mid: sorted((m["course_id"], m["kind"]) for m in db["member_marks"] if m["member_id"] == mid)
flat = lambda t: " ".join(t.split())

# ── 1. Marks: add, remove, sign-in, owner only, bad input, table absent ──
r = c.post("/my-cpd/marks/add", data={"course_id": "MER-DEA-002", "kind": "favourite"}, headers=JSON)
check("adding a mark needs a sign-in (JSON 401)", r.status_code == 401 and marks("bea") == [])
r = c.post("/my-cpd/marks/add", data={"course_id": "MER-DEA-002", "kind": "favourite"})
check("and without script it sends you to sign in", r.status_code == 302 and r.headers["location"] == "/my-cpd")
r = c.post("/my-cpd/marks/add", data={"course_id": "MER-DEA-002", "kind": "favourite"}, headers=JSON, cookies=BEA)
check("a signed-in member adds a favourite", r.status_code == 200 and r.json() == {"ok": True, "on": True} and marks("bea") == [("MER-DEA-002", "favourite")])
c.post("/my-cpd/marks/add", data={"course_id": "MER-DEA-002", "kind": "favourite"}, headers=JSON, cookies=BEA)
check("adding it twice keeps one row", marks("bea") == [("MER-DEA-002", "favourite")])
r = c.post("/my-cpd/marks/add", data={"course_id": "MER-DEA-002", "kind": "read_later"}, cookies=BEA)
check("read later, posted without script, redirects back to the dashboard", r.status_code == 303 and r.headers["location"] == "/my-cpd/dashboard"
      and ("MER-DEA-002", "read_later") in marks("bea"))
r = c.post("/my-cpd/marks/add", data={"course_id": "MER-RA-002", "kind": "favourite", "member_id": "sue"}, headers=JSON, cookies=BEA)
check("a member id in the form is ignored: the mark is the signed-in member's", ("MER-RA-002", "favourite") in marks("bea")
      and ("MER-RA-002", "favourite") not in marks("sue"))
r = c.post("/my-cpd/marks/remove", data={"course_id": "MER-RA-001", "kind": "favourite", "member_id": "sue"}, headers=JSON, cookies=BEA)
check("one member cannot remove another member's mark", r.status_code == 200 and marks("sue") == [("MER-RA-001", "favourite")])
r = c.post("/my-cpd/marks/remove", data={"course_id": "MER-RA-002", "kind": "favourite"}, headers=JSON, cookies=BEA)
check("removing a mark", r.status_code == 200 and r.json() == {"ok": True, "on": False} and ("MER-RA-002", "favourite") not in marks("bea"))
db["_race"] = True
r = c.post("/my-cpd/marks/add", data={"course_id": "MER-RA-003", "kind": "favourite"}, headers=JSON, cookies=BEA)
check("a double click (duplicate key on insert) is a success, not a 503, and leaves one row",
      r.status_code == 200 and r.json() == {"ok": True, "on": True} and marks("bea").count(("MER-RA-003", "favourite")) == 1)
c.post("/my-cpd/marks/remove", data={"course_id": "MER-RA-003", "kind": "favourite"}, headers=JSON, cookies=BEA)
check("removing needs a sign-in too", c.post("/my-cpd/marks/remove", data={"course_id": "MER-RA-001", "kind": "favourite"}, headers=JSON).status_code == 401
      and marks("sue") == [("MER-RA-001", "favourite")])
check("an unknown kind or action is a 400", c.post("/my-cpd/marks/add", data={"course_id": "MER-DEA-002", "kind": "star"}, headers=JSON, cookies=BEA).status_code == 400
      and c.post("/my-cpd/marks/toggle", data={"course_id": "MER-DEA-002", "kind": "favourite"}, headers=JSON, cookies=BEA).status_code == 400)
check("an unknown course is a 404", c.post("/my-cpd/marks/add", data={"course_id": "MER-XXX-999", "kind": "favourite"}, headers=JSON, cookies=BEA).status_code == 404
      and c.post("/my-cpd/marks/add", data={"course_id": "SUBSCRIPTION", "kind": "favourite"}, headers=JSON, cookies=BEA).status_code == 404)
db["_no_marks"] = True
r = c.post("/my-cpd/marks/add", data={"course_id": "MER-DEA-005", "kind": "favourite"}, headers=JSON, cookies=BEA)
check("table absent: adding answers 503, not 500", r.status_code == 503 and r.json()["ok"] is False)
r = c.get("/my-cpd/dashboard", cookies=BEA)
check("table absent: the dashboard still loads, with no mark buttons and no Favourites row",
      r.status_code == 200 and 'class="mark"' not in r.text and "<h2>Favourites</h2>" not in r.text and "Read now" in r.text)
db["_no_marks"] = False

# ── 2. The dashboard ──
r = c.get("/my-cpd/dashboard", cookies=BEA); t = flat(r.text)
hero_sid = main._newest_series()
check("hero: the newest series, its parts, Series info", f'<h1>{main.SERIES[hero_sid]["title"]}</h1>' in t and "New series" in t
      and f'href="/my-cpd/series/{hero_sid}">Series info' in t and all(main._short(x) in t for x in main.SERIES[hero_sid]["courses"]))
check("hero for a series the member does not hold offers it at £39.99", hero_sid != "FW-INSULATION" and "Buy the series, £39.99" in t.split("</section>", 1)[0])
check("the hero is the series published last", max(main.COURSES[x]["published"] for x in main.SERIES[hero_sid]["courses"])
      == max(main.COURSES[x]["published"] for s in main.SERIES.values() for x in s["courses"]))
heads = re.findall(r"<h2>([^<]+)</h2>", r.text)
check("rows from the member's data and the tags, in order", heads[:3] == ["Continue where you left off", "Your series", "Favourites"]
      and "Read later" in heads and "Completed" in heads and "Field Work" in heads and "For DEAs" in heads and "Retrofit" in heads
      and "Scotland" in heads and heads.index("Continue where you left off") < heads.index("Completed"))
fav_row = r.text.split("<h2>Favourites</h2>", 1)[1].split("</section>", 1)[0]
check("Favourites row holds the member's favourite", 'data-course="MER-DEA-002"' in fav_row and fav_row.count('class="card"') == 1)
check("the New row is built from the published dates", ("New" in heads and "New this month" not in r.text) == any(
      "new" in member_ui.course_tags(v, main._course_text(k)) for k, v in main.COURSES.items() if k != "SUBSCRIPTION"))
deck_card = r.text.split('data-course="MER-ALL-019"', 1)[1].split('</div></div>', 1)[0]
check("deck card: Watch now, Info, favourite, read later, hours, status, Download links",
      'href="/download/MER-ALL-019" target="_blank" rel="noopener">Watch now' in deck_card and 'href="/my-cpd/course/MER-ALL-019">Info' in deck_card
      and 'aria-label="Add to favourites"' in deck_card and 'aria-label="Read later"' in deck_card and "2 CPD hours" in deck_card
      and "In progress" in deck_card and "Download slides" in deck_card and 'class="stmt"' in deck_card)
notes_card = r.text.split('data-course="MER-DEA-001"', 1)[1].split('</div></div>', 1)[0]
check("notes card: Read now, Certificate issued, a link to the certificate", ">Read now<" in notes_card and "Certificate issued" in notes_card
      and ">Certificate</a>" in notes_card and "Download PDF" in notes_card)
fav_btn = r.text.split('data-course="MER-DEA-002" data-kind="favourite"', 1)[1][:400]
check("a marked card shows the mark as on, with a remove form", 'class="icon-btn on"' in fav_btn and 'aria-pressed="true"' in fav_btn
      and 'action="/my-cpd/marks/remove" data-course="MER-DEA-002" data-kind="favourite"' in r.text)
other = r.text.split('data-course="MER-DEA-005"', 1)[1].split('</div></div>', 1)[0]
check("a course outside a single buyer's library: Not in your library, See the course, no download",
      "Not in your library" in other and "See the course" in other and "/download/" not in other and "courses.html?open=MER-DEA-005" in other)
results = r.text.split('<section class="results"', 1)[1]
catalogue = [k for k in main.COURSES if k != "SUBSCRIPTION" and main.is_available(k)]
check("the results list holds every course once, for search and chips", all(results.count(f'class="card" data-course="{k}"') == 1 for k in catalogue))
check("a failed save shows a note on the card and does not post the form again",
      "Could not save that. Try again." in r.text and "f.submit()" not in r.text and "!window.fetch" in r.text)
check("search box, topic chips and the script", 'id="q"' in r.text and 'placeholder="Search courses"' in r.text
      and all(f'data-tag="{tag}"' in r.text for tag, _ in member_ui.TOPICS) and "rows.classList.toggle('filtering'" in r.text)
check("cards carry their tags and search text", 'data-tags="field-work' in r.text and 'data-q="' in r.text)
check("the tally offers the CPD record for this year", f'href="/my-cpd/certificates/record.pdf?year={YEAR}">Download CPD record (PDF)' in r.text)
r = c.get("/my-cpd/dashboard", cookies=ED); t = flat(r.text)
check("a member with no data: 200, the hero, the library rows, no member rows, a zero tally",
      r.status_code == 200 and "New series" in t and "<h2>For DEAs</h2>" in t and "Continue where you left off" not in t
      and "<h2>Your series</h2>" not in t and "<h2>Completed</h2>" not in t and "<h2>Favourites</h2>" not in t
      and '<div class="num">0</div>' in t)
r = c.get("/my-cpd/dashboard", cookies=SUE); t = flat(r.text)
real_sc = main.series_courses
main.series_courses = lambda sid: []
r0 = c.get("/my-cpd/dashboard", cookies=SUE)
main.series_courses = real_sc
check("no complete series in the catalogue: the dashboard still loads, without the series hero",
      main.series_courses("FW-INSULATION") and r0.status_code == 200 and "New series" not in r0.text and "<h2>For DEAs</h2>" in r0.text)
check("a subscriber's cards all open the material", "See the course" not in t and "Not in your library" not in t
      and "<h2>Favourites</h2>" in t)
own = re.sub(r'data-q="[^"]*"|<svg.*?</svg>', "", r.text, flags=re.S)
for k, v in main.COURSE_TEXT.items():  # the catalogue's own descriptions name regulations and schemes; Phase 1 exempts them too
    own = own.replace(member_ui._esc(member_ui.statement(v["desc"])), "")
check("no 'accredited' or 'approved' in the dashboard's own words", not re.search(r"accredit|approved(?! document)", own, re.I))

# ── 3. Tags and the one-line statement ──
today = date(2026, 11, 8)
tag = lambda k: member_ui.course_tags(main.COURSES[k], main._course_text(k), today)
check("tags come from the catalogue", tag("MER-ALL-020")[0] == "field-work" and tag("MER-DEA-002") == ["dea"]
      and tag("MER-RA-001") == ["retrofit"] and tag("MER-ALL-001") == ["all"] and "scotland" in tag("MER-SCO-001")
      and "new" in tag("MER-SCO-001") and "new" not in tag("MER-DEA-002"))
stmts = [member_ui.statement(v["desc"]) for v in main.COURSE_TEXT.values()]
check("every course has a one-line statement under 122 characters", all(0 < len(x) <= 121 for x in stmts))

# ── 4. The CPD record PDF ──
check("the record needs a sign-in", c.get("/my-cpd/certificates/record.pdf").status_code == 302)
seen = []
real = main.generate_cpd_record
main.generate_cpd_record = lambda name, year, certs: (seen.append((name, year, [x["cert_number"] for x in certs])), real(name, year, certs))[1]
r = c.get("/my-cpd/certificates/record.pdf", cookies=BEA)
check("the record downloads as a PDF for this year", r.status_code == 200 and r.headers["content-type"].startswith("application/pdf")
      and r.content.startswith(b"%PDF") and f"Meridian-CPD-record-{YEAR}.pdf" in r.headers["content-disposition"])
check("only the member's own certificates for the year, with the name on their certificates", seen[-1] == ("Bea B. Buyer", YEAR, [f"MER-{YEAR}-0101"]))
r = c.get(f"/my-cpd/certificates/record.pdf?year={YEAR - 1}", cookies=BEA)
check("the year filter", r.status_code == 200 and seen[-1][1:] == (YEAR - 1, [f"MER-{YEAR - 1}-0042"]))
r = c.get("/my-cpd/certificates/record.pdf?year=1066", cookies=BEA)
check("a silly year falls back to this year", seen[-1][1] == YEAR)
r = c.get("/my-cpd/certificates/record.pdf", cookies=SUE)
check("another member's record never includes Bea's certificates", seen[-1][2] == [f"MER-{YEAR}-0102"])
r = c.get("/my-cpd/certificates/record.pdf", cookies=ED)
check("no certificates: still a PDF, with nothing listed", r.status_code == 200 and r.content.startswith(b"%PDF") and seen[-1][2] == [])
# A course certified twice (issued before the unique index): the earliest stands everywhere
# the member sees hours, so nothing is counted twice; nothing is deleted.
db["certificates"].append({"id": "z9", "member_id": "bea", "cert_number": f"MER-{YEAR}-0201", "course_id": "MER-DEA-001",
    "member_name": "Bea B. Buyer", "course_title": main.COURSES["MER-DEA-001"]["title"], "cpd_hours": 2.0, "issued_at": f"{YEAR}-05-01T09:00:00+00:00"})
r = c.get("/my-cpd/certificates/record.pdf", cookies=BEA)
check("a duplicate certificate for one course: the record lists the earliest only", seen[-1][2] == [f"MER-{YEAR}-0101"])
r = c.get("/my-cpd/certificates", cookies=BEA)
check("and My certificates shows it once", f"MER-{YEAR}-0101" in r.text and f"MER-{YEAR}-0201" not in r.text)
check("one_per_course keeps the earliest per course and the input order",
      [x["cert_number"] for x in main.one_per_course(sorted(db["certificates"], key=lambda x: x["issued_at"], reverse=True)) if x["member_id"] == "bea"]
      == [f"MER-{YEAR}-0101", f"MER-{YEAR - 1}-0042"])
check("the duplicate still verifies", c.get(f"/verify/MER-{YEAR}-0201").status_code == 200)
db["certificates"].pop()
main.generate_cpd_record = real
check("record.pdf is not read as a certificate number", c.get("/my-cpd/certificates/record.pdf", cookies=BEA).status_code == 200)
from reportlab import rl_config
rl_config.pageCompression = 0  # plain page streams, so the words can be read back
pdf = cpd_record.generate_cpd_record("A. N. Assessor", 2026, [db["certificates"][0]])
text = pdf.decode("latin-1")
check("the record shows name, year, course, number, verify address, total and the scheme line",
      all(s in text for s in ("A. N. Assessor", "CPD record 2026", f"MER-{YEAR}-0101", "/verify/", "Total", "Check your own scheme",
                              "Anyone can check a certificate at its verify address.")) and "beside it" not in text)
r = c.get("/my-cpd/certificates", cookies=BEA)
check("My certificates offers the record for the year shown", f'href="/my-cpd/certificates/record.pdf?year={YEAR}">Download CPD record (PDF)' in r.text)
r = c.get("/my-cpd/certificates?year=all", cookies=BEA)
check("for all years it offers this year's record", f'record.pdf?year={YEAR}"' in r.text)

# ── 5. The public pages ──
# a number of courses in words ("37 courses"; not "PAS 2035:2023 courses"), or the page computing one
COUNT = re.compile(r"(?<![:\d])\b\d+\s+(?:CPD\s+)?(?:[Cc]ourses|[Mm]odules)\b|(?<![\w.])(?:ALL_)?COURSES\.length|countAll|resultsMeta")
PR56 = "£79 a year until 31 December. £99 from 1 January 2027. Subscribe before then and you keep £79 for as long as you stay."
index = (ROOT / "landing-page" / "index.html").read_text(encoding="utf-8")
courses = (ROOT / "landing-page" / "courses.html").read_text(encoding="utf-8")
unent = lambda h: h.replace("&#163;", "£").replace("&pound;", "£")
for name, html in (("index.html", index), ("courses.html", courses)):
    check(f"{name}: no course count", not COUNT.search(html.split("const ALL_COURSES = [", 1)[0] + (html.split("\n];", 1)[1] if "\n];" in html else "")))
    check(f"{name}: PR #56's line word for word", PR56 in unent(html))
hero = index.split('<section id="hero">', 1)[1].split("</section>", 1)[0]
hero_css = index.split("/* ── SECTION 1: HERO", 1)[1].split("/* ── SECTION", 1)[0]
check("index.html: the hero shows the platform (My certificates, poster template), not stock imagery",
      "unsplash" not in hero and "unsplash" not in hero_css and 'class="hero-screen"' in hero and "<svg" in hero
      and "Your certificates.<br>In one place." in hero and "Download CPD record (PDF)" in hero
      and "Download any year as one PDF." in hero and "your year" not in hero)
check("index.html: the hero headline is sized to its own column beside the screen (no overlap at desktop widths)",
      "#hero .hero-headline { font-size: clamp(3.6rem, 6.6vw, 8rem); }" in hero_css and "min(560px, 38vw)" in hero_css)
check("index.html: the hero line as passed by the Matt check (no 'Practitioner-written')",
      '<p class="hero-sub">CPD for DEAs and Retrofit Assessors, written from the source documents.</p>' in hero
      and "Practitioner-written" not in index)
how = index.split('id="how"', 1)[1].split("</section>", 1)[0]
check("index.html: How certificates work, four plain steps", "How certificates<br>work." in how and '<span class="label on-light">Certificates</span>' in how and how.count('class="step"') == 4
      and all(w in how for w in ("Read", "Confirm", "Certificate", "QR")))
check("index.html: the structured data and meta tags are kept", 'application/ld+json' in index and '"legalName": "FistralAI Ltd"' in index
      and 'rel="canonical"' in index and 'property="og:image"' in index)
check("courses.html: topic rows, search and chips; series first, then the £79 strip (flex order), then the singles",
      'id="topicRows"' in courses and "function courseTags(" in courses and 'class="filter-tab topic-chip' in courses and 'id="searchInput"' in courses
      and courses.index('id="seriesGrid"') < courses.index('id="topicRows"') and ".sub-strip { order: -1; }" in courses
      and ".page-hero, .series-grid { order: -2; }" in courses and "Single courses, £19.99 each" in courses and "Buy, £19.99" in courses)
check("courses.html: the rolling row is called New, never New this month", "New this month" not in courses
      and "['new', 'New']" in courses and 'data-filter="new">New</button>' in courses)
check("courses.html: published dates mirror the app catalogue", all(
      f"'{k}': '{v['published']}'" in courses for k, v in main.COURSES.items() if k != "SUBSCRIPTION"))
for name, html in (("index.html", index), ("courses.html", courses)):
    body = html.split("const ALL_COURSES = [", 1)[0] + (html.split("\n];", 1)[1] if "\n];" in html else "")
    check(f"{name}: no accreditation words or 'unlock'", not re.search(r"accredited|cpd accredit|\bunlock", body, re.I))

print(f"\n{'ALL CHECKS PASSED' if not fails else f'{fails} FAILED'}")
if fails:
    raise SystemExit(1)
