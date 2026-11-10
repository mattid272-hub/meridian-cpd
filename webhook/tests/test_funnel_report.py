"""The daily funnel report (.github/scripts/funnel.py) and the two app changes it needs.
Run: python3 tests/test_funnel_report.py (or pytest)

What must hold: yesterday and the 7-day column count UK days (also across the clock
change); a series is one order, test orders and test members never count; each red line
appears exactly when its condition holds (app down, free code refused, series price
missing, no Stripe key, Stripe key not answering, a paid checkout with no purchase row,
a checkout started and not finished, no free orders for 2 days) and none on a good day;
the email fits one screen and carries no em dash or exclamation mark; /health says
whether the series price is set; a sign-in is counted and a failed count never blocks it."""
import os, sys
from datetime import datetime, timezone, timedelta

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "..", ".github", "scripts"))
sys.path.insert(0, os.path.join(HERE, ".."))
import funnel

NOW = datetime(2026, 11, 10, 7, 20, tzinfo=timezone.utc)          # Tue 10 Nov 2026, GMT
YDAY = datetime(2026, 11, 9, 12, 0, tzinfo=timezone.utc)
DAYS_AGO = lambda n: (YDAY - timedelta(days=n))
iso = lambda d: d.isoformat()


def good_day():
    """A day with nothing wrong: one free order yesterday, one the day before, a series
    and an annual yesterday, and every Stripe checkout recorded."""
    purchases = [
        {"member_id": "m1", "course_id": "MER-ALL-001", "amount_gbp": 0, "stripe_session_id": "cs_live_free1", "purchased_at": iso(YDAY)},
        {"member_id": "m2", "course_id": "MER-ALL-001", "amount_gbp": 0, "stripe_session_id": "cs_live_free2", "purchased_at": iso(DAYS_AGO(1))},
        # a series: three rows, one session, £39.99 split
        {"member_id": "m3", "course_id": "MER-ALL-021", "amount_gbp": 13.33, "stripe_session_id": "cs_live_ser", "purchased_at": iso(YDAY), "series_id": "FW-HEATING"},
        {"member_id": "m3", "course_id": "MER-ALL-022", "amount_gbp": 13.33, "stripe_session_id": "cs_live_ser", "purchased_at": iso(YDAY), "series_id": "FW-HEATING"},
        {"member_id": "m3", "course_id": "MER-ALL-023", "amount_gbp": 13.33, "stripe_session_id": "cs_live_ser", "purchased_at": iso(YDAY), "series_id": "FW-HEATING"},
        {"member_id": "m4", "course_id": "SUBSCRIPTION", "amount_gbp": 79, "stripe_session_id": "cs_live_sub", "purchased_at": iso(YDAY)},
        {"member_id": "m5", "course_id": "MER-DEA-001", "amount_gbp": 19.99, "stripe_session_id": "cs_live_one", "purchased_at": iso(DAYS_AGO(3))},
        # test orders never count
        {"member_id": "t1", "course_id": "MER-DEA-001", "amount_gbp": 19.99, "stripe_session_id": "cs_test_abc", "purchased_at": iso(YDAY)},
        {"member_id": "m6", "course_id": "MER-ALL-001", "amount_gbp": 0, "stripe_session_id": "cs_live_old", "purchased_at": iso(DAYS_AGO(30))},
    ]
    sessions = [{"id": s, "created": int((t + timedelta(minutes=-1)).timestamp()), "status": "complete", "amount_total": a}
                for s, t, a in [("cs_live_free1", YDAY, 0), ("cs_live_free2", DAYS_AGO(1), 0),
                                ("cs_live_ser", YDAY, 3999), ("cs_live_sub", YDAY, 7900),
                                ("cs_live_one", DAYS_AGO(3), 1999)]]
    members = [
        {"id": "m1", "plan": "single", "stripe_customer_id": "cus_1", "joined_at": iso(YDAY), "marketing_consent": True},
        {"id": "m2", "plan": "single", "stripe_customer_id": "cus_2", "joined_at": iso(DAYS_AGO(1)), "marketing_consent": False},
        {"id": "m3", "plan": "single", "stripe_customer_id": "cus_3", "joined_at": iso(YDAY), "marketing_consent": None},
        {"id": "m4", "plan": "subscription", "stripe_customer_id": "cus_4", "joined_at": iso(YDAY), "marketing_consent": True},
        {"id": "m5", "plan": "single", "stripe_customer_id": "cus_5", "joined_at": iso(DAYS_AGO(3))},
        {"id": "m6", "plan": "single", "stripe_customer_id": "cus_6", "joined_at": iso(DAYS_AGO(30))},
        {"id": "t1", "plan": "single", "stripe_customer_id": "cus_test", "joined_at": iso(YDAY)},
    ]
    return {
        "health": {"status": "ok", "available": 51, "free_code": "ok", "series_price": "set"},
        "stripe_sessions": sessions,
        "members": members,
        "purchases": purchases,
        "last_free_order": "2026-11-09",
        "opened": [{"downloaded_at": iso(YDAY)}, {"downloaded_at": iso(DAYS_AGO(2))}],
        "completed": [{"completed_at": iso(YDAY)}],
        "certificates": [{"issued_at": "2026-11-09T12:00:00.12345+00:00"}],
        "signins": [{"signed_in_at": iso(YDAY)}, {"signed_in_at": iso(YDAY)}],
        "followups": [{"sent_at": iso(YDAY), "status": "sent"}, {"sent_at": iso(YDAY), "status": "failed"}],
        "outreach_sends": [],
        "suppressed": [{"suppressed_at": iso(YDAY), "reason": "unsubscribed"},
                       {"suppressed_at": iso(YDAY), "reason": "bounced"}],
    }


