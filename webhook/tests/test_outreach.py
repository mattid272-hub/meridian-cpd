"""The daily outreach sender (outreach.py) and its admin page. Run: python3 tests/test_outreach.py

What must hold: one email per contact ever; nobody suppressed, listed or a member is
emailed; the daily limit counts every send that day; bounces and complaints suppress;
pausing stops everything; the scheduler fires once a weekday inside the window."""
import asyncio, os, sys, types, base64
from datetime import datetime, timedelta
os.environ.update(STRIPE_SECRET_KEY="sk_test_x", STRIPE_WEBHOOK_SECRET="whsec_x", SUPABASE_URL="https://example.supabase.co",
                  SUPABASE_SERVICE_ROLE_KEY="eyJhbGciOiJIUzI1NiJ9.eyJyb2xlIjoic2VydmljZV9yb2xlIn0.x",
                  ADMIN_PASSWORD="test-admin", DASHBOARD_SECRET="dash-secret", UNSUBSCRIBE_SECRET="unsub-secret",
                  RESEND_API_KEY="re_x", OUTREACH_SCHEDULER="off", OUTREACH_DAILY_LIMIT="3")
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
import main, outreach
from fastapi.testclient import TestClient


# ── A small in-memory stand-in for the Supabase client ──
class Res:
    def __init__(self, data): self.data, self.count = data, len(data)
class Q:
    def __init__(s, db, t): s.db, s.t, s.f, s.op, s.pl, s.ord, s.lim = db, t, [], "select", None, None, None
    def select(s, *a, **k): return s
    def eq(s, c, v): s.f.append(lambda r: r.get(c) == v); return s
    def in_(s, c, vals): s.f.append(lambda r: r.get(c) in vals); return s
    def gte(s, c, v): s.f.append(lambda r: (r.get(c) or "") >= v); return s
    def is_(s, c, _n): s.f.append(lambda r: r.get(c) is None); return s
    def order(s, c, desc=False): s.ord = (c, desc); return s
    def limit(s, n): s.lim = n; return s
    def insert(s, row): s.op, s.pl = "insert", row; return s
    def upsert(s, row): s.op, s.pl = "upsert", row; return s
    def update(s, row): s.op, s.pl = "update", row; return s
    def execute(s):
        rows = s.db.setdefault(s.t, [])
        if s.op == "insert":
            row = {"id": f"{s.t}-{len(rows) + 1}", **s.pl}; rows.append(row); return Res([row])
        if s.op == "upsert":
            hit = [r for r in rows if r.get("email") == s.pl.get("email")]
            if hit: hit[0].update(s.pl)
            else: rows.append({"id": f"{s.t}-{len(rows) + 1}", "suppressed_at": "2026-10-23", **s.pl})
            return Res([s.pl])
        hit = [r for r in rows if all(f(r) for f in s.f)]
        if s.op == "update":
            for r in hit: r.update(s.pl)
            return Res(hit)
        if s.ord: hit.sort(key=lambda r: r.get(s.ord[0]) or 0, reverse=s.ord[1])
        if s.lim is not None: hit = hit[:s.lim]
        return Res(hit)


def client(db):
    return types.SimpleNamespace(table=lambda t: Q(db, t))


def fresh_db():
    return {
        "outreach_campaigns": [{"id": "camp-1", "name": "Wave 1", "status": outreach.STATUS_ACTIVE, "created_at": "2026-10-22T00:00:00+01:00"}],
        "outreach_contacts": [
            {"id": "c1", "email": "jo@smithsurvaying.co.uk", "first_name": "Jo", "suppressed": False},
            {"id": "c2", "email": "sam@listed.co.uk", "first_name": "SAM", "suppressed": False},       # on the list
            {"id": "c3", "email": "pat@flagged.co.uk", "first_name": "Pat", "suppressed": True},       # flagged
            {"id": "c4", "email": "member@firm.co.uk", "first_name": "M", "suppressed": False},        # a member
            {"id": "c5", "email": "not-an-address", "first_name": "X", "suppressed": False},
            {"id": "c6", "email": "ali@acme-epc.co.uk", "first_name": "Ali", "suppressed": False},
            {"id": "c7", "email": "kim@acme-epc.co.uk", "first_name": "kim", "suppressed": False},
            {"id": "c8", "email": "lee@other.co.uk", "first_name": "Lee", "suppressed": False},
        ],
        "outreach_queue": [{"id": f"q{i}", "campaign_id": "camp-1", "contact_id": f"c{i}", "position": i, "status": "queued"} for i in range(1, 9)],
        "outreach_suppressed": [{"id": "s1", "email": "sam@listed.co.uk", "reason": "unsubscribed", "suppressed_at": "2026-06-01"}],
        "members": [{"id": "m1", "email": "member@firm.co.uk"}],
        "outreach_sends": [], "outreach_runs": [],
    }


