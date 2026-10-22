"""Tests for correcting a mistyped email address after checkout: the /thanks page the payment
links send buyers to, and Admin → Members → Fix email. Run: python3 tests/test_fix_email.py"""
import asyncio, os, sys, time, types
os.environ.update(STRIPE_SECRET_KEY="sk_test_x", STRIPE_WEBHOOK_SECRET="whsec_x", SUPABASE_URL="https://example.supabase.co",
                  SUPABASE_SERVICE_ROLE_KEY="eyJhbGciOiJIUzI1NiJ9.eyJyb2xlIjoic2VydmljZV9yb2xlIn0.x", SESSION_SECRET="s",
                  ADMIN_PASSWORD="test-admin")
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
import main
from fastapi.testclient import TestClient


class Res:
    def __init__(self, data): self.data, self.count = data, len(data)
class Q:
    def __init__(s, db, t): s.db, s.t, s.f, s.op, s.pl = db, t, [], "select", None
    def select(s, *a, **k): return s
    def eq(s, c, v): s.f.append(lambda r, c=c, v=v: r.get(c) == v); return s
    def order(s, *a, **k): return s
    def limit(s, *a): return s
    def like(s, *a): return s
    @property
    def not_(s): s._neg = True; return s
    def is_(s, c, _n):
        neg = getattr(s, "_neg", False); s._neg = False
        s.f.append((lambda r: r.get(c) is not None) if neg else (lambda r: r.get(c) is None)); return s
    def insert(s, row): s.op, s.pl = "insert", row; return s
    def update(s, row): s.op, s.pl = "update", row; return s
    def execute(s):
        rows = s.db.setdefault(s.t, [])
        if s.op == "insert":
            row = dict(s.pl); row.setdefault("id", f"{s.t}-{len(rows) + 1}"); rows.append(row); return Res([row])
        hit = [r for r in rows if all(f(r) for f in s.f)]
        if s.op == "update": [r.update(s.pl) for r in hit]
        return Res(hit)


def fresh_db():
    return {
        "members": [
            # created by the order with the typo
            {"id": "typo", "email": "jo@smithsurvaying.co.uk", "name": "Jo", "plan": "single", "stripe_customer_id": ""},
            # a real, separate customer whose address someone else mistyped into
            {"id": "pat", "email": "pat@firm.co.uk", "name": "Pat", "plan": "single", "stripe_customer_id": "cus_pat"},
            # a subscriber's real account, and the record their mistyped renewal order created
            {"id": "sue", "email": "sue@firm.co.uk", "name": "Sue", "plan": "single", "stripe_customer_id": ""},
            {"id": "suetypo", "email": "sue@frim.co.uk", "name": "Sue", "plan": "subscription",
             "stripe_customer_id": "cus_new", "subscription_expires_at": "2027-10-29T00:00:00+00:00"},
        ],
        "purchases": [
            {"id": "p1", "member_id": "typo", "course_id": "MER-DEA-001", "amount_gbp": 0, "stripe_session_id": "cs_live_typo1234567"},
            {"id": "p2", "member_id": "pat", "course_id": "MER-DEA-002", "amount_gbp": 19.99, "stripe_session_id": "cs_live_patold12345"},
            {"id": "p3", "member_id": "pat", "course_id": "MER-DEA-003", "amount_gbp": 19.99, "stripe_session_id": "cs_live_intopat1234"},
            {"id": "p4", "member_id": "suetypo", "course_id": "SUBSCRIPTION", "amount_gbp": 79, "stripe_session_id": "cs_live_subtypo1234"},
        ],
        "completions": [
            {"id": "c1", "member_id": "typo", "course_id": "MER-DEA-001", "completion_token": "tok-typo", "completed_at": None},
            {"id": "c2", "member_id": "pat", "course_id": "MER-DEA-002", "completion_token": "tok-pat", "completed_at": "2026-10-01"},
            {"id": "c3", "member_id": "pat", "course_id": "MER-DEA-003", "completion_token": "tok-intopat", "completed_at": None},
        ],
        "certificates": [{"id": "z1", "member_id": "pat", "cert_number": "MER-2026-0100"}],
    }


db = fresh_db()
main.supabase = types.SimpleNamespace(table=lambda t: Q(db, t),
    storage=types.SimpleNamespace(from_=lambda b: types.SimpleNamespace(download=lambda f: (_ for _ in ()).throw(RuntimeError("no catalogue")))))
main._refresh_under_review = lambda: None

