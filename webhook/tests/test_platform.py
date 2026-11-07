"""Platform Phase 1: series pages, course pages with completion inside the app, My
certificates, the certificate PDF route, 90-day sign-in, sign-in from the thank-you page,
the poster template, and the public courses page led by the series.
Run from anywhere: python3 tests/test_platform.py (or python -m pytest -q from webhook/)."""
import os, re, sys, time, types
from datetime import datetime, timezone
from pathlib import Path
os.environ.update(STRIPE_SECRET_KEY="sk_test_x", STRIPE_WEBHOOK_SECRET="whsec_x", SUPABASE_URL="https://example.supabase.co",
                  SUPABASE_SERVICE_ROLE_KEY="eyJhbGciOiJIUzI1NiJ9.eyJyb2xlIjoic2VydmljZV9yb2xlIn0.x", SESSION_SECRET="s",
                  ADMIN_PASSWORD="test-admin", DASHBOARD_SECRET="dash-secret-for-tests", UNSUBSCRIBE_SECRET="u",
                  STRIPE_PRICE_SINGLE="price_single", STRIPE_PRICE_SUBSCRIPTION="price_sub", STRIPE_PRICE_SERIES="price_series")
HERE = Path(__file__).resolve().parent
ROOT = HERE.parent.parent
sys.path.insert(0, str(HERE.parent))
sys.path.insert(0, str(ROOT / "tools"))
import main, member_ui
from course_text import COURSE_TEXT
from build_course_text import read_site_courses
from fastapi.testclient import TestClient

YEAR = datetime.now(timezone.utc).year


class Res:
    def __init__(self, data): self.data, self.count = data, len(data)
class Q:
    def __init__(s, db, t): s.db, s.t, s.f, s.op, s.pl, s.o = db, t, [], "select", None, None
    def select(s, *a, **k): return s
    def eq(s, c, v): s.f.append(lambda r, c=c, v=v: r.get(c) == v); return s
    def in_(s, c, v): s.f.append(lambda r, c=c, v=v: r.get(c) in v); return s
    def like(s, c, pat): s.f.append(lambda r, c=c, p=pat.rstrip("%"): str(r.get(c) or "").startswith(p)); return s
    def order(s, c, desc=False, **k): s.o = (c, desc); return s
    def limit(s, *a): return s
    @property
    def not_(s): s._neg = True; return s
    def is_(s, c, _n):
        neg = getattr(s, "_neg", False); s._neg = False
        s.f.append((lambda r, c=c: r.get(c) is not None) if neg else (lambda r, c=c: r.get(c) is None)); return s
    def insert(s, row): s.op, s.pl = "insert", row; return s
    def update(s, row): s.op, s.pl = "update", row; return s
    def execute(s):
        rows = s.db.setdefault(s.t, [])
        if s.op == "insert":
            row = dict(s.pl); row.setdefault("id", f"{s.t}-{len(rows) + 1}")
            if s.t == "certificates": row.setdefault("issued_at", datetime.now(timezone.utc).isoformat())
            rows.append(row); return Res([row])
        hit = [r for r in rows if all(f(r) for f in s.f)]
        if s.op == "update":
            if s.db.get("_fail_update") and s.db["_fail_update"](s.t, s.pl): raise RuntimeError("update failed (test)")
            [r.update(s.pl) for r in hit]
        if s.o: hit = sorted(hit, key=lambda r: str(r.get(s.o[0]) or ""), reverse=s.o[1])
        if s.t == "completions" and s.op == "select":
            hit = [dict(r, members=next(m for m in s.db["members"] if m["id"] == r["member_id"])) for r in hit]
        return Res(hit)


