"""The optional step after completion: feedback for Meridian (course_feedback) and the
learner's reflection (on the completion record), on the emailed link and inside My CPD.
Completion and the certificate must work exactly as before when the step is skipped, and
when the migration has not been run.
Run from anywhere: python3 tests/test_completion_feedback.py (or python -m pytest -q from webhook/)."""
import asyncio, os, re, sys, types
from datetime import datetime, timezone
from pathlib import Path
os.environ.update(STRIPE_SECRET_KEY="sk_test_x", STRIPE_WEBHOOK_SECRET="whsec_x", SUPABASE_URL="https://example.supabase.co",
                  SUPABASE_SERVICE_ROLE_KEY="eyJhbGciOiJIUzI1NiJ9.eyJyb2xlIjoic2VydmljZV9yb2xlIn0.x", SESSION_SECRET="s",
                  ADMIN_PASSWORD="test-admin", DASHBOARD_SECRET="dash-secret-for-tests", UNSUBSCRIBE_SECRET="u",
                  STRIPE_PRICE_SINGLE="price_single", STRIPE_PRICE_SUBSCRIPTION="price_sub", STRIPE_PRICE_SERIES="price_series",
                  RESEND_API_KEY="re_test")
HERE = Path(__file__).resolve().parent
ROOT = HERE.parent.parent
sys.path.insert(0, str(HERE.parent))
import main, email_sender
from fastapi.testclient import TestClient

YEAR = datetime.now(timezone.utc).year


class Res:
    def __init__(self, data): self.data, self.count = data, len(data)
class Q:
    def __init__(s, db, t): s.db, s.t, s.f, s.op, s.pl, s.o, s.cols = db, t, [], "select", None, None, ""
    def select(s, *a, **k): s.cols = a[0] if a else ""; return s
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
        # Before the migration: no course_feedback table and no reflection columns.
        if not s.db["_migrated"] and (s.t == "course_feedback" or "reflect" in s.cols
                                      or (s.op == "update" and any(k.startswith("reflect") for k in s.pl))):
            raise RuntimeError("relation or column does not exist (test)")
        rows = s.db.setdefault(s.t, [])
        if s.op == "insert":
            row = dict(s.pl); row.setdefault("id", f"{s.t}-{len(rows) + 1}")
            if s.t == "certificates": row.setdefault("issued_at", datetime.now(timezone.utc).isoformat())
            if s.t == "course_feedback":
                if any(r["member_id"] == row["member_id"] and r["course_id"] == row["course_id"] for r in rows):
                    raise RuntimeError("duplicate key (test)")
                row.setdefault("created_at", datetime.now(timezone.utc).isoformat())
            rows.append(row); return Res([row])
        hit = [r for r in rows if all(f(r) for f in s.f)]
        if s.op == "update":
            [r.update(s.pl) for r in hit]
        if s.o: hit = sorted(hit, key=lambda r: str(r.get(s.o[0]) or ""), reverse=s.o[1])
        if s.t == "completions" and s.op == "select":
            hit = [dict(r, members=next(m for m in s.db["members"] if m["id"] == r["member_id"])) for r in hit]
        return Res(hit)


db = {
    "_migrated": False,
    "members": [
        {"id": "ann", "email": "ann@example.com", "name": "Ann Assessor", "plan": "subscription",
         "subscription_expires_at": f"{YEAR + 1}-12-31T00:00:00+00:00", "joined_at": f"{YEAR}-01-05T10:00:00+00:00"},
        {"id": "bob", "email": "bob@example.com", "name": "Bob Buyer", "plan": "single", "joined_at": f"{YEAR}-01-05T10:00:00+00:00"},
    ],
    "purchases": [
        {"id": "p1", "member_id": "bob", "course_id": "MER-DEA-002", "amount_gbp": 19.99, "stripe_session_id": "cs_live_bob1234567890"},
        {"id": "p2", "member_id": "bob", "course_id": "MER-DEA-003", "amount_gbp": 19.99, "stripe_session_id": "cs_live_bob1234567891"},
        {"id": "p3", "member_id": "bob", "course_id": "MER-DEA-004", "amount_gbp": 19.99, "stripe_session_id": "cs_live_bob1234567892"},
    ],
    "completions": [
        {"id": "c1", "member_id": "bob", "course_id": "MER-DEA-002", "completion_token": "tok-skip", "completed_at": None, "downloaded_at": f"{YEAR}-11-01"},
        {"id": "c2", "member_id": "bob", "course_id": "MER-DEA-003", "completion_token": "tok-both", "completed_at": None, "downloaded_at": f"{YEAR}-11-01"},
        {"id": "c3", "member_id": "bob", "course_id": "MER-DEA-004", "completion_token": "tok-old", "completed_at": None, "downloaded_at": f"{YEAR}-11-01"},
        {"id": "c4", "member_id": "ann", "course_id": "MER-ALL-019", "completion_token": "tok-ann", "completed_at": None, "downloaded_at": f"{YEAR}-11-01"},
        {"id": "c5", "member_id": "bob", "course_id": "MER-DEA-001", "completion_token": "tok-open", "completed_at": None, "downloaded_at": None},
    ],
    "certificates": [],
}
main.supabase = types.SimpleNamespace(table=lambda t: Q(db, t),
    storage=types.SimpleNamespace(from_=lambda b: types.SimpleNamespace(download=lambda f: (_ for _ in ()).throw(RuntimeError("no catalogue")))))
