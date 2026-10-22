"""Mail link checkers (Outlook Safe Links and others) check links with HEAD and open them by
themselves. Links in our emails must pass those checks and must never record a choice just
by being opened. Run: python3 tests/test_link_checkers.py"""
import asyncio, base64, hashlib, hmac, os, sys, time, types
os.environ.update(STRIPE_SECRET_KEY="sk_test_x", STRIPE_WEBHOOK_SECRET="whsec_x", SUPABASE_URL="https://example.supabase.co",
                  SUPABASE_SERVICE_ROLE_KEY="eyJhbGciOiJIUzI1NiJ9.eyJyb2xlIjoic2VydmljZV9yb2xlIn0.x",
                  ADMIN_PASSWORD="test-admin", DASHBOARD_SECRET="dash-secret", UNSUBSCRIBE_SECRET="unsub-secret",
                  RESEND_API_KEY="re_x")
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
import main, email_sender
from fastapi.testclient import TestClient


class Res:
    def __init__(self, data): self.data, self.count = data, len(data)
class Q:
    def __init__(s, db, t): s.db, s.t, s.f, s.op, s.pl = db, t, [], "select", None
    def select(s, *a, **k): return s
    def eq(s, c, v): s.f.append(lambda r, c=c, v=v: r.get(c) == v); return s
    def order(s, *a, **k): return s
    def limit(s, *a): return s
    def is_(s, c, _n): s.f.append(lambda r: r.get(c) is None); return s
    def insert(s, row): s.op, s.pl = "insert", row; return s
    def upsert(s, row): s.op, s.pl = "insert", row; return s
    def update(s, row): s.op, s.pl = "update", row; return s
    def execute(s):
        rows = s.db.setdefault(s.t, [])
        if s.op == "insert":
            row = dict(s.pl); rows.append(row); return Res([row])
        hit = [r for r in rows if all(f(r) for f in s.f)]
        if s.op == "update": [r.update(s.pl) for r in hit]
        return Res(hit)


db = {"members": [{"id": "7b0c5a8e-1111-4222-8333-944455556666", "email": "jo@firm.co.uk", "name": "Jo",
                   "plan": "single", "marketing_consent": None}],
      "outreach_contacts": [{"email": "lead@firm.co.uk", "suppressed": False}], "outreach_suppressed": []}
main.supabase = types.SimpleNamespace(table=lambda t: Q(db, t))
main._refresh_under_review = lambda: None
sent = []
class FakeHTTP:
    def __init__(s, **k): pass
    async def __aenter__(s): return s
    async def __aexit__(s, *a): return False
    async def post(s, url, headers=None, json=None, timeout=None):
        sent.append(json); return types.SimpleNamespace(status_code=200, raise_for_status=lambda: None)
main.httpx.AsyncClient = FakeHTTP
email_sender.httpx.AsyncClient = FakeHTTP

c = TestClient(main.app, follow_redirects=False)
fails = 0
def check(name, cond):
    global fails
    print(("PASS " if cond else "FAIL ") + name)
    fails += 0 if cond else 1
jo = db["members"][0]

# ── HEAD requests ──
for path in ["/my-cpd", "/verify", "/health"]:
    r = c.head(path)
    check(f"HEAD {path} answers like GET, without a body", r.status_code == c.get(path).status_code and r.content == b"")
r = c.head("/no-such-page")
check("HEAD on a missing page is still 404", r.status_code == 404)
tok = hmac.new(b"unsub-secret", b"lead@firm.co.uk", hashlib.sha256).hexdigest()[:16]
r = c.head(f"/unsubscribe?email=lead@firm.co.uk&token={tok}")
check("HEAD on an unsubscribe link changes nothing", r.status_code == 200 and not db["outreach_suppressed"]
      and db["outreach_contacts"][0]["suppressed"] is False)

# ── Sign-in link ──
sent.clear()
r = c.post("/my-cpd/send-link", data={"email": "jo@firm.co.uk"})
mail = sent[-1]
url = mail["text"].split("\n\n")[2]
token = url.rsplit("/", 1)[-1]
check("sign-in email has a plain-text version", "It works for 1 hour" in mail["text"])
check("sign-in link does not contain the email address, plain or encoded",
      "jo@firm.co.uk" not in url and base64.urlsafe_b64encode(b"jo@firm.co.uk")[:12].decode() not in url)
