"""
Meridian CPD — course correction notices (admin only)

When a published course is found to be wrong and is replaced, the people who studied
the old edition have to be told and given the corrected one. This module adds an admin
page that does that safely:

  GET  /admin/corrections        who would receive the notice, and the email they would get
  POST /admin/corrections/test   send one copy to an address you type (nothing recorded)
  POST /admin/corrections/send   send to the ticked members (needs the word SEND typed in)

Safeguards:
  - Nothing is sent by loading the page. Sending needs an explicit, typed confirmation.
  - Each member can receive a given notice once. That is recorded in the
    correction_notices table (see migrations/2026-10-12_correction_notices.sql); if the
    table is missing, sending is refused rather than risking duplicates.
  - The corrected PDFs must already be in storage. If any attached course's file is older
    than the notice's cut-off date, sending is refused, so an old edition can never be
    attached to a correction.
  - This is a service message about a product the member already holds, so it does not
    depend on marketing consent and carries no promotion.
"""
import asyncio
import base64
import html
from datetime import datetime, timezone

from fastapi import APIRouter, Depends, Request
from fastapi.responses import HTMLResponse

from email_sender import _send
from settings import APP_HOST

# ── The notices ───────────────────────────────────────────────────────────────
# "changes" holds one plain statement per course of what the earlier edition got wrong.
# Each is taken from the corrected course's own introduction; keep them factual.

NOTICES = {
    "2026-10-rdsap": {
        "label": "RdSAP 10 courses, corrected October 2026",
        # The corrected PDFs were published on or after this moment (UTC).
        "pdfs_updated_after": "2026-10-12T00:00:00+00:00",
        "changes": {
            "MER-DEA-001": (
                "Its description of Room in Roof Type 1 and Type 2 was wrong. "
                "Section 4 now gives the definitions that are in the conventions."
            ),
            "MER-DEA-002": (
                "It said windows are measured as the structural opening from the external face "
                "of the wall, with an addition for reveal depth when measured inside. Convention "
                "2.15 says otherwise, and Section 2 now sets out the rule as written."
            ),
            "MER-DEA-003": (
                "It taught rules on trickle vents, cooker hoods, a default duct type, commissioning "
                "evidence and default air permeability by age band. None of these is in the "
                "conventions or the specification, and they have been removed."
            ),
            "MER-DEA-004": (
                "It defined Type 1 and Type 2 by whether a separating ceiling exists between the "
                "roof room and the storey below. The conventions define the types by the common "
                "wall, as Section 2 now explains."
            ),
            "MER-DEA-005": (
                "Its boiler efficiency defaults, its ranking of heating controls and its list of "
                "common audit failures could not be traced to the conventions or the specification "
                "and have been removed."
            ),
            "MER-DEA-006": (
                "Its efficiency statements, its checklist for telling storage heater types apart on "
                "site and its percentage figures for heat from secondary heating could not be traced "
                "to the conventions or the specification and have been removed."
            ),
            "MER-DEA-007": (
                "It taught rules for a combi boiler keep-hot facility. Neither the conventions nor "
                "the specification mentions one, so those rules have been removed."
            ),
            "MER-DEA-008": (
                "It said loft insulation depth is recorded at the centre of the loft. Convention 3.04 "
                "says to use an area-weighted average where the level varies. Other statements that "
                "could not be traced to a source have been removed."
            ),
            "MER-DEA-010": (
                "It described lighting efficacy bands chosen by the assessor and lighting controls as "
                "an input. Neither is in convention 7.01 or in the specification's data set."
            ),
            "MER-DEA-011": (
                "It gave 4 kWh as the default for a battery of unknown capacity. Convention 9.05 gives "
                "5 kWh. Its per-panel wattage defaults and its rule for arrays on more than three roof "
                "planes are not in either document and have been removed."
            ),
            "MER-DEA-014": (
                "It gave audit sampling rates, an annual audit cycle and a list of common failures. "
                "None could be traced to a source and they have been removed. The course is now "
                "titled 'EPC Audit Preparation: Building an Evidence File That Stands Up'."
            ),
            "MER-DEA-021": (
                "It gave a three-year limit on the age of a pressure test certificate and named "
                "testing standards. Neither is in the conventions or the specification, and both "
                "have been removed."
            ),
        },
    },
}

