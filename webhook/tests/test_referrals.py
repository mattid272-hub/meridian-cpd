"""Tests for refer a colleague (referrals.py, /my-cpd/refer, /r/<code>, the webhook credit).
Run from anywhere: python3 test_referrals.py"""
import os, sys, types, time, re
os.environ.update(STRIPE_SECRET_KEY="sk_test_x", STRIPE_WEBHOOK_SECRET="whsec_x", SUPABASE_URL="https://example.supabase.co",
                  SUPABASE_SERVICE_ROLE_KEY="eyJhbGciOiJIUzI1NiJ9.eyJyb2xlIjoic2VydmljZV9yb2xlIn0.x", SESSION_SECRET="s",
                  ADMIN_PASSWORD="test-admin", STRIPE_PRICE_SUBSCRIPTION="price_sub", STRIPE_PRICE_SINGLE="price_single")
os.environ.pop("REFERRAL_COUPON_ID", None)
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, ".."))
import main
import referrals
import followup
from fastapi.testclient import TestClient

failures = 0
def check(ok, label):
    global failures
    print(("PASS " if ok else "FAIL ") + label)
    if not ok:
        failures += 1

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
            row = dict(s.pl); row.setdefault("id", f"{s.t}-{len(rows) + 1}")
            row.setdefault("created_at", f"2026-11-09T10:{len(rows):02d}:00Z")
            rows.append(row); return Res([row])
        hit = [r for r in rows if all(f(r) for f in s.f)]
        if s.op == "update": [r.update(s.pl) for r in hit]
        return Res(hit)

future = int(time.time()) + 300 * 86400
db = {"members": [
        {"id": "m1", "email": "matt@example.com", "name": "Matt Davies", "plan": "subscription", "stripe_customer_id": "cus_1"},
        {"id": "m2", "email": "single@example.com", "name": "Sam Single", "plan": "single", "stripe_customer_id": "cus_2"},
        {"id": "m5", "email": "back@example.com", "name": "Bea Back", "plan": "subscription", "stripe_customer_id": "cus_5",
         "subscription_expires_at": "2026-01-01T00:00:00+00:00"}],
      "purchases": [{"member_id": "m5", "course_id": "SUBSCRIPTION", "stripe_session_id": "cs_live_old5"}],
      "completions": [], "certificates": [], "referrals": []}
main.supabase = types.SimpleNamespace(table=lambda t: Q(db, t),
    storage=types.SimpleNamespace(from_=lambda b: types.SimpleNamespace(download=lambda f: (_ for _ in ()).throw(RuntimeError("no catalogue")))))
main._refresh_under_review = lambda: None
sent_emails = []
async def _fake_send(**kw): sent_emails.append(kw)
main.send_course_email = _fake_send

# Stripe stand-ins
_so = lambda d: main.stripe.StripeObject.construct_from(d, "sk_test_x")
promos, balances, txns, fail_credit = {}, {"cus_1": 0}, [], {"on": False}
price = {"unit_amount": 7900}
def _promo_create(**kw):
    pid = f"promo_{len(promos) + 1}"
    promos[pid] = dict(kw, id=pid); return _so(promos[pid])
def _promo_retrieve(pid):
    if pid == "promo_meridian10":
        return _so({"id": pid, "code": "MERIDIAN10", "metadata": {}})
    return _so(promos[pid])
def _balance_txn(customer, **kw):
    if fail_credit["on"]:
        raise main.stripe.error.APIConnectionError("network down")
    txns.append(dict(kw, customer=customer)); balances[customer] = balances.get(customer, 0) + kw["amount"]
    return _so({"id": f"cbtxn_{len(txns)}", "amount": kw["amount"]})
