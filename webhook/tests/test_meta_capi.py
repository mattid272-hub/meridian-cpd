"""Tests for the Meta Pixel and Conversions API: nothing without the variables, nothing without
consent, the beacon forwards only our browser events with their ids, the pixel goes only on pages
whose address is safe to send, and /thanks sends Lead for a free order and Purchase for a paid one.
Run: python3 tests/test_meta_capi.py"""
import asyncio, json, os, sys, time, types
os.environ.update(STRIPE_SECRET_KEY="sk_test_x", STRIPE_WEBHOOK_SECRET="whsec_x", SUPABASE_URL="https://example.supabase.co",
                  SUPABASE_SERVICE_ROLE_KEY="eyJhbGciOiJIUzI1NiJ9.eyJyb2xlIjoic2VydmljZV9yb2xlIn0.x", SESSION_SECRET="s",
                  ADMIN_PASSWORD="test-admin")
for k in ("META_PIXEL_ID", "META_CAPI_TOKEN", "META_TEST_EVENT_CODE"):
    os.environ.pop(k, None)
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
import httpx
import stripe
import main
import meta_capi
from fastapi.testclient import TestClient


class Res:
    def __init__(self, data): self.data, self.count = data, len(data)
class Q:
    def __init__(s, db, t): s.db, s.t, s.f = db, t, []
    def select(s, *a, **k): return s
    def eq(s, c, v): s.f.append(lambda r, c=c, v=v: r.get(c) == v); return s
    def order(s, *a, **k): return s
    def limit(s, *a): return s
    def execute(s): return Res([r for r in s.db.get(s.t, []) if all(f(r) for f in s.f)])


db = {
    "members": [{"id": "m1", "email": "Free@Example.co.uk", "name": "F", "plan": "single", "marketing_consent": True},
                {"id": "m2", "email": "sub@example.co.uk", "name": "S", "plan": "subscription", "marketing_consent": True},
                {"id": "m3", "email": "ser@example.co.uk", "name": "R", "plan": "single", "marketing_consent": True}],
    "purchases": [{"member_id": "m1", "course_id": "MER-DEA-001", "amount_gbp": 0, "stripe_session_id": "cs_live_free1234567"},
                  {"member_id": "m2", "course_id": "SUBSCRIPTION", "amount_gbp": 79, "stripe_session_id": "cs_live_subs1234567"},
                  {"member_id": "m3", "course_id": "MER-ALL-019", "amount_gbp": 13.33, "series_id": "FW-INSULATION", "stripe_session_id": "cs_live_seri1234567"},
                  {"member_id": "m3", "course_id": "MER-ALL-020", "amount_gbp": 13.33, "series_id": "FW-INSULATION", "stripe_session_id": "cs_live_seri1234567"}],
}
main.supabase = types.SimpleNamespace(table=lambda t: Q(db, t))
now = time.time()
SESSIONS = {
    "cs_live_free1234567": {"id": "cs_live_free1234567", "status": "complete", "created": now, "amount_total": 0, "currency": "gbp",
                            "customer_details": {"email": "free@example.co.uk"}},
    "cs_live_subs1234567": {"id": "cs_live_subs1234567", "status": "complete", "created": now, "amount_total": 7900, "currency": "gbp",
                            "customer_details": {"email": "sub@example.co.uk"}},
    "cs_live_seri1234567": {"id": "cs_live_seri1234567", "status": "complete", "created": now, "amount_total": 3999, "currency": "gbp",
                            "customer_details": {"email": "ser@example.co.uk"}},
}
main._paid_session = lambda sid: SESSIONS.get(sid)

posted = []
class FakeClient:
    def __init__(self, *a, **k): pass
    async def __aenter__(self): return self
    async def __aexit__(self, *a): return False
    async def post(self, url, json=None, **k):
        posted.append((url, json)); return types.SimpleNamespace(status_code=200, text="{}")
httpx.AsyncClient = FakeClient

c = TestClient(main.app)
SITE = {"origin": "https://meridiancpd.co.uk"}
beacon = json.dumps({"event_name": "ViewContent", "event_id": "abc123def456", "custom_data": {"content_ids": ["MER-DEA-001"], "content_type": "product", "email": "x@y.z"},
                     "event_source_url": "https://meridiancpd.co.uk/courses.html?open=MER-DEA-001&email=x@y.z"})

# 1. No variables: no script on app pages, beacon accepted and dropped, /thanks sends nothing.
r = c.get("/my-cpd")
assert r.status_code == 200 and "consent.js" not in r.text, "pixel loaded without META_PIXEL_ID"
r = c.post("/meta/event", content=beacon, headers=SITE, cookies={"mcpd_consent": "yes"})
assert r.status_code == 204 and posted == []
c.get("/thanks?session_id=cs_live_subs1234567", cookies={"mcpd_consent": "yes"})
assert posted == [], "sent to Meta without the variables"