now = time.time()
db = {
    "members": [
        {"id": "buyer", "email": "buyer@example.com", "name": "Bea Buyer", "plan": "single", "stripe_customer_id": "cus_b"},
        {"id": "sub", "email": "sub@example.com", "name": "Sue Sub", "plan": "subscription", "stripe_customer_id": "cus_s"},
        {"id": "other", "email": "other@example.com", "name": "Otto Other", "plan": "single", "stripe_customer_id": ""},
        {"id": "newb", "email": "new@example.com", "name": "Nia New", "plan": "single", "stripe_customer_id": ""},
    ],
    "purchases": [
        # Bea bought Field Work: Insulation last week and has Part 1 done already
        {"id": "p1", "member_id": "buyer", "course_id": "MER-ALL-019", "series_id": "FW-INSULATION", "amount_gbp": 13.33, "stripe_session_id": "cs_live_bea12345678", "thanks_signin_at": "2026-11-01T10:00:00+00:00"},
        {"id": "p2", "member_id": "buyer", "course_id": "MER-ALL-020", "series_id": "FW-INSULATION", "amount_gbp": 13.33, "stripe_session_id": "cs_live_bea12345678", "thanks_signin_at": "2026-11-01T10:00:00+00:00"},
        {"id": "p3", "member_id": "buyer", "course_id": "MER-ALL-021", "series_id": "FW-INSULATION", "amount_gbp": 13.33, "stripe_session_id": "cs_live_bea12345678", "thanks_signin_at": "2026-11-01T10:00:00+00:00"},
        {"id": "p4", "member_id": "other", "course_id": "MER-DEA-002", "amount_gbp": 19.99, "stripe_session_id": "cs_live_otto12345678"},
        # Nia has just bought a single course and is on the thank-you page
        {"id": "p5", "member_id": "newb", "course_id": "MER-DEA-001", "amount_gbp": 0, "stripe_session_id": "cs_live_nia123456789"},
        # Otto's older order, more than a week ago
        {"id": "p6", "member_id": "other", "course_id": "MER-DEA-003", "amount_gbp": 19.99, "stripe_session_id": "cs_live_ottoold12345"},
    ],
    "completions": [
        {"id": "c1", "member_id": "buyer", "course_id": "MER-ALL-019", "completion_token": "tok-019", "completed_at": f"{YEAR}-11-02T09:00:00+00:00", "downloaded_at": f"{YEAR}-11-02T08:00:00+00:00"},
        {"id": "c2", "member_id": "buyer", "course_id": "MER-ALL-020", "completion_token": "tok-020", "completed_at": None, "downloaded_at": None},
        {"id": "c3", "member_id": "buyer", "course_id": "MER-ALL-021", "completion_token": "tok-021", "completed_at": None, "downloaded_at": None},
        {"id": "c4", "member_id": "other", "course_id": "MER-DEA-002", "completion_token": "tok-otto", "completed_at": None, "downloaded_at": None},
        {"id": "c5", "member_id": "newb", "course_id": "MER-DEA-001", "completion_token": "tok-nia", "completed_at": None, "downloaded_at": None},
    ],
    "certificates": [
        {"id": "z1", "member_id": "buyer", "cert_number": f"MER-{YEAR}-0007", "course_id": "MER-ALL-019", "member_name": "Bea Buyer",
         "course_title": main.COURSES["MER-ALL-019"]["title"], "cpd_hours": 2.0, "issued_at": f"{YEAR}-11-02T09:00:00+00:00"},
        {"id": "z0", "member_id": "buyer", "cert_number": f"MER-{YEAR - 1}-0003", "course_id": "MER-DEA-004", "member_name": "Bea Buyer",
         "course_title": main.COURSES["MER-DEA-004"]["title"], "cpd_hours": 1.0, "issued_at": f"{YEAR - 1}-06-02T09:00:00+00:00"},
        {"id": "z2", "member_id": "other", "cert_number": f"MER-{YEAR}-0005", "course_id": "MER-DEA-003", "member_name": "Otto Other",
         "course_title": main.COURSES["MER-DEA-003"]["title"], "cpd_hours": 1.0, "issued_at": f"{YEAR}-09-02T09:00:00+00:00"},
    ],
}
main.supabase = types.SimpleNamespace(table=lambda t: Q(db, t),
    storage=types.SimpleNamespace(from_=lambda b: types.SimpleNamespace(download=lambda f: (_ for _ in ()).throw(RuntimeError("no catalogue")))))
