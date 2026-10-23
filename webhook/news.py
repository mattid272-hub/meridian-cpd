"""News and insights for the admin sidebar.

Every few hours the web process checks a short list of sources and stores anything new in
the news_items table:

- feeds (RSS or Atom): each new entry becomes an item. Feeds from the assessment schemes
  are kept whole; government feeds are broad, so only entries that mention one of the
  topics in TOPICS are kept.
- watched pages (no feed): the page's main text is hashed; when it changes, one
  "Page updated" item is stored, at most once a week per page so a page that changes on
  every load cannot flood the list.

Nothing here sends anything anywhere. NEWS_SCHEDULER=off stops the checks without a
deploy; Admin → News → Check now runs one by hand. Each source's last result is kept in
news_sources so a broken feed shows up in Admin rather than failing silently.
"""
import asyncio
import hashlib
import html
import random
import re
from datetime import datetime, timedelta, timezone
from email.utils import parsedate_to_datetime
from xml.etree import ElementTree as ET

import httpx

USER_AGENT = "MeridianCPD-news/1.0 (+https://meridiancpd.co.uk)"
TIMEOUT = 20.0
DEFAULT_INTERVAL_HOURS = 3
PAGE_ITEM_GAP = timedelta(days=7)      # at most one "page updated" item per page per week
SUMMARY_CHARS = 280

# kind: "feed" or "page". filter: keep only entries that match a topic (broad feeds).
SOURCES = [
    {"id": "desnz", "name": "DESNZ (GOV.UK)", "kind": "feed", "filter": True,
     "url": "https://www.gov.uk/government/organisations/department-for-energy-security-and-net-zero.atom"},
    {"id": "mhclg", "name": "MHCLG (GOV.UK)", "kind": "feed", "filter": True,
     "url": "https://www.gov.uk/government/organisations/ministry-of-housing-communities-local-government.atom"},
    {"id": "ofgem", "name": "Ofgem (GOV.UK)", "kind": "feed", "filter": True,
     "url": "https://www.gov.uk/government/organisations/ofgem.atom"},
    {"id": "elmhurst", "name": "Elmhurst Energy", "kind": "feed", "filter": False,
     "url": "https://www.elmhurstenergy.co.uk/feed/"},
    {"id": "ecmk", "name": "ECMK", "kind": "feed", "filter": False,
     "url": "https://www.ecmk.co.uk/feed/"},
    {"id": "quidos", "name": "Quidos", "kind": "feed", "filter": False,
     "url": "https://www.quidos.co.uk/feed/"},
    {"id": "gov-sap-hem", "name": "GOV.UK: SAP and the Home Energy Model", "kind": "page",
     "url": "https://www.gov.uk/guidance/standard-assessment-procedure"},
    {"id": "bre-sap10", "name": "BRE: SAP 10 and RdSAP 10 documents", "kind": "page",
     "url": "https://bregroup.com/expertise/energy/sap/sap-10"},
    {"id": "trustmark-news", "name": "TrustMark news", "kind": "page",
     "url": "https://www.trustmark.org.uk/news"},
    {"id": "scot-epc-reform", "name": "gov.scot: EPC reform updates", "kind": "page",
     "url": "https://www.gov.scot/publications/energy-performance-certificate-reform-updates/"},
    {"id": "seai-deap", "name": "SEAI: DEAP software and methodology", "kind": "page",
     "url": "https://www.seai.ie/ber/support-for-ber-assessors/deap"},
]

# Topic tags. A broad feed's entry is kept only if it matches at least one.
TOPICS = [
    ("HEM", r"\bhome energy model\b|\bHEM\b"),
    ("RdSAP", r"\brd ?sap\b|\bsap 10\b|\bstandard assessment procedure\b"),
    ("EPC", r"\benergy performance certificate|\bEPCs?\b|\benergy performance of buildings\b"),
    ("MEES", r"\bminimum energy efficiency\b|\bMEES\b|\bprivate rented\b|\brenters'? rights\b"),
    ("Retrofit", r"\bPAS ?2035\b|\bretrofit\b|\bTrustMark\b"),
    ("Schemes", r"\bECO4?\b|\bgreat british insulation\b|\bGBIS\b|\bwarm homes\b|\bboiler upgrade\b|\benergy company obligation\b"),
    ("Heat pumps", r"\bheat pumps?\b"),
    ("Building regs", r"\bfuture homes standard\b|\bbuilding regulations\b|\bapproved document\b|\bpart [lfo]\b"),
    ("Damp", r"\bdamp\b|\bmould\b|\bawaab"),
    ("Scotland", r"\bscotland\b|\bscottish\b"),
    ("Ireland", r"\bSEAI\b|\bDEAP\b|\bBER\b|\bireland\b|\birish\b"),
    ("Efficiency", r"\benergy efficien|\binsulation\b|\bfuel poverty\b"),
]
_TOPIC_RES = [(name, re.compile(rx, re.I)) for name, rx in TOPICS]