PDF_BUCKET = "courses"
TABLE = "correction_notices"
SEND_GAP_SECONDS = 0.7  # stay inside the email provider's rate limit

# Progress of the current send, shown on the page. One send at a time.
_run = {"running": False, "total": 0, "sent": 0, "failed": 0, "skipped": 0, "finished_at": "", "task": None}


# ── Email text ────────────────────────────────────────────────────────────────

def notice_subject(course_ids: list[str]) -> str:
    plural = "courses" if len(course_ids) != 1 else "course"
    return f"Correction to your Meridian CPD RdSAP {plural}: updated edition attached"


def notice_body(notice: dict, name: str, course_ids: list[str], titles: dict, has_certificate: bool) -> str:
    first = (name or "").strip().split(" ")[0]
    greeting = f"Hello {first}," if first and "@" not in first else "Hello,"
    many = len(course_ids) != 1
    holding = (
        "you hold a Meridian CPD certificate for" if has_certificate
        else "you bought or downloaded"
    )
    listed = "\n\n".join(
        f"{cid}  {titles.get(cid, cid)}\nEarlier edition: {notice['changes'][cid]}"
        for cid in course_ids
    )
    return f"""{greeting}

I am writing because {holding} the RdSAP 10 {'courses' if many else 'course'} listed below.

We have re-checked our RdSAP 10 courses line by line against the Conventions (v12.2) for RdSAP 10, which apply from 6 August 2026, and the RdSAP10 Specification. The earlier {'editions' if many else 'edition'} contained statements that were wrong, or that we could not trace to either document. That should not have happened, and I am sorry.

The corrected {'editions are' if many else 'edition is'} attached. Every rule now carries its convention or specification reference, so you can check it for yourself.

WHAT CHANGED

{listed}

WHAT TO DO

1. Use the attached {'editions' if many else 'edition'} from now on and delete the earlier PDF.
2. If you applied something from the earlier edition on a survey and are unsure about it, check it against the reference given in the new edition. If you would like help finding the passage, reply to this email.

You do not need to retake anything, and your certificate still stands as a record of the CPD you completed. The corrected {'editions are' if many else 'edition is'} also in your library at {APP_HOST}/my-cpd.

Questions or concerns? Reply to this email and it comes straight to me.

Matt
Meridian CPD
hello@meridiancpd.co.uk
"""


# ── Data ──────────────────────────────────────────────────────────────────────

def _parse_ts(value) -> datetime | None:
    if not value:
        return None
    try:
        ts = datetime.fromisoformat(str(value).replace("Z", "+00:00"))
        return ts if ts.tzinfo else ts.replace(tzinfo=timezone.utc)
    except ValueError:
        return None


def find_recipients(supabase, notice: dict) -> list[dict]:
    """Members who hold a certificate for, bought, or downloaded an affected course."""
    course_ids = sorted(notice["changes"])
    held: dict[str, dict] = {}

    def note(member_id, course_id, reason):
        if not member_id or course_id not in notice["changes"]:
            return
        entry = held.setdefault(member_id, {"courses": set(), "reasons": set()})
        entry["courses"].add(course_id)
        entry["reasons"].add(reason)

    certs = supabase.table("certificates").select("member_id, course_id").in_("course_id", course_ids).execute()
    for row in certs.data or []:
        note(row.get("member_id"), row.get("course_id"), "certificate")

    purchases = supabase.table("purchases").select("member_id, course_id").in_("course_id", course_ids).execute()
    for row in purchases.data or []:
        note(row.get("member_id"), row.get("course_id"), "purchase")

    downloads = (
        supabase.table("completions").select("member_id, course_id, downloaded_at")
        .in_("course_id", course_ids).not_.is_("downloaded_at", "null").execute()
    )
    for row in downloads.data or []:
        note(row.get("member_id"), row.get("course_id"), "download")

    if not held:
        return []

    members = supabase.table("members").select("id, email, name, plan").in_("id", list(held)).execute()
    recipients = []
    for m in members.data or []:
        entry = held.get(m["id"])
        if not entry or not m.get("email"):
            continue
        recipients.append({
            "member_id": m["id"],
            "email": m["email"],
            "name": m.get("name") or "",
            "plan": m.get("plan") or "",
            "courses": sorted(entry["courses"]),
            "reasons": sorted(entry["reasons"]),
        })
    recipients.sort(key=lambda r: r["email"].lower())
    return recipients


