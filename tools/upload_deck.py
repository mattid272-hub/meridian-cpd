"""
Meridian CPD — Upload a course's slide deck to Supabase Storage.

A course delivered as a deck (catalogue entry "deliverable": "deck") has two files in the
'courses' bucket: {id}-deck.pdf, the NotebookLM export that is the course, and {id}.pdf,
the written notes built from the markdown. This uploads the deck under its own name, so
the republish workflow (which only ever writes {id}.pdf) can never overwrite it.

Usage:
    SUPABASE_SERVICE_ROLE_KEY=eyJ... \
    python3 tools/upload_deck.py MER-ALL-019 "/path/to/Insulation Part 1.pdf"
    python3 tools/upload_deck.py MER-ALL-019 deck.pdf --notes courses/MER-ALL-019/MER-ALL-019.pdf

After uploading, take the course out of UNDER_REVIEW in webhook/main.py,
landing-page/courses.html and landing-page/under-review.json, and check Admin → System.
"""
import os
import re
import sys
import urllib.error
import urllib.request
from pathlib import Path

SUPABASE_URL = os.environ.get("SUPABASE_URL", "https://cpkyloywjmpesmjgqaxm.supabase.co")
SERVICE_KEY = os.environ.get("SUPABASE_SERVICE_ROLE_KEY", "")
BUCKET = "courses"
COURSE_ID_RE = re.compile(r"^MER-[A-Z]{2,4}-\d{3}$")
MIN_BYTES = 50_000  # a real deck is a megabyte or two; anything smaller is the wrong file


def upload(filename: str, pdf_bytes: bytes) -> str:
    """Put one PDF in the bucket (overwriting) and return its public URL."""
    url = f"{SUPABASE_URL}/storage/v1/object/{BUCKET}/{filename}"
    req = urllib.request.Request(
        url,
        data=pdf_bytes,
        method="POST",
        headers={
            "Authorization": f"Bearer {SERVICE_KEY}",
            "Content-Type": "application/pdf",
            "x-upsert": "true",
        },
    )
    try:
        with urllib.request.urlopen(req) as resp:
            if resp.status not in (200, 201):
                raise RuntimeError(f"HTTP {resp.status}")
    except urllib.error.HTTPError as e:
        raise RuntimeError(f"HTTP {e.code}: {e.read().decode()[:200]}") from None
    return f"{SUPABASE_URL}/storage/v1/object/public/{BUCKET}/{filename}"


def read_pdf(path: str) -> bytes:
    p = Path(path)
    if not p.is_file():
        raise FileNotFoundError(f"Not found: {p}")
    data = p.read_bytes()
    if not data.startswith(b"%PDF"):
        raise ValueError(f"Not a PDF: {p}")
    if len(data) < MIN_BYTES:
        raise ValueError(f"{p} is only {len(data):,} bytes; refusing to upload")
    return data


def main() -> int:
    args = sys.argv[1:]
    notes_path = ""
    if "--notes" in args:
        i = args.index("--notes")
        notes_path = args[i + 1] if i + 1 < len(args) else ""
        del args[i:i + 2]
    if len(args) != 2 or not COURSE_ID_RE.match(args[0]):
        print("Usage: upload_deck.py MER-XXX-000 /path/to/deck.pdf [--notes /path/to/notes.pdf]")
        return 1
    if not SERVICE_KEY:
        print("ERROR: set SUPABASE_SERVICE_ROLE_KEY first (never paste it into a file).")
        return 1

    course_id, deck_path = args
    try:
        deck = read_pdf(deck_path)
        notes = read_pdf(notes_path) if notes_path else None
    except (OSError, ValueError) as e:
        print(f"ERROR: {e}")
        return 1

    try:
        url = upload(f"{course_id}-deck.pdf", deck)
        print(f"  {course_id} deck: {len(deck) // 1024:,} KB → {url}")
        if notes is not None:
            url = upload(f"{course_id}.pdf", notes)
            print(f"  {course_id} notes: {len(notes) // 1024:,} KB → {url}")
    except RuntimeError as e:
        print(f"ERROR uploading {course_id}: {e}")
        return 1

    print(f"\nDone. Now remove {course_id} from UNDER_REVIEW (webhook/main.py, landing-page/courses.html,"
          " landing-page/under-review.json) and check Admin → System.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
