"""
Meridian CPD — Automated Content Engine

Runs on the 1st and 15th of each month via GitHub Actions.
Each run:
  1. Scrapes industry sources for new developments
  2. Identifies the most CPD-worthy topic from new material
  3. Generates a brand new course via Claude API
  4. Saves to courses/ folder
  5. Triggers course_publisher.py to build PDF + upload + notify subscribers

Never repeats a topic. Every run adds permanently to the library.
"""
import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path

import anthropic
import httpx
from supabase import create_client

# ── Config ────────────────────────────────────────────────────────────────────
ROOT = Path(__file__).parent.parent
SOURCES_FILE = Path(__file__).parent / "sources.json"
COURSES_DIR = ROOT / "courses"
COURSES_DIR.mkdir(exist_ok=True)

supabase = create_client(
    os.environ["SUPABASE_URL"],
    os.environ["SUPABASE_SERVICE_ROLE_KEY"],
)
claude = anthropic.Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])


# ── Helpers ───────────────────────────────────────────────────────────────────

def fetch_source(url: str) -> str:
    """Fetch a URL and return readable article text (strips nav/footer/scripts)."""
    try:
        from bs4 import BeautifulSoup
        import re
        headers = {"User-Agent": "MeridianCPD-ContentBot/1.0 (hello@meridiancpd.co.uk)"}
        r = httpx.get(url, headers=headers, timeout=15, follow_redirects=True)
        if r.status_code != 200:
            return ""
        soup = BeautifulSoup(r.text, "html.parser")
        # Remove noise elements
        for tag in soup(["script", "style", "nav", "header", "footer",
                          "aside", "form", "button", "noscript", "iframe"]):
            tag.decompose()
        # Prefer article/main content areas
        content = (
            soup.find("main") or soup.find("article") or
            soup.find(id=re.compile(r"content|main|article", re.I)) or
            soup.find(class_=re.compile(r"content|article|post|news|body", re.I)) or
            soup.body
        )
        if not content:
            return ""
        # Get clean text
        text = content.get_text(separator=" ", strip=True)
        text = re.sub(r"\s+", " ", text)
        return text[:8000]
    except Exception as e:
        print(f"  Warning: could not fetch {url}: {e}")
    return ""


def get_existing_topics() -> list[str]:
    """Return list of all existing course titles to avoid repetition."""
    existing = []
    for course_dir in COURSES_DIR.iterdir():
        if course_dir.is_dir():
            md_files = list(course_dir.glob("*.md"))
            if md_files:
                first_line = md_files[0].read_text(encoding="utf-8").split("\n")[0]
                existing.append(first_line.lstrip("# ").strip())
    return existing


def next_course_id(prefix: str = "MER-ALL") -> str:
    """Generate the next course ID in sequence for a given prefix."""
    existing_ids = [
        d.name for d in COURSES_DIR.iterdir()
        if d.is_dir() and d.name.startswith(prefix)
    ]
    if not existing_ids:
        return f"{prefix}-100"
    nums = []
    for cid in existing_ids:
        try:
            nums.append(int(cid.split("-")[-1]))
        except ValueError:
            pass
    return f"{prefix}-{max(nums) + 1:03d}" if nums else f"{prefix}-100"


# ── Phase 1: Harvest new developments ─────────────────────────────────────────

def harvest_sources() -> str:
    """Fetch all configured sources and return combined digest."""
    with open(SOURCES_FILE) as f:
        config = json.load(f)

    print("Harvesting sources...")
    combined = []
    for source in config["sources"]:
        print(f"  Fetching: {source['name']}")
        text = fetch_source(source["url"])
        if text:
            combined.append(f"=== {source['name']} ({source['url']}) ===\n{text}\n")

    return "\n".join(combined)


# ── Phase 2: Identify best CPD topic ──────────────────────────────────────────