main._refresh_under_review = lambda: None
main.UNDER_REVIEW.clear()

SESSIONS = {
    "cs_live_nia123456789": {"id": "cs_live_nia123456789", "status": "complete", "created": now - 30, "customer": None,
                             "customer_details": {"email": "new@example.com"}},
    "cs_live_ottoold12345": {"id": "cs_live_ottoold12345", "status": "complete", "created": now - 10 * 86400, "customer": None,
                             "customer_details": {"email": "other@example.com"}},
    "cs_live_bea12345678": {"id": "cs_live_bea12345678", "status": "complete", "created": now - 6 * 86400, "customer": "cus_b",
                            "customer_details": {"email": "buyer@example.com"}},
}
def _retrieve(sid):
    if sid not in SESSIONS:
        raise main.stripe.error.InvalidRequestError("No such checkout.session", "id")
    return SESSIONS[sid]
main.stripe.checkout.Session.retrieve = _retrieve
certs_sent = []
async def fake_cert(**k): certs_sent.append(k)
main.send_certificate_email = fake_cert
fail_cert_email = {"on": False}
async def flaky_cert(**k):
    if fail_cert_email["on"]: raise RuntimeError("Resend down (test)")
    certs_sent.append(k)
main.send_certificate_email = flaky_cert

c = TestClient(main.app, follow_redirects=False)
fails = 0
def check(name, cond):
    global fails
    print(("PASS " if cond else "FAIL ") + name)
    fails += 0 if cond else 1
cookie = lambda email: {"session_token": main._make_session_token(email)}
BEA, SUE, OTTO, NIA = cookie("buyer@example.com"), cookie("sub@example.com"), cookie("other@example.com"), cookie("new@example.com")
certs_of = lambda mid: [x for x in db["certificates"] if x["member_id"] == mid]
completion = lambda cid: next(x for x in db["completions"] if x["id"] == cid)
flat = lambda t: " ".join(t.split())

# ── 0. Catalogue text, series introductions and the words on the pages ──
site = {x["id"]: x for x in read_site_courses()}
check("course_text.py matches the public catalogue (ids, descriptions, objectives, strand, where)",
      set(site) == set(COURSE_TEXT) and all(
          site[k]["desc"] == COURSE_TEXT[k]["desc"] and list(site[k].get("objectives") or []) == COURSE_TEXT[k]["objectives"]
          and site[k]["strand"] == COURSE_TEXT[k]["strand"] and site[k]["where"] == COURSE_TEXT[k]["where"] for k in site))
check("every course in the app catalogue has text for its page", all(k in COURSE_TEXT for k in main.COURSES if k != "SUBSCRIPTION"))
check("every series has an introduction", set(main.SERIES_INTRO) == set(main.SERIES))
check("the Moisture introduction does not promise slides for every part (MER-ALL-018 is notes only)",
      "where a part has them" in main.SERIES_INTRO["FW-MOISTURE"] and "Slides for the site visit, written notes" not in main.SERIES_INTRO["FW-MOISTURE"])
banned = re.compile(r"accredit|approved(?! document)", re.I)  # "Approved Document F" is a regulation's name
check("no 'accredited' or 'approved' in the series introductions or the member UI",
      not any(banned.search(t) for t in main.SERIES_INTRO.values()) and not banned.search(Path(member_ui.__file__).read_text()))

# ── 1. Poster template ──
svg = member_ui.poster("Field Work series", "Insulation", "Three parts", "layers")
check("poster: inline SVG with kicker, title, part label and the Meridian mark, no claims",
      svg.startswith("<svg") and "FIELD WORK SERIES" in svg and ">INSULATION<" in svg and "THREE PARTS" in svg
      and "MERIDIAN CPD" in svg and not banned.search(svg))
