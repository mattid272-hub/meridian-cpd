"""Guard the Meridian claim rules in the public site and the app copy.

No accreditation scheme is named, nothing says "accreditation body", and the site
quotes no course count, hour total or cost per course worked out from a count.
Course titles and descriptions in the catalogue may still cite a document or
scheme they are about; this test checks the marketing and app wording only.
"""
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]

APP_FILES = ["webhook/main.py", "webhook/email_sender.py", "webhook/certificate_generator.py"]
SITE_FILES = ["landing-page/index.html", "landing-page/courses.html"]

BANNED = [
    r"accreditation bod(y|ies)",
    r"\bElmhurst\b",
    r"\bQuidos\b",
    r"\bECMK\b",
    r"\bStroma\b",
    r"most scheme",
    r"Pays for itself",
    r"average cost per course",
    r"in the library today",
    r"less than £3 a course",
    r"Courses available",
    r"CPD hours in library",
]


def _text(rel):
    return (ROOT / rel).read_text(encoding="utf-8")


def test_no_banned_claims():
    hits = []
    for rel in APP_FILES + SITE_FILES:
        for n, line in enumerate(_text(rel).splitlines(), 1):
            for pat in BANNED:
                if re.search(pat, line, re.IGNORECASE):
                    hits.append(f"{rel}:{n}: {pat}")
    assert not hits, "\n".join(hits)


def test_site_has_no_stat_counters():
    courses = _text("landing-page/courses.html")
    assert 'id="statTotal"' not in courses
    assert 'id="statHours"' not in courses


# The scripts in this folder run stand-alone (python3 tests/test_claim_rules.py) and
# through conftest.py, which runs each file as one test; both call the checks here.
test_no_banned_claims()
test_site_has_no_stat_counters()
print("claim rules: ok")