def identify_topic(source_digest: str, existing_topics: list[str]) -> dict:
    """Ask Claude to identify the most valuable new CPD topic."""
    existing_str = "\n".join(f"- {t}" for t in existing_topics)

    prompt = f"""You are the content director for Meridian CPD, a UK CPD platform for Domestic Energy Assessors (DEAs), Retrofit Assessors, and Retrofit Coordinators.

I've scraped these UK energy industry sources today:

{source_digest}

We already have these courses (do NOT repeat any of these topics):
{existing_str}

Based on what is genuinely new or updated in the source material, identify the SINGLE most valuable CPD topic for UK energy assessors right now. The topic must:
1. Be genuinely new or updated (not something we've already covered)
2. Have clear practical relevance to DEAs or Retrofit Assessors in their day-to-day work
3. Be based on real developments in the scraped content (not invented)
4. Be specific enough to fill a 1-hour CPD course

Respond with a JSON object:
{{
  "course_id_prefix": "MER-DEA" or "MER-RA" or "MER-ALL",
  "title": "Course title (max 70 chars)",
  "topic_summary": "2-3 sentences explaining the topic and why it's timely",
  "key_sources": ["url1", "url2"],
  "cpd_hours": 1,
  "target_audience": "DEAs" or "Retrofit Assessors" or "All assessors"
}}

If no genuinely new topic is found in the sources, respond with:
{{"skip": true, "reason": "brief explanation"}}"""

    response = claude.messages.create(
        model="claude-opus-4-6",
        max_tokens=1000,
        messages=[{"role": "user", "content": prompt}],
    )

    text = response.content[0].text.strip()
    # Extract JSON from response
    import re
    json_match = re.search(r"\{.*\}", text, re.DOTALL)
    if json_match:
        return json.loads(json_match.group())
    raise ValueError(f"Could not parse topic JSON from: {text}")


# ── Phase 3: Generate course content ──────────────────────────────────────────

def generate_course(topic: dict, course_id: str) -> str:
    """Generate a full course from a topic dict."""
    prompt = f"""You are writing a CPD course for Meridian CPD, a UK platform for Domestic Energy Assessors and Retrofit professionals.

Course to write:
- Course ID: {course_id}
- Title: {topic['title']}
- CPD Hours: {topic['cpd_hours']}
- Target audience: {topic['target_audience']}
- Topic context: {topic['topic_summary']}

Tone: Expert-to-expert. Peer professional. Assume the reader is a working assessor. No corporate padding. No hand-holding.

Write a complete CPD course in this exact structure:

# {topic['title']}
**Course ID:** {course_id} | **CPD Hours:** {topic['cpd_hours']} | **Published:** {datetime.now(timezone.utc).strftime('%B %Y')}
*© Meridian CPD 2026. All rights reserved.*

---

## Learning Objectives
[5 bullet points — measurable, specific]

## Introduction
[~300 words — why this topic matters now, what's changed, what the assessor needs to understand]

## Section 1: [Descriptive title]
[~400 words]

## Section 2: [Descriptive title]
[~400 words]

## Section 3: [Descriptive title]
[~400 words]

## Section 4: [Descriptive title — practical application]
[~350 words]

## Key Takeaways
[7 bullet points — actionable]

## Self-Assessment Questions
[5 multiple choice questions, A/B/C/D options, correct answer + brief explanation]

## Further Reading
[4 references to primary sources with URLs where available]

---
*© Meridian CPD 2026. All rights reserved. Unauthorised reproduction prohibited.*
*This course material is licensed to individual subscribers only.*

IMPORTANT: Base all content on factual, accurate information. Do not invent regulatory figures, dates, or technical standards. If unsure about a specific value, describe the principle and note that the specific figure should be verified against the primary source."""

    response = claude.messages.create(
        model="claude-opus-4-6",
        max_tokens=6000,
        messages=[{"role": "user", "content": prompt}],
    )
    return response.content[0].text


# ── Phase 2b: Curriculum gap fallback ────────────────────────────────────────

