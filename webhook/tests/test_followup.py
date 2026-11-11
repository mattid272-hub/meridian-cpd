"""Free-course follow-up emails (followup.py). Run: python3 tests/test_followup.py

What must hold: off by default and nothing sent unless switched on; dry-run sends and
writes nothing; each step once per person; the right step at the right time; the sequence
stops for buyers, subscribers, the suppressed and anyone who said no; the gap and the
lifetime cap hold; the sales emails respect the consent setting; the daily limit holds;
the annual price in an email is the one checkout charges (the Stripe price), and with no
known price no email names one; the price-rise email waits for FREE_FOLLOWUP_PRICE_RISE;
every email carries a working unsubscribe link, the approved prices and none of the
banned words; bounces suppress; the admin page and the Friday figures work."""
import asyncio, os, sys, types, re
from datetime import datetime, timedelta
os.environ.update(STRIPE_SECRET_KEY="sk_test_x", STRIPE_WEBHOOK_SECRET="whsec_x", SUPABASE_URL="https://example.supabase.co",
                  SUPABASE_SERVICE_ROLE_KEY="eyJhbGciOiJIUzI1NiJ9.eyJyb2xlIjoic2VydmljZV9yb2xlIn0.x",
                  ADMIN_PASSWORD="test-admin", DASHBOARD_SECRET="dash-secret", UNSUBSCRIBE_SECRET="unsub-secret",
                  RESEND_API_KEY="re_x", OUTREACH_SCHEDULER="off", NEWS_SCHEDULER="off")
os.environ.pop("FREE_FOLLOWUP", None)
os.environ.pop("FREE_FOLLOWUP_CONSENT", None)
os.environ.pop("FREE_FOLLOWUP_PRICE_RISE", None)
os.environ["STRIPE_PRICE_SUBSCRIPTION"] = "price_annual_test"
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
import main, followup, outreach
from fastapi.testclient import TestClient


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
            if s.t == followup.TABLE and any(r["member_id"] == s.pl["member_id"] and r["step"] == s.pl["step"] for r in rows):
                raise RuntimeError("duplicate key (member_id, step)")
            row = {"id": f"{s.t}-{len(rows) + 1}", **s.pl}; rows.append(row); return Res([row])
        if s.op == "upsert":
            hit = [r for r in rows if r.get("email") == s.pl.get("email")]
            if hit: hit[0].update(s.pl)
            else: rows.append({"id": f"{s.t}-{len(rows) + 1}", **s.pl})
            return Res([s.pl])
        hit = [r for r in rows if all(f(r) for f in s.f)]
        if s.op == "update":
            for r in hit: r.update(s.pl)
            return Res(hit)
        if s.ord: hit.sort(key=lambda r: r.get(s.ord[0]) or "", reverse=s.ord[1])
        if s.lim is not None: hit = hit[:s.lim]
        return Res(hit)


def client(db):
    return types.SimpleNamespace(table=lambda t: Q(db, t))


UK = followup.UK
NOV_20 = datetime(2026, 11, 20, 10, 0, tzinfo=UK)    # a Friday, inside the window
DEC_07 = datetime(2026, 12, 7, 10, 0, tzinfo=UK)     # a Monday in the price-notice window
JAN_12 = datetime(2027, 1, 12, 10, 0, tzinfo=UK)     # after the rise
iso = lambda d: d.isoformat()


NAMES = ["", "Alex", "Bryn", "Cara", "Dewi", "Eira", "Ffion", "Gwen", "Huw", "Iolo", "Jac"]


def member(i, **kw):
    return {"id": f"m{i}", "email": f"person{i}@firm{i}.co.uk", "name": f"{NAMES[i]} Surname", "plan": "single",
            "marketing_consent": True, "stripe_customer_id": f"cus_{i}", **kw}


def free(i, days_ago, now=NOV_20, course="MER-DEA-001"):
    return {"member_id": f"m{i}", "course_id": course, "amount_gbp": 0, "stripe_session_id": f"cs_live_{i}",
            "purchased_at": iso(now - timedelta(days=days_ago))}


