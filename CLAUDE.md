# Meridian CPD: working instructions
**Last updated:** 2026-10-23
**Status:** live and selling; Ireland and Scotland in research

Claude: read this file at the start of every session, then the project docs in the Claude Project "Meridian CPD" (the launch checklist is the running state). Work autonomously; ask Matt only when a decision can't be undone and could go either way.

---

## What Meridian CPD is

An automated CPD platform for UK Domestic Energy Assessors, Retrofit Assessors and Retrofit Coordinators, written from primary sources and sold as PDF courses with certificates issued on completion. Trading name of FistralAI Ltd (company 17091704, England and Wales). Run by Matt Davies and Ceri Pearce, both practising assessors.

- **Site:** meridiancpd.co.uk (GitHub Pages from `landing-page/`, DNS at GoDaddy)
- **App:** app.meridiancpd.co.uk (FastAPI in `webhook/`, Railway service laudable-eagerness, auto-deploys from `main`)
- **Email:** hello@meridiancpd.co.uk (Google Workspace); transactional and outreach mail through Resend
- **Data:** Supabase project cpkyloywjmpesmjgqaxm (members, purchases, completions, certificates, outreach tables, Storage bucket `courses`)
- **Payments:** Stripe Payment Links, £19.99 a course and £79 a year (rising to £99 on 1 January 2027); promo MERIDIAN10 gives the RdSAP 10 overview free
- **Brand:** dark green #0D1F0E and lime #D4FF00 (site, social and email all use it). Tagline: Stay Sharp. Stay Certified. Tone: expert to expert; peer professional; no marketing fluff.
- **Library:** 37 courses, 39 CPD hours (12 DEA, 12 RA, 13 for every assessor), each labelled with where it applies (England, Wales and Scotland / England and Wales / England / Scotland / UK-wide).

Secrets (Stripe, Resend, Supabase service key, admin password, Instantly, Apify, Anthropic) live in Railway Variables and in git-ignored `.env` files. They are never written into this repo, the handover notes or a chat.

---

## Repository map

```
CLAUDE.md                       this file
MERIDIAN_SYSTEM.md              original system design and curriculum map (historical; the catalogue in webhook/main.py is the truth)
ACCREDITATION_ACTION_PACK.md    accreditation-body approach notes
webhook/                        the app: main.py (routes, catalogue, checkout, certificates, members area, admin), outreach.py (drip sender), certificate_generator.py, email_sender.py, settings.py, migrations/, tests/, DEPLOY.md
landing-page/                   the public site (index, courses.html with the catalogue array, pricing, verify, legal pages, CNAME)
courses/                        one folder per course: <id>.md source and the built PDF (PDFs are git-ignored; the live copies are in Supabase Storage); build scripts
content-engine/                 the twice-monthly course generator (paused) and its sources.json / reference_library.json
logo/                           brand assets
tools/                          one-off scripts (upload_pdfs_to_supabase.py)
reference/                      git-ignored working material: standards/ (full-text extractions of SEAI, gov.ie, BRE and gov.scot documents, UK and Ireland), rdsap-conventions/, course-correction/
.github/workflows/              deploy-pages, health-report, content-engine (cron commented out), republish-courses
```

Only on Matt's Mac, never in the repo: `Meridian Ire&Sco/` (unreviewed Irish and Scottish drafts), `Meridian/meridian-outreach/` (the old SendGrid engine, idle), `HANDOVER.md`, `_to_delete/`, `.env`.

---

## How the pieces work

- **Checkout:** Stripe Payment Link → `POST /stripe-webhook` → member and purchase rows → course email with a one-time completion link → `/complete/<token>` → certificate generated, numbered MER-YYYY-NNNN, emailed, verifiable at `/verify/<number>`. Certificates evidence completion, never payment.
- **Catalogue:** `COURSES` in `webhook/main.py` is the baseline; `courses/catalogue.json` in Storage adds anything published since the last deploy; `UNDER_REVIEW` hides a course from sale. The site's catalogue is the array in `landing-page/courses.html` (keep the two in step, including the `where` label).
- **Outreach:** `webhook/outreach.py` drips the queued campaign 08:00 to 18:00 UK, Monday to Friday, 50 a day, with one-click unsubscribe and bounce polling; Admin → Outreach pauses and resumes. Campaign statuses are `app_active` / `app_paused` only.
- **Admin:** `/admin` on the app, basic auth. System page lists the environment variables it expects.
- **Content:** every course is written from primary documents, cited by section or convention, with gaps declared in the text. Structure: objectives, introduction, 3 to 8 sections, key takeaways, five MCQs with answers, further reading, copyright footer. 1 hour ≈ 3,000 to 3,500 words. Source texts are in `reference/standards/`; the extraction procedure is the `meridian-source-library` skill. A NotebookLM notebook "Meridian CPD — Ireland" holds the Irish sources.

---

## Where things stand (23 October 2026)

Done: site, app, checkout, certificates, members area, admin, 37-course library (rewritten against current sources, autumn 2026), outreach sender (corporate wave 1 running from 23 October), social schedule to 24 November, jurisdiction labels (PR 24).

In progress: Ireland (seven draft courses MER-IE-001 to 007 written from the DEAP Guide 4.3.1 portal, the Code of Practice v1.6, TGD L 2022 and TGD F 2019; platform route agreed as "integrated"; nothing sold until SEAI confirms in writing how an independent provider's course is treated under the CPD policy and an Irish BER assessor has lodged a Meridian certificate), Scotland (two draft courses; 27 of 37 library courses apply there as they stand), HEM course series (back burner until the government response to the January 2026 HEM-for-EPCs consultation), admin news banner, £99 price rise on 1 January.

Matt's touchpoints: merge PRs; send the SEAI email and the Irish-assessor ask; Ceri's yes on social post 11; reshare LinkedIn page posts from his profile; Instagram connection; ad spend caps.

---

## Safety rules

- Never delete Instantly campaigns, Supabase rows, contact data or Railway services without Matt's explicit confirmation. Files on Matt's Mac go to `_to_delete/` for him, never deleted.
- Never push to GitHub without checking `.gitignore`; this repository is public. Never commit `.env`, handover notes, course drafts, licensed standards or extracted source texts.
- Never write a password, key or token into a file or a chat, and never repeat one that appears in a file; compare by hash if a check is needed.
- Never echo contacts' or customers' names or emails from the database or inbox into chat.
- Never set `outreach_campaigns.status` to `active`: that word belongs to the old Node engine and would start it sending.
- Emails to customers or prospects are drafted in hello@ for Matt to send; never sent by Claude. Nothing is posted or scheduled publicly without Matt's approval, and no ad spend without his cap.
- All course content comes from primary regulatory sources, never fabricated; where a source could not be opened, the course says so. Certificates are issued only for courses the member purchased and completed.
- The 12 June-2026 unsubscribers stay on the suppression list for good.