# Known valuable topics not yet covered — engine works through these when no news found
CURRICULUM_BACKLOG = [
    {"course_id_prefix": "MER-DEA", "title": "Flat Roof and Roof Room Insulation in RdSAP 10", "cpd_hours": 1, "target_audience": "DEAs", "topic_summary": "RdSAP 10 introduced updated conventions for flat roof U-values and room-in-roof assessments. This course covers correct identification, measurement and data entry."},
    {"course_id_prefix": "MER-DEA", "title": "Party Walls and Heat Loss in Semi-Detached Properties", "cpd_hours": 1, "target_audience": "DEAs", "topic_summary": "Correct treatment of party wall heat loss is a common source of error in RdSAP assessments. This course covers the conventions and their practical application."},
    {"course_id_prefix": "MER-DEA", "title": "Heating System Controls: Programmers, TRVs and Smart Controls", "cpd_hours": 1, "target_audience": "DEAs", "topic_summary": "RdSAP 10 scoring of heating controls has changed. This course covers correct identification and data entry for all common control types including smart thermostats."},
    {"course_id_prefix": "MER-RA", "title": "Moisture Risk Assessment in Solid Wall Retrofit", "cpd_hours": 1, "target_audience": "Retrofit Assessors", "topic_summary": "PAS 2035 requires moisture risk assessment before solid wall insulation. This course covers the assessment process, risk factors and documentation requirements."},
    {"course_id_prefix": "MER-RA", "title": "Structural Surveys and Retrofit: When to Refer On", "cpd_hours": 1, "target_audience": "Retrofit Assessors", "topic_summary": "Retrofit assessors must identify structural issues that affect the suitability of retrofit measures. This course covers recognition, documentation and referral pathways."},
    {"course_id_prefix": "MER-ALL", "title": "Data Protection and GDPR for Energy Assessors", "cpd_hours": 1, "target_audience": "All assessors", "topic_summary": "Energy assessors hold significant personal and property data. This course covers GDPR obligations, data storage, consent and breach reporting requirements."},
    {"course_id_prefix": "MER-ALL", "title": "Professional Indemnity Insurance: What Assessors Need to Know", "cpd_hours": 1, "target_audience": "All assessors", "topic_summary": "PII requirements for DEAs and retrofit professionals. Covers minimum cover levels, common exclusions, claim scenarios and choosing appropriate cover."},
    {"course_id_prefix": "MER-DEA", "title": "Extensions and Conservatories in RdSAP 10", "cpd_hours": 1, "target_audience": "DEAs", "topic_summary": "Correct treatment of extensions, conservatories and glazed additions in RdSAP 10 assessments, including thermal separation rules and heated/unheated space conventions."},
    {"course_id_prefix": "MER-RA", "title": "Heat Pump Readiness Assessment: A Practical Guide", "cpd_hours": 1, "target_audience": "Retrofit Assessors", "topic_summary": "Assessing whether a property is suitable for heat pump installation under PAS 2035. Covers fabric first principles, heat loss calculations, radiator sizing and common barriers."},
    {"course_id_prefix": "MER-ALL", "title": "Energy Poverty and Vulnerable Occupants: Assessor Responsibilities", "cpd_hours": 1, "target_audience": "All assessors", "topic_summary": "Recognising fuel poverty, safeguarding obligations, signposting to ECO4/GBIS and local authority schemes, and handling sensitive situations on site."},
]

def generate_curriculum_gap_topic(existing_topics: list[str]) -> dict | None:
    """Return the next undelivered curriculum topic, or None if all done."""
    existing_lower = [t.lower() for t in existing_topics]
    for topic in CURRICULUM_BACKLOG:
        if topic["title"].lower() not in existing_lower:
            print(f"  Selected curriculum gap: {topic['title']}")
            return topic
    return None


# ── Main ─────────────────────────────────────────────────────────────────────

def main():
    print(f"\n=== Meridian CPD Content Engine — {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M UTC')} ===\n")

    # Phase 1: Harvest
    source_digest = harvest_sources()

    # Phase 2: Identify topic
    print("\nIdentifying CPD topic...")
    existing_topics = get_existing_topics()
    print(f"  {len(existing_topics)} existing courses found")

    topic = identify_topic(source_digest, existing_topics)

    if topic.get("skip"):
        print(f"\nNo fresh news topic found: {topic.get('reason')}")
        print("Falling back to curriculum gap generation...")
        topic = generate_curriculum_gap_topic(existing_topics)
        if not topic:
            print("No curriculum gaps remaining. Skipping this run.")
            sys.exit(0)

    print(f"\nSelected topic: {topic['title']}")
    print(f"  Prefix: {topic['course_id_prefix']}")
    print(f"  Audience: {topic['target_audience']}")

    # Generate course ID
    course_id = next_course_id(topic["course_id_prefix"])
    print(f"  Course ID: {course_id}")

    # Phase 3: Generate content
    print("\nGenerating course content...")
    course_md = generate_course(topic, course_id)

    # Save markdown
    course_dir = COURSES_DIR / course_id
    course_dir.mkdir(exist_ok=True)
    md_path = course_dir / f"{course_id}.md"
    md_path.write_text(course_md, encoding="utf-8")
    print(f"\nCourse saved: {md_path}")
    print(f"Word count: {len(course_md.split())}")

    # Phase 4: Build PDF + publish
    print("\nTriggering publisher...")
    import subprocess
    publisher = Path(__file__).parent / "course_publisher.py"
    result = subprocess.run(
        ["python3", str(publisher), course_id],
        capture_output=True,
        text=True,
    )
    if result.returncode == 0:
        print(result.stdout)
    else:
        print(f"Publisher error: {result.stderr}")
        sys.exit(1)

    print(f"\n=== Done. New course {course_id} added to library. ===\n")


if __name__ == "__main__":
    main()