check("poster: long titles wrap to at most three lines", member_ui.poster("x", "a very long course title that goes on and on and on and on", "", "fan").count("<text x=\"24\"") == 3)
check("poster: a title with a quote is escaped", "&#x27;" in member_ui.poster("x", "What's Changed", "", "meridian") or "&#39;" in member_ui.poster("x", "What's Changed", "", "meridian"))
check("every course and series gets a poster", all(main._poster(k).startswith("<svg") for k in main.COURSES if k != "SUBSCRIPTION")
      and all(member_ui.series_poster(s["title"]).startswith("<svg") for s in main.SERIES.values()))
check("short titles: the part prefix and the subtitle are dropped",
      main._short("MER-ALL-020") == "External Wall Insulation" and main._short("MER-DEA-001") == "RdSAP 10" and main._short("MER-ALL-018") == "Damp, Condensation and Thermal Bridging")

# ── 2. Sign-in: 90 days ──
tok = main._make_session_token("buyer@example.com")
exp = int(tok.split(":")[1])
check("session token lasts 90 days", abs(exp - (time.time() + 90 * 86400)) < 60 and main.SESSION_DAYS == 90)
r = main._signed_in("buyer@example.com"); sc = r.headers["set-cookie"]
check("session cookie: Max-Age 90 days, HttpOnly, Secure, SameSite=lax",
      f"Max-Age={90 * 86400}" in sc and "HttpOnly" in sc and "Secure" in sc and "SameSite=lax" in sc.replace("Lax", "lax"))
for path in ["/my-cpd/dashboard", "/my-cpd/series", "/my-cpd/series/FW-INSULATION", "/my-cpd/course/MER-ALL-020",
             "/my-cpd/certificates", f"/my-cpd/certificates/MER-{YEAR}-0007.pdf"]:
    r = c.get(path)
    check(f"{path} needs a sign-in", r.status_code == 302 and r.headers["location"] == "/my-cpd")
r = c.post("/my-cpd/course/MER-ALL-020/complete", data={"confirm": "on"})
check("completing needs a sign-in", r.status_code == 302 and not certs_of("buyer")[2:])

# ── 3. The course page and completion inside the app ──
r = c.get("/my-cpd/course/MER-ALL-020", cookies=BEA); t = flat(r.text)
check("course page: material links, objectives, the declaration and a locked button before the material is opened",
      r.status_code == 200 and 'href="/download/MER-ALL-020"' in t and 'href="/download/MER-ALL-020/notes"' in t
      and "Open the slide deck" in t and "Open the written notes" in t and "What you will be able to do" in t
      and COURSE_TEXT["MER-ALL-020"]["objectives"][0] in t
      and "I confirm I have read and understood the course material." in t
      and 'disabled>Confirm completion and get my certificate' in t and "Open the slide deck or the notes first" in t
      and "Part 2 of 3" in t and "Field Work: Insulation" in t and "England and Wales" in t and "No certificate yet" in t)
r = c.post("/my-cpd/course/MER-ALL-020/complete", data={"confirm": "on", "cert_name": "Bea Buyer"}, cookies=BEA)
check("confirm is refused until the material has been opened", r.status_code == 400 and "Open the slide deck or the notes first" in r.text
      and len(certs_of("buyer")) == 2 and completion("c2")["completed_at"] is None)
r = c.get("/download/MER-ALL-020/notes", cookies=BEA)
check("opening the notes counts as opening the course", r.status_code == 302 and r.headers["location"].endswith("MER-ALL-020.pdf")
      and completion("c2")["downloaded_at"])
r = c.get("/my-cpd/course/MER-ALL-020", cookies=BEA); t = flat(r.text)
check("after opening: the button is live and the page says In progress", "disabled" not in t.split('<form method="post"', 1)[1].split("</form>")[0]
      and "In progress" in t)
