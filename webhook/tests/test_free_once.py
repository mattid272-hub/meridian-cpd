"""The free course is once per person (board row mer-free-code-reuse).
Run: python3 tests/test_free_once.py (or python -m pytest -q from webhook/).

What must hold:
- an address that already holds a real £0 single course is known (admin test rows, the
  subscription, series parts and paid courses do not count; a database error never turns
  a first-timer away);
- the webhook does not record or send a second £0 single course for that address, and
  still handles a first free course, a paid course and a repeat delivery as before;
- /free/<course> asks for the email first, turns a second claim away with a plain page
  that offers the annual membership, and otherwise opens a checkout with the address
  fixed and the discount applied by the app (no typed codes), or the Payment Link with the
  address and code filled in when Checkout Sessions are off;
- /thanks for a £0 order the webhook turned away says so instead of waiting."""
import asyncio, os, sys, types
os.environ.update(STRIPE_SECRET_KEY="sk_test_x", STRIPE_WEBHOOK_SECRET="whsec_x", SUPABASE_URL="https://example.supabase.co",
                  SUPABASE_SERVICE_ROLE_KEY="eyJhbGciOiJIUzI1NiJ9.eyJyb2xlIjoic2VydmljZV9yb2xlIn0.x",
                  ADMIN_PASSWORD="test-admin", STRIPE_PRICE_SINGLE="price_single",
                  STRIPE_PRICE_SUBSCRIPTION="price_sub", STRIPE_PRICE_SERIES="price_series",
                  OUTREACH_SCHEDULER="off", NEWS_SCHEDULER="off")
os.environ.pop("CHECKOUT_SESSIONS", None)
os.environ.pop("FREE_COURSE_CODE", None)
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
import main
from fastapi.testclient import TestClient

fails = 0
def check(name, cond):
    global fails
    print(("PASS " if cond else "FAIL ") + name)
    fails += 0 if cond else 1

main.supabase = types.SimpleNamespace(table=lambda t: (_ for _ in ()).throw(RuntimeError("no database in this test")))
main._refresh_under_review = lambda: None
main.refresh_catalogue = lambda force=False: None
main.UNDER_REVIEW.clear()

# ── A tiny members/purchases store in place of the database ──
MEMBERS: dict = {}     # email -> member
PURCHASES: list = []   # rows as the purchases table holds them
def reset(**rows_by_email):
    MEMBERS.clear(); PURCHASES.clear()
    for i, (email, rows) in enumerate(rows_by_email.items()):
        email = email.replace("_at_", "@") + ".co"
        MEMBERS[email] = {"id": f"m{i}", "email": email}
        for r in rows:
            PURCHASES.append(dict(r, member_id=f"m{i}"))
main._member_by_email = lambda email: MEMBERS.get(email)
main._member_purchases = lambda mid: [p for p in PURCHASES if p["member_id"] == mid]
main._order_purchases = lambda sid: [p for p in PURCHASES if p["stripe_session_id"] == sid]

FREE = {"course_id": "MER-DEA-001", "amount_gbp": 0, "stripe_session_id": "cs_live_first0000001"}
PAID = {"course_id": "MER-ALL-022", "amount_gbp": 19.99, "stripe_session_id": "cs_live_paid00000001"}

# ── 1. Who has had a free course ──
reset(a_at_x=[FREE])
check("an address with a £0 course has had its free course", main.had_free_course("a@x.co"))
check("the address is read in lower case", main.had_free_course("  A@X.CO "))
check("the same order does not count against itself", not main.had_free_course("a@x.co", except_session=FREE["stripe_session_id"]))
check("an unknown address has not", not main.had_free_course("new@x.co") and not main.had_free_course(""))
reset(a_at_x=[PAID])
check("a paid course is not a free course", not main.had_free_course("a@x.co"))
reset(a_at_x=[dict(FREE, stripe_session_id="cs_test_admin123")])
check("an admin test row is not a free course", not main.had_free_course("a@x.co"))
reset(a_at_x=[dict(FREE, course_id="SUBSCRIPTION")])
check("a £0 subscription row is not a free course", not main.had_free_course("a@x.co"))
reset(a_at_x=[dict(FREE, series_id="FW-HEATING")])
check("a series part is not a free course", not main.had_free_course("a@x.co"))
real_by_email = main._member_by_email
main._member_by_email = lambda e: (_ for _ in ()).throw(RuntimeError("database down"))
check("database down: a first-timer is not turned away", not main.had_free_course("a@x.co"))
main._member_by_email = real_by_email


