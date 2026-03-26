"""
Meridian CPD — Upload all course PDFs to Supabase Storage.

Run once to populate the 'courses' bucket.

Usage:
    SUPABASE_URL=https://cpkyloywjmpesmjgqaxm.supabase.co \
    SUPABASE_SERVICE_ROLE_KEY=eyJ... \
    python3 upload_pdfs_to_supabase.py
"""
import os
import sys
import urllib.request
import urllib.error
from pathlib import Path

SUPABASE_URL = os.environ.get("SUPABASE_URL", "https://cpkyloywjmpesmjgqaxm.supabase.co")
SERVICE_KEY  = os.environ.get("SUPABASE_SERVICE_ROLE_KEY", "")

if not SERVICE_KEY:
    print("ERROR: Set SUPABASE_SERVICE_ROLE_KEY env var first.")
    sys.exit(1)

COURSES_DIR = Path(__file__).parent / "courses"
BUCKET = "courses"

# All launch-pack courses that the webhook knows about
COURSE_IDS = [
    "MER-DEA-001",
    "MER-DEA-002",
    "MER-DEA-003",
    "MER-DEA-004",
    "MER-DEA-010",
    "MER-DEA-011",
    "MER-DEA-021",
    "MER-RA-001",
    "MER-RA-006",
    "MER-RA-009",
    "MER-ALL-001",
    "MER-ALL-004",
]


def upload(course_id: str) -> str:
    pdf_path = COURSES_DIR / course_id / f"{course_id}.pdf"
    if not pdf_path.exists():
        print(f"  SKIP {course_id} — PDF not found at {pdf_path}")
        return ""

    pdf_bytes = pdf_path.read_bytes()
    filename  = f"{course_id}.pdf"
    url = f"{SUPABASE_URL}/storage/v1/object/{BUCKET}/{filename}"

    req = urllib.request.Request(
        url,
        data=pdf_bytes,
        method="POST",
        headers={
            "Authorization":  f"Bearer {SERVICE_KEY}",
            "Content-Type":   "application/pdf",
            "x-upsert":       "true",          # overwrite if exists
        },
    )
    try:
        with urllib.request.urlopen(req) as resp:
            status = resp.status
    except urllib.error.HTTPError as e:
        # Supabase returns 200 on success
        if e.code == 200:
            status = 200
        else:
            print(f"  ERROR {course_id}: HTTP {e.code} — {e.read().decode()[:200]}")
            return ""

    public_url = f"{SUPABASE_URL}/storage/v1/object/public/{BUCKET}/{filename}"
    size_kb = len(pdf_bytes) // 1024
    print(f"  {course_id}: {size_kb} KB uploaded → {public_url}")
    return public_url


def main():
    print(f"\nUploading {len(COURSE_IDS)} PDFs to Supabase Storage bucket '{BUCKET}'...\n")
    uploaded = {}
    for cid in COURSE_IDS:
        url = upload(cid)
        if url:
            uploaded[cid] = url

    print(f"\n✓ Done. {len(uploaded)}/{len(COURSE_IDS)} uploaded.")
    print("\n─── Add these to Railway env vars ───────────────────────────────")
    for cid, url in uploaded.items():
        env_key = f"PDF_{cid.replace('-', '_')}"
        print(f"{env_key}={url}")


if __name__ == "__main__":
    main()