def fresh_db():
    return {
        "members": [
            member(1),                                   # free, 20 days ago, unfinished -> nudge
            member(2),                                   # free, finished 10 days ago -> next
            member(3),                                   # free, then paid -> never
            member(4, plan="subscription"),              # subscriber -> never
            member(5),                                   # unsubscribed -> never
            member(6, marketing_consent=False),          # said no -> never
            member(7, marketing_consent=None),           # never answered, finished -> next only if not_no
            member(8, email="test@meridiancpd.co.uk"),   # our own address -> never
            member(9),                                   # took it 5 days ago -> nothing yet
            member(10),                                  # test checkout only -> never
        ],
        "purchases": [
            free(1, 20), free(2, 30), free(3, 30),
            {"member_id": "m3", "course_id": "MER-ALL-019", "amount_gbp": 39.99, "stripe_session_id": "cs_live_3b", "purchased_at": iso(NOV_20 - timedelta(days=3))},
            free(4, 30), free(5, 30), free(6, 30), free(7, 30), free(8, 30), free(9, 5),
            {"member_id": "m10", "course_id": "MER-DEA-001", "amount_gbp": 0, "stripe_session_id": "cs_test_10", "purchased_at": iso(NOV_20 - timedelta(days=30))},
        ],
        "completions": [
            {"member_id": "m1", "course_id": "MER-DEA-001", "completed_at": None, "completion_token": "tok-1"},
            {"member_id": "m2", "course_id": "MER-DEA-001", "completed_at": iso(NOV_20 - timedelta(days=10)), "completion_token": "tok-2"},
            {"member_id": "m7", "course_id": "MER-DEA-001", "completed_at": iso(NOV_20 - timedelta(days=10)), "completion_token": "tok-7"},
        ],
        "outreach_suppressed": [{"id": "s1", "email": "person5@firm5.co.uk", "reason": "unsubscribed", "suppressed_at": "2026-06-12"}],
        "outreach_contacts": [], "outreach_sends": [],
        followup.TABLE: [],
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
followup.httpx.AsyncClient = FakeHTTP
main.httpx.AsyncClient = FakeHTTP
followup.PACE_SECONDS = 0

price_reads = []
def set_price(pence):
    """What the Stripe price in STRIPE_PRICE_SUBSCRIPTION charges, as the app would read it."""
    def fetch():
        price_reads.append(pence)
        if isinstance(pence, Exception):
            raise pence
        return pence
    followup._fetch_annual_pence = fetch
    followup._price_cache.update(at=None, gbp=None)
set_price(7900)

fails = 0
def check(name, cond):
    global fails
    print(("PASS " if cond else "FAIL ") + name)
    fails += 0 if cond else 1

go = lambda db, now, **kw: asyncio.run(followup.run(client(db), now, main.COURSES, **kw))
steps_of = lambda res: sorted((w["member_id"], w["step"]) for w in res["would_send"])

# ── The switch ──
check("the switch defaults to off", followup.mode() == "off")
db = fresh_db(); sent.clear()
res = go(db, NOV_20, dry_run=False)
check("switched off: a real pass sends nothing and writes nothing", res["sent"] == 0 and not sent and not db[followup.TABLE] and res["note"] == "switched off")
os.environ["FREE_FOLLOWUP"] = "nonsense"
check("an unknown value counts as off", followup.mode() == "off")

# ── Dry run ──
os.environ["FREE_FOLLOWUP"] = "dry_run"
db = fresh_db(); sent.clear()
res = go(db, NOV_20)
check("dry run in November: m1 gets the nudge, m2 what's next, nobody else",
      steps_of(res) == [("m1", "nudge"), ("m2", "next")])
check("dry run sends nothing and writes nothing", not sent and not db[followup.TABLE])
check("dry run counts the free-course takers (buyers, subscribers, test accounts excluded)", res["takers"] == 6)
check("dry run says why the rest are not due",
      res["skipped"].get("on suppression list") == 1 and res["skipped"].get("said no to marketing") == 1
      and res["skipped"].get("no marketing consent") == 1 and res["skipped"].get("nothing due yet") == 1)

os.environ["FREE_FOLLOWUP_CONSENT"] = "not_no"
res = go(fresh_db(), NOV_20)
check("with FREE_FOLLOWUP_CONSENT=not_no, someone who never answered gets what's next too",
      ("m7", "next") in steps_of(res) and ("m6", "next") not in steps_of(res))
os.environ.pop("FREE_FOLLOWUP_CONSENT")
db = fresh_db(); db["members"][0]["marketing_consent"] = None
check("the nudge is not a sales email: it goes to someone who never answered",
      ("m1", "nudge") in steps_of(go(db, NOV_20)))

# ── Sending ──
os.environ["FREE_FOLLOWUP"] = "on"
db = fresh_db(); sent.clear()
res = go(db, NOV_20)
check("on: sends the two due emails and logs each with Resend's id",
      res["sent"] == 2 and len(sent) == 2 and {r["step"] for r in db[followup.TABLE]} == {"nudge", "next"}
      and all(r["resend_id"].startswith("msg-") and r["status"] == "sent" for r in db[followup.TABLE]))
nudge = next(m for m in sent if m["to"][0] == "person1@firm1.co.uk")
nxt = next(m for m in sent if m["to"][0] == "person2@firm2.co.uk")
check("the nudge points at My CPD (sign in, open the course, tick the declaration, certificate in My certificates) and greets by first name",
      "/my-cpd\n" in nudge["text"] and "/complete/" not in nudge["text"] and "tick the declaration" in nudge["text"]
      and "My certificates at once" in nudge["text"] and "a copy comes by email" in nudge["text"]
      and "Mark Complete" not in nudge["text"] and nudge["text"].startswith("Hello Alex,") and "two CPD hours" in nudge["text"])
check("what's next names the price checkout charges (£79 now)", "£79 a year" in nxt["text"] and "£99" not in nxt["text"])
unsub = nudge["headers"]["List-Unsubscribe"].split(", <")[1].rstrip(">")
tok = unsub.rsplit("token=", 1)[1]
check("every email has a working unsubscribe link in the body and the headers",
      all(m["headers"]["List-Unsubscribe-Post"] == "List-Unsubscribe=One-Click" and "/unsubscribe?email=" in m["text"] for m in sent)
      and main._verify_unsubscribe_token("person1@firm1.co.uk", tok))
res = go(db, NOV_20 + timedelta(hours=2))
check("a second pass the same day sends nothing more", res["sent"] == 0 and len(sent) == 2)

res = go(db, NOV_20 + timedelta(days=10))
check("the gap holds: ten days later m1 and m2 get nothing (m9 is now due its nudge)",
      [r["member_id"] for r in db[followup.TABLE][2:]] == ["m9"])
d = NOV_20 + timedelta(days=31)  # Monday 21 December: inside the price window
os.environ["FREE_FOLLOWUP"] = "dry_run"
res = go(db, d)
check("in December the price email is held while FREE_FOLLOWUP_PRICE_RISE is off (m1 gets what's next instead)",
      steps_of(res) == [("m1", "next")])
os.environ["FREE_FOLLOWUP_PRICE_RISE"] = "on"
set_price(9900)
res = go(db, d)
check("and it never goes once checkout already charges £99; with no £99 subscribe link, what's next is held too",
      steps_of(res) == [] and res["skipped"].get("annual price not known") == 3)
followup.SUBSCRIBE_URLS[99] = "https://buy.stripe.com/test-99"
res = go(db, d)
check("once a £99 link exists, m1 gets what's next at £99 instead", steps_of(res) == [("m1", "next")])
del followup.SUBSCRIBE_URLS[99]
os.environ["FREE_FOLLOWUP"] = "on"
set_price(7900)
res = go(db, d)
check("with FREE_FOLLOWUP_PRICE_RISE=on and checkout at £79, both get the price email (it takes priority)",
      sorted(r["step"] for r in db[followup.TABLE] if r["sent_at"] == d.isoformat()) == ["price", "price"])
os.environ.pop("FREE_FOLLOWUP_PRICE_RISE")
res = go(db, datetime(2027, 3, 1, 10, 0, tzinfo=UK))
check("price supersedes what's next: m1 never gets 'next' after the price email, and with no monthly edition nothing more goes",
      not any(r["member_id"] in ("m1", "m2") and r["sent_at"] >= "2027" for r in db[followup.TABLE])
      and not any(r["member_id"] == "m1" and r["step"] == "next" for r in db[followup.TABLE]))

# The annual price comes from Stripe, not the calendar
os.environ["FREE_FOLLOWUP"] = "dry_run"
set_price(None)
res = go(fresh_db(), NOV_20)
check("no annual price known: what's next is held for m2 and m7 and says why, the nudge still goes",
      steps_of(res) == [("m1", "nudge")] and res["skipped"].get("annual price not known") == 2)
set_price(RuntimeError("Stripe unreachable"))
res = go(fresh_db(), NOV_20)
check("Stripe unreadable: the same", steps_of(res) == [("m1", "nudge")] and res["skipped"].get("annual price not known") == 2)
set_price(8900)
res = go(fresh_db(), NOV_20)
check("a price the texts were not written for (£89): what's next is held", steps_of(res) == [("m1", "nudge")])
set_price(9900)
res = go(fresh_db(), NOV_20)
check("checkout at £99 with no £99 subscribe link: what's next is held and says why, the nudge still goes",
      followup.SUBSCRIBE_URLS == {79: "https://buy.stripe.com/fZufZgbse3BpcXE7TY73G01"}
      and steps_of(res) == [("m1", "nudge")] and res["skipped"].get("annual price not known") == 2)
try:
    followup.render_next("Jo", "x", "u", 99); no_link_ok = False
except ValueError:
    no_link_ok = True
check("and there is no £99 email to render until the link exists", no_link_ok)
followup.SUBSCRIBE_URLS[99] = "https://buy.stripe.com/test-99"
os.environ["FREE_FOLLOWUP"] = "on"
db = fresh_db(); sent.clear()
go(db, JAN_12 - timedelta(days=50))
nxt99 = next(m for m in sent if m["to"][0] == "person2@firm2.co.uk")
check("checkout at £99 with a £99 link: what's next says £99 and not £79, and links the £99 link",
      "£99 a year" in nxt99["text"] and "£79" not in nxt99["text"] and "buy.stripe.com/test-99" in nxt99["text"]
      and "fZufZgbse3BpcXE7TY73G01" not in nxt99["text"])
del followup.SUBSCRIBE_URLS[99]
set_price(7900)
price_reads.clear()
for _ in range(3):
    go(fresh_db(), NOV_20, dry_run=True)
check("the price is read from Stripe at most once in six hours", len(price_reads) == 1)
followup._price_cache.update(at=None, gbp=None)

# Buying stops it
db = fresh_db(); sent.clear()
db["purchases"].append({"member_id": "m1", "course_id": "SUBSCRIPTION", "amount_gbp": 79, "stripe_session_id": "cs_live_1b", "purchased_at": iso(NOV_20)})
res = go(db, NOV_20)
check("someone who buys gets nothing more", not any(m["to"][0] == "person1@firm1.co.uk" for m in sent))

# Unsubscribing through the email's link stops it
db = fresh_db(); sent.clear()
main.supabase = client(db)
main._refresh_under_review = lambda: None
c = TestClient(main.app, follow_redirects=False)
r = c.post(f"/unsubscribe?email=person1@firm1.co.uk&token={tok}")
res = go(db, NOV_20)
check("after a one-click unsubscribe the sequence stops", r.status_code == 200 and not any(m["to"][0] == "person1@firm1.co.uk" for m in sent if m["subject"] != "Removed from Meridian CPD emails"))

# A recent outreach email counts towards the gap
db = fresh_db(); sent.clear()
db["outreach_contacts"].append({"id": "c1", "email": "person1@firm1.co.uk"})
db["outreach_sends"].append({"contact_id": "c1", "sent_at": iso(NOV_20 - timedelta(days=5))})
res = go(db, NOV_20)
check("an outreach email five days ago holds the nudge back", not any(m["to"][0] == "person1@firm1.co.uk" for m in sent))

# Lifetime cap
os.environ["FREE_FOLLOWUP_MAX_EMAILS"] = "1"
db = fresh_db(); sent.clear()
db[followup.TABLE].append({"id": "x", "member_id": "m2", "email": "person2@firm2.co.uk", "step": "monthly:old", "status": "delivered", "sent_at": iso(NOV_20 - timedelta(days=90))})
res = go(db, NOV_20)
check("the lifetime cap holds", not any(m["to"][0] == "person2@firm2.co.uk" for m in sent))
os.environ.pop("FREE_FOLLOWUP_MAX_EMAILS")

# Daily limit
os.environ["FREE_FOLLOWUP_DAILY_LIMIT"] = "1"
db = fresh_db(); sent.clear()
res = go(db, NOV_20)
check("the daily limit holds", res["sent"] == 1 and len(sent) == 1)
os.environ.pop("FREE_FOLLOWUP_DAILY_LIMIT")

# A failed send is logged and not retried (it may have gone)
db = fresh_db(); sent.clear()
db["members"][0]["email"] = "person1@down.co.uk"
res = go(db, NOV_20)
check("a failed send is logged as failed", res["failed"] == 1 and any(r["status"] == "failed" and r["step"] == "nudge" for r in db[followup.TABLE]))
res = go(db, NOV_20 + timedelta(days=40))
check("and that step is never retried", not any(r["member_id"] == "m1" and r["step"] == "nudge" and r["status"] == "sent" for r in db[followup.TABLE]))

# Bounces suppress
db = fresh_db(); sent.clear()
go(db, NOV_20)
first = db[followup.TABLE][0]
events[first["resend_id"]] = "bounced"
asyncio.run(followup.poll_delivery(client(db), NOV_20 + timedelta(days=1)))
check("a bounce goes on the suppression list and is marked in the log",
      first["status"] == "bounced" and any(s["email"] == first["email"] and s["reason"] == "bounced" for s in db["outreach_suppressed"]))
res = go(db, DEC_07 + timedelta(days=14))
check("and nothing more goes to that address", not any(m["to"][0] == first["email"] for m in sent[2:]))

# Not outside the window, not by the scheduler when off
check("the send window is weekdays 09:00 to 17:00", followup.in_send_window(NOV_20) and not followup.in_send_window(datetime(2026, 11, 21, 10, 0, tzinfo=UK))
      and not followup.in_send_window(datetime(2026, 11, 20, 8, 59, tzinfo=UK)))

# ── The words ──
BANNED = ["accredited", "approved", "Elmhurst", "Stroma", "Quidos", "ECMK", "Sterling", "NHER", "TrustMark",
          "—", "–", "!", "#", "delve", "unlock", "seamless", "exciting", "guarantee", "the best", "the only"]
texts = followup.previews()
for step, subject, text in texts:
    body = re.sub(r"https?://\S+", "", subject + "\n" + text.split("Kind regards,")[0])  # a '#' in a link is not a hashtag
    check(f"{step}: no banned words, dashes or exclamation marks", not [w for w in BANNED if w.lower() in body.lower()])
    check(f"{step}: ends at 'Kind regards,' then the hello@ signature and the unsubscribe line",
          "Kind regards,\n\n" + outreach.SIGNATURE_TEXT in text and "unsubscribe" in text.lower())
v = {s: t for s, _, t in followup.previews()}
check("every email and both versions of what's next are previewed",
      list(v) == ["nudge", "next (annual £79)", "price"])
followup.SUBSCRIBE_URLS[99] = "https://buy.stripe.com/test-99"
check("a £99 version is previewed only once a £99 link exists",
      [s for s, _, _ in followup.previews()] == ["nudge", "next (annual £79)", "next (annual £99)", "price"])
v["next (annual £99)"] = followup.render_next("Jo", "x", "u", 99)[1]
del followup.SUBSCRIBE_URLS[99]
check("prices are exactly as approved",
      "£39.99" in v["next (annual £79)"] and "£79 a year" in v["next (annual £79)"] and "£99" not in v["next (annual £79)"]
      and "£99 a year" in v["next (annual £99)"] and "£79" not in v["next (annual £99)"]
      and "from £79 to £99 a year on 1 January 2027" in v["price"] and "£99 a year" in v["price"] and "£39.99" in v["price"])
check("the nudge no longer claims a re-download from the completion page or 'straight to your inbox'",
      "download the course again" not in v["nudge"] and "straight to your inbox" not in v["nudge"])
check("the sales emails say the Field Work series are written for England and Wales and to check scheme rules",
      all("written for England and Wales" in v[k] and "check your own scheme's cpd rules" in v[k].lower()
          for k in ("next (annual £79)", "next (annual £99)", "price")))
check("'certificate of completion' is the wording", all("certificate of completion" in t for t in v.values()))
check("no course counts", not any(re.search(r"\b\d+\s+courses\b", t) for t in v.values()))
try:
    followup.render_next("Jo", "x", "u", 89); unknown_ok = False
except ValueError:
    unknown_ok = True
check("there is no text for an annual price other than £79 or £99", unknown_ok)
check("the price-rise email gives the founder rate in the site's words, not 'your first year is £79'",
      "Subscribe before then and you keep £79 for as long as you stay." in v["price"] and "first year" not in v["price"])
os.environ["FREE_FOLLOWUP_PRICE_RISE"] = "on"
on79 = followup.render_next("Jo", "x", "u", 79)[1]
followup.SUBSCRIBE_URLS[99] = "https://buy.stripe.com/test-99"
on99 = followup.render_next("Jo", "x", "u", 99)[1]
del followup.SUBSCRIBE_URLS[99]
check("with FREE_FOLLOWUP_PRICE_RISE on, what's next at £79 carries the January heads-up, and the £99 version does not",
      "£99 a year on 1 January 2027" in on79 and "keep £79" in on79 and "keep £79" not in on99 and "£79" not in on99)
check("and the preview of what's next at £79 shows the heads-up then",
      "keep £79" in {s: t for s, _, t in followup.previews()}["next (annual £79)"])
check("the founder-rate line is word for word where the January price appears",
      followup.FOUNDER_RATE in on79 and followup.FOUNDER_RATE in v["price"]
      and "at every renewal" not in on79 + v["price"] and "One thing to know" not in on79)
check("the founder-rate line is the site's wording, word for word",
      followup.FOUNDER_RATE == "Subscribe before then and you keep £79 for as long as you stay.")
_site = open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "landing-page", "courses.html"), encoding="utf-8").read()
check("and that wording is on the site's subscription card", followup.FOUNDER_RATE in _site)
check("'then' follows a sentence that names 1 January 2027, in both emails that carry it",
      "1 January 2027. " + followup.FOUNDER_RATE in on79 and "1 January 2027. " + followup.FOUNDER_RATE in v["price"])