sent, events = [], {}
class FakeHTTP:
    def __init__(s, **k): pass
    async def __aenter__(s): return s
    async def __aexit__(s, *a): return False
    async def post(s, url, headers=None, json=None, timeout=None):
        if json["to"][0].endswith("@down.co.uk"):
            raise RuntimeError("Resend is down")
        sent.append(json)
        return types.SimpleNamespace(status_code=200, raise_for_status=lambda: None, json=lambda: {"id": f"msg-{len(sent)}"})
    async def get(s, url, headers=None, timeout=None):
        ev = events.get(url.rsplit("/", 1)[-1], "sent")
        return types.SimpleNamespace(status_code=200, json=lambda: {"last_event": ev})
outreach.httpx.AsyncClient = FakeHTTP
main.httpx.AsyncClient = FakeHTTP
outreach.PACE_SECONDS = 0  # no pacing in tests

fails = 0
def check(name, cond):
    global fails
    print(("PASS " if cond else "FAIL ") + name)
    fails += 0 if cond else 1

MON_10 = datetime(2026, 10, 26, 10, 0, tzinfo=outreach.UK)   # a Monday, inside the window
SAT = datetime(2026, 10, 24, 10, 0, tzinfo=outreach.UK)

# ── The email itself ──
subject, text, html = outreach.render("Jo", "https://app.meridiancpd.co.uk/unsubscribe?email=x&token=y")
check("email greets by first name", text.startswith("Hello Jo,"))
check("email has the free code, the price, the deadline and the unsubscribe link",
      all(w in text for w in ("MERIDIAN10", "£79", outreach.OFFER_DEADLINE, "unsubscribe?email=x&token=y", "privacy.html")))
check("html carries the same link", "unsubscribe?email=x&token=y" in html and "MERIDIAN10" in html)
check("odd first names become 'there'", [outreach.greeting_name(n) for n in ("", None, "J", "A.", "Smith Surveying", "123", "x" * 25)] == ["there"] * 7)
check("shouted names are calmed down", outreach.greeting_name("SAM") == "Sam" and outreach.greeting_name("McDonald") == "McDonald")

# ── Unsubscribe links ──
url = outreach.unsubscribe_url("jo@smithsurvaying.co.uk")
tok = url.rsplit("token=", 1)[1]
check("unsubscribe link verifies with the app's own check", main._verify_unsubscribe_token("jo@smithsurvaying.co.uk", tok))
db = fresh_db()
main.supabase = client(db)
main._refresh_under_review = lambda: None
c = TestClient(main.app, follow_redirects=False)
r = c.post(url.replace(main.BASE_URL, ""), data={"List-Unsubscribe": "One-Click"})
check("one-click unsubscribe (POST from the mail provider) suppresses the address",
      r.status_code == 200 and any(s["email"] == "jo@smithsurvaying.co.uk" for s in db["outreach_suppressed"])
      and db["outreach_contacts"][0]["suppressed"] is True)
r = c.post("/unsubscribe?email=jo@smithsurvaying.co.uk&token=0000000000000000")
check("one-click with a bad token is refused", r.status_code == 400)

# ── Sending a batch ──
db = fresh_db(); sent.clear()
res = asyncio.run(outreach.run_batch(client(db), trigger="admin", now=MON_10))
check("sends up to the daily limit, in queue order, skipping the ineligible",
      res["sent"] == 3 and [m["to"][0] for m in sent] == ["jo@smithsurvaying.co.uk", "ali@acme-epc.co.uk", "kim@acme-epc.co.uk"])