r = c.post("/my-cpd/course/MER-ALL-020/complete", data={"cert_name": "Bea Buyer"}, cookies=BEA)
check("the declaration must be ticked", r.status_code == 400 and "Tick the declaration" in r.text and len(certs_of("buyer")) == 2)
n_before = len(db["certificates"])
r = c.post("/my-cpd/course/MER-ALL-020/complete", data={"confirm": "on", "cert_name": "Bea B. Buyer"}, cookies=BEA)
mine = certs_of("buyer")
check("confirm issues the certificate at once and sends the email copy",
      r.status_code == 303 and r.headers["location"] == "/my-cpd/course/MER-ALL-020?issued=1&sent=1"
      and len(mine) == 3 and mine[-1]["course_id"] == "MER-ALL-020" and mine[-1]["member_name"] == "Bea B. Buyer"
      and mine[-1]["cpd_hours"] == 2.0 and completion("c2")["completed_at"] and len(certs_sent) == 1
      and certs_sent[0]["to_email"] == "buyer@example.com" and certs_sent[0]["cert_number"] == mine[-1]["cert_number"])
new_number = mine[-1]["cert_number"]
check("numbering follows the existing MER-YYYY-NNNN sequence", new_number == f"MER-{YEAR}-0008")
r = c.get(r.headers["location"], cookies=BEA); t = flat(r.text)
check("the course page now shows the certificate: number, Download PDF, Verify, My certificates, the email copy, next part",
      "Certificate issued" in t and new_number in t and f'href="/my-cpd/certificates/{new_number}.pdf"' in t
      and f'href="/verify/{new_number}"' in t and "Saved in" in t and "My certificates" in t
      and "A copy is on its way to your email" in t and "Next: Part 3, Internal Wall Insulation and Hidden Moisture" in t
      and "Your certificate has been issued." in t)
r = c.post("/my-cpd/course/MER-ALL-020/complete", data={"confirm": "on", "cert_name": "Bea Buyer"}, cookies=BEA)
check("a second confirm issues nothing more", r.status_code == 303 and len(certs_of("buyer")) == 3 and len(certs_sent) == 1)
# a second unused completion row for the same course (an old email link) cannot earn a second certificate either
db["completions"].append({"id": "c2b", "member_id": "buyer", "course_id": "MER-ALL-020", "completion_token": "tok-020-old", "completed_at": None, "downloaded_at": f"{YEAR}-11-03"})
r = c.post("/complete/tok-020-old", data={"confirm": "on", "cert_name": "Bea Buyer"})
check("the emailed link for an already-certified course retires without a second certificate",
      r.status_code == 200 and "already hold" in r.text and new_number in r.text and len(certs_of("buyer")) == 3 and completion("c2b")["completed_at"])
# the email copy failing does not stop the certificate
fail_cert_email["on"] = True
r = c.get("/download/MER-ALL-021", cookies=BEA)
r = c.post("/my-cpd/course/MER-ALL-021/complete", data={"confirm": "on", "cert_name": "Bea Buyer"}, cookies=BEA)
fail_cert_email["on"] = False
check("if the email copy fails the certificate is still issued and the page says so",
      r.status_code == 303 and r.headers["location"].endswith("?issued=1&sent=0") and len(certs_of("buyer")) == 4
      and "We could not send the email copy" in flat(c.get(r.headers["location"], cookies=BEA).text))
r = c.get("/my-cpd/course/MER-ALL-021", cookies=BEA)
check("a finished series offers the series page, not a next part", "Back to the series" in r.text and "Next: Part" not in r.text)

# ── 4. Access ──
r = c.get("/my-cpd/course/MER-ALL-022", cookies=BEA)
check("a course not in the member's library is a 404 with a way to buy it", r.status_code == 404 and "not in your library" in r.text and "courses.html?open=MER-ALL-022" in r.text)
r = c.post("/my-cpd/course/MER-ALL-022/complete", data={"confirm": "on"}, cookies=BEA)
check("nor can it be completed", r.status_code == 404 and len(certs_of("buyer")) == 4)
check("an unknown course is a 404", c.get("/my-cpd/course/MER-XXX-999", cookies=BEA).status_code == 404
      and c.get("/my-cpd/course/SUBSCRIPTION", cookies=BEA).status_code == 404)