os.environ.pop("FREE_FOLLOWUP_PRICE_RISE")
off79 = followup.render_next("Jo", "x", "u", 79)[1]
check("with the switch off, what's next at £79 says nothing about £99", "£99" not in off79 and "keep £79" not in off79)


# ── Greeting, sign-in, claims and links (copy round 3, 10 Nov) ──
check("the greeting capitalises the first name", followup.first_name("jo smith") == "Jo"
      and followup.first_name("SAM") == "Sam" and followup.first_name("McDonald") == "McDonald"
      and followup.render_nudge(followup.first_name("jo"), "x", 2, "u")[1].startswith("Hello Jo,\n"))
check("no usable name: the greeting is plain 'Hello,'",
      all(followup.first_name(n) == "" for n in (None, "", "J", "A.", "123"))
      and followup.render("price", {"name": "123"}, {}, "u", NOV_20)[1].startswith("Hello,\n")
      and "Hello there" not in followup.render_nudge("", "x", 2, "u")[1])
check("the nudge says how the live sign-in works (enter the email, a login link is emailed) and sells nothing",
      "enter this email address and we'll email you a login link" in v["nudge"] and "Sign in at the link" not in v["nudge"]
      and "£" not in v["nudge"] and "buy.stripe.com" not in v["nudge"])