main._refresh_under_review = lambda: None
main.UNDER_REVIEW.clear()
certs_sent, refl_sent = [], []
async def fake_cert(**k): certs_sent.append(k)
main.send_certificate_email = fake_cert
fail_refl = {"on": False}
async def fake_refl(**k):
    if fail_refl["on"]: raise RuntimeError("Resend down (test)")
    refl_sent.append(k)
main.send_reflection_email = fake_refl

def migrate(done: bool):
    db["_migrated"] = done
    main._feedback_ready_cache.update(ok=False, checked=0.0)

c = TestClient(main.app, follow_redirects=False)
fails = 0
def check(name, cond):
    global fails
    print(("PASS " if cond else "FAIL ") + name)
    fails += 0 if cond else 1
flat = lambda t: " ".join(t.split())
cookie = lambda email: {"session_token": main._make_session_token(email)}
ANN, BOB = cookie("ann@example.com"), cookie("bob@example.com")
completion = lambda cid: next(x for x in db["completions"] if x["id"] == cid)
certs_of = lambda mid, course: [x for x in db["certificates"] if x["member_id"] == mid and x["course_id"] == course]
feedback = lambda: db.setdefault("course_feedback", [])

# ── 1. Before the migration: completion exactly as before, no step ──
migrate(False)
r = c.post("/complete/tok-skip", data={"confirm": "on", "cert_name": "Bob Buyer"})
check("no migration: the emailed link still completes and issues the certificate",
      r.status_code == 200 and "CPD Completed" in r.text and completion("c1")["completed_at"] and len(certs_of("bob", "MER-DEA-002")) == 1
      and len(certs_sent) == 1)
check("no migration: the step is not shown", 'action="/complete/tok-skip/feedback"' not in r.text and "What have you learned?" not in r.text)
r = c.post("/complete/tok-skip/feedback", data={"learned": "x", "clear": "yes"})
check("no migration: a save is harmless (nothing written, back to My CPD)",
      r.status_code == 303 and "reflected_at" not in completion("c1") and not db.get("course_feedback"))
r = c.get("/my-cpd/course/MER-DEA-002", cookies=BOB)
check("no migration: the course page with a certificate shows no step", r.status_code == 200 and "Certificate issued" in r.text
      and "/feedback" not in r.text)
r = c.get("/my-cpd/certificates", cookies=BOB)
check("no migration: My certificates still loads", r.status_code == 200 and "Your reflection" not in r.text)

# ── 2. After the migration: the step appears after the tick is accepted ──
migrate(True)
r = c.get("/complete/tok-both")
check("the form before the tick is unchanged: no step until the declaration is accepted",
      r.status_code == 200 and "Confirm Completion" in r.text and "What have you learned?" not in r.text)
r = c.post("/complete/tok-both", data={"confirm": "on", "cert_name": "Bob Buyer"}); t = flat(r.text)
check("the confirmation page issues the certificate and then offers the step, both parts",
      r.status_code == 200 and "CPD Completed" in t and len(certs_of("bob", "MER-DEA-003")) == 1
      and 'action="/complete/tok-both/feedback"' in t and "Was the course clear?" in t and "Was it useful for your work?" in t
      and "Anything wrong, missing or out of date?" in t and "What have you learned?" in t
      and "What will you do differently in your practice?" in t and ">Skip<" in t and "Your certificate is already issued." in t)
