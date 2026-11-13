"""Buy buttons say what they buy, and Stripe's page names the course (board row mer-pricing-links).
/buy/<course or series id> on the app: with CHECKOUT_SESSIONS off (the default) it sends the buyer
to the Payment Link exactly as the site does today; on, it opens a Checkout Session on the same
price with the course or series named above the Pay button and the same client_reference_id, so
the webhook records the sale as before. The site's pricing cards and free-course links go to the
library, and the course window's buttons name the part, course or series.
Run: python3 tests/test_buy_links.py (or python -m pytest -q from webhook/)."""
import os, re, shutil, subprocess, sys, types
from pathlib import Path
os.environ.update(STRIPE_SECRET_KEY="sk_test_x", STRIPE_WEBHOOK_SECRET="whsec_x", SUPABASE_URL="https://example.supabase.co",
                  SUPABASE_SERVICE_ROLE_KEY="eyJhbGciOiJIUzI1NiJ9.eyJyb2xlIjoic2VydmljZV9yb2xlIn0.x",
                  ADMIN_PASSWORD="test-admin", STRIPE_PRICE_SINGLE="price_single",
                  STRIPE_PRICE_SUBSCRIPTION="price_sub", STRIPE_PRICE_SERIES="price_series")
os.environ.pop("CHECKOUT_SESSIONS", None)
HERE = Path(__file__).resolve().parent
ROOT = HERE.parent.parent
sys.path.insert(0, str(HERE.parent))
import main
from fastapi.testclient import TestClient

main.supabase = types.SimpleNamespace(table=lambda t: (_ for _ in ()).throw(RuntimeError("no database in this test")))
main._refresh_under_review = lambda: None
main.UNDER_REVIEW.clear()

fails = 0
def check(name, cond):
    global fails
    print(("PASS " if cond else "FAIL ") + name)
    fails += 0 if cond else 1

created, promo_lookups = [], []
def fake_create(**params):
    created.append(params)
    return main.stripe.StripeObject.construct_from({"id": "cs_test_1", "url": "https://checkout.stripe.com/c/pay/cs_test_1"}, "sk_test_x")
def fake_promo_list(**kw):
    promo_lookups.append(kw)
    data = [{"id": "promo_m10"}] if kw.get("code") == "MERIDIAN10" else []
    return main.stripe.StripeObject.construct_from({"data": data}, "sk_test_x")
main.stripe.checkout.Session.create = staticmethod(fake_create)
main.stripe.PromotionCode.list = staticmethod(fake_promo_list)

c = TestClient(main.app, follow_redirects=False)
SINGLE, SERIES = main.PAYMENT_LINK_SINGLE, main.PAYMENT_LINK_SERIES

# ── 1. Off (the default): the Payment Link, as today; Stripe is not called ──
r = c.get("/buy/MER-ALL-022")
check("off: a course goes to the £19.99 Payment Link with its id", r.status_code == 302
      and r.headers["location"] == SINGLE + "?client_reference_id=MER-ALL-022")
r = c.get("/buy/MER-DEA-001?code=meridian10")
check("off: a code goes through as prefilled_promo_code", r.headers["location"] == SINGLE + "?client_reference_id=MER-DEA-001&prefilled_promo_code=MERIDIAN10")
r = c.get("/buy/FW-HEATING?code=MERIDIAN10")
check("off: a series goes to the £39.99 Payment Link, with no code", r.headers["location"] == SERIES + "?client_reference_id=FW-HEATING")
r = c.get("/buy/fw-heating")
check("an id in lower case is read as the id", r.headers["location"] == SERIES + "?client_reference_id=FW-HEATING")
check("off: no Checkout Session is made", created == [] and promo_lookups == [])
for bad in ("/buy/SUBSCRIPTION", "/buy/MER-XXX-999", "/buy/FW-NOPE"):
    r = c.get(bad)
    check(f"{bad}: not sold here, sent to the courses page", r.status_code == 302 and r.headers["location"] == main.SITE_URL + "/courses.html")
main.UNDER_REVIEW.add("MER-ALL-023")
check("a course under review is not sold, nor its series", c.get("/buy/MER-ALL-023").headers["location"].endswith("/courses.html")
      and c.get("/buy/FW-HEATING").headers["location"].endswith("/courses.html"))
