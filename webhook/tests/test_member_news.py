"""News and insights on My CPD. Run: python3 tests/test_member_news.py

What must hold: nothing reaches a member unless an admin has switched it on; an item from a
scheme or lodging-software company, one that names them, a watched-page notice and anything
dated in the future never reach a member even if switched on; the member panel shows title,
source, date and the source link and none of the admin actions (Mark read, Hide, Copy as
post, the switch); before the migration is run (no member_visible column) members see no
panel and the dashboard still works; the admin switch is admin-only, off by default, and
refuses an item the rule keeps out."""
import base64, os, sys, types
from datetime import datetime, timezone
os.environ.update(STRIPE_SECRET_KEY="sk_test_x", STRIPE_WEBHOOK_SECRET="whsec_x", SUPABASE_URL="https://example.supabase.co",
                  SUPABASE_SERVICE_ROLE_KEY="eyJhbGciOiJIUzI1NiJ9.eyJyb2xlIjoic2VydmljZV9yb2xlIn0.x", SESSION_SECRET="s",
                  ADMIN_PASSWORD="test-admin", DASHBOARD_SECRET="dash-secret-for-tests", UNSUBSCRIBE_SECRET="u",
                  OUTREACH_SCHEDULER="off", NEWS_SCHEDULER="off")
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
import main, news
from fastapi.testclient import TestClient


class Res:
    def __init__(self, data): self.data, self.count = data, len(data)
class Q:
    """A stand-in for the Supabase table client. With db["_no_column"] set, any filter or
    update on member_visible fails the way PostgREST does before the migration."""
    def __init__(s, db, t): s.db, s.t, s.f, s.op, s.pl, s.o, s.lim = db, t, [], "select", None, None, None
    def _col(s, c):
        if s.t == "news_items" and c.startswith("member_") and s.db.get("_no_column"):
            raise RuntimeError("column news_items.member_visible does not exist")
    def select(s, *a, **k): return s
    def eq(s, c, v): s._col(c); s.f.append(lambda r, c=c, v=v: r.get(c) == v); return s
    def in_(s, c, v): s.f.append(lambda r, c=c, v=v: r.get(c) in v); return s
    def order(s, c, desc=False, **k): s.o = (c, desc); return s
    def limit(s, n, *a): s.lim = n; return s
    @property
    def not_(s): return s
    def __getattr__(s, name): return lambda *a, **k: s
    def insert(s, row): s.op, s.pl = "insert", row; return s
    def update(s, row):
        for c in row: s._col(c)
        s.op, s.pl = "update", row; return s
    def execute(s):
        rows = s.db.setdefault(s.t, [])
        if s.op == "insert":
            row = dict(s.pl); row.setdefault("id", f"{s.t}-{len(rows) + 1}"); rows.append(row); return Res([row])
        hit = [r for r in rows if all(f(r) for f in s.f)]
        if s.op == "update":
            [r.update(s.pl) for r in hit]
        if s.o: hit = sorted(hit, key=lambda r: str(r.get(s.o[0]) or ""), reverse=s.o[1])
        if s.lim is not None: hit = hit[:s.lim]
        return Res(hit)


fails = 0
def check(name, cond):
    global fails
    print(("PASS " if cond else "FAIL ") + name)
    fails += 0 if cond else 1


NOW = datetime(2026, 11, 24, 9, 0, tzinfo=timezone.utc)
item = lambda iid, title, source="DESNZ (GOV.UK)", url=None, kind="feed", when="2026-11-20T10:00:00+00:00", on=True, **k: {
    "id": iid, "key": iid, "title": title, "source": source, "kind": kind, "url": url or f"https://www.gov.uk/government/news/{iid}",
    "published_at": when, "summary": k.pop("summary", ""), "tags": ["EPC"], "dismissed": k.pop("dismissed", False),
    "member_visible": on, **k}

# ── 1. The rule ──
R = lambda it: news.member_block_reason(it, NOW)
check("a government item on topic, dated today or before, passes", R(item("ok", "Energy Performance Certificates: guidance updated")) == "")
check("a scheme or software company's feed is kept out", all(R(item(f"s{n}", "Opening hours", source=name)) for n, name in
      enumerate(["ECMK", "Elmhurst Energy", "Quidos", "TrustMark news"])))
