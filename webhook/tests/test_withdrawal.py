"""Withdrawn courses: no download, no completion, no certificate, marked on the dashboard.
Run: python3 tests/test_withdrawal.py"""
import os, sys, types
os.environ.update(STRIPE_SECRET_KEY="sk_test_x", STRIPE_WEBHOOK_SECRET="whsec_x", SUPABASE_URL="https://example.supabase.co",
                  SUPABASE_SERVICE_ROLE_KEY="eyJhbGciOiJIUzI1NiJ9.eyJyb2xlIjoic2VydmljZV9yb2xlIn0.x", SESSION_SECRET="s")
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
import main
from fastapi.testclient import TestClient

class Res:
    def __init__(self, data): self.data, self.count = data, len(data)
class Q:
    def __init__(s, db, t): s.db, s.t, s.f, s.op, s.pl = db, t, [], "select", None
    def select(s, *a, **k): return s
    def eq(s, c, v): s.f.append(lambda r: r.get(c) == v); return s
    def in_(s, c, v): s.f.append(lambda r: r.get(c) in v); return s
    def like(s, *a): return s
    def order(s, *a, **k): return s
    def limit(s, *a): return s
    @property
    def not_(s): s._neg = True; return s
    def is_(s, c, _n):
        neg = getattr(s, "_neg", False); s._neg = False
        s.f.append((lambda r: r.get(c) is not None) if neg else (lambda r: r.get(c) is None)); return s
    def insert(s, row): s.op, s.pl = "insert", row; return s
    def update(s, row): s.op, s.pl = "update", row; return s
    def execute(s):
        rows = s.db.setdefault(s.t, [])
        if s.op == "insert": rows.append(dict(s.pl)); return Res([s.pl])
        hit = [r for r in rows if all(f(r) for f in s.f)]
        if s.op == "update": [r.update(s.pl) for r in hit]
        if s.t == "completions" and s.op == "select":
            hit = [dict(r, members=next(m for m in s.db["members"] if m["id"] == r["member_id"])) for r in hit]
        return Res(hit)
db = {"members": [{"id": "m1", "email": "sub@example.com", "name": "Sub Scriber", "plan": "subscription"}],
      "purchases": [], "certificates": [],
      "completions": [{"member_id": "m1", "course_id": "MER-ALL-016", "completion_token": "tok-ra", "completed_at": None, "downloaded_at": "2026-09-01"},
                      {"member_id": "m1", "course_id": "MER-ALL-004", "completion_token": "tok-done", "completed_at": "2026-09-02", "downloaded_at": "2026-09-01"},
                      {"member_id": "m1", "course_id": "MER-DEA-002", "completion_token": "tok-dea", "completed_at": None, "downloaded_at": None}]}
fake = types.SimpleNamespace(table=lambda t: Q(db, t), storage=types.SimpleNamespace(from_=lambda b: types.SimpleNamespace(download=lambda f: (_ for _ in ()).throw(RuntimeError("no catalogue")))))
main.supabase = fake
main._refresh_under_review = lambda: None
# Nothing is withdrawn on the live site now; withdraw one course here so the mechanism stays tested.
main.UNDER_REVIEW.clear(); main.UNDER_REVIEW.add("MER-ALL-016")
c = TestClient(main.app, follow_redirects=False)
h = c.get("/health").json(); print("health", h); N = h["available"]; W = h["under_review"]; assert N + W == h["courses"] and W == len(main.UNDER_REVIEW)
cookie = {"session_token": main._make_session_token("sub@example.com")}
r = c.get("/download/MER-ALL-016", cookies=cookie); assert r.status_code == 200 and "being updated" in r.text, r.status_code
r = c.get("/download/MER-DEA-002", cookies=cookie); assert r.status_code == 302 and "MER-DEA-002.pdf" in r.headers["location"], r.status_code
r = c.get("/complete/tok-ra"); assert r.status_code == 200 and "being updated" in r.text
r = c.post("/complete/tok-ra", data={"confirm": "on", "cert_name": "X"}); assert "being updated" in r.text and not db["certificates"]
assert next(x for x in db["completions"] if x["completion_token"] == "tok-ra")["completed_at"] is None
r = c.get("/complete/tok-dea"); assert r.status_code == 200 and "being updated" not in r.text
r = c.get("/my-cpd/dashboard", cookies=cookie); assert r.status_code == 200, r.status_code
t = r.text
assert t.count("Being updated") == W, t.count("Being updated")
assert t.count('href="/download/') == N, t.count('href="/download/')
assert "/download/MER-ALL-016" not in t and "/complete/tok-ra" not in t
new_tokens = [x["course_id"] for x in db["completions"] if x["completion_token"] not in ("tok-ra", "tok-done", "tok-dea")]
had = {"MER-ALL-016", "MER-ALL-004", "MER-DEA-002"}
expected = {k for k in main.COURSES if main.is_available(k)} - had
assert set(new_tokens) == expected, (sorted(set(new_tokens) ^ expected))
print(f"dashboard: {N} downloadable, {W} marked being updated, tokens created only for available courses")
print("ALL CHECKS PASSED")
