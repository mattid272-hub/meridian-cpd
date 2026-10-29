"""Tests for the series product: one £39.99 purchase unlocks three courses, each with its own
completion link and certificate, and deck courses are delivered as slides plus notes.
Run from anywhere: python3 tests/test_series.py (or python -m pytest -q from webhook/)."""
import asyncio, json, os, re, sys, types
from pathlib import Path
os.environ.update(STRIPE_SECRET_KEY="sk_test_x", STRIPE_WEBHOOK_SECRET="whsec_x", SUPABASE_URL="https://example.supabase.co",
                  SUPABASE_SERVICE_ROLE_KEY="eyJhbGciOiJIUzI1NiJ9.eyJyb2xlIjoic2VydmljZV9yb2xlIn0.x", SESSION_SECRET="s",
                  ADMIN_PASSWORD="test-admin", STRIPE_PRICE_SINGLE="price_single",
                  STRIPE_PRICE_SUBSCRIPTION="price_sub", STRIPE_PRICE_SERIES="price_series")
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent))
import main, email_sender
from fastapi.testclient import TestClient

class Res:
    def __init__(self, data): self.data, self.count = data, len(data)
class Q:
    def __init__(s, db, t): s.db, s.t, s.f, s.op, s.pl = db, t, [], "select", None
    def select(s, *a, **k): return s
    def eq(s, c, v): s.f.append(lambda r, c=c, v=v: r.get(c) == v); return s
    def in_(s, c, v): s.f.append(lambda r, c=c, v=v: r.get(c) in v); return s
    def like(s, *a): return s
    def order(s, *a, **k): return s
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
            if s.db.get("_fail_insert") and s.db["_fail_insert"](s.t, s.pl): raise RuntimeError("insert failed (test)")
            row = dict(s.pl); row.setdefault("id", f"{s.t}-{len(rows) + 1}")  # Supabase generates ids
            if s.t == "certificates": row.setdefault("issued_at", "2026-10-29T12:00:00+00:00")  # and the issue date
            rows.append(row); return Res([row])
        hit = [r for r in rows if all(f(r) for f in s.f)]
        if s.op == "update": [r.update(s.pl) for r in hit]
        if s.t == "completions" and s.op == "select":  # the "*, members(name, email)" join
            hit = [dict(r, members=next(m for m in s.db["members"] if m["id"] == r["member_id"])) for r in hit]
        return Res(hit)

db = {"members": [{"id": "sub1", "email": "sub@example.com", "name": "Sue Sub", "plan": "subscription", "stripe_customer_id": "cus_s"},
                  {"id": "tok1", "email": "tok@example.com", "name": "Tom Token", "plan": "single", "stripe_customer_id": ""}],
      "purchases": [], "certificates": [],
      "completions": [{"id": "c-tok-020", "member_id": "tok1", "course_id": "MER-ALL-020", "completion_token": "tok-020-unused", "completed_at": None, "downloaded_at": None},
                      {"id": "c-tok-019", "member_id": "tok1", "course_id": "MER-ALL-019", "completion_token": "tok-019-done", "completed_at": "2026-10-01", "downloaded_at": "2026-10-01"}]}
main.supabase = types.SimpleNamespace(table=lambda t: Q(db, t),
    storage=types.SimpleNamespace(from_=lambda b: types.SimpleNamespace(download=lambda f: (_ for _ in ()).throw(RuntimeError("no catalogue")))))
main._refresh_under_review = lambda: None
DEFAULT_UNDER_REVIEW = set(main.UNDER_REVIEW)  # what main.py ships with (checked against the site below)
main.UNDER_REVIEW.clear()                      # put the Insulation series on sale for these tests

# Stripe and email stand-ins
_so = lambda d: main.stripe.StripeObject.construct_from(d, "sk_test_x")
prices = {}  # session id -> price id on its one line item
main.stripe.checkout.Session.list_line_items = staticmethod(lambda sid, limit: types.SimpleNamespace(
    data=[types.SimpleNamespace(price=types.SimpleNamespace(id=prices[sid]))]))
pending = {}
main.stripe.Webhook.construct_event = staticmethod(lambda payload, sig, secret: pending["event"])
sent, certs_sent = [], []
fail_email = set()  # course ids whose email send should fail
async def fake_send(**k):
    if k.get("course_id") in fail_email: raise RuntimeError("Resend down (test)")
    sent.append(k)
async def fake_cert(**k): certs_sent.append(k)
main.send_course_email = fake_send
main.send_certificate_email = fake_cert
main.generate_certificate = lambda **k: b"%PDF-1.4 test"