r = c.get("/my-cpd/course/MER-ALL-022", cookies=SUE)
check("a subscriber can open any course, and a completion record is made for it",
      r.status_code == 200 and any(x["member_id"] == "sub" and x["course_id"] == "MER-ALL-022" for x in db["completions"]))
main.UNDER_REVIEW.add("MER-DEA-002")
r = c.get("/my-cpd/course/MER-DEA-002", cookies=OTTO)
check("a withdrawn course shows the being-updated page", r.status_code == 200 and "being updated" in r.text)
main.UNDER_REVIEW.discard("MER-DEA-002")

# ── 5. My certificates and the PDF ──
r = c.get("/my-cpd/certificates", cookies=BEA); t = flat(r.text)
check("My certificates lists this year's certificates with course, date, hours, number, Download PDF and Verify",
      r.status_code == 200 and t.count("Download PDF") == 3 and t.count(">Verify<") == 3
      and new_number in t and f"MER-{YEAR}-0007" in t and f"MER-{YEAR - 1}-0003" not in t
      and main.COURSES["MER-ALL-020"]["title"] in t and "2 CPD hours" in t and "Field Work: Insulation, Part 2" in t
      and f'href="/my-cpd/certificates/{new_number}.pdf"' in t and f'href="/verify/{new_number}"' in t)
check("the tally is by calendar year, with the scheme line", f"CPD hours in {YEAR}" in t and ">6<" in t and ">3<" in t
      and "Check your own scheme's CPD rules" in t)
r = c.get(f"/my-cpd/certificates?year={YEAR - 1}", cookies=BEA); t = flat(r.text)
check("the year filter shows last year's certificate and tally", f"MER-{YEAR - 1}-0003" in t and new_number not in t and f"CPD hours in {YEAR - 1}" in t and ">1<" in t)
r = c.get("/my-cpd/certificates?year=all", cookies=BEA); t = flat(r.text)
check("all years", t.count("Download PDF") == 4 and "CPD hours in all years" in t and ">7<" in t)
r = c.get("/my-cpd/certificates", cookies=NIA)
check("no certificates yet: an empty state, no error", r.status_code == 200 and "No certificates yet" in r.text)
r = c.get(f"/my-cpd/certificates/{new_number}.pdf", cookies=BEA)
check("the member's own certificate downloads as a PDF drawn from its record",
      r.status_code == 200 and r.headers["content-type"].startswith("application/pdf") and r.content.startswith(b"%PDF")
      and new_number in r.headers["content-disposition"])
r = c.get(f"/my-cpd/certificates/MER-{YEAR}-0005.pdf", cookies=BEA)
check("another member's certificate is a 404", r.status_code == 404)
check("a certificate that does not exist is a 404", c.get("/my-cpd/certificates/MER-2099-9999.pdf", cookies=BEA).status_code == 404)
r = c.get(f"/my-cpd/certificates/MER-{YEAR}-0005.pdf", cookies=OTTO)
check("but its owner can download it", r.status_code == 200 and r.content.startswith(b"%PDF"))

# ── 6. Series pages ──
r = c.get("/my-cpd/series", cookies=BEA); t = flat(r.text)
check("the series index shows all four series, with progress for the one held and a Buy link for the rest",
      r.status_code == 200 and all(s["title"] in t for s in main.SERIES.values()) and "3 of 3 parts complete" in t
      and t.count("Not in your library") == 3 and t.count("Buy the series, £39.99") == 3 and "View series" in t)
r = c.get("/my-cpd/series/FW-INSULATION", cookies=BEA); t = flat(r.text)
check("series page: cover, introduction, facts, progress, three parts with status, numbers, Download PDF, Open again",
      r.status_code == 200 and main.SERIES_INTRO["FW-INSULATION"] in t and "6 CPD hours" in t and "Three parts" in t
      and "A certificate for each part" in t and "3 of 3 parts complete · 3 certificates issued" in t
      and t.count("Certificate issued") == 3 and f"MER-{YEAR}-0007" in t and new_number in t
      and t.count("Download PDF") == 3 and t.count("Open again") == 3 and "Principles and Cavity Wall Insulation" in t
      and "3 of 3 issued." in t and "Open My certificates" in t)