def tags_for(*texts: str) -> list:
    blob = " ".join(t for t in texts if t)
    return [name for name, rx in _TOPIC_RES if rx.search(blob)]


def utcnow() -> datetime:
    return datetime.now(timezone.utc)


def _iso(dt) -> str | None:
    return dt.astimezone(timezone.utc).isoformat() if dt else None


def clean_text(s: str, limit: int | None = None) -> str:
    """HTML or entity-laden text to one plain line."""
    s = re.sub(r"<(script|style)\b.*?</\1>", " ", s or "", flags=re.S | re.I)
    s = re.sub(r"<[^>]+>", " ", s)
    s = html.unescape(s)
    s = re.sub(r"\s+", " ", s).strip()
    if limit and len(s) > limit:
        s = s[:limit].rsplit(" ", 1)[0].rstrip(",.;:") + "…"
    return s


def _parse_date(s: str | None):
    if not s:
        return None
    s = s.strip()
    try:
        return parsedate_to_datetime(s)                       # RSS: RFC 822
    except (TypeError, ValueError, IndexError):
        pass
    try:
        return datetime.fromisoformat(s.replace("Z", "+00:00"))  # Atom: RFC 3339
    except ValueError:
        return None


def _local(tag: str) -> str:
    return tag.rsplit("}", 1)[-1]


def parse_feed(xml_text: str) -> list:
    """RSS 2.0 or Atom to [{title, url, published, summary}]. Unknown shapes give []."""
    try:
        root = ET.fromstring(xml_text.encode("utf-8") if isinstance(xml_text, str) else xml_text)
    except ET.ParseError:
        return []
    entries = []
    if _local(root.tag) == "rss":
        for item in root.iter("item"):
            get = lambda name: (item.findtext(name) or "").strip()
            entries.append({"title": clean_text(get("title")), "url": get("link"),
                            "published": _parse_date(get("pubDate")),
                            "summary": clean_text(get("description"), SUMMARY_CHARS)})
    elif _local(root.tag) == "feed":
        for entry in [e for e in root if _local(e.tag) == "entry"]:
            fields = {_local(c.tag): c for c in entry}
            link = ""
            for c in entry:
                if _local(c.tag) == "link" and c.get("rel", "alternate") == "alternate":
                    link = c.get("href", "")
                    break
            summary = fields.get("summary") if "summary" in fields else fields.get("content")
            published = fields.get("published") if "published" in fields else fields.get("updated")
            entries.append({"title": clean_text("".join(fields["title"].itertext()) if "title" in fields else ""),
                            "url": link,
                            "published": _parse_date(published.text if published is not None else None),
                            "summary": clean_text("".join(summary.itertext()) if summary is not None else "", SUMMARY_CHARS)})
    return [e for e in entries if e["title"] and e["url"].startswith(("http://", "https://"))]


def page_fingerprint(html_text: str) -> tuple:
    """(title, sha256 of the page's main text, an 'updated' hint or '')."""
    m = re.search(r"<title[^>]*>(.*?)</title>", html_text, re.S | re.I)
    title = clean_text(m.group(1)) if m else ""
    main = re.search(r"<main\b.*?</main>", html_text, re.S | re.I)
    body = main.group(0) if main else html_text
    body = re.sub(r"<(nav|header|footer|aside|form)\b.*?</\1>", " ", body, flags=re.S | re.I)
    text = clean_text(body)
    hint = re.search(r"\b(?:Last updated|Updated|Published)\s*:?\s*(\d{1,2} [A-Z][a-z]+ \d{4})", text)
    return title, hashlib.sha256(text.encode("utf-8")).hexdigest(), (hint.group(0) if hint else "")


# ── Storage ───────────────────────────────────────────────────────────────────

def _state(db, source_id: str) -> dict | None:
    rows = db.table("news_sources").select("*").eq("source_id", source_id).limit(1).execute().data or []
    return rows[0] if rows else None