c = TestClient(main.app, follow_redirects=False)
def send(etype, obj):
    obj = main.stripe.StripeObject.construct_from(obj, "sk_test_x")
    pending["event"] = {"type": etype, "data": {"object": obj}}
    r = c.post("/stripe-webhook", content=b"{}", headers={"stripe-signature": "x"}); assert r.status_code == 200, r.text
def checkout(sid, email, price="price_series", client_ref="FW-INSULATION", amount=3999, expect_error=False, **extra):
    prices[sid] = price
    obj = {"id": sid, "mode": "payment", "customer": "cus_" + sid,
           "customer_details": {"email": email, "name": email.split("@")[0].title()},
           "amount_total": amount, "client_reference_id": client_ref, **extra}
    if not expect_error:
        return send("checkout.session.completed", obj)
    # the handler must fail (non-2xx to Stripe) so the event is delivered again
    pending["event"] = {"type": "checkout.session.completed", "data": {"object": main.stripe.StripeObject.construct_from(obj, "sk_test_x")}}
    try: c.post("/stripe-webhook", content=b"{}", headers={"stripe-signature": "x"})
    except RuntimeError as e: return e
    raise SystemExit(f"{sid}: expected the webhook to fail")
def rows(sid): return [p for p in db["purchases"] if p["stripe_session_id"] == sid]
def member(email): return next(m for m in db["members"] if m["email"] == email)
def comps(mid): return [x for x in db["completions"] if x["member_id"] == mid]
PARTS = ["MER-ALL-019", "MER-ALL-020", "MER-ALL-021"]

# 0. Definitions: the series is complete, the others are defined but not on sale, the split adds up
assert main.series_courses("FW-INSULATION") == PARTS and main.series_courses("FW-HEATING") == [] and main.series_courses("nope") == []
assert main._split_amount(3999, 3) == [1333, 1333, 1333] and main._split_amount(4000, 3) == [1334, 1333, 1333]
assert main._series_label("MER-ALL-020") == "Part 2 of 3 · Field Work: Insulation" and main._series_label("MER-DEA-001") == ""
assert main.PRICE_TO_COURSE == {"price_single": "MER-DEA-001", "price_sub": "SUBSCRIPTION", "price_series": "SERIES"}
for cid in PARTS: assert main._is_deck(cid) and main._pdf_url(cid).endswith(f"{cid}-deck.pdf") and main._notes_url(cid).endswith(f"{cid}.pdf")
assert not main._is_deck("MER-ALL-018") and main._pdf_url("MER-ALL-018").endswith("MER-ALL-018.pdf")
# a definition error stops the app from starting
bad = main.COURSES["MER-ALL-020"]["part"]; main.COURSES["MER-ALL-020"]["part"] = 3
try: main._check_series(); raise SystemExit("wrong part accepted")
except ValueError: pass
finally: main.COURSES["MER-ALL-020"]["part"] = bad
main.SERIES["FW-X"] = {"title": "x", "courses": ["MER-ALL-019"]}
try: main._check_series(); raise SystemExit("course in two series accepted")
except ValueError: pass
finally: del main.SERIES["FW-X"]
main.COURSES["MER-DEA-002"]["series"] = "FW-HEATING"
try: main._check_series(); raise SystemExit("course naming an incomplete series accepted")
except ValueError: pass
finally: del main.COURSES["MER-DEA-002"]["series"]
main._check_series()
print("0 series definitions, price split, deck and notes URLs, import-time checks")

# 1. Series bought through the site link (client_reference_id): three rows, three links, three emails
checkout("cs_live_s1", "ann@example.com")
got = rows("cs_live_s1"); ann = member("ann@example.com")
assert [p["course_id"] for p in got] == PARTS and all(p["series_id"] == "FW-INSULATION" for p in got)
assert round(sum(p["amount_gbp"] for p in got), 2) == 39.99 and [p["amount_gbp"] for p in got] == [13.33, 13.33, 13.33]
assert ann["plan"] == "single" and len(comps(ann["id"])) == 3
tokens = {x["course_id"]: x["completion_token"] for x in comps(ann["id"])}
assert len(set(tokens.values())) == 3
assert [e["course_id"] for e in sent] == PARTS and [e["part"] for e in sent] == [1, 2, 3]
assert all(e["parts_total"] == 3 and e["series_title"] == "Field Work: Insulation" and e["held_parts"] is None for e in sent)
assert all(e["pdf_url"].endswith(f"{e['course_id']}-deck.pdf") and e["notes_url"].endswith(f"{e['course_id']}.pdf") for e in sent)
assert [e["completion_link"].rsplit("/", 1)[1] for e in sent] == [tokens[k] for k in PARTS]
print("1 series via client_reference_id: three rows summing to £39.99, three distinct links, three emails")