# ── 2. The webhook backstop ──
def run_checkout(sid, amount, ref="MER-DEA-001", price="price_single", email="a@x.co", subscription=None):
    made = []
    main.get_or_create_member = lambda e, n, c, plan: MEMBERS.setdefault(e, {"id": f"m{len(MEMBERS)}", "email": e})
    def log(member_id, cid, session_id, amt, series_id=""):
        made.append(("purchase", cid))
        PURCHASES.append({"member_id": member_id, "course_id": cid, "stripe_session_id": session_id,
                          "amount_gbp": amt / 100, "emailed_at": None})
    main.log_purchase = log
    main.ensure_completion_token = lambda m, c: "tok"
    main._mark_emailed = lambda s, c: [p.update(emailed_at="now") for p in PURCHASES if p["stripe_session_id"] == s and p["course_id"] == c]
    async def send(**kw): made.append(("email", kw["course_id"]))
    main.send_course_email = send
    main.sync_subscription = lambda sub: None
    main.stripe.Subscription.retrieve = lambda s: {}
    item = types.SimpleNamespace(price=types.SimpleNamespace(id=price))
    main.stripe.checkout.Session.list_line_items = lambda s, limit=5: types.SimpleNamespace(data=[item])
    session = types.SimpleNamespace(id=sid, customer="cus_1", amount_total=amount, client_reference_id=ref,
                                    subscription=subscription, metadata={},
                                    customer_details={"email": email, "name": "Buyer"})
    asyncio.run(main.handle_checkout(session))
    return made

reset()
made = run_checkout("cs_live_first0000001", 0)
check("webhook: a first free course is recorded and sent", made == [("purchase", "MER-DEA-001"), ("email", "MER-DEA-001")])
made = run_checkout("cs_live_second000001", 0, ref="MER-ALL-022")
check("webhook: a second free course for the same address is not recorded or sent", made == [])
check("webhook: nothing was written for the refused order", not main._order_purchases("cs_live_second000001"))
made = run_checkout("cs_live_second000001", 0, ref="MER-ALL-022", email="A@X.CO")
check("webhook: the address in capitals is the same address", made == [])
made = run_checkout("cs_live_first0000001", 0)
check("webhook: a repeat delivery of the first order is still ignored as before", made == [])
made = run_checkout("cs_live_paid00000002", 1999, ref="MER-ALL-022")
check("webhook: a paid course after the free one is recorded and sent", made == [("purchase", "MER-ALL-022"), ("email", "MER-ALL-022")])
made = run_checkout("cs_live_other0000001", 0, email="b@x.co")
check("webhook: a free course for another address goes through", made == [("purchase", "MER-DEA-001"), ("email", "MER-DEA-001")])
made = run_checkout("cs_live_subs00000001", 0, ref="", price="price_sub", subscription="sub_1")
check("webhook: a £0 subscription checkout is not touched by the check",
      ("purchase", "SUBSCRIPTION") in made and ("email", "SUBSCRIPTION") in made)
reset(a_at_x=[dict(FREE, stripe_session_id="cs_test_admin123")])
made = run_checkout("cs_live_first0000009", 0)
check("webhook: an admin test send does not use up the free course", made == [("purchase", "MER-DEA-001"), ("email", "MER-DEA-001")])


# ── 3. /free/<course>: email first ──
created, lookups = [], []
def fake_create(**params):
    created.append(params)
    return main.stripe.StripeObject.construct_from({"id": "cs_live_new", "url": "https://checkout.stripe.com/c/pay/cs_live_new"}, "sk_test_x")
def fake_promo_list(**kw):
    lookups.append(kw)
    return main.stripe.StripeObject.construct_from({"data": [{"id": "promo_m10"}] if kw.get("code") == "MERIDIAN10" else []}, "sk_test_x")
main.stripe.checkout.Session.create = staticmethod(fake_create)
main.stripe.PromotionCode.list = staticmethod(fake_promo_list)
c = TestClient(main.app, follow_redirects=False)

r = c.get("/free/mer-dea-001")
check("/free: a form asking for the email, naming the course", r.status_code == 200 and 'name="email"' in r.text
      and main._esc(main.COURSES["MER-DEA-001"]["title"]) in r.text and 'action="/free/MER-DEA-001"' in r.text)
check("/free: a series or an unknown id is not free", c.get("/free/FW-HEATING").headers["location"] == main.SITE_URL + "/courses.html"
      and c.get("/free/MER-XXX-999").headers["location"] == main.SITE_URL + "/courses.html")
r = c.post("/free/MER-DEA-001", data={"email": "not an email"})
check("/free: a bad address is asked for again", r.status_code == 400 and "does not look like an email address" in r.text)