check("the three-point scale is Yes, Partly, No", t.count('value="yes"') == 2 and t.count('value="partly"') == 2 and t.count('value="no"') == 2)
check("nothing in the step is required", ' required' not in t.split('class="fb"', 1)[1])

# ── 3. Skipping both parts ──
r = c.post("/complete/tok-skip/feedback", data={})
check("skipping both parts (an empty save) writes nothing and goes to My CPD",
      r.status_code == 303 and r.headers["location"].endswith("/my-cpd/dashboard")
      and not completion("c1").get("reflected_at") and not feedback() and not refl_sent)
check("and the certificate from the skipped completion stands", len(certs_of("bob", "MER-DEA-002")) == 1 and completion("c1")["completed_at"])
r = c.post("/complete/tok-skip/feedback", data={"clear": "maybe", "useful": "<b>", "comment": "  \n\t ", "learned": "\x00\x07"})
check("answers that are not on the scale, or only blanks and control characters, count as skipped",
      r.status_code == 303 and not feedback() and not completion("c1").get("reflected_at"))

# ── 4. Both parts given on the emailed link ──
r = c.post("/complete/tok-both/feedback", data={
    "clear": "yes", "useful": "partly", "comment": "Section 3 cites the old\r\nconvention.\x07",
    "learned": "How <script>x</script> works", "change": "Check the age band first."})
fb = feedback()
check("Part A goes to course_feedback with course, member, completion and the answers",
      r.status_code == 200 and len(fb) == 1 and fb[0]["course_id"] == "MER-DEA-003" and fb[0]["member_id"] == "bob"
      and fb[0]["completion_id"] == "c2" and fb[0]["clear"] == "yes" and fb[0]["useful"] == "partly"
      and fb[0]["comment"] == "Section 3 cites the old\nconvention.")
row = completion("c2")
check("Part B goes on the completion record", row["reflection_learned"] == "How <script>x</script> works"
      and row["reflection_change"] == "Check the age band first." and row["reflected_at"])
check("a one-line thank-you", "Thank you. Your answers are saved." in r.text)
check("the learner is emailed a copy of the reflection with the certificate number",
      len(refl_sent) == 1 and refl_sent[0]["to_email"] == "bob@example.com" and refl_sent[0]["learned"] == row["reflection_learned"]
      and refl_sent[0]["cert_number"] == certs_of("bob", "MER-DEA-003")[0]["cert_number"])
r = c.post("/complete/tok-both/feedback", data={"clear": "no", "learned": "Overwritten"})
check("a second save from the same link adds no feedback and does not overwrite the reflection",
      len(feedback()) == 1 and completion("c2")["reflection_learned"] == "How <script>x</script> works" and len(refl_sent) == 1
      and r.status_code == 303)
r = c.get("/complete/tok-both")
check("the completion link itself is still single-use", r.status_code == 404)
r = c.post("/complete/tok-open/feedback", data={"learned": "x"})
check("the step cannot be reached with a link for a course not yet completed", r.status_code == 404 and not completion("c5").get("reflected_at"))
r = c.post("/complete/tok-nope/feedback", data={"learned": "x"})
check("nor with an unknown link", r.status_code == 404)
check("long answers are capped", len(main._clean_answer("x" * 5000)) == main.FEEDBACK_TEXT_MAX)

# ── 5. The reflection in My CPD ──
r = c.get("/my-cpd/course/MER-DEA-003", cookies=BOB); t = flat(r.text)
check("the course page shows the reflection under the course, escaped, and asks nothing more",
      r.status_code == 200 and "Your reflection" in t and "What I learned" in t and "How &lt;script&gt;x&lt;/script&gt; works" in t
      and "<script>x</script>" not in t and "Check the age band first." in t and 'class="fb"' not in t)
r = c.get("/my-cpd/certificates", cookies=BOB); t = flat(r.text)
check("My certificates shows the reflection under that course only",
      "Your reflection" in t and t.count("What I learned") == 1 and "Check the age band first." in t)