check("an item naming lodging software or a scheme is kept out, whoever published it",
      R(item("n1", "ECMK launches new RdSAP 10 software")) and R(item("n2", "Stroma and Elmhurst merge"))
      and R(item("n3", "New lodgement software version released")) and R(item("n4", "Update", summary="Accreditation schemes must report by March")))
check("an 'Approved Document' title is not caught by the scheme rule", R(item("ad", "Approved Document L: 2026 edition")) == "")
check("a GOV.UK statistics release notice is kept out",
      R(item("st", "Household energy efficiency statistics", url="https://www.gov.uk/government/statistics/announcements/hees-dec")))
check("a title naming a month still to come is kept out (SHDF statistics: May 2027)",
      R(item("f1", "Social Housing Decarbonisation Fund statistics: May 2027")) and R(item("f2", "Statistics release: 3 December 2026")))
check("a title naming a past month or an earlier day this month passes",
      R(item("p1", "EPC statistics: October 2026")) == "" and R(item("p2", "Guidance published 2 November 2026")) == "")
check("an item published after today is kept out", R(item("fut", "EPC guidance", when="2026-12-01T09:00:00+00:00")))
check("a watched-page 'Page updated' notice is kept out", R(item("pg", "Page updated: SAP", kind="page")))
check("a non-https link is kept out", R(item("h", "EPC guidance", url="http://example.org/x")) and R(item("j", "x", url="javascript:alert(1)")))

# ── 2. Member feed ──
db = {
    "members": [{"id": "m1", "email": "sub@example.com", "name": "Sue Sub", "plan": "subscription",
                 "stripe_customer_id": "cus_s", "joined_at": "2026-01-05T10:00:00+00:00"}],
    "news_items": [
        item("a1", "Energy Performance Certificates: guidance updated", when="2026-11-20T10:00:00+00:00"),
        item("a2", "Home Energy Model: consultation response <published>", when="2026-11-18T10:00:00+00:00"),
        item("off", "Retrofit guidance not switched on", on=False, when="2026-11-22T10:00:00+00:00"),
        item("nul", "An item from before the migration", on=None, when="2026-11-22T10:00:00+00:00"),
        item("hid", "A switched-on item later hidden", dismissed=True),
        item("ecmk", "ECMK software launch", source="ECMK", url="https://www.ecmk.co.uk/launch"),
        item("shdf", "Social Housing Decarbonisation Fund statistics: May 2099"),
        item("pgu", "Page updated: BRE SAP 10", kind="page", url="https://bregroup.com/x"),
    ],
}
main.supabase = types.SimpleNamespace(table=lambda t: Q(db, t),
    storage=types.SimpleNamespace(from_=lambda b: types.SimpleNamespace(download=lambda f: (_ for _ in ()).throw(RuntimeError("no catalogue")))))
main._refresh_under_review = lambda: None
main.subscription_active = lambda m: m.get("plan") == "subscription"
got = [i["id"] for i in news.member_items(main.supabase, now=NOW)]
check("members get only switched-on items that pass the rule, newest first", got == ["a1", "a2"])
db["news_items"] += [item(f"x{n}", f"EPC note {n}", when=f"2026-11-0{n}T10:00:00+00:00") for n in range(1, 8)]
check(f"at most {news.MEMBER_LIMIT} items", len(news.member_items(main.supabase, now=NOW)) == news.MEMBER_LIMIT)
db["news_items"] = db["news_items"][:8]

c = TestClient(main.app, follow_redirects=False)
SUE = {"session_token": main._make_session_token("sub@example.com")}
r = c.get("/my-cpd/dashboard", cookies=SUE); t = r.text
panel = t.split('class="row news-panel"', 1)[1].split("</section>", 1)[0] if 'class="row news-panel"' in t else ""
check("the dashboard shows the News and insights panel", r.status_code == 200 and "<h2 id=\"newsHead\">News and insights</h2>" in panel)
check("each item: title, source, date and the source link (opening in a new tab)",
      "Energy Performance Certificates: guidance updated" in panel and "DESNZ (GOV.UK)" in panel and "20 Nov 2026" in panel
      and 'href="https://www.gov.uk/government/news/a1" target="_blank" rel="noopener">Source ↗</a>' in panel)