now = time.time()
SESSIONS = {
    "cs_live_typo1234567": {"id": "cs_live_typo1234567", "status": "complete", "created": now - 60, "customer": None,
                            "customer_details": {"email": "jo@smithsurvaying.co.uk"}},
    "cs_live_intopat1234": {"id": "cs_live_intopat1234", "status": "complete", "created": now - 60, "customer": None,
                            "customer_details": {"email": "pat@firm.co.uk"}},
    "cs_live_subtypo1234": {"id": "cs_live_subtypo1234", "status": "complete", "created": now - 60, "customer": "cus_new",
                            "subscription": "sub_1", "customer_details": {"email": "sue@frim.co.uk"}},
    "cs_live_pending1234": {"id": "cs_live_pending1234", "status": "complete", "created": now - 5, "customer": None,
                            "customer_details": {"email": "new@buyer.co.uk"}},
    "cs_live_oldorder123": {"id": "cs_live_oldorder123", "status": "complete", "created": now - 10 * 86400, "customer": None,
                            "customer_details": {"email": "old@buyer.co.uk"}},
    "cs_live_unpaid12345": {"id": "cs_live_unpaid12345", "status": "open", "created": now, "customer": None,
                            "customer_details": {"email": "x@y.co.uk"}},
}
db["purchases"].append({"id": "p5", "member_id": "oldm", "course_id": "MER-DEA-004", "amount_gbp": 19.99,
                        "stripe_session_id": "cs_live_oldorder123"})
db["members"].append({"id": "oldm", "email": "old@buyer.co.uk", "name": "Old", "plan": "single", "stripe_customer_id": ""})

calls = {"modify": [], "sent": [], "sublist": []}
def _retrieve(sid):
    if sid not in SESSIONS:
        raise main.stripe.error.InvalidRequestError("No such checkout.session", "id")
    return SESSIONS[sid]
main.stripe.checkout.Session.retrieve = _retrieve
main.stripe.Customer.modify = lambda cid, **kw: calls["modify"].append((cid, kw.get("email")))
def _sublist(**kw):
    calls["sublist"].append(kw.get("customer"))
    return types.SimpleNamespace(auto_paging_iter=lambda: iter([]))
main.stripe.Subscription.list = _sublist
async def _send(**kw): calls["sent"].append(kw)
main.send_course_email = _send

c = TestClient(main.app, follow_redirects=False)
A = ("admin", "test-admin")
fails = 0
def check(name, cond):
    global fails
    print(("PASS " if cond else "FAIL ") + name)
    fails += 0 if cond else 1
member = lambda mid: next(m for m in db["members"] if m["id"] == mid)
purchase = lambda pid: next(p for p in db["purchases"] if p["id"] == pid)
completion = lambda cid: next(x for x in db["completions"] if x["id"] == cid)

# ── The page after paying ──
r = c.get("/thanks?session_id=nonsense")
check("unknown order: friendly page, not an error trace", r.status_code == 404 and "hello@meridiancpd.co.uk" in r.text)
r = c.get("/thanks?session_id=cs_live_unpaid12345")
check("unpaid checkout is not treated as an order", r.status_code == 404)
r = c.get("/thanks?session_id=cs_live_pending1234")
check("order not yet recorded: page waits and refreshes", "Finishing your order" in r.text and 'http-equiv="refresh"' in r.text and "n=1" in r.text)
r = c.get("/thanks?session_id=cs_live_pending1234&n=20")
check("stops refreshing after a minute and says what to do", "refresh" not in r.text.split("<style>")[0] and "taking longer" in r.text)
r = c.get("/thanks?session_id=cs_live_typo1234567")
check("thanks page asks about news with buttons, not links", "Hear about new courses" in r.text
      and 'action="/my-cpd/consent/yes"' in r.text and "/my-cpd/consent/yes?" not in r.text)
check("shows the address the course went to", "jo@smithsurvaying.co.uk" in r.text and "What&#x27;s Changed" in r.text)
check("offers the correction form", 'action="/thanks/email"' in r.text and 'name="email2"' in r.text)

# ── Buyer corrects their own typo ──
post = lambda sid, e1, e2: c.post("/thanks/email", data={"session_id": sid, "email": e1, "email2": e2})
r = post("cs_live_typo1234567", "jo@smithsurveying.co.uk", "jo@smithsurvey.co.uk")
check("addresses that don't match are refused", r.status_code == 400 and "do not match" in r.text
      and member("typo")["email"] == "jo@smithsurvaying.co.uk")
r = post("cs_live_typo1234567", "not-an-email", "not-an-email")
check("an invalid address is refused", r.status_code == 400 and "does not look like" in r.text)
r = post("cs_live_typo1234567", "jo@smithsurvaying.co.uk", "jo@smithsurvaying.co.uk")
check("the same address is refused", r.status_code == 400 and "already used" in r.text)
calls["sent"].clear()
r = post("cs_live_typo1234567", " jo@smithsurveying.co.uk ", "jo@smithsurveying.co.uk")
check("correction accepted", r.status_code == 200 and "jo@smithsurveying.co.uk" in r.text and "Done" in r.text)
check("record created by the typo is renamed in place", member("typo")["email"] == "jo@smithsurveying.co.uk")
check("course sent again to the new address with the same completion link",
      len(calls["sent"]) == 1 and calls["sent"][0]["to_email"] == "jo@smithsurveying.co.uk"
      and calls["sent"][0]["completion_link"].endswith("/complete/tok-typo") and calls["sent"][0]["pdf_url"])