main.stripe.PromotionCode.create = staticmethod(_promo_create)
main.stripe.PromotionCode.retrieve = staticmethod(_promo_retrieve)
main.stripe.Customer.retrieve = staticmethod(lambda cid: _so({"id": cid, "email": "", "balance": balances.get(cid, 0)}))
main.stripe.Customer.create_balance_transaction = staticmethod(_balance_txn)
main.stripe.Subscription.list = staticmethod(lambda **kw: _so({"data": [
    {"id": "sub_1", "status": "active", "items": {"data": [{"price": {"unit_amount": 7900}}]}}]}))
main.stripe.Subscription.retrieve = staticmethod(lambda sid: _so({"id": sid, "customer": "cus_x", "status": "active", "current_period_end": future}))
main.stripe.Price.retrieve = staticmethod(lambda pid: _so(dict(price, id=pid)))
expanded = {}
main.stripe.checkout.Session.retrieve = staticmethod(lambda sid, **kw: _so(expanded.get(sid, {"id": sid})))
line_items = {}
main.stripe.checkout.Session.list_line_items = staticmethod(lambda sid, limit=5: _so({"data": [{"price": {"id": line_items.get(sid, "price_sub")}}]}))
pending = {}
main.stripe.Webhook.construct_event = staticmethod(lambda payload, sig, secret: pending["event"])

c = TestClient(main.app, follow_redirects=False, raise_server_exceptions=False)
def signed(email): return {"session_token": main._make_session_token(email)}
def m(i): return next(x for x in db["members"] if x["id"] == i)
def send(session):
    obj = main.stripe.StripeObject.construct_from(session, "sk_test_x")
    pending["event"] = {"type": "checkout.session.completed", "data": {"object": obj}}
    return c.post("/stripe-webhook", content=b"{}", headers={"stripe-signature": "x"})
def session(sid, email, name="Jo Bloggs", promo=None, mode="subscription", amount=6900, customer="cus_new"):
    s = {"id": sid, "mode": mode, "payment_status": "paid", "amount_total": amount, "customer": customer,
         "customer_details": {"email": email, "name": name}}
    if promo:
        s["discounts"] = [{"coupon": "coupon_ref", "promotion_code": promo}]
    return s
def ref(sid): return next((r for r in db["referrals"] if r["stripe_session_id"] == sid), None)
def text_only(html):
    html = re.sub(r"<style.*?</style>", " ", html, flags=re.S)
    return __import__("html").unescape(re.sub(r"<[^>]+>", " ", html))

# 1. Off until REFERRAL_COUPON_ID is set: no tab, no code, the link page is not active
r = c.get("/my-cpd/refer", cookies=signed("matt@example.com"))
check(r.status_code == 200 and "This is not open yet." in r.text and not promos, "off: the page says not open and makes no code")
check("/my-cpd/refer" not in c.get("/my-cpd/dashboard", cookies=signed("matt@example.com")).text, "off: no Refer tab in the member area")
check(c.get("/r/MATT-ABCD").status_code == 404, "off: a referral link is not active")
send(session("cs_live_off", "off@example.com", promo="promo_1"))
check(not db["referrals"], "off: the webhook records nothing")

os.environ["REFERRAL_COUPON_ID"] = "coupon_ref"

# 2. A subscriber's page makes one personal code on Matt's coupon, once
r = c.get("/my-cpd/refer", cookies=signed("matt@example.com"))
code = m("m1").get("referral_code") or ""
check(r.status_code == 200 and re.fullmatch(r"MATT-[A-Z2-9]{4}", code) is not None, f"subscriber gets a personal code ({code})")
p = promos.get(m("m1").get("referral_promo_id"), {})
check(p.get("promotion") == {"type": "coupon", "coupon": "coupon_ref"} and p.get("code") == code
      and p.get("restrictions") == {"first_time_transaction": True} and p.get("metadata", {}).get("member_id") == "m1",
      "the promotion code is on the referral coupon, first-time only, and names the member")