check("sign-in link is short", len(url) < 130)
check("HTML version also shows the link to copy", mail["html"].count(url) == 3)
r = c.head(url.replace(main.BASE_URL, ""))
check("HEAD on the sign-in link passes the check", r.status_code == 302 and r.content == b"")
r = c.get(url.replace(main.BASE_URL, ""))
cookie = (r.cookies.get("session_token") or "").strip('"')
check("sign-in link signs the member in", r.status_code == 302 and r.headers["location"] == "/my-cpd/dashboard"
      and main._verify_session_token(cookie) == "jo@firm.co.uk")
r = c.get(url.replace(main.BASE_URL, ""))
check("sign-in link still works after a link checker has opened it", r.status_code == 302
      and r.headers["location"] == "/my-cpd/dashboard")
mid, exp, sig = token.split(".")
r = c.get(f"/my-cpd/login/{mid}.{exp}.{'0' * 32}")
check("tampered sign-in link refused", r.headers["location"] == "/my-cpd?msg=invalid")
old = int(time.time()) - 10
r = c.get(f"/my-cpd/login/{mid}.{old}.{main._login_sig(mid, old)}")
check("expired sign-in link refused", r.headers["location"] == "/my-cpd?msg=invalid")
r = c.get(f"/my-cpd/login/00000000-0000-4000-8000-000000000000.{exp}.{main._login_sig('00000000-0000-4000-8000-000000000000', int(exp))}")
check("link for a member that doesn't exist refused", r.headers["location"] == "/my-cpd?msg=invalid")
e = int(time.time()) + 600
legacy_sig = hmac.new(b"dash-secret", f"jo@firm.co.uk:{e}".encode(), hashlib.sha256).hexdigest()
legacy = base64.urlsafe_b64encode(f"jo@firm.co.uk:{e}:{legacy_sig}".encode()).decode()
r = c.get(f"/my-cpd/login/{legacy}")
check("links sent before the change still work", r.headers["location"] == "/my-cpd/dashboard")

# ── Marketing consent ──
sent.clear()
asyncio.run(email_sender.send_course_email(to_email="jo@firm.co.uk", to_name="Jo", course_title="x", course_id="SUBSCRIPTION",
                                           pdf_url=None, completion_link=None, is_subscription=True))
body = sent[-1]["text"]
yes_link = next(l for l in body.splitlines() if "/consent/yes?" in l).split("→ ")[1].strip()
check("welcome email's consent links are signed", "token=" in yes_link)
path = yes_link.replace(main.BASE_URL, "")
for method in ("HEAD", "GET"):
    r = c.request(method, path)
    check(f"{method} on the consent link records nothing", r.status_code == 200 and jo["marketing_consent"] is None)
check("the consent page asks with buttons", "Yes, keep me in the loop" in c.get(path).text and 'method="post"' in c.get(path).text)
q = dict(p.split("=", 1) for p in path.split("?", 1)[1].split("&"))
r = c.post("/my-cpd/consent/yes", data={"email": "jo@firm.co.uk", "token": "wrong"})
check("consent with a wrong token refused", jo["marketing_consent"] is None and r.status_code == 400)
r = c.post("/my-cpd/consent/yes", data={"email": "jo@firm.co.uk", "token": q["token"]})
check("pressing Yes records consent", jo["marketing_consent"] is True and "in the loop" in r.text)
r = c.post("/my-cpd/consent/no", data={"email": "jo@firm.co.uk", "token": q["token"]})
check("pressing No records no consent", jo["marketing_consent"] is False)
r = c.get("/my-cpd/consent/yes?email=jo@firm.co.uk")
check("old unsigned consent links record nothing and say what to do", r.status_code == 400 and jo["marketing_consent"] is False
      and "hello@meridiancpd.co.uk" in r.text)

print(f"\n{'ALL PASSED' if not fails else f'{fails} FAILED'}")
sys.exit(1 if fails else 0)