# 2. The same through session metadata (a Payment Link can carry the series that way)
sent.clear(); checkout("cs_live_s2", "bob@example.com", client_ref="", metadata={"series": "FW-INSULATION"})
assert [p["course_id"] for p in rows("cs_live_s2")] == PARTS and [e["course_id"] for e in sent] == PARTS
print("2 series via metadata")

# 3. A series price the app cannot place: recorded once as SERIES, nothing sent; same for a series not yet complete
sent.clear(); checkout("cs_live_s3", "cat@example.com", client_ref="FW-NOPE")
assert [p["course_id"] for p in rows("cs_live_s3")] == ["SERIES"] and rows("cs_live_s3")[0]["amount_gbp"] == 39.99 and not sent
checkout("cs_live_s3b", "cat@example.com", client_ref="FW-HEATING")
assert [p["course_id"] for p in rows("cs_live_s3b")] == ["SERIES"] and not sent and not comps(member("cat@example.com")["id"])
assert "your order" in main._order_what(rows("cs_live_s3")) and "SERIES" not in main._order_what(rows("cs_live_s3"))
assert "Field Work series" in main._course_label("SERIES")
print("3 unknown or incomplete series reference: one SERIES row, nothing sent")

# 4. Stripe delivers the event again: nothing is added and nothing is sent twice
n_p, n_c = len(db["purchases"]), len(db["completions"])
sent.clear(); checkout("cs_live_s1", "ann@example.com")
assert len(db["purchases"]) == n_p and len(db["completions"]) == n_c and not sent
print("4 redelivered event makes no duplicate rows and sends nothing")
assert all(p.get("emailed_at") for p in rows("cs_live_s1"))

# 4b. The insert of part 2 fails: part 1 is recorded and sent, the webhook fails so Stripe retries,
#     and the retry finishes parts 2 and 3 only, with no second email for part 1
db["_fail_insert"] = lambda t, row: t == "purchases" and row.get("course_id") == "MER-ALL-020"
sent.clear(); e = checkout("cs_live_s4b", "eve@example.com", expect_error=True)
assert "insert failed" in str(e)
assert [p["course_id"] for p in rows("cs_live_s4b")] == ["MER-ALL-019"] and rows("cs_live_s4b")[0].get("emailed_at")
assert [x["course_id"] for x in sent] == ["MER-ALL-019"]
db["_fail_insert"] = None
import contextlib, io
log = io.StringIO()
with contextlib.redirect_stdout(log): sent.clear(); checkout("cs_live_s4b", "eve@example.com")
assert "ACTION NEEDED: checkout cs_live_s4b was only partly handled" in log.getvalue(), log.getvalue()
assert [p["course_id"] for p in rows("cs_live_s4b")] == PARTS and all(p.get("emailed_at") for p in rows("cs_live_s4b"))
assert [x["course_id"] for x in sent] == ["MER-ALL-020", "MER-ALL-021"], [x["course_id"] for x in sent]
assert round(sum(p["amount_gbp"] for p in rows("cs_live_s4b")), 2) == 39.99 and len(comps(member("eve@example.com")["id"])) == 3
sent.clear(); checkout("cs_live_s4b", "eve@example.com"); assert not sent and len(rows("cs_live_s4b")) == 3
print("4b insert fails on part 2: redelivery finishes parts 2 and 3 only, part 1 is not sent again")

# 4c. The email for part 3 fails after its row is recorded: the webhook fails so Stripe retries,
#     and the retry sends part 3 only
fail_email.add("MER-ALL-021")
sent.clear(); e = checkout("cs_live_s4c", "fay@example.com", expect_error=True)
assert "email failed for ['MER-ALL-021']" in str(e)
assert [p["course_id"] for p in rows("cs_live_s4c")] == PARTS and [bool(p.get("emailed_at")) for p in rows("cs_live_s4c")] == [True, True, False]
assert [x["course_id"] for x in sent] == ["MER-ALL-019", "MER-ALL-020"]
fail_email.clear()
sent.clear(); checkout("cs_live_s4c", "fay@example.com")
assert [x["course_id"] for x in sent] == ["MER-ALL-021"] and all(p.get("emailed_at") for p in rows("cs_live_s4c"))
assert len(comps(member("fay@example.com")["id"])) == 3 and len(rows("cs_live_s4c")) == 3
print("4c email fails on part 3 after its row: redelivery sends part 3 only")

