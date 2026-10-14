"""Tests for the back office: who counts as a subscriber, buyer, free-course taker or test,
and that tests never reach the figures. Run: python3 tests/test_admin.py"""
import os, sys, types
from datetime import datetime, timezone, timedelta
os.environ.update(STRIPE_SECRET_KEY="sk_test_x", STRIPE_WEBHOOK_SECRET="whsec_x", SUPABASE_URL="https://example.supabase.co",
                  SUPABASE_SERVICE_ROLE_KEY="eyJhbGciOiJIUzI1NiJ9.eyJyb2xlIjoic2VydmljZV9yb2xlIn0.x", SESSION_SECRET="s",
                  ADMIN_PASSWORD="test-admin", ADMIN_TEST_EMAILS="mytest@gmail.com")
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
import main
from fastapi.testclient import TestClient

class Res:
    def __init__(self, data): self.data, self.count = data, len(data)
class Q:
    def __init__(s, db, t): s.db, s.t, s.f, s.op, s.pl = db, t, [], "select", None
    def select(s, *a, **k): return s
    def eq(s, c, v): s.f.append(lambda r: r.get(c) == v); return s
    def order(s, *a, **k): return s
    def limit(s, *a): return s
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

now = datetime.now(timezone.utc)
iso = lambda d: d.isoformat()
db = {
  "members": [
    {"id": "sub", "email": "sub@firm.co.uk", "name": "Sue Sub", "plan": "subscription", "stripe_customer_id": "cus_a",
     "subscription_expires_at": iso(now + timedelta(days=30)), "joined_at": "2026-05-01"},
    {"id": "unc", "email": "unc@firm.co.uk", "name": "Una Unconfirmed", "plan": "subscription", "stripe_customer_id": "", "joined_at": "2026-05-02"},
    {"id": "end", "email": "end@firm.co.uk", "name": "Ed Ended", "plan": "subscription", "stripe_customer_id": "cus_e",
     "subscription_expires_at": iso(now - timedelta(days=3)), "joined_at": "2026-05-03"},
    {"id": "buy", "email": "buy@firm.co.uk", "name": "Bea Buyer", "plan": "single", "stripe_customer_id": "cus_b", "joined_at": "2026-05-04"},
    {"id": "fre", "email": "free@firm.co.uk", "name": "Fred Free", "plan": "single", "stripe_customer_id": "cus_f", "joined_at": "2026-05-05"},
    {"id": "non", "email": "none@firm.co.uk", "name": "Nora None", "plan": "single", "stripe_customer_id": "", "joined_at": "2026-05-06"},
    {"id": "t1", "email": "hello@meridiancpd.co.uk", "name": "Matt Test", "plan": "subscription", "stripe_customer_id": "", "joined_at": "2026-03-17"},
    {"id": "t2", "email": "someone@gmail.com", "name": "Test Fire", "plan": "single", "stripe_customer_id": "cus_test", "joined_at": "2026-03-18"},
    {"id": "t3", "email": "mytest@gmail.com", "name": "Env Test", "plan": "single", "stripe_customer_id": "cus_z", "joined_at": "2026-03-19"},
    {"id": "t4", "email": "real@looking.co.uk", "name": "Only Test Purchases", "plan": "single", "stripe_customer_id": "cus_q", "joined_at": "2026-03-20"},
  ],
  "purchases": [
    {"member_id": "sub", "course_id": "SUBSCRIPTION", "amount_gbp": 79.0, "stripe_session_id": "cs_live_1", "purchased_at": "2026-05-01T10:00"},
    {"member_id": "buy", "course_id": "MER-DEA-002", "amount_gbp": 19.99, "stripe_session_id": "cs_live_2", "purchased_at": "2026-05-04T10:00"},
    {"member_id": "fre", "course_id": "MER-DEA-001", "amount_gbp": 0, "stripe_session_id": "cs_live_3", "purchased_at": "2026-05-05T10:00"},
    {"member_id": "t1", "course_id": "MER-DEA-001", "amount_gbp": 0, "stripe_session_id": "cs_live_4", "purchased_at": "2026-03-17T10:00"},
    {"member_id": "t2", "course_id": "MER-DEA-001", "amount_gbp": 2.0, "stripe_session_id": "cs_test_aa", "purchased_at": "2026-03-18T10:00"},
    {"member_id": "t3", "course_id": "MER-DEA-002", "amount_gbp": 19.99, "stripe_session_id": "cs_live_5", "purchased_at": "2026-03-19T10:00"},
    {"member_id": "t4", "course_id": "MER-DEA-003", "amount_gbp": 1.0, "stripe_session_id": "cs_test_bb", "purchased_at": "2026-03-20T10:00"},
  ],
  "certificates": [
    {"id": "c1", "member_id": "buy", "cert_number": "MER-2026-0002", "course_id": "MER-DEA-002", "cpd_hours": 1, "issued_at": "2026-05-10", "members": {"name": "Bea Buyer", "email": "buy@firm.co.uk"}},
    {"id": "c2", "member_id": "t1", "cert_number": "MER-2026-0001", "course_id": "MER-DEA-001", "cpd_hours": 2, "issued_at": "2026-03-17", "members": {"name": "Matt Test", "email": "hello@meridiancpd.co.uk"}},
  ],
  "completions": [{"id": "x1", "member_id": "buy", "completed_at": "2026-05-10"}, {"id": "x2", "member_id": "t1", "completed_at": "2026-03-17"}],
  "outreach_suppressed": [{"email": "a@b.c"}, {"email": "d@e.f"}],
}
main.supabase = types.SimpleNamespace(table=lambda t: Q(db, t),
    storage=types.SimpleNamespace(from_=lambda b: types.SimpleNamespace(download=lambda f: (_ for _ in ()).throw(RuntimeError("no catalogue")))))