r = c.get("/my-cpd/series/FW-MOISTURE", cookies=SUE); t = flat(r.text)
check("Moisture series page for a subscriber: the notes-only caveat, Open Part 1, every part in the library",
      "where a part has them" in t and "Open Part 1" in t and "Not in your library" not in t and "0 of 3 parts complete" in t)
r = c.get("/my-cpd/series/FW-HEATING", cookies=BEA); t = flat(r.text)
check("a series the member does not hold: every part marked, Buy the series", t.count("Not in your library") == 3 and "Buy the series, £39.99" in t)
check("an unknown series is a 404", c.get("/my-cpd/series/FW-NOPE", cookies=BEA).status_code == 404)
r = c.get("/my-cpd/course/MER-ALL-028", cookies=SUE)  # the course page makes the completion record /download marks
r = c.get("/download/MER-ALL-028", cookies=SUE)
r = c.get("/my-cpd/series/FW-MOISTURE", cookies=SUE); t = flat(r.text)
check("an opened part shows In progress and Continue", "In progress" in t and "Continue Part 2" in t)

# ── 7. Dashboard ──
r = c.get("/my-cpd/dashboard", cookies=SUE); t = flat(r.text)
check("dashboard: Your series row with all four series for a subscriber, the hours tally, the continue hero",
      r.status_code == 200 and "Your series" in t and all(s["title"] in t for s in main.SERIES.values())
      and f"CPD hours with Meridian in {YEAR}" in t and "Continue where you left off" in t and "Continue Part 2" in t
      and "Field Work: Moisture" in t and "/my-cpd/series/FW-MOISTURE" in t and "Annual Subscription" in t and "/my-cpd/billing" in t)
r = c.get("/my-cpd/dashboard", cookies=BEA); t = flat(r.text)
check("a single buyer's dashboard: only the series held, the completed row, the upsell, course cards link to the course page",
      "Your series" in t and "Field Work: Insulation" in t and "Field Work: Heating" not in t and "Completed" in t
      and 'href="/my-cpd/course/MER-ALL-020"' in t and "Upgrade to Annual — £79/year" in t and "Pay Per Course" in t)
r = c.get("/my-cpd/dashboard", cookies=NIA); t = flat(r.text)
check("a new buyer: Start here, the course, no series row", "Start here" in t and 'href="/my-cpd/course/MER-DEA-001"' in t and "Your series" not in t)

# ── 8. The emailed completion link still works without a sign-in ──
r = c.get("/complete/tok-otto")
check("emailed link: asks for the download first", r.status_code == 200 and "Please read the course first" in r.text)
r = c.get("/download/MER-DEA-002", cookies=OTTO)
r = c.get("/complete/tok-otto")
check("emailed link: the form", r.status_code == 200 and "Confirm Completion" in r.text)
r = c.post("/complete/tok-otto", data={"confirm": "on", "cert_name": "Otto Other"})
check("emailed link: certificate issued and emailed, same numbering", r.status_code == 200 and "CPD Completed" in r.text
      and certs_of("other")[-1]["course_id"] == "MER-DEA-002" and certs_of("other")[-1]["cert_number"] == f"MER-{YEAR}-0010"
      and certs_sent[-1]["to_email"] == "other@example.com")
r = c.post("/complete/tok-otto", data={"confirm": "on"})
check("emailed link: used once", r.status_code == 400)

# ── 9. Sign in from the thank-you page ──
r = c.get("/thanks?session_id=cs_live_nia123456789"); t = flat(r.text)
check("the thank-you page offers Go to My CPD", r.status_code == 200 and 'action="/thanks/signin"' in t and "Go to My CPD" in t and "Start now" in t)
r = c.post("/thanks/signin", data={"session_id": "cs_live_nia123456789"})
sc = r.headers.get("set-cookie", "")
check("the button signs the buyer in: 302 to the dashboard with a 90-day session for the member",
      r.status_code == 302 and r.headers["location"] == "/my-cpd/dashboard" and "session_token=" in sc and f"Max-Age={90 * 86400}" in sc
      and main._verify_session_token((r.cookies.get("session_token") or "").strip('"')) == "new@example.com")