# 4d. A single course bought on its own is unchanged by all this: row, then email, then the mark
sent.clear(); checkout("cs_live_s4d", "gus@example.com", price="price_single", client_ref="MER-ALL-018", amount=1999)
assert [p["course_id"] for p in rows("cs_live_s4d")] == ["MER-ALL-018"] and rows("cs_live_s4d")[0]["amount_gbp"] == 19.99
assert "series_id" not in rows("cs_live_s4d")[0] and rows("cs_live_s4d")[0].get("emailed_at")
assert [x["course_id"] for x in sent] == ["MER-ALL-018"] and sent[0]["series_title"] is None and sent[0]["notes_url"] is None
# and the thanks page calls it a course, not a series (MER-ALL-018 will one day be part of FW-MOISTURE)
what = main._order_what(rows("cs_live_s4d"))
assert what.startswith("your course, <strong>Damp, Condensation") and "Field Work" not in what, what
assert "Field Work" not in main._order_what([{"course_id": "MER-ALL-019"}]), "one part without series_id is just a course"
assert main._order_what(rows("cs_live_s1")) == "the 3 courses in <strong>Field Work: Insulation</strong>"
assert main._order_what([{"course_id": k} for k in PARTS]) == "the 3 courses in <strong>Field Work: Insulation</strong>"
assert main._order_what([dict(rows("cs_live_s1")[0])]).startswith("the first 1 course of <strong>Field Work: Insulation</strong>")
print("4d single course on its own: recorded, sent, marked; the thanks page calls it a course")

# 5. A member who already has an unused link for a part keeps it; a part already certified gets no new link
sent.clear(); checkout("cs_live_s5", "tok@example.com")
tom = member("tok@example.com")
assert len(comps(tom["id"])) == 2 + 1, comps(tom["id"])  # 019 done, 020 reused, 021 new
by = {e["course_id"]: e for e in sent}
assert by["MER-ALL-020"]["completion_link"].endswith("/complete/tok-020-unused")
assert by["MER-ALL-019"]["completion_link"] is None and by["MER-ALL-021"]["completion_link"]
assert len(rows("cs_live_s5")) == 3
print("5 existing unused token reused; completed part is sent without a link")

# 6. One part withdrawn at the time of purchase: two emails that say the third follows; resend works once restored
main.UNDER_REVIEW.add("MER-ALL-020")
sent.clear(); checkout("cs_live_s6", "dee@example.com")
dee = member("dee@example.com")
assert [p["course_id"] for p in rows("cs_live_s6")] == PARTS and round(sum(p["amount_gbp"] for p in rows("cs_live_s6")), 2) == 39.99
assert [e["course_id"] for e in sent] == ["MER-ALL-019", "MER-ALL-021"]
assert all(e["held_parts"] == [main.COURSES["MER-ALL-020"]["title"]] for e in sent)
assert {x["course_id"] for x in comps(dee["id"])} == {"MER-ALL-019", "MER-ALL-021"}
main.UNDER_REVIEW.discard("MER-ALL-020")
sent.clear(); n = asyncio.run(main.resend_order_emails(dee, rows("cs_live_s6")))
assert n == 3 and [e["course_id"] for e in sent] == PARTS and all(e["completion_link"] for e in sent)
assert {x["course_id"] for x in comps(dee["id"])} == set(PARTS) and len(comps(dee["id"])) == 3
assert "the 3 courses in <strong>Field Work: Insulation</strong>" in main._order_what(rows("cs_live_s6"))
print("6 withdrawn part: two emails say it follows; resend after restore sends all three with links")