main._refresh_under_review = lambda: None

class FakeHTTP:
    def __init__(s, **k): pass
    async def __aenter__(s): return s
    async def __aexit__(s, *a): return False
    async def head(s, url): return types.SimpleNamespace(status_code=404 if "MER-DEA-005" in url else 200)
main.httpx.AsyncClient = FakeHTTP

c = TestClient(main.app, follow_redirects=False)
A = ("admin", "test-admin")

# 1. Classification
by = main._purchases_by_member(); tests = main._test_emails()
got = {m["id"]: main.classify_member(m, by.get(m["id"], []), tests)[0] for m in db["members"]}
assert got == {"sub": "subscriber", "unc": "unconfirmed", "end": "ended", "buy": "buyer", "fre": "free",
               "non": "none", "t1": "test", "t2": "test", "t3": "test", "t4": "test"}, got
print("1 classification: subscriber, unconfirmed, ended, buyer, free, none and four kinds of test")

# 2. Dashboard leaves tests out of every figure
r = c.get("/admin", auth=A); assert r.status_code == 200, r.status_code; t = " ".join(r.text.split())
def tile(label):
    i = t.index(f'<div class="lbl">{label}</div>'); j = t.rindex('<div class="val">', 0, i)
    return t[j + 17:t.index("</div>", j)]
assert tile("Active subscribers") == "1" and "1 more not yet confirmed in Stripe" in t
assert tile("Course buyers") == "1" and "1 took a free course only" in t and "1 subscription ended" in t
assert tile("Revenue recorded") == "£99" and "2 paid purchases" in t
assert tile("Certificates issued") == "1" and "1 course completed" in t
assert "4 test accounts" in t and "Needs attention" in t
for leaked in ("hello@meridiancpd.co.uk", "mytest@gmail.com", "someone@gmail.com", "real@looking.co.uk"):
    assert leaked not in t, leaked
assert "Sue Sub" in t.split("Renewals in the next 60 days")[1].split("Recent purchases")[0]
assert "Annual subscription" in t and "Free course" in t
print("2 dashboard: tests excluded from counts, revenue, certificates and recent purchases; renewals listed")

# 3. Members filters
r = c.get("/admin/members", auth=A); t = " ".join(r.text.split())
assert "All members (6)" in t and "Tests (4)" in t and "Subscribers (1)" in t and "Unconfirmed (1)" in t
assert "hello@meridiancpd.co.uk" not in t and "Sync subscriptions from Stripe" in t
r = c.get("/admin/members?show=test", auth=A); t = r.text
assert all(e in t for e in ("hello@meridiancpd.co.uk", "mytest@gmail.com", "someone@gmail.com", "real@looking.co.uk")) and "sub@firm.co.uk" not in t
r = c.get("/admin/members?show=nonsense", auth=A); assert "All members (6)" in r.text
print("3 members page filters")

# 4. Certificates page marks tests
r = c.get("/admin/certificates", auth=A); assert "1 to members, 1 test" in " ".join(r.text.split()) and "badge-test" in r.text
print("4 certificates page separates test certificates")

# 5. System page
r = c.get("/admin/system", auth=A); t = " ".join(r.text.split()); assert r.status_code == 200
n_live = sum(1 for k in main.COURSES if k != "SUBSCRIPTION" and main.is_available(k))
assert f"({n_live - 1} of {n_live} downloadable)" in t and "Problem (404)" in t
assert "DASHBOARD_SECRET" in t and "Not set" in t and "Paused" in t and "<td>2</td>" in t
print("5 system page: PDF checks, settings, outreach")

# 6. Test purchases are never revenue
async def fake_send(**k): pass
main.send_course_email = fake_send
r = c.post("/test-purchase", data={"email": "check@example.com", "course_id": "MER-DEA-002"}, auth=A); assert r.status_code == 200
p = db["purchases"][-1]; assert p["amount_gbp"] == 0 and p["stripe_session_id"].startswith("cs_test_")
print("6 test purchase recorded at £0 and as a test")

for path in ("/admin", "/admin/members", "/admin/system", "/admin/certificates"):
    assert c.get(path).status_code == 401, path
print("ALL CHECKS PASSED")
