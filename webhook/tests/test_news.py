"""News and insights for the admin sidebar (news.py). Run: python3 tests/test_news.py

What must hold: RSS and Atom both parse; broad government feeds keep only on-topic items;
nothing is stored twice; a watched page gives no item on its first check, one item when it
changes, and at most one a week; a failing source is recorded, not fatal; the sidebar and
the News page render and never break the rest of Admin."""
import asyncio, os, sys, types, base64
from datetime import datetime, timedelta, timezone
os.environ.update(STRIPE_SECRET_KEY="sk_test_x", STRIPE_WEBHOOK_SECRET="whsec_x", SUPABASE_URL="https://example.supabase.co",
                  SUPABASE_SERVICE_ROLE_KEY="eyJhbGciOiJIUzI1NiJ9.eyJyb2xlIjoic2VydmljZV9yb2xlIn0.x",
                  ADMIN_PASSWORD="test-admin", DASHBOARD_SECRET="dash-secret", UNSUBSCRIBE_SECRET="unsub-secret",
                  RESEND_API_KEY="re_x", OUTREACH_SCHEDULER="off", NEWS_SCHEDULER="off")
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
import httpx
import main, news
from fastapi.testclient import TestClient


class Res:
    def __init__(self, data): self.data, self.count = data, len(data)
class Q:
    def __init__(s, db, t): s.db, s.t, s.f, s.op, s.pl, s.ord, s.lim = db, t, [], "select", None, None, None
    def select(s, *a, **k): return s
    def eq(s, c, v): s.f.append(lambda r: r.get(c) == v); return s
    def order(s, c, desc=False): s.ord = (c, desc); return s
    def limit(s, n): s.lim = n; return s
    def insert(s, row): s.op, s.pl = "insert", row; return s
    def update(s, row): s.op, s.pl = "update", row; return s
    @property
    def not_(s): return s
    def __getattr__(s, name):            # other filters the dashboard uses: accept and ignore
        return lambda *a, **k: s
    def execute(s):
        rows = s.db.setdefault(s.t, [])
        if s.op == "insert":
            if s.t == "news_items" and any(r["key"] == s.pl["key"] for r in rows):
                raise RuntimeError("duplicate key")                      # the unique constraint
            row = {"id": f"{s.t}-{len(rows) + 1}", **s.pl}; rows.append(row); return Res([row])
        hit = [r for r in rows if all(f(r) for f in s.f)]
        if s.op == "update":
            for r in hit: r.update(s.pl)
            return Res(hit)
        if s.ord: hit.sort(key=lambda r: r.get(s.ord[0]) or "", reverse=s.ord[1])
        if s.lim is not None: hit = hit[:s.lim]
        return Res(hit)


def client(db):
    return types.SimpleNamespace(table=lambda t: Q(db, t))


passed = 0
def check(cond, msg):
    global passed
    assert cond, msg
    passed += 1


RSS = """<?xml version="1.0"?><rss version="2.0"><channel><title>ecmk</title>
<item><title>Update: Changes to Scottish EPC Register Lodgement Fees</title><link>https://www.ecmk.co.uk/a</link>
<pubDate>Thu, 22 Oct 2026 11:50:13 +0000</pubDate><description>&lt;p&gt;The fee rises on 31 October.&lt;/p&gt;</description></item>
<item><title>Christmas opening hours</title><link>https://www.ecmk.co.uk/b</link><pubDate>Wed, 21 Oct 2026 09:00:00 +0000</pubDate></item>
</channel></rss>"""

ATOM = """<?xml version="1.0" encoding="UTF-8"?><feed xmlns="http://www.w3.org/2005/Atom"><title>DESNZ - Activity on GOV.UK</title>
<entry><title>Home Energy Model: Energy Performance Certificates consultation response</title>
<link rel="alternate" type="text/html" href="https://www.gov.uk/government/consultations/hem-epc"/>
<updated>2026-10-22T09:30:00+01:00</updated><summary>Government response on replacing RdSAP.</summary></entry>
<entry><title>Oil and gas: offshore environmental legislation</title>
<link rel="alternate" href="https://www.gov.uk/guidance/oil-and-gas"/><updated>2026-10-22T08:00:00Z</updated></entry>
</feed>"""