check("what's next does not thank people for finishing, and its subject has the price",
      all("Thanks for taking" not in v[k] and "If it was useful" not in v[k] for k in ("next (annual £79)", "next (annual £99)"))
      and followup.render_next("Jo", "x", "u", 79)[0] == "The whole library for £79 a year")
check("new courses are 'added during your year' (register M-LC-6), never 'every new one we add'",
      all("every new course added during your year" in v[k] and "every new one we add" not in v[k]
          for k in ("next (annual £79)", "next (annual £99)", "price")))
check("the filler lines are gone",
      not any(p in t for t in v.values() for p in ("Whichever you choose", "A short note on price", "Both are here")))
_, nt, nh = followup.render_next("Jo", "x", "u", 79)
SUB79 = followup.SUBSCRIBE_URLS[79]
_, pt, ph = followup.render_price("Jo", "u")
check("the annual links to the site's Subscribe link (STRIPE_SUB), in text and HTML",
      SUB79 == "https://buy.stripe.com/fZufZgbse3BpcXE7TY73G01"
      and all(SUB79 in t for t in (nt, nh, pt, ph))
      and "const STRIPE_SUB    = '" + SUB79 + "'" in open(os.path.join(os.path.dirname(__file__), "..", "..", "landing-page", "courses.html")).read())