check("the order is marked as used", all(p.get("thanks_signin_at") for p in db["purchases"] if p["stripe_session_id"] == "cs_live_nia123456789"))
r = c.post("/thanks/signin", data={"session_id": "cs_live_nia123456789"})
check("a second press is refused", r.status_code == 400 and "set-cookie" not in r.headers and "works once" in r.text)
r = c.get("/thanks?session_id=cs_live_nia123456789")
check("and the button is gone from the page", 'action="/thanks/signin"' not in r.text)
r = c.get("/thanks?session_id=cs_live_ottoold12345")
check("an order older than a week has no button", r.status_code == 200 and 'action="/thanks/signin"' not in r.text)
r = c.post("/thanks/signin", data={"session_id": "cs_live_ottoold12345"})
check("and cannot sign in", r.status_code == 400 and "set-cookie" not in r.headers)
r = c.post("/thanks/signin", data={"session_id": "cs_live_doesnotexist1"})
check("an unknown session is a 404", r.status_code == 404 and "set-cookie" not in r.headers)
r = c.post("/thanks/signin", data={"session_id": "nonsense"})
check("a malformed session id is a 404", r.status_code == 404 and "set-cookie" not in r.headers)
# the mark cannot be written (the migration has not been run): nobody is signed in
for p in db["purchases"]:
    if p["stripe_session_id"] == "cs_live_nia123456789": p["thanks_signin_at"] = None
db["_fail_update"] = lambda t, row: t == "purchases" and "thanks_signin_at" in row
r = c.post("/thanks/signin", data={"session_id": "cs_live_nia123456789"})
db["_fail_update"] = None
check("if the used mark cannot be written, nobody is signed in", r.status_code == 503 and "set-cookie" not in r.headers)
check("test_fix_email's pages still carry the correction form", 'action="/thanks/email"' in c.get("/thanks?session_id=cs_live_nia123456789").text)

# ── 10. The public courses page ──
html = (ROOT / "landing-page" / "courses.html").read_text(encoding="utf-8")
i_series, i_strip, i_grid, i_lib = html.index('id="seriesGrid"'), html.index('class="sub-strip"'), html.index('id="courseGrid"'), html.index('class="lib-head"')
check("courses.html: series first, then the £79 strip (placed by flex order, its lines left where PR #56 edits them), then the single courses",
      i_series < i_lib < i_grid < i_strip and ".page-hero, .series-grid { order: -2; }" in html and ".sub-strip { order: -1; }" in html
      and "body { display: flex; flex-direction: column; }" in html)
check("courses.html: the series cards use the poster template and the existing series links at £39.99",
      "function poster(" in html and "function seriesCard(" in html and "getSeriesLink(sid)" in html
      and "Buy, ${SERIES_PRICE}" in html and "SERIES_PRICE = '£39.99'" in html and "renderSeries()" in html)
check("courses.html: the approved series line", "Three courses on one subject, bought together for £39.99. A certificate of completion for each part as you finish it." in html)
check("courses.html: single courses heading with the free course", "Single courses, £19.99 each" in html and "MERIDIAN10" in html)
check("courses.html: the annual strip lines PR #56 edits are untouched",
      '<p class="sub-price-per">per year for the whole library</p>' in html and "seriesNote = ` Each part is its own course" in html)
# (one Scotland course objective in the catalogue describes an assessor "accredited in England and Wales"; the page text itself must not)
page_text = html.split("const ALL_COURSES = [", 1)[0] + html.split("\n];", 1)[1]
check("courses.html: no accreditation words outside the catalogue array", not re.search(r"accredited|cpd accredit", page_text, re.I))

print(f"\n{'ALL CHECKS PASSED' if not fails else f'{fails} FAILED'}")
if fails:
    raise SystemExit(1)