check("no Stripe customer to update on a free single order", calls["modify"] == [])
r = c.get("/thanks?session_id=cs_live_typo1234567")
check("after correcting, the page shows the new address and no form",
      "jo@smithsurveying.co.uk" in r.text and 'action="/thanks/email"' not in r.text and "already been corrected" in r.text)
r = post("cs_live_typo1234567", "someone@else.co.uk", "someone@else.co.uk")
check("only one correction per order", r.status_code == 400 and member("typo")["email"] == "jo@smithsurveying.co.uk")

# ── Someone mistyped their address into another real customer's ──
calls["sent"].clear()
r = post("cs_live_intopat1234", "chris@other.co.uk", "chris@other.co.uk")
chris = next(m for m in db["members"] if m["email"] == "chris@other.co.uk")
check("the other customer's record keeps its address", member("pat")["email"] == "pat@firm.co.uk")
check("the order moves to a new record for the right address", purchase("p3")["member_id"] == chris["id"])
check("the other customer's own purchase stays with them", purchase("p2")["member_id"] == "pat")
check("the unused completion link moves with the order", completion("c3")["member_id"] == chris["id"])
check("the other customer's completed course is untouched", completion("c2")["member_id"] == "pat")
check("the course is resent to the right address", [s["to_email"] for s in calls["sent"]] == ["chris@other.co.uk"])

# ── Subscription bought under a typo, corrected to the buyer's existing account ──
calls["sent"].clear(); calls["modify"].clear()
r = post("cs_live_subtypo1234", "sue@firm.co.uk", "sue@firm.co.uk")
check("subscription moves to the existing account", purchase("p4")["member_id"] == "sue")
check("existing account becomes the subscriber", member("sue")["plan"] == "subscription"
      and member("sue")["stripe_customer_id"] == "cus_new" and member("sue")["subscription_expires_at"])
check("typo record no longer counts as a subscriber", member("suetypo")["plan"] == "single"
      and member("suetypo")["stripe_customer_id"] is None)
check("Stripe customer's email corrected (receipts and renewals)", calls["modify"] == [("cus_new", "sue@firm.co.uk")])
check("access re-synced from Stripe", "cus_new" in calls["sublist"])
check("welcome email resent to the right address", len(calls["sent"]) == 1 and calls["sent"][0]["is_subscription"]
      and calls["sent"][0]["to_email"] == "sue@firm.co.uk")

# ── Too late for self-service ──
next(m for m in db["members"] if m["id"] == "oldm")["marketing_consent"] = False
r = c.get("/thanks?session_id=cs_live_oldorder123")
check("someone who has already answered is not asked again", "Hear about new courses" not in r.text)
check("after 7 days the page points to hello@ instead of offering the form",
      'action="/thanks/email"' not in r.text and "hello@meridiancpd.co.uk" in r.text)
r = post("cs_live_oldorder123", "fixed@buyer.co.uk", "fixed@buyer.co.uk")
check("after 7 days a correction is refused", r.status_code == 400 and member("oldm")["email"] == "old@buyer.co.uk")

# ── Admin → Members → Fix email ──
r = c.get("/admin/members", auth=A)
check("members list links to Fix email", "/admin/members/oldm/email" in r.text)
r = c.get("/admin/members/oldm/email")
check("fix email needs the admin password", r.status_code == 401)
r = c.get("/admin/members/oldm/email", auth=A)
check("admin form shows the member and their orders", r.status_code == 200 and "old@buyer.co.uk" in r.text and "MER-DEA-004" in r.text)
calls["sent"].clear()
r = c.post("/admin/members/oldm/email", auth=A, data={"email": "fixed@buyer.co.uk", "email2": "fixed@buyer.co.uk", "resend": "1"})
check("admin change renames the member", member("oldm")["email"] == "fixed@buyer.co.uk" and "Email changed" in r.text)
check("admin change resends the course", [s["to_email"] for s in calls["sent"]] == ["fixed@buyer.co.uk"]
      and calls["sent"][0]["completion_link"])
calls["sent"].clear()
r = c.post("/admin/members/pat/email", auth=A, data={"email": "pat@newfirm.co.uk", "email2": "pat@newfirm.co.uk", "resend": "1"})
check("admin can rename a member with certificates", member("pat")["email"] == "pat@newfirm.co.uk")
check("a completed course is resent without a completion link (no second certificate)",
      [s["completion_link"] for s in calls["sent"]] == [None])
check("their Stripe customer email follows", ("cus_pat", "pat@newfirm.co.uk") in calls["modify"])
r = c.post("/admin/members/pat/email", auth=A, data={"email": "a@b.co.uk", "email2": "a@c.co.uk"})
check("admin: mismatched addresses refused", r.status_code == 400 and member("pat")["email"] == "pat@newfirm.co.uk")

print(f"\n{'ALL PASSED' if not fails else f'{fails} FAILED'}")
sys.exit(1 if fails else 0)