check("each series links to its own card on courses.html at £39.99",
      all(f"{n}: https://meridiancpd.co.uk/courses.html#fw-{n.lower()}" in t and "£39.99" in t
          for n in ("Insulation", "Heating", "Ventilation", "Moisture") for t in (nt, pt))
      and all(f'href="https://meridiancpd.co.uk/courses.html#fw-{n.lower()}"' in h and f">{n}</a>" in h
              for n in ("Insulation", "Heating", "Ventilation", "Moisture") for h in (nh, ph)))
check("the bare courses page is no longer the destination of a sales email",
      "https://meridiancpd.co.uk/courses.html\n" not in nt and "https://meridiancpd.co.uk/courses.html\n" not in pt)

# ── Admin and the Friday figures ──
db = fresh_db(); sent.clear()
go(db, NOV_20)
db["purchases"].append({"member_id": "m2", "course_id": "SUBSCRIPTION", "amount_gbp": 79, "stripe_session_id": "cs_live_2b", "purchased_at": iso(NOV_20 + timedelta(days=2))})
s = followup.summary(client(db))
check("summary counts sends by email and people who paid afterwards",
      s["steps"]["nudge"]["sent"] == 1 and s["steps"]["next"]["sent"] == 1 and s["people"] == 2 and s["buyers_after"] == 1 and s["revenue_after"] == 79)
