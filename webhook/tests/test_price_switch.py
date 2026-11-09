"""The £99 switch on 1 January 2027 and the founder rate (board row mer-price-99).
  - a checkout on either annual price (the live one, or the £79 founder price kept in
    STRIPE_PRICE_SUBSCRIPTION_FOUNDER) is a subscription
  - a renewal at £79 keeps access whatever STRIPE_PRICE_SUBSCRIPTION says: sync_subscription
    follows the subscription and never looks at, or changes, its price
  - My CPD offers the year at the price checkout charges, read from Stripe, through the link in
    STRIPE_LINK_SUBSCRIPTION; no banner if the price cannot be read
Run from anywhere: python3 tests/test_price_switch.py (or python -m pytest -q from webhook/)."""
import os, sys, types
from datetime import datetime
from pathlib import Path
os.environ.update(STRIPE_SECRET_KEY="sk_test_x", STRIPE_WEBHOOK_SECRET="whsec_x", SUPABASE_URL="https://example.supabase.co",
                  SUPABASE_SERVICE_ROLE_KEY="eyJhbGciOiJIUzI1NiJ9.eyJyb2xlIjoic2VydmljZV9yb2xlIn0.x", SESSION_SECRET="s",
                  ADMIN_PASSWORD="test-admin", STRIPE_PRICE_SINGLE="price_single",
                  STRIPE_PRICE_SUBSCRIPTION="price_99", STRIPE_PRICE_SUBSCRIPTION_FOUNDER="price_79",
                  STRIPE_PRICE_SERIES="price_series")
os.environ.pop("STRIPE_LINK_SUBSCRIPTION", None)
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
import main, followup

failed = 0
def check(label, ok):
    global failed
    print(("PASS " if ok else "FAIL ") + label)
    failed += 0 if ok else 1

# 1. Both annual prices are recognised at checkout; nothing else changes
assert main.PRICE_TO_COURSE == {"price_single": "MER-DEA-001", "price_99": "SUBSCRIPTION",
                                "price_79": "SUBSCRIPTION", "price_series": "SERIES"}, main.PRICE_TO_COURSE
item = lambda pid: types.SimpleNamespace(price=types.SimpleNamespace(id=pid))
for pid in ("price_99", "price_79"):
    keys, plan, series = main._keys_for_checkout({}, [item(pid)], "")
    check(f"checkout on {pid} is the annual subscription", keys == ["SUBSCRIPTION"] and plan == "subscription" and series == "")
keys, plan, _ = main._keys_for_checkout({}, [item("price_unknown")], "")
check("an unknown price is still not a subscription", keys == [] and plan == "single")

# 2. A founder renewal: the subscription is on price_79 while checkout charges £99; access follows the period end
db = {"members": [{"id": "m1", "email": "founder@example.com", "plan": "subscription", "stripe_customer_id": "cus_f",
                   "subscription_expires_at": "2027-11-20T00:00:00+00:00"}]}
class Q:
    def __init__(s, t): s.t, s.f, s.up = t, [], None
    def select(s, *a): return s
    def eq(s, c, v): s.f.append((c, v)); return s
    def update(s, row): s.up = row; return s
    def execute(s):
        hit = [r for r in db[s.t] if all(r.get(c) == v for c, v in s.f)]
        if s.up is not None:
            [r.update(s.up) for r in hit]
        return types.SimpleNamespace(data=hit)
main.supabase = types.SimpleNamespace(table=lambda t: Q(t))
end_2028 = int(datetime(2028, 11, 13).timestamp())
sub = {"id": "sub_f", "customer": "cus_f", "status": "active", "current_period_end": end_2028,
       "items": {"data": [{"price": {"id": "price_79", "unit_amount": 7900}}]}}
upd = main.sync_subscription(sub)
check("a £79 renewal after the switch extends access (period end plus grace)",
      upd["plan"] == "subscription" and db["members"][0]["subscription_expires_at"].startswith("2028-11-20"))
src = Path(main.__file__).read_text()
check("nothing in the app changes a subscription's price",
      "Subscription.modify" not in src and "SubscriptionItem" not in src and "Subscription.update" not in src)

# 3. My CPD banner follows the price checkout charges
UK = followup.UK
def banner(pence, when):
    followup._price_cache.update(at=None, gbp=None)
    followup._fetch_annual_pence = lambda: pence
    return main.upsell_banner(when)
nov, jan = datetime(2026, 11, 20, 9, tzinfo=UK), datetime(2027, 1, 2, 9, tzinfo=UK)
b = banner(7900, nov)
check("£79 in November: £79, the January line, the default link",
      "£79 a year." in b and "£99 from 1 January 2027" in b and "Upgrade to Annual, £79 a year →" in b
      and main.DEFAULT_SUBSCRIPTION_LINK in b)
b = banner(7900, jan)
check("£79 still live in January (switch late): no stale 'until 31 December' line",
      "£79 a year." in b and "31 December" not in b and "£99" not in b)
os.environ["STRIPE_LINK_SUBSCRIPTION"] = "https://buy.stripe.com/test_new99"
b = banner(9900, jan)
check("£99 after the switch: £99, no founder line, the new link",
      "£99 a year." in b and "£79" not in b and "Upgrade to Annual, £99 a year →" in b
      and "https://buy.stripe.com/test_new99" in b and main.DEFAULT_SUBSCRIPTION_LINK not in b)
check("price unreadable: no banner", banner(None, jan) == "")
check("a price no text is written for: no banner", banner(8900, jan) == "")

if failed:
    print(f"\n{failed} FAILED"); sys.exit(1)
print("\nall passed")
