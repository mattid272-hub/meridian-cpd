"""Member news emails to paying members (member_news.py). Run: python3 tests/test_member_news.py

What must hold: off by default and nothing sent unless switched on; dry-run sends and
writes nothing; only paying members (active subscribers get version A, course and series
buyers with no subscription get version B); never free-course-only members, lapsed
subscribers, test accounts, anyone who said no or anyone suppressed; each edition once per
member; never within 30 days of any other email from us (and the gap cannot be set lower);
held addresses never get the edition; no send unless checkout charges £79 (and £39.99 for
B); the text is word for word the approved text, with the series a buyer holds left out;
every email has a working unsubscribe link and the one-click headers; the daily limit
holds; bounces suppress; the admin page, CSV and hold form work."""
import asyncio, os, sys, types
from datetime import datetime, timedelta
os.environ.update(STRIPE_SECRET_KEY="sk_test_x", STRIPE_WEBHOOK_SECRET="whsec_x", SUPABASE_URL="https://example.supabase.co",
                  SUPABASE_SERVICE_ROLE_KEY="eyJhbGciOiJIUzI1NiJ9.eyJyb2xlIjoic2VydmljZV9yb2xlIn0.x",
                  ADMIN_PASSWORD="test-admin", DASHBOARD_SECRET="dash-secret", UNSUBSCRIBE_SECRET="unsub-secret",
                  RESEND_API_KEY="re_x", OUTREACH_SCHEDULER="off", NEWS_SCHEDULER="off")
for k in ("MEMBER_NEWS", "MEMBER_NEWS_DAILY_LIMIT", "MEMBER_NEWS_MIN_GAP_DAYS", "FREE_FOLLOWUP"):
    os.environ.pop(k, None)
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
import main, member_news, followup, outreach
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
        if s.t not in s.db:
            raise RuntimeError(f"relation {s.t} does not exist")
        rows = s.db[s.t]
        if s.op == "insert":
            if s.t == member_news.TABLE and any(r["member_id"] == s.pl["member_id"] and r["edition"] == s.pl["edition"] for r in rows):
                raise RuntimeError("duplicate key (member_id, edition)")
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


UK = member_news.UK
NOV_20 = datetime(2026, 11, 20, 10, 0, tzinfo=UK)    # a Friday, inside the window
iso = lambda d: d.isoformat()
NAMES = ["", "Alex", "Bryn", "Cara", "Dewi", "Eira", "Ffion", "Gwen", "Huw", "Iolo", "Jac", "Kit", "Lowri", "Mair"]


def member(i, **kw):
    return {"id": f"m{i}", "email": f"person{i}@firm{i}.co.uk", "name": f"{NAMES[i]} Surname", "plan": "single",
            "marketing_consent": True, "stripe_customer_id": f"cus_{i}", "subscription_expires_at": None, **kw}


def buy(i, course, amount, days_ago=20, series_id=None, session=None):
    row = {"member_id": f"m{i}", "course_id": course, "amount_gbp": amount, "stripe_session_id": session or f"cs_live_{i}_{course}",
           "purchased_at": iso(NOV_20 - timedelta(days=days_ago))}
    if series_id:
        row["series_id"] = series_id
    return row


SUB_UNTIL = iso(NOV_20 + timedelta(days=200))
LAPSED = iso(NOV_20 - timedelta(days=20))