# 2. Pixel id only: the banner script on safe pages, never on pages with a private address; still no server sends.
os.environ["META_PIXEL_ID"] = "1133939432819396"
r = c.get("/my-cpd")
assert 'src="https://meridiancpd.co.uk/consent.js" data-pixel="1133939432819396"' in r.text
assert r.text.rstrip().endswith("</html>") and int(r.headers["content-length"]) == len(r.content)
assert "consent.js" not in c.get("/thanks?session_id=cs_live_subs1234567").text, "pixel on /thanks sends the session id to Meta"
assert "consent.js" not in c.get("/unsubscribe?email=a@b.co&token=x").text
assert "consent.js" not in c.get("/verify/MER-2026-0001").text, "pixel on a certificate check page"
assert "consent.js" not in c.get("/verify").text
assert not main._pixel_page("/verify/MER-2026-0001") and not main._pixel_page("/verify") \
    and not main._pixel_page("/complete/tok") \
    and not main._pixel_page("/my-cpd/login/tok") and not main._pixel_page("/admin")
c.post("/meta/event", content=beacon, headers=SITE, cookies={"mcpd_consent": "yes"})
assert posted == [], "server send without META_CAPI_TOKEN"

# 3. Both set: nothing without Accept, nothing from another site, nothing for events we do not forward.
os.environ["META_CAPI_TOKEN"] = "test-token"
for cookies in ({}, {"mcpd_consent": "no"}):
    c.post("/meta/event", content=beacon, headers=SITE, cookies=cookies)
    c.get("/thanks?session_id=cs_live_subs1234567", cookies=cookies)
assert posted == [], "sent to Meta without consent"
c.post("/meta/event", content=beacon, headers={"origin": "https://evil.example"}, cookies={"mcpd_consent": "yes"})
c.post("/meta/event", content=json.dumps({"event_name": "Purchase", "event_id": "abc123def456"}), headers=SITE, cookies={"mcpd_consent": "yes"})
c.post("/meta/event", content="not json", headers=SITE, cookies={"mcpd_consent": "yes"})
assert posted == [], "forwarded a beacon it should have dropped"

# 4. A consented beacon: same name and id as the browser event, clean address, no stray fields.
r = c.post("/meta/event", content=beacon, cookies={"mcpd_consent": "yes", "_fbp": "fb.1.1700000000.123"},
           headers={**SITE, "x-forwarded-for": "203.0.113.9, 10.0.0.1", "user-agent": "Safari"})
assert r.status_code == 204 and len(posted) == 1
url, payload = posted.pop()
assert url == "https://graph.facebook.com/v24.0/1133939432819396/events" and payload["access_token"] == "test-token"
ev = payload["data"][0]
assert ev["event_name"] == "ViewContent" and ev["event_id"] == "abc123def456" and ev["action_source"] == "website"
assert ev["event_source_url"] == "https://meridiancpd.co.uk/courses.html", ev["event_source_url"]
assert ev["custom_data"] == {"content_ids": ["MER-DEA-001"], "content_type": "product"}
assert ev["user_data"] == {"client_user_agent": "Safari", "client_ip_address": "203.0.113.9", "fbp": "fb.1.1700000000.123"}
assert "test_event_code" not in payload

# 5. /thanks: Lead for the free course, Purchase with value for the subscription and the series.
def thanks(sid):
    r = c.get(f"/thanks?session_id={sid}", cookies={"mcpd_consent": "yes"})
    assert r.status_code == 200 and "consent.js" not in r.text and len(posted) == 1
    return posted.pop()[1]["data"][0]

ev = thanks("cs_live_free1234567")
assert ev["event_name"] == "Lead" and ev["custom_data"]["value"] == 0 and ev["custom_data"]["content_ids"] == ["MER-DEA-001"]
assert ev["user_data"]["em"] == [meta_capi._sha("free@example.co.uk")], "email not hashed the way Meta asks"
assert "cs_live" not in json.dumps(ev), "checkout session id sent to Meta"
ev2 = thanks("cs_live_free1234567")
assert ev2["event_id"] == ev["event_id"], "a reload must reuse the event id so Meta drops it"
ev = thanks("cs_live_subs1234567")
assert ev["event_name"] == "Purchase" and ev["custom_data"]["value"] == 79.0 and ev["custom_data"]["currency"] == "GBP"
assert ev["custom_data"]["content_name"] == "subscription"
ev = thanks("cs_live_seri1234567")
assert ev["event_name"] == "Purchase" and ev["custom_data"]["value"] == 39.99 and ev["custom_data"]["content_ids"] == ["FW-INSULATION"]

# 6. A refusal or a network failure from Meta never breaks the page.
class Broken(FakeClient):
    async def post(self, *a, **k): raise httpx.ConnectError("down")
httpx.AsyncClient = Broken
r = c.get("/thanks?session_id=cs_live_subs1234567", cookies={"mcpd_consent": "yes"})
assert r.status_code == 200
assert asyncio.run(meta_capi.send([{"event_name": "PageView"}])) is False

print("meta capi: all checks passed")
