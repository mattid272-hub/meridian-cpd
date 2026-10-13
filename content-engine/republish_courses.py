"""
Meridian CPD — Republish corrected courses

Rebuilds the PDF for one or more existing courses from their markdown and replaces
the file in Supabase Storage. Unlike course_publisher.py it sends no emails and does
not touch the catalogue: use it when a course's content has been corrected.

Usage:
  python3 republish_courses.py MER-DEA-004 MER-DEA-011
  python3 republish_courses.py --dry-run MER-DEA-004     # build only, no upload
"""
import os
import re
import sys
from pathlib import Path

ROOT = Path(__file__).parent.parent
COURSES_DIR = ROOT / "courses"
COURSE_ID_RE = re.compile(r"^MER-[A-Z]{2,4}-\d{3}$")


def build(course_id: str) -> bytes:
    md_path = COURSES_DIR / course_id / f"{course_id}.md"
    if not md_path.exists():
        raise FileNotFoundError(f"Markdown not found: {md_path}")
    sys.path.insert(0, str(COURSES_DIR))
    from build_pdfs_v2 import build_pdf
    return build_pdf(course_id, md_path.read_text(encoding="utf-8"))


def main() -> int:
    args = [a for a in sys.argv[1:] if a.strip()]
    dry_run = "--dry-run" in args
    course_ids = [a for a in args if not a.startswith("--")]
    bad = [c for c in course_ids if not COURSE_ID_RE.match(c)]
    if bad or not course_ids:
        print(f"Usage: republish_courses.py [--dry-run] MER-XXX-000 ...  (bad ids: {bad})")
        return 1

    bucket = None
    if not dry_run:
        from supabase import create_client
        client = create_client(os.environ["SUPABASE_URL"], os.environ["SUPABASE_SERVICE_ROLE_KEY"])
        bucket = client.storage.from_("courses")

    failed = []
    for course_id in course_ids:
        try:
            pdf = build(course_id)
            if len(pdf) < 20_000:
                raise ValueError(f"PDF is only {len(pdf)} bytes; refusing to publish")
            if bucket is not None:
                bucket.upload(
                    f"{course_id}.pdf",
                    pdf,
                    file_options={"content-type": "application/pdf", "upsert": "true"},
                )
            print(f"{'Built' if dry_run else 'Republished'} {course_id}: {len(pdf):,} bytes")
        except Exception as e:
            failed.append(course_id)
            print(f"::error title=Course not republished::{course_id}: {type(e).__name__}: {str(e)[:300]}")

    if failed:
        print(f"Failed: {', '.join(failed)}")
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