def sent_log(supabase, notice_id: str) -> tuple[dict, str]:
    """Returns ({member_id: row}, problem). problem is non-empty if the table is unusable."""
    try:
        res = supabase.table(TABLE).select("member_id, status, sent_at").eq("notice_id", notice_id).execute()
        return {row["member_id"]: row for row in (res.data or [])}, ""
    except Exception as e:
        return {}, f"{type(e).__name__}"


def pdf_ages(supabase) -> dict:
    """{course_id: last-updated datetime} for the PDFs currently in storage."""
    ages = {}
    try:
        for obj in supabase.storage.from_(PDF_BUCKET).list("", {"limit": 1000}) or []:
            name = obj.get("name") or ""
            if not name.endswith(".pdf"):
                continue
            meta = obj.get("metadata") or {}
            stamps = [_parse_ts(obj.get("updated_at")), _parse_ts(meta.get("lastModified"))]
            stamps = [s for s in stamps if s]
            if stamps:
                ages[name[:-4]] = max(stamps)
    except Exception as e:
        print(f"Corrections: could not list course PDFs ({type(e).__name__})")
    return ages


def stale_courses(notice: dict, ages: dict, course_ids) -> list[str]:
    """Courses whose stored PDF is missing or older than the corrected edition."""
    cutoff = _parse_ts(notice["pdfs_updated_after"])
    return sorted(c for c in course_ids if c not in ages or ages[c] < cutoff)


def load_attachments(supabase, course_ids, cache: dict) -> list[dict]:
    attachments = []
    for cid in course_ids:
        if cid not in cache:
            data = supabase.storage.from_(PDF_BUCKET).download(f"{cid}.pdf")
            if not data or len(data) < 20_000:
                raise ValueError(f"PDF for {cid} is missing or too small to be a course")
            cache[cid] = base64.b64encode(data).decode()
        attachments.append({"filename": f"{cid}.pdf", "content": cache[cid]})
    return attachments


def _claim(supabase, notice_id: str, recipient: dict) -> bool:
    """Record that this member is being sent the notice. False means they already were."""
    row = {
        "notice_id": notice_id,
        "member_id": recipient["member_id"],
        "course_ids": recipient["courses"],
        "status": "sending",
    }
    try:
        supabase.table(TABLE).insert(row).execute()
        return True
    except Exception:
        # Already recorded. Only a previous failure may be retried.
        existing = (
            supabase.table(TABLE).select("status")
            .eq("notice_id", notice_id).eq("member_id", recipient["member_id"]).execute()
        )
        if existing.data and existing.data[0].get("status") == "failed":
            supabase.table(TABLE).update({"status": "sending", "error": None}).eq(
                "notice_id", notice_id).eq("member_id", recipient["member_id"]).execute()
            return True
        return False


async def _send_all(supabase, notice_id: str, notice: dict, recipients: list[dict], titles: dict):
    cache: dict = {}
    try:
        for r in recipients:
            try:
                claimed = _claim(supabase, notice_id, r)
            except Exception as e:
                # Could not record the send, so do not send: a duplicate is worse than a retry.
                _run["failed"] += 1
                print(f"Corrections: could not record member {r['member_id']} ({type(e).__name__})")
                continue
            if not claimed:
                _run["skipped"] += 1
                continue
            try:
                attachments = load_attachments(supabase, r["courses"], cache)
                await _send(
                    r["email"], r["name"] or "Meridian CPD member",
                    notice_subject(r["courses"]),
                    notice_body(notice, r["name"], r["courses"], titles, "certificate" in r["reasons"]),
                    attachments,
                )
                supabase.table(TABLE).update({
                    "status": "sent", "sent_at": datetime.now(timezone.utc).isoformat(),
                }).eq("notice_id", notice_id).eq("member_id", r["member_id"]).execute()
                _run["sent"] += 1
            except Exception as e:
                # Never put the member's address in the log.
                _run["failed"] += 1
                reason = f"{type(e).__name__}"
                print(f"Corrections: send failed for member {r['member_id']} ({reason})")
                try:
                    supabase.table(TABLE).update({"status": "failed", "error": reason}).eq(
                        "notice_id", notice_id).eq("member_id", r["member_id"]).execute()
                except Exception:
                    pass
            await asyncio.sleep(SEND_GAP_SECONDS)
    finally:
        _run["running"] = False
        _run["finished_at"] = datetime.now(timezone.utc).strftime("%H:%M UTC")