link = f"{main.APP_URL}/r/{code}"
check(code in r.text and link in r.text, "the page shows the code and the link")
check(f"I do my CPD with Meridian CPD. My code {code} takes £10 off your first year: {link}" in r.text, "the page shows the message to send")
check("None yet." in r.text and "Credit for your next renewal: £0" in r.text, "nobody referred yet, no credit yet")
check("/my-cpd/refer" in c.get("/my-cpd/dashboard", cookies=signed("matt@example.com")).text, "on: the Refer tab is in the member area")
c.get("/my-cpd/refer", cookies=signed("matt@example.com"))
check(len(promos) == 1 and m("m1")["referral_code"] == code, "a second visit keeps the same code")

# 3. A single-course buyer has no code
r = c.get("/my-cpd/refer", cookies=signed("single@example.com"))
check("Referral codes come with the annual subscription." in r.text and not m("m2").get("referral_code") and len(promos) == 1,
      "a single-course buyer gets no code")

# 4. The link page: price from the live Stripe price, code filled in at checkout
r = c.get(f"/r/{code.lower()}")
check(r.status_code == 200 and f"The annual subscription with code {code}: £69 for your first year." in r.text, "link page: £69 while the annual price is £79")
check(f"https://buy.stripe.com/fZufZgbse3BpcXE7TY73G01?prefilled_promo_code={code}" in r.text, "link page: checkout with the code filled in")
check('name="robots" content="noindex"' in r.text, "link page is not indexed")
price["unit_amount"] = 9900; followup._price_cache.update(at=None, gbp=None)
check("£89 for your first year." in c.get(f"/r/{code}").text, "link page: £89 once the annual price is £99")
price["unit_amount"] = 12345; followup._price_cache.update(at=None, gbp=None)
r = c.get(f"/r/{code}")
check(f"The annual subscription with code {code}." in r.text and "for your first year." not in r.text.split("£10 off your first year")[-1],
      "link page: no total if the live price is not one the copy is written for")
price["unit_amount"] = 7900; followup._price_cache.update(at=None, gbp=None)
check(c.get("/r/NOBODY-1234").status_code == 404 and c.get("/r/<script>").status_code == 404, "unknown or malformed codes are not active")

promo_id = m("m1")["referral_promo_id"]

# 5. A colleague subscribes with the code: order delivered, £10 credit for the referrer, once
r = send(session("cs_live_jo", "jo@example.com", promo=promo_id))
row = ref("cs_live_jo")
check(r.status_code == 200 and row and row["status"] == "credited" and row["credit_pence"] == 1000, "a paid referral is recorded and credited")
check(txns == [{"amount": -1000, "currency": "gbp", "description": "Referral credit, Meridian CPD",
                "metadata": {"purpose": "referral", "checkout_session": "cs_live_jo"},
                "idempotency_key": "referral-credit-cs_live_jo", "customer": "cus_1"}],
      "the credit is £10 on the referrer's Stripe balance, with an idempotency key")
check(any(e.get("is_subscription") for e in sent_emails), "the newcomer's welcome email still goes")
send(session("cs_live_jo", "jo@example.com", promo=promo_id))
check(len(txns) == 1 and len([x for x in db["referrals"] if x["stripe_session_id"] == "cs_live_jo"]) == 1, "a repeat delivery credits nothing more")
r = c.get("/my-cpd/refer", cookies=signed("matt@example.com"))
check("Jo: £10 credit" in r.text and "Bloggs" not in r.text and "jo@example.com" not in r.text, "the referrer sees the first name only")
check("Credit for your next renewal: £10" in r.text, "the referrer sees the credit waiting")