def test_windows_are_uk_days():
    w = funnel.windows(NOW)
    assert w["yday"] == (datetime(2026, 11, 9, tzinfo=timezone.utc), datetime(2026, 11, 10, tzinfo=timezone.utc))
    assert w["week"][0] == datetime(2026, 11, 3, tzinfo=timezone.utc)
    assert w["yday_label"] == "Mon 09 Nov"
    # Clocks went forward on Sun 29 Mar 2026: that UK day is 23 hours long.
    w = funnel.windows(datetime(2026, 3, 30, 7, 20, tzinfo=timezone.utc))
    assert w["yday"] == (datetime(2026, 3, 29, 0, tzinfo=timezone.utc), datetime(2026, 3, 29, 23, tzinfo=timezone.utc))
    # 23:30 UTC on Sun 8 Nov is still Sun 8 Nov in the UK (GMT), 23:30 UTC on 9 Nov is Mon
    assert not funnel.inside("2026-11-08T23:30:00+00:00", funnel.windows(NOW)["yday"])
    assert funnel.inside("2026-11-09T23:30:00Z", funnel.windows(NOW)["yday"])
    assert funnel.ts("2026-11-09T12:00:00.1+00:00") == datetime(2026, 11, 9, 12, 0, 0, 100000, tzinfo=timezone.utc)
    assert funnel.ts("garbage") is None and funnel.ts(None) is None


def test_figures():
    d = good_day()
    w = funnel.windows(NOW)
    y = funnel.figures(d, w["yday"])
    assert (y["started"], y["completed"], y["not_finished"]) == (3, 3, 0)
    assert y["free"] == 1 and y["series"] == 1 and y["series_gbp"] == 39.99
    assert y["annual"] == 1 and y["annual_gbp"] == 79 and y["single"] == 0
    assert y["paid_gbp"] == 118.99
    assert y["members"] == 3            # the test member does not count
    assert y["signins"] == 2 and y["opened"] == 1 and y["completions"] == 1 and y["certificates"] == 1
    assert y["followups"] == 1          # a failed send is not a send
    assert y["unsubscribes"] == 1       # a bounce is not an unsubscribe
    k = funnel.figures(d, w["week"])
    assert k["free"] == 2 and k["single"] == 1 and k["single_gbp"] == 19.99 and k["opened"] == 2
    assert k["paid_gbp"] == 138.98
    # a table the report could not read shows n/a, not 0
    d["signins"] = None; d["stripe_sessions"] = None
    y = funnel.figures(d, w["yday"])
    assert y["signins"] is None and y["started"] is None
    assert funnel.cell(y, "signins", None) == "n/a"


