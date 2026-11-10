"""Free-course code watch and the checkout guard. Run: python3 tests/test_free_code.py (or pytest)

What must hold: /health says whether Stripe would accept MERIDIAN10 today and why not
(inactive, expired, redemption limit, coupon no longer valid, no such code), says
'unknown' when Stripe cannot be asked, asks Stripe at most every ten minutes; and a
checkout for a price the app does not know creates no member and records nothing."""
import asyncio, os, sys, time, types
os.environ.update(STRIPE_SECRET_KEY="sk_test_x", STRIPE_WEBHOOK_SECRET="whsec_x", SUPABASE_URL="https://example.supabase.co",
                  SUPABASE_SERVICE_ROLE_KEY="eyJhbGciOiJIUzI1NiJ9.eyJyb2xlIjoic2VydmljZV9yb2xlIn0.x",
                  ADMIN_PASSWORD="test-admin", DASHBOARD_SECRET="dash-secret", UNSUBSCRIBE_SECRET="unsub-secret",
                  RESEND_API_KEY="re_x", OUTREACH_SCHEDULER="off", NEWS_SCHEDULER="off")
os.environ.pop("FREE_FOLLOWUP", None)
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
import main

NOW = 1_800_000_000


def _pc(**k):
    base = {"active": True, "expires_at": None, "max_redemptions": None, "times_redeemed": 3,
            "coupon": {"valid": True}}
    base.update(k)
    return base


def _with_codes(codes, fn, raises=False):
    real = main.stripe.PromotionCode.list
    def fake(**kw):
        if raises:
            raise RuntimeError("stripe down")
        return types.SimpleNamespace(data=codes)
    main.stripe.PromotionCode.list = fake
    try:
        return fn()
    finally:
        main.stripe.PromotionCode.list = real


def test_states():
    st = lambda codes, **k: _with_codes(codes, lambda: main._promo_code_state("MERIDIAN10", NOW), **k)
    assert st([_pc()]) == "ok"
    assert st([_pc(active=False)]) == "invalid: inactive"
    assert st([_pc(expires_at=NOW - 1)]) == "invalid: expired"
    assert st([_pc(expires_at=NOW + 100)]) == "ok"
    assert st([_pc(max_redemptions=83, times_redeemed=83)]) == "invalid: redemption limit reached"
    assert st([_pc(max_redemptions=100, times_redeemed=83)]) == "ok"
    assert st([_pc(coupon={"valid": False})]) == "invalid: coupon no longer valid"
    assert st([_pc(coupon=None, promotion={"coupon": {"valid": False}})]) == "invalid: coupon no longer valid"
    assert st([_pc(coupon="coupon_id_only")]) == "ok"
    assert st([]) == "invalid: no such code"
    # an old archived code next to a new live one with the same name: live wins
    assert st([_pc(active=False), _pc()]) == "ok"
    assert st([_pc()], raises=True) == "unknown"


def test_cached_and_in_health():
    calls = []
    def fake(**kw):
        calls.append(kw)
        return types.SimpleNamespace(data=[_pc(active=False)])
    real_list, real_refresh = main.stripe.PromotionCode.list, main.refresh_catalogue
    main.stripe.PromotionCode.list = fake
    main.refresh_catalogue = lambda force=False: None
    main._free_code_cache.update(at=0.0, state="unknown")
    try:
        assert main.health()["free_code"] == "invalid: inactive"
        assert main.health()["free_code"] == "invalid: inactive"
        assert len(calls) == 1 and calls[0]["code"] == "MERIDIAN10"
        main._free_code_cache["at"] = time.time() - main.FREE_CODE_CHECK_SECONDS - 1
        main.health()
        assert len(calls) == 2
    finally:
        main.stripe.PromotionCode.list, main.refresh_catalogue = real_list, real_refresh
        main._free_code_cache.update(at=0.0, state="unknown")


def test_unknown_price_makes_no_member():
    made = []
    saved = {n: getattr(main, n) for n in ("_order_purchases", "refresh_catalogue", "get_or_create_member", "log_purchase")}
    real_items = main.stripe.checkout.Session.list_line_items
    main._order_purchases = lambda sid: []
    main.refresh_catalogue = lambda force=False: None
    main.get_or_create_member = lambda *a, **k: made.append(a) or {"id": "m1"}
    main.log_purchase = lambda *a, **k: made.append(a)
    item = types.SimpleNamespace(price=types.SimpleNamespace(id="price_nobody_knows"))
    main.stripe.checkout.Session.list_line_items = lambda sid, limit=5: types.SimpleNamespace(data=[item])
    session = types.SimpleNamespace(id="cs_test_1", customer="", amount_total=0, client_reference_id="",
                                    customer_details={"email": "buyer@example.com", "name": "B"})
    try:
        asyncio.run(main.handle_checkout(session))
    finally:
        for n, v in saved.items():
            setattr(main, n, v)
        main.stripe.checkout.Session.list_line_items = real_items
    assert made == []


if __name__ == "__main__":
    test_states(); test_cached_and_in_health(); test_unknown_price_makes_no_member()
    print("ALL CHECKS PASSED")