# 6. Refusals: own code, someone who subscribed before, not a subscription, someone already referred
send(session("cs_live_self", "matt@example.com", promo=promo_id, customer="cus_1"))
check(ref("cs_live_self")["status"] == "refused_self", "own code: no credit")
send(session("cs_live_back", "back@example.com", promo=promo_id, customer="cus_5"))
check(ref("cs_live_back")["status"] == "refused_existing", "someone who subscribed before: no credit")
line_items["cs_live_course"] = "price_single"
send(session("cs_live_course", "kim@example.com", promo=promo_id, mode="payment", amount=999))
check(ref("cs_live_course")["status"] == "refused_not_subscription", "not an annual subscription: no credit")
send(session("cs_live_jo2", "jo@example.com", promo=promo_id))
check(ref("cs_live_jo2")["status"] in ("refused_duplicate", "refused_existing"), "the same colleague twice: no second credit")
check(len(txns) == 1, "none of the refusals added credit")

# 7. Another code (MERIDIAN10) is not a referral
send(session("cs_live_free", "free@example.com", promo="promo_meridian10", mode="payment", amount=0))
check(ref("cs_live_free") is None, "MERIDIAN10 is not a referral")

# 8. The event shape without session.discounts: read from the expanded totals
expanded["cs_live_ann"] = {"id": "cs_live_ann", "total_details": {"breakdown": {"discounts": [{"amount": 1000, "discount": {"promotion_code": promo_id}}]}}}
send(session("cs_live_ann", "ann@example.com", name="Ann Other"))
check(ref("cs_live_ann") and ref("cs_live_ann")["status"] == "credited", "the promotion code is found in the expanded totals")

# 9. Credits stack up to a free year (the referrer's renewal price), then stop
balances["cus_1"] = -7500
send(session("cs_live_p1", "p1@example.com", name="Pat One", promo=promo_id))
check(ref("cs_live_p1")["credit_pence"] == 400 and balances["cus_1"] == -7900, "the credit tops up to a free year and no further")
send(session("cs_live_p2", "p2@example.com", name="Pip Two", promo=promo_id))
check(ref("cs_live_p2")["status"] == "capped" and balances["cus_1"] == -7900, "past a free year the referral counts with no credit")
r = c.get("/my-cpd/refer", cookies=signed("matt@example.com"))
check("Pip: no credit, your credit had already reached a free year" in r.text and "Credit for your next renewal: £79" in r.text, "the page shows the capped referral and the free year")

# 10. Stripe refuses the credit: the webhook asks Stripe to retry, the retry credits once
balances["cus_1"] = 0
fail_credit["on"] = True
r = send(session("cs_live_q", "q@example.com", name="Quinn Q", promo=promo_id))
check(r.status_code == 500 and ref("cs_live_q")["status"] == "credit_failed", "a refused credit is recorded and Stripe is asked to retry")
fail_credit["on"] = False
r = send(session("cs_live_q", "q@example.com", name="Quinn Q", promo=promo_id))
check(r.status_code == 200 and ref("cs_live_q")["status"] == "credited"
      and [t["idempotency_key"] for t in txns].count("referral-credit-cs_live_q") == 1, "the retry credits once")

# 11. Copy rules on the two pages and the terms page
terms_path = os.path.join(HERE, "..", "..", "landing-page", "referral-terms.html")
pages = {"member page": text_only(c.get("/my-cpd/refer", cookies=signed("matt@example.com")).text),
         "link page": text_only(c.get(f"/r/{code}").text),
         "terms page": text_only(open(terms_path, encoding="utf-8").read())}
banned = ["accredit", "approved", "endorse", "certified", "best value", "guarantee", "the only", "free course",
          "!", "—", "#", "exciting", "unlock"]
for label, t in pages.items():
    low = t.lower().replace("&#", "")
    hits = [w for w in banned if w in low and not (w == "free course" and label == "terms page")]
    check(not hits, f"{label}: none of the banned words or marks ({hits})")
terms = pages["terms page"]
check("£10 off" in terms and "first year" in terms and "next renewal" in terms and "free year" in terms
      and "single course" in terms and "own code" in terms, "terms page: the scheme in plain words")

print("\nALL PASS" if not failures else f"\n{failures} FAILED")
if failures:
    sys.exit(1)
