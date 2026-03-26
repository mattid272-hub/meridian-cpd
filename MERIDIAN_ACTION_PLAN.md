# Meridian CPD — Action Plan
**Created:** 2026-03-13
**Priority:** Build the full automated platform during the 2-3 week email warm-up window

---

## The Goal

A fully automated CPD subscription platform for UK DEAs and Retrofit Assessors.
Zero hands-on operation after setup. Two new CPD sessions published per month
(24 hrs/year for subscribers). Self-building content library. Tamper-proof certificates.

---

## What We Have Right Now

- [x] meridiancpd.co.uk domain (GoDaddy)
- [x] hello@meridiancpd.co.uk (Google Workspace, £7/month)
- [x] Stripe — single course £19.99 + annual subscription £79/year
- [x] Course MER-DEA-001: RdSAP 10 What Changed (14-slide PowerPoint)
- [x] Email outreach engine (GitHub Actions, Instantly, Apify — warming up)
- [x] Logo (SVG + PNG)

---

## What Needs Building (Priority Order)

---

### PRIORITY 1 — Course Delivery (must exist before first sale)

**The problem:** Someone pays on Stripe → nothing happens automatically.

**The solution:** Stripe webhook → auto-email the PDF course + download link.

**Build:**
- Stripe webhook endpoint (simple Python/Node function, deploy on Railway or Vercel)
- On `checkout.session.completed` event:
  - Send transactional email via Gmail API (hello@meridiancpd.co.uk)
  - Email contains: welcome message + secure download link to PDF
  - Log customer in Supabase: `members` table (email, name, plan, joined_at, courses[])
- Secure download links: time-limited signed URLs (24hr expiry) — prevents sharing

**Deliverable:** Pay → receive email with PDF within 60 seconds. Automatic.

---

### PRIORITY 2 — Tamper-Proof Certificate Generation

**Requirements:**
- Unique certificate number (e.g. MER-2026-0001)
- Candidate name, course title, CPD hours, date issued
- QR code linking to a verification URL (meridiancpd.co.uk/verify/MER-2026-0001)
- Issued as a **flattened PDF** — no editable fields, no copy-paste of text
- Background watermark pattern (makes scanning/editing obvious)
- Issued monthly in batch for all active subscribers

**Build:**
- Python script using `reportlab` or `weasyprint` to generate PDFs
- Certificate records stored in Supabase: `certificates` table
- Verification endpoint: meridiancpd.co.uk/verify/[cert-id] → shows cert details
- Monthly GitHub Actions cron triggers batch certificate generation + email delivery
- Certificates emailed as PDF attachments (not download links — attachment is harder to tamper with)

**Security note:** Flattened PDF + embedded QR verification means any edited copy
will fail verification. Accreditation bodies can check the QR code.

---

### PRIORITY 3 — Member CPD Tracker

**What members see at meridiancpd.co.uk/dashboard:**
- Total CPD hours logged this year
- List of completed courses with certificate download links
- Progress toward annual target (10 hrs minimum)
- Upcoming course release dates

**Build:**
- Simple Next.js app (reuse Supabase already set up for RetroTrack)
- Auth: magic link email (no password needed — they click a link in email)
- Dashboard reads from Supabase `members` + `certificates` tables
- Mobile-friendly (DEAs check this on phone)

---

### PRIORITY 4 — Automated Content Engine

**How it works:**
- Cron runs twice a month (1st and 15th)
- Scrapes industry sources for new developments
- Claude compiles a structured 2-hour CPD session from the raw material
- Output: PDF course + metadata (title, CPD hours, category, release date)
- Auto-publishes to member library + triggers email bulletin to all subscribers

**Authoritative sources to scrape:**
- GOV.UK: planning updates, energy efficiency consultations (DLUHC)
- BRE Group (bre.co.uk): SAP/RdSAP technical notes
- CIBSE (cibse.org): guidance documents and TM updates
- Elmhurst Energy (elmhurstenergy.co.uk): DEA software updates, bulletins
- Quidos (quidos.co.uk): accreditation notices
- ECMK (ecmk.co.uk): scheme updates
- Stroma Certification: technical bulletins
- TrustMark (trustmark.org.uk): retrofit standards updates
- PAS 2035/2030 BSI updates

**Course structure (Claude generates from scraped content):**
- Title + CPD hours (always 2.0)
- Learning objectives (3-5 bullet points)
- Main content sections (4-6 sections, ~400 words each)
- Key takeaways
- Self-assessment questions (5 questions, multiple choice)
- References/further reading

**Build:**
- `content_engine.py` — scraper + Claude content generator
- `course_publisher.py` — PDF generation + Supabase upload + member notification
- Output stored in: `/courses/[YEAR]/[MER-XXX-NNN]/` with PDF + metadata.json
- GitHub Actions cron: 1st and 15th of each month

---

### PRIORITY 5 — Landing Page (meridiancpd.co.uk)

**Must have before campaigns fire:**
- Hero: "CPD for energy assessors. Built by assessors."
- RdSAP 10 urgency hook
- Pricing: £19.99/course or £79/year unlimited
- Course catalogue (even just 1-2 to start)
- Sample certificate image
- Payment links to Stripe

**Build:** Single HTML page, deploy on GitHub Pages (free, instant, no server needed).
Can be upgraded to Next.js later.

---

## Back Catalogue Build Plan (Next 2-3 Weeks)

Use the warm-up window to build a library of 6 courses before first email goes out.
Target course list:

| Code | Title | CPD Hrs | Status |
|------|-------|---------|--------|
| MER-DEA-001 | RdSAP 10: What Changed | 2.0 | Done (PowerPoint) — needs PDF conversion |
| MER-DEA-002 | PAS 2035 Retrofit Coordinator Essentials | 2.0 | To build |
| MER-DEA-003 | EPC Lodgement: Common Errors and How to Avoid Them | 2.0 | To build |
| MER-DEA-004 | Fabric First: Insulation Options Under RdSAP 10 | 2.0 | To build |
| MER-DEA-005 | Heat Pumps and EPCs: What DEAs Need to Know | 2.0 | To build |
| MER-DEA-006 | GDPR for Energy Assessors: Client Data Handling | 2.0 | To build |

MER-DEA-002 through MER-DEA-006 can be generated by the content engine using
Claude + authoritative sources. Each takes ~10 minutes to generate and review.

---

## Infrastructure Summary

| Component | Tool | Cost |
|-----------|------|------|
| Database | Supabase (existing) | Free tier |
| Email delivery | Gmail API (hello@) | Included in £7/month |
| PDF generation | Python reportlab | Free |
| Webhook host | Railway | ~£5/month |
| Landing page | GitHub Pages | Free |
| Content cron | GitHub Actions | Free |
| Certificate cron | GitHub Actions | Free |

---

## Session Start Instructions (Tomorrow)

When this file is opened, work through the following in order:

1. **Convert MER-DEA-001 PowerPoint → PDF** (Adobe or LibreOffice)
2. **Build Stripe webhook + delivery email** (Priority 1)
3. **Set up Supabase members + certificates tables**
4. **Generate MER-DEA-002 using content engine** (test the pipeline)
5. **Build certificate PDF template** (Priority 2)
6. **Build landing page** (Priority 5 — needed before campaigns fire)

Do not start the member dashboard (Priority 3) until Priorities 1, 2, and 5 are done.