# ── Parsing ──
rss = news.parse_feed(RSS)
check(len(rss) == 2 and rss[0]["url"] == "https://www.ecmk.co.uk/a", "RSS items parsed with links")
check(rss[0]["summary"] == "The fee rises on 31 October.", "RSS description is unescaped and stripped of tags")
check(rss[0]["published"].year == 2026 and rss[0]["published"].tzinfo is not None, "RSS date parsed with a time zone")
atom = news.parse_feed(ATOM)
check(len(atom) == 2 and atom[0]["url"].endswith("/hem-epc"), "Atom entries parsed with alternate links")
check(atom[0]["published"].utcoffset() == timedelta(hours=1), "Atom date keeps its offset")
check(news.parse_feed("<html>not a feed</html>") == [] and news.parse_feed("not xml at all <") == [], "junk gives no items")
check(news.tags_for("Home Energy Model: EPC consultation response") == ["HEM", "EPC"], "topic tags in a fixed order")
check(news.tags_for("Military planes to fight wildfires") == [], "off-topic text gets no tags")
check(news.clean_text("a " * 400, 50).endswith("…") and len(news.clean_text("a " * 400, 50)) <= 51, "summaries are trimmed")

# ── Feeds into storage ──
NOW = datetime(2026, 10, 23, 12, 0, tzinfo=timezone.utc)
db = {}
desnz = next(s for s in news.SOURCES if s["id"] == "desnz")
ecmk = next(s for s in news.SOURCES if s["id"] == "ecmk")
check(news.ingest_feed(client(db), desnz, ATOM, NOW) == 1, "a broad feed keeps only the on-topic entry")
check(db["news_items"][0]["tags"] == ["HEM", "RdSAP", "EPC"] and db["news_items"][0]["source"] == "DESNZ (GOV.UK)",
      "stored with source name and tags")
check(news.ingest_feed(client(db), desnz, ATOM, NOW) == 0, "the same entry is never stored twice")
check(news.ingest_feed(client(db), ecmk, RSS, NOW) == 2, "a scheme feed keeps everything, on topic or not")
check(len(db["news_items"]) == 3, "three items in all")

# ── Watched pages ──
PAGE_A = "<html><title>Standard Assessment Procedure - GOV.UK</title><nav>menu 1</nav><main><p>SAP 10.3 is current. Last updated 8 June 2026</p></main></html>"
PAGE_A_NAV = PAGE_A.replace("menu 1", "menu 2")
PAGE_B = PAGE_A.replace("SAP 10.3 is current. Last updated 8 June 2026", "HEM is approved. Last updated 2 November 2026")
PAGE_C = PAGE_B.replace("HEM is approved", "HEM is approved for new homes")
hem = next(s for s in news.SOURCES if s["id"] == "gov-sap-hem")
pdb = {}
check(news.ingest_page(client(pdb), hem, PAGE_A, NOW) == 0, "first check stores a baseline, no item")
check(news.ingest_page(client(pdb), hem, PAGE_A_NAV, NOW + timedelta(hours=3)) == 0, "a change outside <main> is ignored")
check(news.ingest_page(client(pdb), hem, PAGE_B, NOW + timedelta(hours=6)) == 1, "a change in the page body gives one item")
item = pdb["news_items"][0]
check(item["title"] == "Page updated: Standard Assessment Procedure - GOV.UK" and item["summary"] == "Last updated 2 November 2026",
      "the item names the page and quotes its updated date")
check("HEM" in item["tags"] and "RdSAP" in item["tags"], "page items are tagged too")
check(news.ingest_page(client(pdb), hem, PAGE_C, NOW + timedelta(days=2)) == 0, "a second change within a week gives no item")
PAGE_D = PAGE_C.replace("for new homes", "for new homes and EPCs")
check(news.ingest_page(client(pdb), hem, PAGE_D, NOW + timedelta(days=8)) == 1, "a change after a week gives another")
check(news.ingest_page(client(pdb), hem, PAGE_B, NOW + timedelta(days=20)) == 0, "content already reported is not reported again")
check(news.page_fingerprint(PAGE_A)[1] == news.page_fingerprint(PAGE_A_NAV)[1], "fingerprint ignores navigation")