main.UNDER_REVIEW.clear()

# ── 2. On: a Checkout Session on the existing price that names what is bought ──
os.environ["CHECKOUT_SESSIONS"] = "on"
r = c.get("/buy/MER-ALL-022")
p = created[-1]
title = main.COURSES["MER-ALL-022"]["title"]
check("on: the buyer goes to the Checkout Session", r.status_code == 303 and r.headers["location"] == "https://checkout.stripe.com/c/pay/cs_test_1")
check("on: the existing £19.99 price, one of it, payment mode", p["mode"] == "payment" and p["line_items"] == [{"price": "price_single", "quantity": 1}])
check("on: client_reference_id and metadata name the course", p["client_reference_id"] == "MER-ALL-022" and p["metadata"] == {"course_id": "MER-ALL-022"})
check("on: Stripe's page names the course above the Pay button",
      p["custom_text"]["submit"]["message"] == f"You are buying one course: {title} (MER-ALL-022).")
check("on: after paying, the app's thanks page, as the Payment Links do", p["success_url"] == main.APP_URL + "/thanks?session_id={CHECKOUT_SESSION_ID}")
check("on: going back opens the same course on the site", p["cancel_url"] == main.SITE_URL + "/courses.html?open=MER-ALL-022")
check("on: name collected, customer made, codes can be typed", p["name_collection"] == {"individual": {"enabled": True}}
      and p["customer_creation"] == "always" and p.get("allow_promotion_codes") is True and "discounts" not in p)
check("on: no price, product or link is made inline", "price_data" not in str(p) and "product_data" not in str(p))

c.get("/buy/MER-DEA-001?code=MERIDIAN10"); p = created[-1]
check("on: a code from the site is applied (looked up read-only)", p.get("discounts") == [{"promotion_code": "promo_m10"}]
      and "allow_promotion_codes" not in p and promo_lookups[-1] == {"code": "MERIDIAN10", "active": True, "limit": 1})
c.get("/buy/MER-DEA-001?code=NOTACODE"); p = created[-1]
check("on: an unknown code is dropped; the buyer can still type one", "discounts" not in p and p.get("allow_promotion_codes") is True)

c.get("/buy/FW-HEATING"); p = created[-1]
msg = p["custom_text"]["submit"]["message"]
check("on: a series uses the £39.99 price and carries the series id", p["line_items"] == [{"price": "price_series", "quantity": 1}]
      and p["client_reference_id"] == "FW-HEATING" and p["metadata"] == {"series": "FW-HEATING"})
check("on: Stripe's page names the series and its three parts",
      msg.startswith("You are buying Field Work: Heating, all three parts. Part 1: ") and "Part 2: " in msg and "Part 3: " in msg
      and "Series, Part" not in msg and len(msg) <= 1200)
check("on: going back from a series lands on its card", p["cancel_url"] == main.SITE_URL + "/courses.html#fw-heating")
check("every message fits Stripe's 1,200 characters and has no em dash or exclamation mark",
      all(len(m) <= 1200 and "—" not in m and "!" not in m for m in
          [main.buy_message("course", k) for k in main.COURSES if k != "SUBSCRIPTION"] +
          [main.buy_message("series", s) for s in main.SERIES]))

# Stripe refuses, or the price is not set: the buyer still gets to pay, on the Payment Link
def refuse(**params): raise main.stripe.InvalidRequestError("No such price", "line_items")
main.stripe.checkout.Session.create = staticmethod(refuse)
r = c.get("/buy/MER-ALL-022")
check("on, Stripe refuses: the Payment Link instead", r.status_code == 302 and r.headers["location"] == SINGLE + "?client_reference_id=MER-ALL-022")
main.stripe.checkout.Session.create = staticmethod(fake_create)
n = len(created); os.environ["STRIPE_PRICE_SERIES"] = ""
r = c.get("/buy/FW-HEATING")
check("on, no series price set: the Payment Link, no session", r.headers["location"] == SERIES + "?client_reference_id=FW-HEATING" and len(created) == n)
os.environ["STRIPE_PRICE_SERIES"] = "price_series"
os.environ["CHECKOUT_SESSIONS"] = "off"