check("titles are escaped", "consultation response &lt;published&gt;" in panel and "<published>" not in panel)
check("nothing not switched on, hidden, or kept out by the rule",
      not any(s in t for s in ["not switched on", "before the migration", "later hidden", "ECMK", "May 2099", "Page updated"]))
check("none of the admin actions reach a member",
      not any(s in t for s in ["Mark read", "Hide</a>", "Copy as post", "newsAct", "newsShare", "Show to members", "/admin/news"]))

# ── 3. Before the migration: no column, no panel, dashboard fine ──
db["_no_column"] = True
check("no member_visible column: the feed is empty", news.member_items(main.supabase, now=NOW) == [])
r = c.get("/my-cpd/dashboard", cookies=SUE)
check("no member_visible column: the dashboard loads with no news panel", r.status_code == 200 and 'class="row news-panel"' not in r.text
      and "News and insights" not in r.text and "Your series" in r.text)
auth = {"Authorization": "Basic " + base64.b64encode(b"admin:test-admin").decode()}
r = c.post("/admin/news/off/members", headers=auth)
check("no member_visible column: the admin switch says to run the migration", r.status_code == 409
      and "2026-11-24_news_for_members.sql" in r.json()["error"])
db["_no_column"] = False

# Nothing switched on: no panel either
saved = [dict(i) for i in db["news_items"]]
for i in db["news_items"]: i["member_visible"] = False
check("nothing switched on: no panel", 'class="row news-panel"' not in c.get("/my-cpd/dashboard", cookies=SUE).text)
db["news_items"] = saved

# ── 4. The admin switch ──
check("the switch needs the admin login", c.post("/admin/news/off/members").status_code == 401
      and c.post("/admin/news/a1/withdraw").status_code == 401)
r = c.get("/admin/news", headers=auth); t = r.text
check("Admin → News: an item not switched on offers Show to members",
      "Not shown to members" in t and "newsShare('off', true, this)" in t)
check("Admin → News: a switched-on item says so and can be withdrawn", "Shown to members" in t and "newsShare('a1', false, this)" in t)
check("Admin → News: a kept-out item says why and has no switch",
      "Kept from members: from a scheme or software company" in t and "newsShare('ecmk'" not in t
      and "Kept from members: a notice of something still to come" in t and "newsShare('shdf'" not in t)
check("the admin sidebar carries the switch too", "news-share" in c.get("/admin/dashboard", headers=auth).text)
r = c.post("/admin/news/off/members", headers=auth)
off = next(i for i in db["news_items"] if i["id"] == "off")
check("Show to members switches it on and records when", r.status_code == 200 and off["member_visible"] is True
      and off.get("member_approved_at") and "Shown to members" in r.json()["html"])
check("and it reaches members", "Retrofit guidance not switched on" in c.get("/my-cpd/dashboard", cookies=SUE).text)
r = c.post("/admin/news/off/withdraw", headers=auth)
check("Withdraw switches it off", r.status_code == 200 and off["member_visible"] is False and off.get("member_approved_at") is None
      and "Retrofit guidance not switched on" not in c.get("/my-cpd/dashboard", cookies=SUE).text)
ecmk = next(i for i in db["news_items"] if i["id"] == "ecmk"); ecmk["member_visible"] = False
r = c.post("/admin/news/ecmk/members", headers=auth)
check("an item the rule keeps out cannot be switched on", r.status_code == 409 and ecmk["member_visible"] is False
      and "scheme or software company" in r.json()["error"])
check("an unknown item is a 404", c.post("/admin/news/nope/members", headers=auth).status_code == 404)
check("other actions are still refused", c.post("/admin/news/a1/delete", headers=auth).status_code == 404)

# ── 5. Words on the member panel ──
import re
check("no 'accredited' or 'approved' in the member panel", not re.search(r"accredit|approved", panel, re.I))

print(f"\n{'All passed' if not fails else f'{fails} FAILED'}")
assert not fails