statuses = {q["contact_id"]: (q["status"], q.get("note")) for q in db["outreach_queue"]}
check("ineligible contacts are skipped with a reason, not sent",
      statuses["c2"] == ("skipped", "on suppression list") and statuses["c3"] == ("skipped", "contact suppressed")
      and statuses["c4"] == ("skipped", "already a member") and statuses["c5"] == ("skipped", "address not valid"))
check("the rest stay queued for another day", statuses["c8"][0] == "queued")
check("every send is logged with Resend's id", len(db["outreach_sends"]) == 3 and db["outreach_sends"][0]["sendgrid_message_id"] == "resend:msg-1")
m = sent[0]
check("email goes from Matt at hello@, with reply-to", m["from"] == "Matt Davies, Meridian CPD <hello@meridiancpd.co.uk>" and m["reply_to"] == "hello@meridiancpd.co.uk")
check("one-click unsubscribe headers are set", "List-Unsubscribe" in m["headers"] and m["headers"]["List-Unsubscribe-Post"] == "List-Unsubscribe=One-Click"
      and outreach.unsubscribe_url("jo@smithsurvaying.co.uk") in m["headers"]["List-Unsubscribe"])
check("Resend tag is made of safe characters only", m["tags"] == [{"name": "campaign", "value": "Wave-1"}])
check("text and html both sent", "MERIDIAN10" in m["text"] and "MERIDIAN10" in m["html"] and m["subject"] == outreach.SUBJECT)
res2 = asyncio.run(outreach.run_batch(client(db), trigger="admin", now=MON_10))
check("a second run the same day sends nothing more", res2["sent"] == 0 and res2["note"] == "daily limit already reached" and len(sent) == 3)
res3 = asyncio.run(outreach.run_batch(client(db), trigger="admin", now=MON_10 + timedelta(days=1)))
check("next day sends the next of the queue, never a repeat", res3["sent"] == 1 and sent[-1]["to"] == ["lee@other.co.uk"]
      and len({m["to"][0] for m in sent}) == len(sent))
check("runs are logged", len(db["outreach_runs"]) == 3 and db["outreach_runs"][0]["sent"] == 3 and db["outreach_runs"][0]["finished_at"])

# ── Paused ──
db = fresh_db(); sent.clear(); db["outreach_campaigns"][0]["status"] = outreach.STATUS_PAUSED
res = asyncio.run(outreach.run_batch(client(db), trigger="scheduler", now=MON_10))
check("paused campaign sends nothing", res["sent"] == 0 and res["note"] == "paused" and not sent)
check("the campaign is never marked 'active' (the old engine's trigger word)",
      "active" not in (outreach.STATUS_ACTIVE, outreach.STATUS_PAUSED))

# ── Resend is down ──
db = fresh_db(); sent.clear()
for i, r_ in enumerate(db["outreach_contacts"]):
    r_["email"] = f"p{i}@down.co.uk"
res = asyncio.run(outreach.run_batch(client(db), trigger="admin", now=MON_10))
check("three failures in a row stop the run", res["failed"] == 3 and res["note"].startswith("stopped") and res["sent"] == 0)

# ── Bounces and complaints ──
db = fresh_db(); sent.clear()
asyncio.run(outreach.run_batch(client(db), trigger="admin", now=MON_10))
events.update({"msg-1": "delivered", "msg-2": "bounced", "msg-3": "complained"})
b, cpl = asyncio.run(outreach.poll_delivery(client(db), "camp-1", MON_10 + timedelta(hours=3)))
sends = {s["sendgrid_message_id"]: s["status"] for s in db["outreach_sends"]}
check("delivered, bounced and complained are recorded", (b, cpl) == (1, 1) and sends == {"resend:msg-1": "delivered", "resend:msg-2": "bounced", "resend:msg-3": "complained"})
supp = {s["email"]: s["reason"] for s in db["outreach_suppressed"]}
check("bounced and complained addresses go on the do-not-email list",
      supp.get("ali@acme-epc.co.uk") == "bounced" and supp.get("kim@acme-epc.co.uk") == "complained"
      and db["outreach_contacts"][6]["suppressed"] is True)