# ── Pages ─────────────────────────────────────────────────────────────────────

def build_router(supabase, check_admin, page, courses: dict) -> APIRouter:
    router = APIRouter()
    notice_id = "2026-10-rdsap"
    notice = NOTICES[notice_id]

    def titles() -> dict:
        return {cid: str(courses.get(cid, {}).get("title", cid)) for cid in notice["changes"]}

    def message(kind: str, text: str) -> str:
        colours = {"ok": ("#f0fdf4", "#22c55e"), "warn": ("#fffbeb", "#f59e0b"), "bad": ("#fef2f2", "#ef4444")}
        bg, border = colours[kind]
        return (f'<div style="background:{bg};border:1px solid {border};border-radius:8px;'
                f'padding:14px 18px;margin-bottom:18px;line-height:1.5">{text}</div>')

    def render(banner: str = "") -> HTMLResponse:
        recipients = find_recipients(supabase, notice)
        log, log_problem = sent_log(supabase, notice_id)
        ages = pdf_ages(supabase)
        stale = stale_courses(notice, ages, notice["changes"])
        t = titles()

        blocks = banner
        if log_problem:
            blocks += message("bad", "The <b>correction_notices</b> table is not available, so sending is "
                              "switched off. Run <code>webhook/migrations/2026-10-12_correction_notices.sql</code> "
                              "in the Supabase SQL editor, then reload this page.")
        if stale:
            blocks += message("bad", "Sending is switched off because the corrected PDF is not yet in storage for: "
                              f"<b>{html.escape(', '.join(stale))}</b>. Publish the corrected courses first.")
        if _run["running"]:
            blocks += message("warn", f"Sending in progress: {_run['sent']} sent, {_run['failed']} failed, "
                              f"{_run['skipped']} skipped, of {_run['total']}. Reload to update.")
        elif _run["finished_at"]:
            blocks += message("ok", f"Last send finished at {_run['finished_at']}: {_run['sent']} sent, "
                              f"{_run['failed']} failed, {_run['skipped']} already sent.")

        can_send = not log_problem and not stale and not _run["running"]
        waiting = [r for r in recipients if log.get(r["member_id"], {}).get("status") not in ("sent", "sending")]

        rows = ""
        for r in recipients:
            state = log.get(r["member_id"], {}).get("status", "")
            if state == "sent":
                tick, status = "", '<span style="color:#15803d">Sent</span>'
            elif state == "sending":
                tick, status = "", '<span style="color:#b45309">Started, not confirmed. Check before resending.</span>'
            else:
                tick = f'<input type="checkbox" name="member_id" value="{html.escape(r["member_id"])}" checked>'
                status = '<span style="color:#b91c1c">Failed, will retry</span>' if state == "failed" else "Not sent"
            rows += (f"<tr><td>{tick}</td><td>{html.escape(r['name']) or '—'}</td><td>{html.escape(r['email'])}</td>"
                     f"<td>{html.escape(r['plan'])}</td><td>{html.escape(', '.join(c[4:] for c in r['courses']))}</td>"
                     f"<td>{html.escape(', '.join(r['reasons']))}</td><td>{status}</td></tr>")

        sample = recipients[0] if recipients else {"name": "Sam Example", "courses": sorted(notice["changes"])[:2],
                                                   "reasons": ["certificate"]}
        preview = (f"Subject: {notice_subject(sample['courses'])}\n\n"
                   + notice_body(notice, sample["name"], sample["courses"], t, "certificate" in sample["reasons"]))

        disabled = "" if can_send else "disabled"
        body = f"""
        {blocks}
        <div class="card">
          <h2>Correction notice: {html.escape(notice['label'])}</h2>
          <p style="margin:10px 0;line-height:1.5">{len(recipients)} member(s) hold a certificate for, bought or
          downloaded an affected course. {len(waiting)} have not been sent the notice. Each person gets one email
          with only their own courses attached. Nothing is sent until you type SEND below.</p>
        </div>
        <div class="card">
          <h2>1. Send a test to yourself</h2>
          <form method="POST" action="/admin/corrections/test" style="margin-top:12px">
            <input type="email" name="email" required placeholder="your own address"
                   style="padding:8px;width:280px;border:1px solid #cbd5e1;border-radius:6px">
            <button {disabled} style="padding:8px 16px;background:#0891b2;color:white;border:none;border-radius:6px">
              Send test (all {len(notice['changes'])} courses attached)</button>
          </form>
        </div>
        <form method="POST" action="/admin/corrections/send">
        <div class="card">
          <h2>2. Who will receive it</h2>
          <p style="margin:8px 0;color:#64748b">Untick anyone who should not get it (test accounts, for example).</p>
          <table>
            <tr><th></th><th>Name</th><th>Email</th><th>Plan</th><th>Courses</th><th>Why</th><th>Status</th></tr>
            {rows or '<tr><td colspan="7" class="empty">Nobody holds an affected course.</td></tr>'}
          </table>
        </div>
        <div class="card">
          <h2>3. Send</h2>
          <p style="margin:8px 0">Type <b>SEND</b> to confirm. This emails every ticked member and cannot be undone.</p>
          <input name="confirm" autocomplete="off" placeholder="SEND"
                 style="padding:8px;width:120px;border:1px solid #cbd5e1;border-radius:6px">
          <button {disabled} style="padding:8px 16px;background:#b91c1c;color:white;border:none;border-radius:6px">
            Send correction notice</button>
        </div>
        </form>
        <div class="card">
          <h2>What they will receive (example)</h2>
          <pre style="white-space:pre-wrap;font-family:inherit;line-height:1.5;margin-top:12px">{html.escape(preview)}</pre>
        </div>"""
        return page("Corrections", "corrections", body)

    @router.get("/admin/corrections", response_class=HTMLResponse)
    async def corrections_page(credentials=Depends(check_admin)):
        return render()

    @router.post("/admin/corrections/test", response_class=HTMLResponse)
    async def corrections_test(request: Request, credentials=Depends(check_admin)):
        form = await request.form()
        email = str(form.get("email", "")).strip()
        if "@" not in email or " " in email:
            return render(message("bad", "Enter the address the test should go to."))
        course_ids = sorted(notice["changes"])
        stale = stale_courses(notice, pdf_ages(supabase), course_ids)
        if stale:
            return render(message("bad", "Test not sent: the corrected PDFs are not all in storage yet."))
        try:
            attachments = load_attachments(supabase, course_ids, {})
            await _send(email, "Test", "[TEST] " + notice_subject(course_ids),
                        notice_body(notice, "Test", course_ids, titles(), True), attachments)
        except Exception as e:
            return render(message("bad", f"Test not sent ({html.escape(type(e).__name__)}). Nothing was recorded."))
        return render(message("ok", f"Test sent to {html.escape(email)}. Nothing was recorded against any member."))

    @router.post("/admin/corrections/send", response_class=HTMLResponse)
    async def corrections_send(request: Request, credentials=Depends(check_admin)):
        form = await request.form()
        if str(form.get("confirm", "")).strip() != "SEND":
            return render(message("bad", "Nothing sent. Type SEND in capitals to confirm."))
        if _run["running"]:
            return render(message("warn", "A send is already running."))
        _, log_problem = sent_log(supabase, notice_id)
        if log_problem:
            return render(message("bad", "Nothing sent: the correction_notices table is not available."))
        chosen = {str(v) for v in form.getlist("member_id")}
        recipients = [r for r in find_recipients(supabase, notice) if r["member_id"] in chosen]
        if not recipients:
            return render(message("bad", "Nothing sent: nobody was ticked."))
        needed = {c for r in recipients for c in r["courses"]}
        stale = stale_courses(notice, pdf_ages(supabase), needed)
        if stale:
            return render(message("bad", "Nothing sent: the corrected PDFs are not all in storage yet."))
        _run.update({"running": True, "total": len(recipients), "sent": 0, "failed": 0, "skipped": 0,
                     "finished_at": ""})
        # Keep a reference so the task cannot be garbage-collected part-way through.
        _run["task"] = asyncio.create_task(_send_all(supabase, notice_id, notice, recipients, titles()))
        return render(message("ok", f"Sending to {len(recipients)} member(s) has started. Reload this page in a "
                                    "minute to see the result."))

    return router