# 7. Completing one part issues one certificate, and a second link for the same part issues none
cookie = {"session_token": main._make_session_token("ann@example.com")}
t19 = tokens["MER-ALL-019"]
r = c.get(f"/complete/{t19}"); assert r.status_code == 200 and "Download the slides" in r.text and "/download/MER-ALL-019/notes" in r.text
r = c.get("/download/MER-ALL-019", cookies=cookie); assert r.status_code == 302 and r.headers["location"].endswith("MER-ALL-019-deck.pdf")
r = c.get(f"/complete/{t19}"); assert r.status_code == 200 and "Confirm Completion" in r.text
r = c.post(f"/complete/{t19}", data={"confirm": "on", "cert_name": "Ann Assessor"}); assert r.status_code == 200 and "CPD Completed" in r.text
mine = [x for x in db["certificates"] if x["member_id"] == ann["id"]]
assert len(mine) == 1 and mine[0]["course_id"] == "MER-ALL-019" and mine[0]["cpd_hours"] == 2.0 and len(certs_sent) == 1
assert sum(1 for x in comps(ann["id"]) if x.get("completed_at")) == 1
r = c.post(f"/complete/{t19}", data={"confirm": "on"}); assert r.status_code == 400  # link used
# a second, unused link for the same course (an old email, a dashboard token) earns nothing more
extra = main.create_completion_token(ann["id"], "MER-ALL-019")
next(x for x in db["completions"] if x["completion_token"] == extra)["downloaded_at"] = "2026-10-29"
r = c.post(f"/complete/{extra}", data={"confirm": "on", "cert_name": "Ann Assessor"})
assert r.status_code == 200 and "already hold" in r.text and mine[0]["cert_number"] in r.text
assert len([x for x in db["certificates"] if x["member_id"] == ann["id"]]) == 1 and len(certs_sent) == 1
assert next(x for x in db["completions"] if x["completion_token"] == extra)["completed_at"]
print("7 one part completed: one certificate; a second link for the same part is retired without a certificate")

# 8. A subscriber who buys a series stays a subscriber (and is not downgraded)
sent.clear(); checkout("cs_live_s8", "sub@example.com")
assert member("sub@example.com")["plan"] == "subscription" and len(rows("cs_live_s8")) == 3 and len(sent) == 3
print("8 subscriber buying a series keeps plan=subscription")

# 9. Download routes: the deck is the course, the notes are the written PDF; both gated the same way
r = c.get("/download/MER-ALL-019/notes", cookies=cookie); assert r.status_code == 302 and r.headers["location"].endswith("/courses/MER-ALL-019.pdf")
r = c.get("/download/MER-DEA-002/notes", cookies=cookie); assert r.status_code == 302 and r.headers["location"].endswith("/courses/MER-DEA-002.pdf")
r = c.get("/download/MER-DEA-002", cookies=cookie); assert r.status_code == 302 and r.headers["location"].endswith("/courses/MER-DEA-002.pdf")
r = c.get("/download/MER-ALL-019/notes"); assert r.status_code == 302 and r.headers["location"] == "/my-cpd"
r = c.get("/download/MER-XXX-999/notes", cookies=cookie); assert r.status_code == 404
main.UNDER_REVIEW.add("MER-ALL-021")
r = c.get("/download/MER-ALL-021/notes", cookies=cookie); assert r.status_code == 200 and "being updated" in r.text
main.UNDER_REVIEW.discard("MER-ALL-021")
r = c.get("/my-cpd/dashboard", cookies=cookie); assert r.status_code == 200
assert r.text.count("Part 1 of 3 · Field Work: Insulation") == 1 and "Part 3 of 3" in r.text
assert "/download/MER-ALL-020/notes" in r.text and "Download slides" in r.text
assert "Field Work: Insulation" in main._course_label("MER-ALL-021") and "Part 3 of 3" in main._course_label("MER-ALL-021")
print("9 deck and notes download routes; dashboard shows the part and both files")

# 10. The email itself: two attachments for a deck course, and the words a series buyer needs
calls = []
async def fake_raw(to_email, to_name, subject, body, attachments=None): calls.append((subject, body, attachments))
async def fake_fetch(url): return b"%PDF deck" if "-deck" in url else b"%PDF notes"
email_sender._send, email_sender._fetch_pdf = fake_raw, fake_fetch
asyncio.run(email_sender.send_course_email(to_email="x@example.com", to_name="X", course_title="T", course_id="MER-ALL-019",
    pdf_url=main._pdf_url("MER-ALL-019"), completion_link="https://app/complete/t", notes_url=main._notes_url("MER-ALL-019"),
    series_title="Field Work: Insulation", part=1, parts_total=3, held_parts=["Insulation Series, Part 2"]))
subject, body, att = calls[-1]
assert [a["filename"] for a in att] == ["MER-ALL-019-slides.pdf", "MER-ALL-019-notes.pdf"]
assert "Part 1 of 3 of Field Work: Insulation" in body and "the slides" in body.lower() and "notes" in body.lower()
assert "One part of your series is being updated" in body and "Insulation Series, Part 2" in body and "will follow" in body
asyncio.run(email_sender.send_course_email(to_email="x@example.com", to_name="X", course_title="T", course_id="MER-DEA-002",
    pdf_url=main._pdf_url("MER-DEA-002"), completion_link="https://app/complete/t"))