# ── 3. The webhook reads a /buy session exactly as a Payment Link session ──
def session(params):
    return main.stripe.StripeObject.construct_from({"id": "cs_x", "client_reference_id": params["client_reference_id"],
                                                    "metadata": params["metadata"]}, "sk_test_x")
item = lambda price: types.SimpleNamespace(price=types.SimpleNamespace(id=price))
pc = main.checkout_session_params("course", "MER-ALL-022")
ps = main.checkout_session_params("series", "FW-HEATING")
check("webhook: a /buy course session records that course", main._keys_for_checkout(session(pc), [item("price_single")], "MER-ALL-022")
      == (["MER-ALL-022"], "single", ""))
check("webhook: a /buy series session records its three parts", main._keys_for_checkout(session(ps), [item("price_series")], "FW-HEATING")
      == (main.SERIES["FW-HEATING"]["courses"], "single", "FW-HEATING"))
check("webhook: the series is found from metadata if the reference were missing",
      main._keys_for_checkout(session(dict(ps, client_reference_id="")), [item("price_series")], "")[0] == main.SERIES["FW-HEATING"]["courses"])
check("webhook: a Payment Link session with no reference still records the default course (unchanged)",
      main._keys_for_checkout(session({"client_reference_id": "", "metadata": {}}), [item("price_single")], "")[0] == ["MER-DEA-001"])

# ── 4. The site ──
idx = (ROOT / "landing-page" / "index.html").read_text(encoding="utf-8")
crs = (ROOT / "landing-page" / "courses.html").read_text(encoding="utf-8")
chk = (ROOT / "landing-page" / "checkout.js").read_text(encoding="utf-8")
check("pricing card: the £19.99 card goes to the single courses, not to Stripe",
      '<a href="courses.html#single-courses" class="btn-s">Choose a Course</a>' in idx and 'id="single-courses"' in crs
      and "Buy a Course" not in idx)
check("pricing card: See the Series goes to the series block", '<a href="courses.html#seriesGrid" class="btn-s">See the Series</a>' in idx
      and 'id="seriesGrid"' in crs)
check("the free-course links open the free course", idx.count('href="courses.html?open=MER-DEA-001">Claim your first course free</a>') == 1
      and '<a href="courses.html?open=MER-DEA-001" class="btn-s">First course free with MERIDIAN10</a>' in idx
      and 'Not ready yet? <a href="courses.html?open=MER-DEA-001">Claim your first course free with code MERIDIAN10 at checkout &#8594;</a>' in idx
      and '>Claim your first course free</a> with code <strong style="color:var(--accent)">MERIDIAN10</strong> at checkout.' in idx)
bare = [h for h in re.findall(r'href="(https://buy\.stripe\.com/[^"]*)"', idx + crs) if "client_reference_id" not in h]
check("every Stripe link left without a reference is the annual subscription", bare and all("fZufZgbse3BpcXE7TY73G01" in h for h in bare))
check("the annual buttons stay direct to Stripe", idx.count('href="https://buy.stripe.com/fZufZgbse3BpcXE7TY73G01" class="btn-p">Get Full Access') == 3)
check("course window: the £19.99 button names what it buys",
      "Buy Part ${c.part} only, £19.99" in crs and "Buy this course, £19.99" in crs and "Enrol" not in crs)
check("course window: the £39.99 button names the series", "Buy the ${escHtml(s.title.replace('Field Work: ', ''))} series, ${SERIES_PRICE}" in crs
      and "All three —" not in crs)
check("both pages load checkout.js, before the course script on courses.html", '<script src="/checkout.js"></script>' in idx
      and crs.index('<script src="/checkout.js"></script>') < crs.index("const STRIPE_SINGLE"))
check("checkout.js ships switched off", "var VIA_APP = false;" in chk)

node = shutil.which("node")
if node:
    out = subprocess.run([node, str(HERE / "checkout_js_check.js")], capture_output=True, text=True)
    check("checkout.js and consent.js in a fake page: " + (out.stdout.strip().splitlines() or ["(no output)"])[-1] + out.stderr.strip(), out.returncode == 0)
else:
    print("SKIP checkout.js browser check (node not installed)")

print(f"\n{'ALL CHECKS PASSED' if not fails else f'{fails} FAILED'}")
if fails:
    raise SystemExit(1)