events.clear()

# ── Scheduler timing: a drip across working hours ──
db = fresh_db()
os.environ["OUTREACH_DAILY_LIMIT"] = "50"
MON_8 = MON_10.replace(hour=8, minute=0)
check("nothing at the weekend or outside 08:00-18:00",
      outreach.drip_size(client(db), SAT) == 0 and outreach.drip_size(client(db), MON_8.replace(hour=7, minute=59)) == 0
      and outreach.drip_size(client(db), MON_8.replace(hour=18, minute=0)) == 0)
check("50 a day is spread evenly: none due at 08:00, 5 by 09:00, 25 by 13:00, all by 18:00",
      [outreach.expected_by_now(MON_8.replace(hour=h), 50) for h in (8, 9, 13, 17)] == [0, 5, 25, 45]
      and outreach.expected_by_now(MON_8.replace(hour=17, minute=59), 50) == 49)
check("a tick sends at most two, even when behind", outreach.drip_size(client(db), MON_8.replace(hour=13)) == 2)
sent.clear()
for _ in range(3):
    asyncio.run(outreach.run_batch(client(db), trigger="scheduler", now=MON_8.replace(hour=9), max_send=2, poll=False))
check("ticks send two at a time until the queue runs dry (4 eligible here), never a repeat",
      [m["to"][0] for m in sent] == ["jo@smithsurvaying.co.uk", "ali@acme-epc.co.uk", "kim@acme-epc.co.uk", "lee@other.co.uk"]
      and outreach.drip_size(client(db), MON_8.replace(hour=9)) == 1)
check("the scheduler's sends in a day share one run row", len([r for r in db["outreach_runs"] if r["trigger"] == "scheduler"]) == 1
      and db["outreach_runs"][0]["sent"] == 4 and db["outreach_runs"][0]["note"] == "queue empty")
check("a paused campaign gets no drip", (db["outreach_campaigns"][0].update({"status": outreach.STATUS_PAUSED}) or True)
      and outreach.drip_size(client(db), MON_8.replace(hour=13)) == 0)
check("next send time after hours is the next weekday at 08:00",
      outreach.next_send_time(datetime(2026, 10, 23, 19, 0, tzinfo=outreach.UK)).strftime("%a %H:%M") == "Mon 08:00")
os.environ["OUTREACH_DAILY_LIMIT"] = "3"
check("daily limit respects the ceiling", 0 <= outreach.daily_limit() <= outreach.HARD_CEILING and outreach.daily_limit() == 3)

# ── Admin page ──
db = fresh_db(); sent.clear()
main.supabase = client(db)
auth = {"Authorization": "Basic " + base64.b64encode(b"admin:test-admin").decode()}
r = c.get("/admin/outreach", headers=auth)
check("admin page shows the campaign, the queue and the email", r.status_code == 200 and "Wave 1" in r.text and "MERIDIAN10" in r.text and "Waiting to send" in r.text)
check("admin page needs the password", c.get("/admin/outreach").status_code == 401)
r = c.post("/admin/outreach/pause", headers=auth)
check("pause button pauses", db["outreach_campaigns"][0]["status"] == outreach.STATUS_PAUSED and "Paused" in r.text)
r = c.post("/admin/outreach/resume", headers=auth)
check("resume button resumes", db["outreach_campaigns"][0]["status"] == outreach.STATUS_ACTIVE)
r = c.post("/admin/outreach/test", headers=auth, data={"email": "matt@example.org"})
check("test copy goes only to the address given", sent and sent[-1]["to"] == ["matt@example.org"] and "Test copy sent" in r.text and not db["outreach_sends"])
r = c.post("/admin/outreach/test", headers=auth, data={"email": "nope"})
check("test copy refuses a bad address", "does not look right" in r.text)
sent.clear()
r = c.post("/admin/outreach/run", headers=auth)
check("send-now button sends the rest of today's allowance", "Batch finished: 3 sent" in r.text and len(sent) == 3)

print(f"\n{'ALL PASSED' if not fails else f'{fails} FAILED'}")
sys.exit(1 if fails else 0)