main.supabase = client(db)
auth = ("admin", "test-admin")
r = c.get("/admin/followup", auth=auth)
check("Admin → Follow-up shows the switch, the figures and every email", r.status_code == 200 and "Sending" in r.text
      and "The whole library for £79 a year" in r.text and "Paid afterwards" in r.text)
check("Admin → Follow-up needs the password", c.get("/admin/followup").status_code == 401)
sent.clear()
r = c.post("/admin/followup/test", data={"email": "matt@example.org"}, auth=auth)
check("a test copy of each email goes to the address given, marked Test, and is not logged",
      r.status_code == 200 and len(sent) == 3 and all(m["subject"].startswith("Test: ") for m in sent) and len(db[followup.TABLE]) == 2)
r = c.get("/admin/system", auth=auth)
check("System lists the switch", "FREE_FOLLOWUP" in r.text)
broken = types.SimpleNamespace(table=lambda t: (_ for _ in ()).throw(RuntimeError("relation does not exist")) if t == followup.TABLE else Q(db, t))
main.supabase = broken
r = c.get("/admin/followup", auth=auth)
check("Admin → Follow-up still opens before the migration is run, and says so", r.status_code == 200 and "2026-11-06_free_course_followup.sql" in r.text)

print(f"\n{'ALL PASSED' if not fails else f'{fails} FAILED'}")
assert not fails, f"{fails} check(s) failed"
if __name__ == "__main__":
    sys.exit(1 if fails else 0)