# ── 6. Inside the app ──
r = c.get("/download/MER-ALL-019", cookies=ANN)
r = c.post("/my-cpd/course/MER-ALL-019/complete", data={"confirm": "on", "cert_name": "Ann Assessor"}, cookies=ANN)
check("in-app completion unchanged", r.status_code == 303 and len(certs_of("ann", "MER-ALL-019")) == 1)
r = c.get(r.headers["location"], cookies=ANN); t = flat(r.text)
check("the course page offers the step after the certificate", 'action="/my-cpd/course/MER-ALL-019/feedback"' in t
      and "For Meridian" in t and "For your CPD record" in t and 'href="/my-cpd/course/MER-ALL-019">Skip' in t)
r = c.post("/my-cpd/course/MER-ALL-019/feedback", data={"clear": "no", "useful": "yes"}, cookies=ANN)
check("feedback only: saved, back to the course with the thank-you",
      r.status_code == 303 and r.headers["location"].endswith("?saved=1") and len(feedback()) == 2 and feedback()[1]["comment"] is None
      and not completion("c4").get("reflected_at"))
t = flat(c.get(r.headers["location"], cookies=ANN).text)
check("then only the reflection is still asked", "Thank you. Your answers are saved." in t and "Was the course clear?" not in t
      and "What have you learned?" in t)
fail_refl["on"] = True
r = c.post("/my-cpd/course/MER-ALL-019/feedback", data={"change": "Photograph the loft hatch."}, cookies=ANN)
fail_refl["on"] = False
check("a reflection with only the second answer is kept even if the email copy fails",
      r.status_code == 303 and completion("c4")["reflection_change"] == "Photograph the loft hatch." and completion("c4")["reflection_learned"] is None)
t = flat(c.get("/my-cpd/course/MER-ALL-019", cookies=ANN).text)
check("and shown on the course page, with no form left", "Photograph the loft hatch." in t and "What I learned" not in t and 'class="fb"' not in t)
r = c.post("/my-cpd/course/MER-DEA-002/feedback", data={"learned": "x"})
check("the in-app save needs a sign-in", r.status_code == 302 and r.headers["location"] == "/my-cpd")
r = c.post("/my-cpd/course/MER-ALL-020/feedback", data={"learned": "x"}, cookies=ANN)
check("and a completed course", r.status_code == 303 and not any(x.get("reflected_at") for x in db["completions"] if x["course_id"] == "MER-ALL-020"))

# ── 7. Skipping on the emailed link of a course completed in-app before; feedback only on tok-old ──
r = c.post("/complete/tok-old", data={"confirm": "on", "cert_name": "Bob Buyer"})
check("a third completion, step skipped by leaving the page: certificate issued, nothing stored",
      r.status_code == 200 and len(certs_of("bob", "MER-DEA-004")) == 1 and len(feedback()) == 2 and not completion("c3").get("reflected_at"))

# ── 8. The email copy and the words ──
sent = []
async def fake_send(to_email, to_name, subject, body, attachments=None): sent.append((subject, body))
email_sender._send = fake_send
asyncio.run(email_sender.send_reflection_email(to_email="b@example.com", to_name="Bob", course_title="Course T",
                                               cert_number="MER-2026-0001", learned="A", change="B"))
subj, body = sent[0]
check("reflection email: subject, certificate number, both answers, the My CPD link",
      subj == "Your reflection: Course T" and "Certificate number: MER-2026-0001" in body and "What I learned:\nA" in body
      and "What I will do differently:\nB" in body and "/my-cpd/certificates" in body)
words = (main._step_form("/x", "/y", True, True) + main._step_thanks_page({"feedback": True, "reflection": False}).body.decode()
         + body + (ROOT / "landing-page" / "quality.html").read_text(encoding="utf-8").split("<h2>Feedback and reflection</h2>")[1].split("<h2>")[0])
words = re.sub(r"<style>.*?</style>", "", words, flags=re.S)
check("new words: no exclamation marks, em dashes, 'accredited' or 'approved'",
      "!" not in re.sub(r"<!DOCTYPE[^>]*>", "", words) and "—" not in words and not re.search(r"accredit|approved", words, re.I))
check("quality page says the step exists, in the present tense", "Both are optional." in words and "being added" not in words)

print(f"\n{'ALL CHECKS PASSED' if not fails else f'{fails} FAILED'}")
if fails:
    raise SystemExit(1)