def test_pool():
    p = funnel.pool(good_day()["members"], good_day()["purchases"])
    # m1, m2, m6 have only free orders; m3 bought the series; m5 a course; m4 subscribes
    assert p == {"members": 6, "subscribers": 1, "free_only": 3, "non_subscribers": 5, "said_yes": 1}


def test_no_red_lines_on_a_good_day():
    r = funnel.build(good_day(), NOW)
    assert r["red"] == [], r["red"]
    assert "Nothing needs you today." in r["text"]
    assert r["subject"] == "Meridian Mon 09 Nov: 1 free, 2 paid (£118.99)"


def test_each_red_line():
    def red(change):
        d = good_day(); change(d)
        return funnel.red_lines(d, NOW)

    assert red(lambda d: d.update(health=None)) == ["The app did not answer. Check Railway."]
    assert red(lambda d: d["health"].update(free_code="invalid: expired")) == [
        "Free course code MERIDIAN10 refused by Stripe (expired). Fix it in Stripe > Product catalogue > Coupons."]
    assert red(lambda d: d["health"].update(series_price="missing")) == [
        "Field Work series cannot be bought: STRIPE_PRICE_SERIES is not set in Railway."]
    assert red(lambda d: d.update(stripe_sessions=None)) == [
        "Checkout figures are off: add the STRIPE_REPORT_KEY secret to the GitHub repo."]
    assert red(lambda d: d.update(stripe_sessions=None, stripe_error=True)) == [
        "Stripe did not answer with STRIPE_REPORT_KEY. Check the key in the GitHub repo secrets."]

    # Stripe took a payment that has no purchase row
    def unrecorded(d):
        d["stripe_sessions"].append({"id": "cs_live_lost", "created": int(YDAY.timestamp()), "status": "complete", "amount_total": 7900})
    assert red(unrecorded) == ["Stripe took 1 order the app has not recorded: cs_live_lost."]
    # ...but not one paid in the last half hour, which may still be recording
    def fresh(d):
        d["stripe_sessions"].append({"id": "cs_live_new", "created": int((NOW - timedelta(minutes=5)).timestamp()), "status": "complete"})
    assert red(fresh) == []

    # a checkout started yesterday and not finished, open or expired
    def abandoned(d):
        d["stripe_sessions"] += [{"id": "cs_live_a", "created": int(YDAY.timestamp()), "status": "expired", "amount_total": 7900},
                                 {"id": "cs_live_b", "created": int(YDAY.timestamp()), "status": "open", "amount_total": 3999}]
    assert red(abandoned) == ["2 checkouts started yesterday and not finished (£79.00, £39.99)."]
    # one abandoned last week is in the 7-day column but is not a red line today
    def old_abandoned(d):
        d["stripe_sessions"].append({"id": "cs_live_c", "created": int(DAYS_AGO(4).timestamp()), "status": "expired", "amount_total": 1999})
    assert red(old_abandoned) == []

    # no free orders yesterday or the day before
    def no_free(d):
        d["purchases"] = [p for p in d["purchases"] if p["stripe_session_id"] not in ("cs_live_free1", "cs_live_free2")]
        d["stripe_sessions"] = [s for s in d["stripe_sessions"] if s["id"] not in ("cs_live_free1", "cs_live_free2")]
        d["last_free_order"] = "2026-10-10"
    assert red(no_free) == ["No free-course orders for 2 days. Last one: 2026-10-10."]
    # one free order the day before yesterday is enough
    def one_free(d):
        d["purchases"] = [p for p in d["purchases"] if p["stripe_session_id"] != "cs_live_free1"]
        d["stripe_sessions"] = [s for s in d["stripe_sessions"] if s["id"] != "cs_live_free1"]
    assert red(one_free) == []
    # a test free order does not stop the red line
    def test_free_only(d):
        no_free(d)
        d["purchases"].append({"member_id": "t1", "course_id": "MER-ALL-001", "amount_gbp": 0, "stripe_session_id": "cs_test_free", "purchased_at": iso(YDAY)})
    assert red(test_free_only) == ["No free-course orders for 2 days. Last one: 2026-10-10."]

    r = funnel.build(good_day() | {"health": None}, NOW)
    assert r["subject"].startswith("1 needs you | ")
    assert "NEEDS YOU" in r["text"] and "The app did not answer." in r["html"]