subject, body, att = calls[-1]
assert [a["filename"] for a in att] == ["MER-DEA-002.pdf"] and "Part " not in body and "being updated" not in body
print("10 course email: slides plus notes attached, series position and the held part explained")

# 11. Admin: the system check looks for both files of a deck course
class FakeHTTP:
    def __init__(s, **k): pass
    async def __aenter__(s): return s
    async def __aexit__(s, *a): return False
    async def head(s, url): return types.SimpleNamespace(status_code=404 if url.endswith("MER-ALL-021.pdf") else 200)
main.httpx.AsyncClient = FakeHTTP
r = c.get("/admin/system", auth=("admin", "test-admin")); t = " ".join(r.text.split()); assert r.status_code == 200
n_live = sum(1 for k in main.COURSES if k != "SUBSCRIPTION" and main.is_available(k))
assert f"({n_live - 1} of {n_live} downloadable)" in t and "Notes: Problem (404)" in t and "STRIPE_PRICE_SERIES" in t
r = c.get("/admin/courses", auth=("admin", "test-admin")); assert "MER-ALL-019-deck.pdf" in r.text and "Part 1 of 3" in r.text
print("11 admin system check covers deck and notes; courses page links both")

# 12. Catalogue parity: the site's array, the app's catalogue, the two series definitions and the withdrawn lists agree
html = (HERE.parent.parent / "landing-page" / "courses.html").read_text(encoding="utf-8")
arr = html.split("const ALL_COURSES = [", 1)[1].split("\n];", 1)[0]
site = {}
for m in re.finditer(r"id: '(MER-[A-Z]+-\d{3})', strand: '(\w+)', hours: ([\d.]+), where: '(\w+)'(?:, series: '([A-Z-]+)', part: (\d+))?,\s*\n\s*title: '((?:[^'\\]|\\.)*)'", arr):
    site[m.group(1)] = {"hours": float(m.group(3)), "where": m.group(4), "series": m.group(5), "part": int(m.group(6)) if m.group(6) else None,
                        "title": m.group(7).replace("\\'", "'")}
assert len(site) == arr.count("\n  {"), "could not parse every course entry in courses.html"
app = {k: v for k, v in main.COURSES.items() if k != "SUBSCRIPTION"}
assert set(site) == set(app), set(site) ^ set(app)
for cid, v in site.items():
    assert v["hours"] == app[cid]["cpd_hours"], (cid, v["hours"], app[cid]["cpd_hours"])
    assert v["series"] == app[cid].get("series") and v["part"] == app[cid].get("part"), (cid, v, app[cid])
    if v["series"]:
        assert v["title"] == app[cid]["title"] and v["where"] == "EW", (cid, v["title"], app[cid]["title"])
site_series = {m.group(1): {"title": m.group(2), "courses": re.findall(r"'(MER-[A-Z]+-\d{3})'", m.group(3))}
               for m in re.finditer(r"'(FW-[A-Z]+)':\s*\{ title: '([^']+)',\s*courses: \[([^\]]*)\]", html.split("const SERIES = {", 1)[1].split("\n};", 1)[0])}
assert site_series == main.SERIES, (site_series, main.SERIES)
site_withdrawn = set(re.findall(r"'(MER-[A-Z]+-\d{3})'", re.search(r"const UNDER_REVIEW = new Set\(\[(.*?)\]\)", html).group(1)))
json_withdrawn = set(json.loads((HERE.parent.parent / "landing-page" / "under-review.json").read_text())["under_review"])
assert site_withdrawn == DEFAULT_UNDER_REVIEW == json_withdrawn == set(PARTS), (site_withdrawn, DEFAULT_UNDER_REVIEW, json_withdrawn)
assert "STRIPE_SERIES" in html and "getSeriesLink" in html and "39.99" in html
index = (HERE.parent.parent / "landing-page" / "index.html").read_text(encoding="utf-8")
i = index.index("Field Work Series"); assert index.rindex("<!--", 0, i) > index.rindex("-->", 0, i), "the £39.99 card must stay commented out until a series is on sale"
assert "&#163;39.99" in index and "pricing-cards three" in index
assert "prefilled_promo_code" not in html.split("function getSeriesLink", 1)[1].split("}", 1)[0]
print("12 catalogue parity: main.py, courses.html, under-review.json and index.html agree")
print("ALL CHECKS PASSED")