def fresh_db():
    return {
        "members": [
            member(1, plan="subscription", subscription_expires_at=SUB_UNTIL),      # subscriber -> A
            member(2),                                                              # bought one course -> B, all four series lines
            member(3),                                                              # bought Insulation series -> B without Insulation
            member(4),                                                              # free course only -> never
            member(5, plan="subscription", subscription_expires_at=LAPSED),         # lapsed -> never (win-back)
            member(6, marketing_consent=False),                                     # bought, said no -> never
            member(7),                                                              # bought, unsubscribed -> never
            member(8, email="hello+t1@meridiancpd.co.uk"),                          # Matt's test order -> never
            member(9, stripe_customer_id="cus_test", plan="subscription"),          # test subscriber -> never
            member(10),                                                             # only a cs_test_ purchase -> never
            member(11, marketing_consent=None),                                     # bought, never answered -> B
            member(12, plan="subscription", subscription_expires_at=SUB_UNTIL, name=""),  # subscriber, no name -> A "Hello,"
            member(13),                                                             # holds all four series -> B, no series lines
        ],
        "purchases": [
            buy(1, "SUBSCRIPTION", 79, 100),
            buy(2, "MER-DEA-001", 0, 60), buy(2, "MER-ALL-001", 19.99, 30),
            *[buy(3, c, 13.33, 10, "FW-INSULATION", "cs_live_3s") for c in main.SERIES["FW-INSULATION"]["courses"]],
            buy(4, "MER-DEA-001", 0, 30),
            buy(5, "SUBSCRIPTION", 79, 400),
            buy(6, "MER-ALL-001", 19.99, 30),
            buy(7, "MER-ALL-001", 19.99, 30),
            buy(8, "MER-ALL-001", 19.99, 30),
            buy(9, "SUBSCRIPTION", 79, 30),
            buy(10, "MER-ALL-001", 19.99, 30, session="cs_test_10"),
            buy(11, "MER-DEA-002", 19.99, 30),
            buy(12, "SUBSCRIPTION", 79, 50),
            *[buy(13, c, 13.33, 40, sid, f"cs_live_13_{sid}") for sid in main.SERIES for c in main.SERIES[sid]["courses"]],
        ],
        "outreach_suppressed": [{"id": "s1", "email": "person7@firm7.co.uk", "reason": "unsubscribed"}],
        "outreach_contacts": [], "outreach_sends": [],
        followup.TABLE: [],
        member_news.TABLE: [],
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
member_news.httpx.AsyncClient = FakeHTTP
main.httpx.AsyncClient = FakeHTTP
member_news.PACE_SECONDS = 0


def set_prices(annual_pence, series_pence):
    followup._fetch_annual_pence = lambda: annual_pence
    followup._price_cache.update(at=None, gbp=None)
    member_news._fetch_series_pence = lambda: series_pence
    member_news._series_cache.update(at=None, pence=None)
set_prices(7900, 3999)

fails = 0
def check(name, cond):
    global fails
    print(("PASS " if cond else "FAIL ") + name)
    fails += 0 if cond else 1

go = lambda db, now=NOV_20, **kw: asyncio.run(member_news.run(client(db), now, main.COURSES, main.SERIES, **kw))
who = lambda res: sorted((w["member_id"], w["version"]) for w in res["would_send"])
EXPECTED = [("m1", "A"), ("m11", "B"), ("m12", "A"), ("m13", "B"), ("m2", "B"), ("m3", "B")]

# ── The switch ──
check("the switch defaults to off", member_news.mode() == "off")
db = fresh_db(); sent.clear()
res = go(db, dry_run=False)
check("switched off: a real pass sends nothing and writes nothing", res["sent"] == 0 and not sent and not db[member_news.TABLE] and res["note"] == "switched off")
os.environ["MEMBER_NEWS"] = "yes please"
check("an unknown value counts as off", member_news.mode() == "off")
check("the scheduler is not started while off", "member_news.scheduler_loop" in open(main.__file__).read())

# ── Dry run ──
os.environ["MEMBER_NEWS"] = "dry_run"
db = fresh_db(); sent.clear()
res = go(db)
check("dry run: subscribers get A, course and series buyers get B, nobody else", who(res) == EXPECTED)
check("dry run sends nothing and writes nothing", not sent and not db[member_news.TABLE])
check("dry run says why the rest are not due",
      res["skipped"].get("said no to marketing") == 1 and res["skipped"].get("on suppression list") == 1
      and res["skipped"].get("lapsed subscriber (win-back, not this email)") == 1)
check("free-course-only members and test accounts are not counted as paying", res["paying"] == 7)
check("no edition is open before 16 November or from 1 January 2027",
      go(fresh_db(), datetime(2026, 11, 13, 10, tzinfo=UK))["note"] == "no edition open"
      and go(fresh_db(), datetime(2027, 1, 4, 10, tzinfo=UK))["note"] == "no edition open")

# ── Prices ──
set_prices(9900, 3999)
res = go(fresh_db())
check("annual not £79 at checkout: nothing goes", not res["would_send"] and res["skipped"].get("annual price at checkout is not £79") == 6)
set_prices(None, 3999)
check("annual price unreadable: nothing goes", not go(fresh_db())["would_send"])
set_prices(7900, 4999)
res = go(fresh_db())
check("series not £39.99: only subscribers, and a buyer who holds all four series, get it",
      who(res) == [("m1", "A"), ("m12", "A"), ("m13", "B")])
set_prices(7900, 3999)

# ── Sending ──
os.environ["MEMBER_NEWS"] = "on"
db = fresh_db(); sent.clear()
res = go(db)
check("on: sends the six due emails and logs each with Resend's id",
      res["sent"] == 6 and len(sent) == 6 and len(db[member_news.TABLE]) == 6
      and all(r["status"] == "sent" and r["resend_id"].startswith("msg-") and r["edition"] == "2026-11-thank-you" for r in db[member_news.TABLE]))
by = {m["to"][0]: m for m in sent}
a, a_noname = by["person1@firm1.co.uk"], by["person12@firm12.co.uk"]
b_course, b_series, b_all = by["person2@firm2.co.uk"], by["person3@firm3.co.uk"], by["person13@firm13.co.uk"]

body = lambda m: m["text"].split("\n\n" + outreach.SIGNATURE_TEXT)[0]
A_TEXT = """Hello Alex,

Thank you for being a Meridian member. Your library is here: https://app.meridiancpd.co.uk/my-cpd

We have rebuilt it so things are quicker to find. Courses sit in rows by topic, with Continue where you left off first and a search box at the top. Mark a course as a favourite or save it to read later and it gets its own row.

The four Field Work series are in your library under Your series: Insulation, Heating, Ventilation and Moisture. Each is three linked courses on one subject, written for England and Wales, with a certificate of completion for each part. They are included in your membership.

My certificates holds every certificate you have earned with us. Download CPD record (PDF) gives you a year's record in one file.

The annual price goes up to £99 on 1 January 2027. Yours stays at £79 for as long as you stay.

If anything is not where you expect it, reply to this email.

Your library: https://app.meridiancpd.co.uk/my-cpd

Kind regards,"""
B_TEXT = """Hello Bryn,

Thank you for buying {title}. The annual membership covers all four Field Work series and every other course in the library, for £79 a year: https://buy.stripe.com/fZufZgbse3BpcXE7TY73G01

It goes up to £99 a year on 1 January 2027. Subscribe before then and you keep £79 for as long as you stay.

A Field Work series is three linked courses on one subject for £39.99, written for England and Wales, with a certificate of completion for each part.

Insulation: https://meridiancpd.co.uk/courses.html#fw-insulation

Heating: https://meridiancpd.co.uk/courses.html#fw-heating

Ventilation: https://meridiancpd.co.uk/courses.html#fw-ventilation

Moisture: https://meridiancpd.co.uk/courses.html#fw-moisture

We have also rebuilt My CPD. Your courses sit in rows by topic with a search box at the top, and My certificates holds every certificate you have earned, with a year's CPD record as one PDF: https://app.meridiancpd.co.uk/my-cpd

Check your own scheme's CPD rules for what counts towards your hours.

Annual membership, £79 a year: https://buy.stripe.com/fZufZgbse3BpcXE7TY73G01

Kind regards,"""
check("version A is the approved text word for word, subject included",
      body(a) == A_TEXT and a["subject"] == "Thank you, and what's new in your library")
check("no name: the greeting is plain 'Hello,'", body(a_noname).startswith("Hello,\n\n"))
course_title = main.COURSES["MER-ALL-001"]["title"]
check("version B is the approved text word for word, with the course they bought",
      body(b_course) == B_TEXT.format(title=course_title) and b_course["subject"] == "Thank you, and what's new at Meridian")
check("a series buyer is thanked for the series and its own line is left out, nothing else changes",
      body(b_series) == B_TEXT.format(title="Field Work: Insulation").replace(
          "Bryn", "Cara").replace("Insulation: https://meridiancpd.co.uk/courses.html#fw-insulation\n\n", ""))
check("a buyer holding all four series gets no series sentence and no series lines",
      "A Field Work series is" not in b_all["text"] and "#fw-" not in b_all["text"] and "£79 a year" in b_all["text"])
check("the body ends at 'Kind regards,' and the hello@ signature follows",
      all(m["text"].split("Kind regards,\n\n", 1)[1].startswith(outreach.SIGNATURE_TEXT) for m in sent))
check("no referral paragraph until the refer-a-colleague scheme is live", not any("colleague" in m["text"] for m in sent))
unsub = a["headers"]["List-Unsubscribe"].split(", <")[1].rstrip(">")
tok = unsub.rsplit("token=", 1)[1]
check("every email has the member footer, a working unsubscribe link and the one-click headers",
      all(m["headers"]["List-Unsubscribe-Post"] == "List-Unsubscribe=One-Click" and "/unsubscribe?email=" in m["text"]
          and "You're getting this because you are a Meridian CPD member. If you'd rather not hear from us:" in m["text"]
          and "unsubscribe</a>" in m["html"] for m in sent)
      and main._verify_unsubscribe_token("person1@firm1.co.uk", tok))
check("HTML links are full https links", 'href="https://buy.stripe.com/fZufZgbse3BpcXE7TY73G01"' in b_course["html"]
      and 'href="https://app.meridiancpd.co.uk/my-cpd"' in a["html"])
check("emails are tagged member-news in Resend", all(m["tags"] == [{"name": "campaign", "value": "member-news"}] for m in sent))

sent.clear()
res = go(db, NOV_20 + timedelta(days=40))
check("each edition goes to a member once, ever", res["sent"] == 0 and not sent
      and res["skipped"].get("already has this edition (or held)") == 6)

# ── The 30-day gap ──
db = fresh_db(); sent.clear()
db[followup.TABLE].append({"member_id": "m2", "email": "person2@firm2.co.uk", "step": "next", "status": "sent", "sent_at": iso(NOV_20 - timedelta(days=10))})
db["outreach_contacts"].append({"id": "c1", "email": "person3@firm3.co.uk"})
db["outreach_sends"].append({"contact_id": "c1", "sent_at": iso(NOV_20 - timedelta(days=29))})
db["outreach_contacts"].append({"id": "c2", "email": "person11@firm11.co.uk"})
db["outreach_sends"].append({"contact_id": "c2", "sent_at": iso(NOV_20 - timedelta(days=31))})
os.environ["MEMBER_NEWS"] = "dry_run"
res = go(db)
check("not within 30 days of a follow-up or outreach email; fine after 30",
      ("m2", "B") not in who(res) and ("m3", "B") not in who(res) and ("m11", "B") in who(res)
      and res["skipped"].get("too soon after the last email") == 2)
os.environ["MEMBER_NEWS_MIN_GAP_DAYS"] = "7"
check("the gap cannot be set below 30 days", member_news.min_gap_days() == 30)
os.environ["MEMBER_NEWS_MIN_GAP_DAYS"] = "45"
check("the gap can be set longer", member_news.min_gap_days() == 45)
os.environ.pop("MEMBER_NEWS_MIN_GAP_DAYS")

# ── Holding an address (one the HQ send guard blocked) ──
db = fresh_db()
held, missing = member_news.hold(client(db), ["Person2@firm2.co.uk", "nobody@nowhere.co.uk"], NOV_20)
res = go(db)
check("a held member never gets the edition, and an unknown address is reported", held == 1 and missing == 1
      and ("m2", "B") not in who(res) and db[member_news.TABLE][0]["status"] == "held")
check("a held row is not a send: it does not start a 30-day gap or count towards the daily limit",
      member_news.sent_today(client(db), NOV_20) == 0)

# ── Daily limit, window, failures ──
os.environ["MEMBER_NEWS"] = "on"
os.environ["MEMBER_NEWS_DAILY_LIMIT"] = "2"
db = fresh_db(); sent.clear()
check("the daily limit holds", go(db)["sent"] == 2 and go(db)["sent"] == 0)
os.environ.pop("MEMBER_NEWS_DAILY_LIMIT")
check("sends only on weekdays 09:00 to 17:00 UK",
      member_news.in_send_window(NOV_20) and not member_news.in_send_window(datetime(2026, 11, 21, 10, tzinfo=UK))
      and not member_news.in_send_window(datetime(2026, 11, 20, 17, 30, tzinfo=UK)))
db = fresh_db(); sent.clear()
db["members"][0]["email"] = "person1@down.co.uk"
res = go(db)
check("a failed send is recorded and never retried", res["failed"] == 1
      and any(r["status"] == "failed" for r in db[member_news.TABLE])
      and go(db, NOV_20 + timedelta(days=40))["sent"] == 0)

# ── Bounces ──
db = fresh_db(); sent.clear(); go(db)
first = db[member_news.TABLE][0]
events[first["resend_id"]] = "bounced"
b, c = asyncio.run(member_news.poll_delivery(client(db), NOV_20 + timedelta(days=1)))
check("a bounce suppresses the address", b == 1 and outreach.is_suppressed(client(db), first["email"]))

# ── Admin ──
os.environ["MEMBER_NEWS"] = "dry_run"
db = fresh_db()
main.supabase = client(db)
real_now = member_news.datetime
class FixedNow(datetime):
    @classmethod
    def now(cls, tz=None): return NOV_20
main.datetime = FixedNow
tc = TestClient(main.app)
auth = ("admin", "test-admin")
r = tc.get("/admin/member-news", auth=auth)
check("Admin → Member news opens and shows the edition, both previews and the switch",
      r.status_code == 200 and "2026-11-thank-you" in r.text and "Thank you, and what&#x27;s new in your library" in r.text
      and "MEMBER_NEWS" in r.text and "Dry run" in r.text)
check("Admin → Member news needs the admin password", tc.get("/admin/member-news").status_code == 401)
r = tc.get("/admin/member-news/list.csv", auth=auth)
check("the CSV lists who is due, with the HQ purpose", r.status_code == 200
      and r.text.splitlines()[0] == "email,edition,version,hq_purpose"
      and "person1@firm1.co.uk,2026-11-thank-you,A,announcement" in r.text and len(r.text.splitlines()) == 7)
r = tc.post("/admin/member-news/hold", data={"emails": "person1@firm1.co.uk\nperson2@firm2.co.uk"}, auth=auth)
check("the hold form holds addresses for this edition", r.status_code == 200 and "2 held" in r.text
      and len(tc.get("/admin/member-news/list.csv", auth=auth).text.splitlines()) == 5)
sent.clear()
r = tc.post("/admin/member-news/test", data={"email": "matt@firm.co.uk"}, auth=auth)
check("a test copy of each version goes to the address given and nothing is recorded",
      r.status_code == 200 and len(sent) == 2 and all(m["subject"].startswith("Test: ") for m in sent)
      and all(row["status"] == "held" for row in db[member_news.TABLE]))
del db[member_news.TABLE]
r = tc.get("/admin/member-news", auth=auth)
check("Admin → Member news still opens before the migration is run, and says so",
      r.status_code == 200 and "2026-11-16_member_news.sql" in r.text)
r = tc.get("/admin/system", auth=auth)
check("Admin → System lists the member news variables", r.status_code == 200 and "MEMBER_NEWS_DAILY_LIMIT" in r.text)
main.datetime = real_now

print()
print("ALL PASSED" if not fails else f"{fails} FAILED")
if fails:
    raise SystemExit(1)
