"""Tests for subscription access following Stripe (cancellations, renewals, portal, sync).
Run from anywhere: python3 test_subscriptions.py"""
import os, sys, types, time
from datetime import datetime, timezone, timedelta
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
    def eq(s, c, v): s.f.append(lambda r: r.get(c) == v); return s
    def in_(s, c, v): s.f.append(lambda r: r.get(c) in v); return s
    def like(s, *a): return s
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
            row = dict(s.pl); row.setdefault("id", f"{s.t}-{len(rows) + 1}")  # Supabase generates ids
            rows.append(row); return Res([row])
        hit = [r for r in rows if all(f(r) for f in s.f)]
        if s.op == "update": [r.update(s.pl) for r in hit]
        return Res(hit)

now = int(time.time())
future, past = now + 300 * 86400, now - 2 * 86400
db = {"members": [
        {"id": "m1", "email": "sub@example.com", "name": "Sub", "plan": "subscription", "stripe_customer_id": "cus_1"},
        {"id": "m2", "email": "single@example.com", "name": "Single", "plan": "single", "stripe_customer_id": "cus_2"},
        {"id": "m3", "email": "leaver@example.com", "name": "Leaver", "plan": "subscription", "stripe_customer_id": "cus_3"},
        {"id": "m4", "email": "newsub@example.com", "name": "New", "plan": "single", "stripe_customer_id": ""}],
      "purchases": [{"member_id": "m3", "course_id": "MER-DEA-003"}],
      "certificates": [],
      "completions": [{"member_id": "m3", "course_id": "MER-DEA-002", "completion_token": "t1", "completed_at": "2026-05-01", "downloaded_at": "2026-04-30"},
                      {"member_id": "m3", "course_id": "MER-DEA-004", "completion_token": "t2", "completed_at": None, "downloaded_at": "2026-05-02"},
                      {"member_id": "m3", "course_id": "MER-DEA-005", "completion_token": "t3", "completed_at": None, "downloaded_at": None}]}
main.supabase = types.SimpleNamespace(table=lambda t: Q(db, t),
    storage=types.SimpleNamespace(from_=lambda b: types.SimpleNamespace(download=lambda f: (_ for _ in ()).throw(RuntimeError("no catalogue")))))
main._refresh_under_review = lambda: None

# Stripe stand-ins
_so = lambda d: main.stripe.StripeObject.construct_from(d, "sk_test_x")
subs = {"sub_1": {"id": "sub_1", "customer": "cus_1", "status": "active", "items": {"data": [{"current_period_end": future + 86400}]}}}
customers = {"cus_new": {"id": "cus_new", "email": "NewSub@example.com"}}
portal_calls = []
_so = lambda d: main.stripe.StripeObject.construct_from(d, "sk_test_x")
main.stripe.Subscription.retrieve = staticmethod(lambda sid: _so(subs[sid]))
main.stripe.Customer.retrieve = staticmethod(lambda cid: _so(customers[cid]))
main.stripe.Customer.list = staticmethod(lambda email, limit: _so({"data": []}))
main.stripe.billing_portal.Session.create = staticmethod(lambda customer, return_url: portal_calls.append(customer) or _so({"url": "https://billing.stripe.com/p/session_x"}))
class _List:
    def __init__(s, items): s.items = items
    def auto_paging_iter(s): return iter(s.items)
main.stripe.Subscription.list = staticmethod(lambda status, limit: _List([_so(x) for x in [
    {"id": "sub_1", "customer": "cus_1", "status": "active", "current_period_end": future},
    {"id": "sub_x", "customer": "cus_unknown", "status": "canceled", "ended_at": past}]]))
customers["cus_unknown"] = {"id": "cus_unknown", "email": "nobody@example.com"}
pending = {}
main.stripe.Webhook.construct_event = staticmethod(lambda payload, sig, secret: pending["event"])

c = TestClient(main.app, follow_redirects=False)
def send(etype, obj):
    # Stripe delivers StripeObjects (not dicts in stripe-python 16), as production will
    obj = main.stripe.StripeObject.construct_from(obj, "sk_test_x")
    pending["event"] = {"type": etype, "data": {"object": obj}}
    r = c.post("/stripe-webhook", content=b"{}", headers={"stripe-signature": "x"}); assert r.status_code == 200, r.text
def m(i): return next(x for x in db["members"] if x["id"] == i)
def exp(i): return datetime.fromisoformat(m(i)["subscription_expires_at"])

# 0. A subscriber not yet synced keeps access
assert main.subscription_active(m("m1")) and not main.subscription_active(m("m2"))

# 1. Renewal or update, newer API shape (period end on the items)
send("customer.subscription.updated", {"id": "sub_1", "customer": "cus_1", "status": "active", "items": {"data": [{"current_period_end": future}]}})
assert abs((exp("m1") - datetime.fromtimestamp(future, timezone.utc)).total_seconds() - 7 * 86400) < 2
assert main.subscription_active(m("m1"))
print("1 update sets access to period end + 7 days")

# 2. Renewal invoice paid, newer API invoice shape
send("invoice.paid", {"id": "in_1", "customer": "cus_1", "parent": {"subscription_details": {"subscription": "sub_1"}}})
assert abs((exp("m1") - datetime.fromtimestamp(future + 86400, timezone.utc)).total_seconds() - 7 * 86400) < 2
print("2 renewal invoice extends access")