reset(a_at_x=[FREE])
r = c.post("/free/MER-ALL-022", data={"email": "A@x.co"})
check("/free: a second claim gets the plain page, no checkout", r.status_code == 200 and created == []
      and "You have already had your free course" in r.text and main.SITE_URL + "/#offer" in r.text
      and "See annual membership" in r.text and main.SITE_URL + "/courses.html?open=MER-ALL-022" in r.text
      and "Nothing was charged" not in r.text)

reset()
r = c.post("/free/MER-DEA-001", data={"email": "new@x.co"})
loc = r.headers.get("location", "")
check("/free, sessions off: the Payment Link with the code and address filled in", r.status_code == 303
      and loc.startswith(main.PAYMENT_LINK_SINGLE + "?client_reference_id=MER-DEA-001&prefilled_promo_code=MERIDIAN10")
      and "prefilled_email=new%40x.co" in loc and created == [])

os.environ["CHECKOUT_SESSIONS"] = "on"
r = c.post("/free/MER-DEA-001", data={"email": "new@x.co"})
p = created[-1] if created else {}
check("/free, sessions on: straight to the checkout", r.status_code == 303 and r.headers["location"] == "https://checkout.stripe.com/c/pay/cs_live_new")
check("/free, sessions on: the address is fixed", p.get("customer_email") == "new@x.co")
check("/free, sessions on: the discount is applied by the app and no code can be typed",
      p.get("discounts") == [{"promotion_code": "promo_m10"}] and "allow_promotion_codes" not in p
      and lookups[-1] == {"code": "MERIDIAN10", "active": True, "limit": 1})
check("/free, sessions on: the same price and reference as a paid course", p.get("line_items") == [{"price": "price_single", "quantity": 1}]
      and p.get("client_reference_id") == "MER-DEA-001" and p.get("metadata") == {"course_id": "MER-DEA-001", "free_course": "yes"})
n = len(created)
main.stripe.PromotionCode.list = staticmethod(lambda **kw: main.stripe.StripeObject.construct_from({"data": []}, "sk_test_x"))
r = c.post("/free/MER-DEA-001", data={"email": "new@x.co"})
check("/free: if the code is not live in Stripe, the Payment Link (and the health check flags the code)",
      len(created) == n and r.headers["location"].startswith(main.PAYMENT_LINK_SINGLE))
main.stripe.PromotionCode.list = staticmethod(fake_promo_list)
check("/buy with the free code goes to /free, not to a discounted checkout",
      c.get("/buy/MER-DEA-001?code=MERIDIAN10").headers["location"] == main.APP_URL + "/free/MER-DEA-001" and len(created) == n)
os.environ["CHECKOUT_SESSIONS"] = "off"


# ── 4. /thanks for a refused order ──
def thanks_for(sid, amount, mode="payment", ref="MER-ALL-022", email="a@x.co"):
    s = main.stripe.StripeObject.construct_from({"id": sid, "status": "complete", "mode": mode, "amount_total": amount,
                                                 "client_reference_id": ref, "created": 0,
                                                 "customer_details": {"email": email}}, "sk_test_x")
    main.stripe.checkout.Session.retrieve = lambda i: s
    return c.get(f"/thanks?session_id={sid}")

reset(a_at_x=[FREE])
r = thanks_for("cs_live_second000001", 0)
check("/thanks: a refused second free course says so at once", r.status_code == 200
      and "You have already had your free course" in r.text and "Nothing was charged for this order" in r.text
      and "Finishing your order" not in r.text)
r = thanks_for("cs_live_brandnew0001", 0, email="new@x.co")
check("/thanks: a first free course still waits for the order as before", "Finishing your order" in r.text)
r = thanks_for("cs_live_subs00000001", 0, mode="subscription", ref="")
check("/thanks: a £0 subscription is never shown the free-course page", "already had your free course" not in r.text)
r = thanks_for("cs_live_paid00000003", 1999)
check("/thanks: a paid order is never shown the free-course page", "already had your free course" not in r.text)

# ── 5. The words ──
pages = [main._free_form("MER-DEA-001").body.decode(), main._free_course_used_page("a@x.co", "MER-DEA-001", ordered=True).body.decode()]
check("no em dash or exclamation mark in the new pages' text",
      all("—" not in p.split("</style>")[1].split('class="small foot"')[0] and "!" not in p.split("</style>")[1] for p in pages))

print(f"\n{'ALL CHECKS PASSED' if not fails else f'{fails} FAILED'}")
if fails:
    raise SystemExit(1)