def test_one_screen_and_house_style():
    d = good_day(); d["health"]["free_code"] = "invalid: expired"; d["stripe_sessions"] = None
    r = funnel.build(d, NOW)
    lines = r["text"].strip().splitlines()
    assert len(lines) <= 30, len(lines)
    for part in (r["subject"], r["text"], r["html"]):
        assert "—" not in part and "!" not in part.replace("<!DOCTYPE", ""), part[:200]
    assert "<script" not in r["html"]
    # nothing about a person (names, emails) goes in the report
    assert "@" not in r["text"]


def test_health_and_signins():
    os.environ.update(STRIPE_SECRET_KEY="sk_test_x", STRIPE_WEBHOOK_SECRET="whsec_x", SUPABASE_URL="https://example.supabase.co",
                      SUPABASE_SERVICE_ROLE_KEY="eyJhbGciOiJIUzI1NiJ9.eyJyb2xlIjoic2VydmljZV9yb2xlIn0.x",
                      ADMIN_PASSWORD="test-admin", DASHBOARD_SECRET="dash-secret", UNSUBSCRIBE_SECRET="unsub-secret",
                      RESEND_API_KEY="re_x", OUTREACH_SCHEDULER="off", NEWS_SCHEDULER="off")
    os.environ.pop("STRIPE_PRICE_SERIES", None)
    import main
    main.free_code_state = lambda wait=3.0: "ok"
    assert main.health()["series_price"] == "missing"
    os.environ["STRIPE_PRICE_SERIES"] = "price_x"
    assert main.health()["series_price"] == "set"

    class Q:
        def __init__(self, db, table): self.db, self.table = db, table
        def select(self, *a): return self
        def eq(self, *a): return self
        def insert(self, row): self.db.inserted.append((self.table, row)); return self
        def execute(self):
            if self.db.broken and self.table == "member_signins":
                raise RuntimeError("relation member_signins does not exist")
            class R: data = [{"id": "m-1"}] if self.table == "members" else []
            return R()

    class DB:
        def __init__(self, broken=False): self.inserted, self.broken = [], broken
        def table(self, name): return Q(self, name)

    real = main.supabase
    try:
        main.supabase = DB()
        resp = main._signed_in("a@example.com")
        assert resp.status_code == 302 and main.supabase.inserted == [("member_signins", {"member_id": "m-1"})]
        # before the migration is run the insert fails, and the member is still signed in
        main.supabase = DB(broken=True)
        resp = main._signed_in("a@example.com")
        assert resp.status_code == 302 and "session_token" in resp.headers.get("set-cookie", "")
    finally:
        main.supabase = real


test_windows_are_uk_days(); test_figures(); test_pool(); test_no_red_lines_on_a_good_day()
test_each_red_line(); test_one_screen_and_house_style(); test_health_and_signins()
print("ALL CHECKS PASSED")