def _save_state(db, source_id: str, fields: dict) -> None:
    if _state(db, source_id):
        db.table("news_sources").update(fields).eq("source_id", source_id).execute()
    else:
        db.table("news_sources").insert({"source_id": source_id, **fields}).execute()


def _exists(db, key: str) -> bool:
    return bool(db.table("news_items").select("id").eq("key", key).limit(1).execute().data)


def _store(db, src: dict, key: str, title: str, url: str, published, summary: str, tags: list) -> bool:
    if _exists(db, key):
        return False
    db.table("news_items").insert({
        "key": key, "source": src["name"], "kind": src["kind"], "title": title[:300], "url": url,
        "published_at": _iso(published) or _iso(utcnow()), "summary": summary, "tags": tags,
        "dismissed": False,
    }).execute()
    return True


# ── Checking ──────────────────────────────────────────────────────────────────

def ingest_feed(db, src: dict, body: str, now: datetime) -> int:
    added = 0
    for e in parse_feed(body):
        tags = tags_for(e["title"], e["summary"])
        if src.get("filter") and not tags:
            continue
        if _store(db, src, e["url"], e["title"], e["url"], e["published"], e["summary"], tags):
            added += 1
    return added


def ingest_page(db, src: dict, body: str, now: datetime) -> int:
    title, digest, hint = page_fingerprint(body)
    state = _state(db, src["id"]) or {}
    previous = state.get("page_hash")
    fields = {"page_hash": digest, "page_title": title}
    added = 0
    if previous and previous != digest:
        last_item = _parse_date(state.get("last_item_at"))
        if not last_item or now - last_item >= PAGE_ITEM_GAP:
            summary = hint or "The page has changed since it was last checked."
            name = title or src["name"]
            if _store(db, src, f"{src['url']}#{digest[:16]}", f"Page updated: {name}", src["url"], now,
                       summary, tags_for(name, src["name"], summary)):
                added = 1
                fields["last_item_at"] = _iso(now)
    _save_state(db, src["id"], fields)
    return added


async def check_source(db, src: dict, http: httpx.AsyncClient, now: datetime) -> int:
    try:
        r = await http.get(src["url"])
        if r.status_code != 200:
            raise RuntimeError(f"HTTP {r.status_code}")
        added = ingest_feed(db, src, r.text, now) if src["kind"] == "feed" else ingest_page(db, src, r.text, now)
        _save_state(db, src["id"], {"url": src["url"], "last_checked": _iso(now), "last_ok": _iso(now),
                                    "last_error": None, "last_added": added})
        return added
    except Exception as e:
        _save_state(db, src["id"], {"url": src["url"], "last_checked": _iso(now), "last_error": str(e)[:300]})
        return 0


async def check_all(db, now: datetime | None = None, transport=None) -> dict:
    now = now or utcnow()
    added = {}
    async with httpx.AsyncClient(timeout=TIMEOUT, follow_redirects=True, transport=transport,
                                 headers={"User-Agent": USER_AGENT}) as http:
        for src in SOURCES:
            added[src["id"]] = await check_source(db, src, http, now)
    return added


async def scheduler_loop(get_db, interval_hours: float = DEFAULT_INTERVAL_HOURS, first_delay: float = 120) -> None:
    """Runs inside the web process: a first check two minutes after start-up, then every few hours."""
    await asyncio.sleep(first_delay)
    while True:
        try:
            added = await check_all(get_db())
            if any(added.values()):
                print(f"News: {added}")
        except Exception as e:
            print(f"News scheduler error: {e}")
        await asyncio.sleep(interval_hours * 3600 * random.uniform(0.9, 1.1))


# ── Reading, for Admin ────────────────────────────────────────────────────────

def latest(db, limit: int = 12, include_dismissed: bool = False, tag: str | None = None) -> list:
    q = db.table("news_items").select("*")
    if not include_dismissed:
        q = q.eq("dismissed", False)
    rows = q.order("published_at", desc=True).limit(limit if not tag else 500).execute().data or []
    if tag:
        rows = [r for r in rows if tag in (r.get("tags") or [])][:limit]
    return rows


def sources_status(db) -> list:
    rows = {r["source_id"]: r for r in (db.table("news_sources").select("*").execute().data or [])}
    return [{**s, "state": rows.get(s["id"], {})} for s in SOURCES]


def mark(db, item_id: str, field: str) -> None:
    if field == "read":
        db.table("news_items").update({"read_at": _iso(utcnow())}).eq("id", item_id).execute()
    elif field == "dismiss":
        db.table("news_items").update({"dismissed": True}).eq("id", item_id).execute()