# ── Checking every source, including failures ──
def handler(request):
    url = str(request.url)
    if "ecmk" in url:
        return httpx.Response(200, text=RSS)
    if "department-for-energy" in url:
        return httpx.Response(200, text=ATOM)
    if "trustmark" in url:
        return httpx.Response(503, text="down")
    if "quidos" in url:
        raise httpx.ConnectError("refused")
    return httpx.Response(200, text="<html><title>t</title><main>body</main></html>" if "gov.uk/guidance" in url or "gov.scot" in url
                          or "seai" in url or "bregroup" in url else "<rss version='2.0'><channel></channel></rss>")
cdb = {}
added = asyncio.run(news.check_all(client(cdb), NOW, transport=httpx.MockTransport(handler)))
check(added["ecmk"] == 2 and added["desnz"] == 1 and added["trustmark-news"] == 0, "check_all adds per source")
state = {r["source_id"]: r for r in cdb["news_sources"]}
check(state["trustmark-news"]["last_error"] == "HTTP 503", "an HTTP error is recorded against the source")
check("refused" in state["quidos"]["last_error"], "a connection error is recorded, the run carries on")
check(state["ecmk"]["last_error"] is None and state["ecmk"]["last_ok"], "a good source is marked OK")
check(len(state) == len(news.SOURCES), "every source has a status row")

# ── Admin ──
main.supabase = client(cdb)
auth = {"Authorization": "Basic " + base64.b64encode(b"admin:test-admin").decode()}
c = TestClient(main.app)
r = c.get("/admin/dashboard", headers=auth)
check(r.status_code == 200 and 'class="newsbar"' in r.text, "the sidebar appears on the dashboard")
check("Update: Changes to Scottish EPC Register Lodgement Fees" in r.text, "sidebar lists the newest items")
check("Christmas opening hours" in r.text and "Oil and gas" not in r.text, "off-topic government items never reach it")
r = c.get("/admin/news", headers=auth)
check(r.status_code == 200 and "Sources" in r.text and "HTTP 503" in r.text, "News page lists sources and their errors")
check('class="newsbar"' not in r.text, "the News page does not repeat the sidebar")
r = c.get("/admin/news?tag=HEM", headers=auth)
check("Home Energy Model" in r.text and "Christmas" not in r.text, "the tag filter works")
first = cdb["news_items"][0]["id"]
r = c.post(f"/admin/news/{first}/read", headers=auth)
check(r.status_code == 200 and cdb["news_items"][0]["read_at"], "mark read")
r = c.post(f"/admin/news/{first}/dismiss", headers=auth)
check(cdb["news_items"][0]["dismissed"] is True, "hide")
check("Home Energy Model" not in c.get("/admin/dashboard", headers=auth).text, "a hidden item leaves the sidebar")
check("Home Energy Model" in c.get("/admin/news?hidden=1", headers=auth).text, "and can still be shown on the News page")
check(c.post("/admin/news/x/delete", headers=auth).status_code == 404, "only read and dismiss are accepted")
check(c.get("/admin/news").status_code == 401, "the News page needs the admin login")
cdb["news_items"].append({"id": "evil", "key": "k", "source": "s", "kind": "feed", "title": "<script>x</script>",
                          "url": "javascript:alert(1)", "published_at": "2026-10-24", "dismissed": False, "tags": []})
cdb["news_items"].append({"id": "esc", "key": "k2", "source": "s", "kind": "feed", "title": "<b>bold</b> & co",
                          "url": "https://example.org/x?a=1&b=2", "published_at": "2026-10-25", "dismissed": False, "tags": []})
t = c.get("/admin/dashboard", headers=auth).text
check("javascript:alert" not in t and "<script>x</script>" not in t, "non-http links are dropped")
check("&lt;b&gt;bold&lt;/b&gt; &amp; co" in t and "a=1&amp;b=2" in t, "titles and links are escaped")

# A broken news table must not break Admin
main.supabase = types.SimpleNamespace(table=lambda t: (_ for _ in ()).throw(RuntimeError("relation news_items does not exist"))
                                      if t.startswith("news") else Q({}, t))
r = c.get("/admin/news", headers=auth)
check(r.status_code == 200 and "migrations/2026-10-23_news.sql" in r.text, "missing tables are explained, not a 500")

print(f"All {passed} news checks passed")