# 3. Cancellation ends access on the end date Stripe gives
send("customer.subscription.deleted", {"id": "sub_3", "customer": "cus_3", "status": "canceled", "ended_at": past})
assert not main.subscription_active(m("m3")) and m("m3")["plan"] == "subscription"
print("3 cancellation ends access")

# 4. Failed payment changes nothing
before = dict(m("m1")); send("invoice.payment_failed", {"id": "in_2", "customer": "cus_1", "subscription": "sub_1"}); assert m("m1") == before
print("4 failed payment logged, access unchanged")

# 5. A subscription for a customer we only know by email: matched, upgraded, customer id stored
send("customer.subscription.created", {"id": "sub_9", "customer": "cus_new", "status": "active", "current_period_end": future})
assert m("m4")["plan"] == "subscription" and m("m4")["stripe_customer_id"] == "cus_new" and main.subscription_active(m("m4"))
print("5 new subscriber matched by email (case-insensitive)")

# 6. Cancellation for a single-course buyer leaves the record alone; incomplete subscriptions change nothing
send("customer.subscription.deleted", {"id": "sub_2", "customer": "cus_2", "status": "canceled", "ended_at": past})
assert m("m2")["plan"] == "single" and "subscription_expires_at" not in m("m2")
send("customer.subscription.created", {"id": "sub_2b", "customer": "cus_2", "status": "incomplete"}); assert m("m2")["plan"] == "single"
print("6 single buyer and incomplete subscription untouched")

# 7. The ex-subscriber's dashboard: no library, no new tokens, keeps what was bought, downloaded or completed
n_tokens = len(db["completions"])
r = c.get("/my-cpd/dashboard", cookies={"session_token": main._make_session_token("leaver@example.com")}); assert r.status_code == 200
t = r.text
assert "Subscription ended" in t and "/my-cpd/billing" in t
assert len(db["completions"]) == n_tokens, "no new tokens for an ex-subscriber"
for cid in ("MER-DEA-002", "MER-DEA-003", "MER-DEA-004"): assert cid in t, cid
assert "MER-DEA-005" not in t and "MER-DEA-006" not in t
print("7 ex-subscriber keeps bought, downloaded and completed courses only")

# 8. Active subscriber's dashboard still gets the full library and the manage link
r = c.get("/my-cpd/dashboard", cookies={"session_token": main._make_session_token("sub@example.com")})
assert r.status_code == 200 and "Annual Subscription" in r.text and "/my-cpd/billing" in r.text
assert sum(1 for x in db["completions"] if x["member_id"] == "m1") == sum(1 for k in main.COURSES if main.is_available(k))
r = c.get("/my-cpd/dashboard", cookies={"session_token": main._make_session_token("single@example.com")})
assert r.status_code == 200 and "/my-cpd/billing" not in r.text
print("8 active subscriber sees the library; single buyer has no manage link")

# 9. Customer portal
r = c.get("/my-cpd/billing", cookies={"session_token": main._make_session_token("sub@example.com")})
assert r.status_code == 303 and r.headers["location"] == "https://billing.stripe.com/p/session_x" and portal_calls == ["cus_1"]
r = c.get("/my-cpd/billing"); assert r.status_code == 302 and r.headers["location"] == "/my-cpd"
db["members"].append({"id": "m5", "email": "nocus@example.com", "name": "N", "plan": "single", "stripe_customer_id": ""})
r = c.get("/my-cpd/billing", cookies={"session_token": main._make_session_token("nocus@example.com")})
assert r.status_code == 200 and "hello@meridiancpd.co.uk" in r.text
print("9 portal redirect, sign-in required, fallback page")

# 10. Admin sync: needs the admin password; updates matched members, counts the rest
r = c.post("/admin/sync-subscriptions"); assert r.status_code == 401
r = c.post("/admin/sync-subscriptions", auth=("admin", "test-admin")); assert r.status_code == 200, r.status_code
assert "Updated 1 member" in r.text and "1 subscription(s) matched no member" in r.text
assert abs((exp("m1") - datetime.fromtimestamp(future, timezone.utc)).total_seconds() - 7 * 86400) < 2
r = c.get("/admin/members", auth=("admin", "test-admin")); assert "Access until" in r.text and "Sub ended" in r.text
print("10 admin sync and members page")

# 11. Checkout for the annual plan records the access date straight away
main.PRICE_TO_COURSE["price_sub"] = "SUBSCRIPTION"
sent = []
async def fake_send(**k): sent.append(k)
main.send_course_email = fake_send
main.stripe.checkout.Session.list_line_items = staticmethod(lambda sid, limit: types.SimpleNamespace(
    data=[types.SimpleNamespace(price=types.SimpleNamespace(id="price_sub"))]))
subs["sub_c"] = {"id": "sub_c", "customer": "cus_c", "status": "active", "items": {"data": [{"current_period_end": future}]}}
send("checkout.session.completed", {"id": "cs_1", "mode": "subscription", "subscription": "sub_c", "customer": "cus_c",
     "customer_details": {"email": "Buyer@Example.com", "name": "Buyer"}, "amount_total": 7900, "client_reference_id": ""})
b = next(x for x in db["members"] if x["email"] == "buyer@example.com")
assert b["plan"] == "subscription" and b["stripe_customer_id"] == "cus_c" and main.subscription_active(b)
assert b["subscription_expires_at"] and sent and sent[0]["is_subscription"]
print("11 checkout creates the subscriber with an access date and sends the welcome email")
print("ALL CHECKS PASSED")
