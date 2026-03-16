# Meridian CPD — Master Build Instructions
**Last updated:** 2026-03-14
**Status:** Active build

Claude: read this file at the start of every session. Work through BUILD STATUS top to bottom.
Do not ask Matt questions unless something is blocked. Build autonomously where possible.

---

## What Meridian CPD Is

A fully automated CPD subscription platform for UK Domestic Energy Assessors (DEAs),
Retrofit Assessors, and Retrofit Coordinators. Zero hands-on operation after setup.

- **Domain:** meridiancpd.co.uk (GoDaddy — DNS managed there)
- **Email:** hello@meridiancpd.co.uk (Google Workspace, £7/month)
- **Tagline:** Stay Sharp. Stay Certified.
- **Tone:** Expert-to-expert. Peer professional. Not corporate, not patronising.
- **Full system design:** `/Users/mac/Documents/meridian-cpd/MERIDIAN_SYSTEM.md`

---

## Accounts & Keys

| Service | Account | Key/Location |
|---------|---------|--------------|
| Stripe | Matt's account | Single course: https://buy.stripe.com/9B6bJ0bsefk72j02zE73G00 (£19.99) |
| Stripe | Matt's account | Annual sub: https://buy.stripe.com/fZufZgbse3BpcXE7TY73G01 (£79/yr) |
| Instantly | Matt's account | API key in Email Optimizer .env |
| Apify | Matt's account | Token in Email Optimizer .env |
| Anthropic | Matt's account | Key in Email Optimizer .env |
| GitHub | mattid272-hub | Email optimizer repo live |
| Supabase | Matt's account | Project: cpkyloywjmpesmjgqaxm.supabase.co |
| Railway | NOT YET CREATED | Matt needs to create — see Priority 1 |

---

## File Locations

```
/Users/mac/Documents/meridian-cpd/
  CLAUDE.md                          ← this file
  MERIDIAN_SYSTEM.md                 ← full system design + curriculum map
  MERIDIAN_ACTION_PLAN.md            ← superseded by this file
  MER-DEA-001_RdSAP10_WhatChanged.pptx  ← flagship course (needs PDF export)
  logo/
    meridian-cpd-logo.svg
    meridian-cpd-logo.svg.png
  courses/                           ← generated course PDFs go here
  webhook/                           ← Stripe webhook app (build here)
  landing-page/                      ← meridiancpd.co.uk site (build here)
  certificates/                      ← certificate generator (build here)
  content-engine/                    ← automated course builder (build here)

/Users/mac/Documents/Email Optimizer Demo/
  ← autonomous A/B email engine (built, deployed, warming up)
```

---

## BUILD STATUS

Work through these in order. Do not skip ahead.

---

### [DONE] Email Outreach Engine
- Instantly.ai connected (hello@meridiancpd.co.uk via Google Workspace)
- GitHub Actions cron deployed (every 4 hours)
- Warm-up running — do not fire campaigns until warm-up score ≥ 80 in Instantly
- Baseline email configured: subject "rdSAP 10 cpd?", targets UK DEAs

---

### [DONE] Stripe Products
- MER-DEA-001 single course: £19.99 payment link live
- Annual subscription: £79/year payment link live
- Promo code: MERIDIAN10 (free 2-hr RdSAP 10 overview)

---

### [ ] PRIORITY 1 — Course Delivery Webhook

**What:** When someone pays on Stripe, they automatically receive the PDF course by email.

**Build location:** `/Users/mac/Documents/meridian-cpd/webhook/`

**Stack:** Python (FastAPI), deploy on Railway (free tier covers this)

**Files to create:**
- `webhook/main.py` — FastAPI app with /stripe-webhook endpoint
- `webhook/requirements.txt`
- `webhook/email_sender.py` — Gmail API sender
- `webhook/Procfile` — for Railway deployment
- `webhook/railway.json`

**Logic:**
1. Stripe sends POST to /stripe-webhook on checkout.session.completed
2. Verify Stripe signature (STRIPE_WEBHOOK_SECRET env var)
3. Extract: customer email, customer name, product purchased
4. Determine which course(s) to send (single course or all for subscription)
5. Send email via Gmail API with PDF attachment (or signed Supabase Storage URL)
6. Log purchase to Supabase: members table

**Supabase tables needed:**
```sql
CREATE TABLE members (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  email TEXT UNIQUE NOT NULL,
  name TEXT,
  plan TEXT CHECK (plan IN ('single', 'subscription')),
  courses_purchased TEXT[] DEFAULT '{}',
  joined_at TIMESTAMPTZ DEFAULT NOW(),
  subscription_expires_at TIMESTAMPTZ,
  stripe_customer_id TEXT
);

CREATE TABLE purchases (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  member_id UUID REFERENCES members(id),
  course_id TEXT,
  stripe_session_id TEXT UNIQUE,
  amount_gbp NUMERIC(10,2),
  purchased_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE completions (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  member_id UUID REFERENCES members(id),
  course_id TEXT NOT NULL,
  completed_at TIMESTAMPTZ DEFAULT NOW(),
  completion_token TEXT UNIQUE  -- single-use token sent in course email
);
```

**Completion + certificate flow:**
1. Customer pays → webhook fires → PDF emailed with a unique completion link
   e.g. `meridiancpd.co.uk/complete/[one-time-token]`
2. Customer reads course, clicks the link → "I have read and completed this course" confirmation page
3. On confirmation: certificate generated instantly + emailed as PDF attachment
4. Completion logged to Supabase completions table
5. Certificate logged to certificates table
6. Token marked used (cannot be reused)

**Important:** Certificate is evidence of COMPLETION, not payment.
This is the correct basis for CPD claims.

**Matt touchpoints (after code is written):**
1. Create Railway account at railway.app → deploy (I'll give exact commands)
2. Copy webhook URL into Stripe Dashboard → Developers → Webhooks → Add endpoint
3. Copy STRIPE_WEBHOOK_SECRET back here

---

### [ ] PRIORITY 2 — Certificate Generator

**What:** Monthly batch job — generates tamper-proof PDF certificates for all members
who completed a course that month. Emails as attachment. Logs to Supabase.

**Build location:** `/Users/mac/Documents/meridian-cpd/certificates/`

**Stack:** Python (reportlab for PDF generation)

**Certificate features:**
- Meridian CPD logo (use logo/meridian-cpd-logo.svg)
- Recipient name, course title, CPD hours, completion date, certificate number
- Unique cert number format: MER-YYYY-NNNN (e.g. MER-2026-0001)
- QR code linking to meridiancpd.co.uk/verify/MER-2026-0001
- Flattened PDF (no editable fields, no selectable text — rasterised output)
- Subtle diagonal watermark pattern in background
- Copyright notice: © Meridian CPD 2026. All rights reserved.
- Disclaimer: "Meridian CPD is an independent CPD provider. Acceptance of CPD hours
  is at the discretion of your accreditation body."

**Supabase table:**
```sql
CREATE TABLE certificates (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  cert_number TEXT UNIQUE NOT NULL,  -- MER-2026-0001
  member_id UUID REFERENCES members(id),
  course_id TEXT NOT NULL,
  course_title TEXT NOT NULL,
  cpd_hours NUMERIC(4,1) NOT NULL,
  issued_at TIMESTAMPTZ DEFAULT NOW(),
  issued_for_month TEXT  -- e.g. "2026-03"
);
```

**Verification endpoint:** Build as part of the landing page.
GET /verify/[cert-number] → returns certificate details from Supabase.

**GitHub Actions cron:** Run on 1st of each month.

---

### [ ] PRIORITY 3 — Landing Page (meridiancpd.co.uk)

**What:** Single-page website. Must be live before campaigns fire.

**Build location:** `/Users/mac/Documents/meridian-cpd/landing-page/`
**Deploy:** GitHub Pages (free) — new repo: `meridian-cpd-site`

**Sections:**
1. Header: logo + nav (Courses / Subscribe / Verify Certificate)
2. Hero: "CPD for energy assessors. Built by assessors." + RdSAP 10 urgency hook
3. Why Meridian: 3 points (practitioner-written / downloadable PDF / certificates issued monthly)
4. Pricing: £19.99/course OR £79/year unlimited — both Stripe links
5. Course catalogue: grid of available courses (start with launch pack)
6. Sample certificate: screenshot/mockup
7. FAQ: Is this CPD accepted by my scheme? / How do I get my certificate? / etc.
8. Footer: © Meridian CPD 2026 | hello@meridiancpd.co.uk | Privacy Policy | Unsubscribe

**Colours (from logo):**
- Navy: #0f2547
- Cyan: #0891b2
- White: #ffffff
- Light grey bg: #f8fafc

**Verify endpoint:** /verify/[cert-number] — simple fetch from Supabase, display cert details.

**Matt touchpoint:** Add CNAME DNS record in GoDaddy pointing meridiancpd.co.uk → GitHub Pages
(I'll give the exact record to add)

---

### [ ] PRIORITY 4 — Course Back Catalogue (Launch Pack)

**Target:** 12 courses ready before first email campaign fires.
**All ⚡ courses from MERIDIAN_SYSTEM.md curriculum map.**

**Process for each course:**
1. Claude generates course content from authoritative sources (see source list below)
2. Output as structured markdown
3. Convert to PDF using weasyprint with Meridian branded template
4. Save to `/Users/mac/Documents/meridian-cpd/courses/[course-id]/`
5. Upload PDF to Supabase Storage (public bucket: `courses`)

**Launch pack — build in this order:**

| # | Course ID | Title | Hours |
|---|-----------|-------|-------|
| 1 | MER-DEA-001 | RdSAP 10: What's Changed and Why | 2 | ← PowerPoint exists, needs PDF export |
| 2 | MER-DEA-002 | Measuring Windows in RdSAP 10 | 1 | ← generate |
| 3 | MER-DEA-003 | Ventilation in RdSAP 10: PIV, MVHR, Natural | 1 | ← generate |
| 4 | MER-DEA-004 | Room in Roof: Type 1 and Type 2 | 1 | ← generate |
| 5 | MER-DEA-010 | Lighting and Renewables in RdSAP 10 | 1 | ← generate |
| 6 | MER-DEA-011 | Solar PV, Battery Storage and PV Diverters | 1 | ← generate |
| 7 | MER-DEA-021 | Airtightness Testing in RdSAP 10 | 1 | ← generate |
| 8 | MER-RA-001 | PAS 2035:2023 Overview | 2 | ← generate |
| 9 | MER-RA-006 | EPR Variation: RdSAP 10 Transition | 1 | ← generate |
| 10 | MER-RA-009 | EWI: Planning Permission and Fire Risk | 1 | ← generate |
| 11 | MER-ALL-001 | UK Energy Policy 2026 | 1 | ← generate |
| 12 | MER-ALL-004 | Fire Safety in Retrofit | 1 | ← generate |

**Authoritative sources for course generation:**
- RdSAP 10 Technical Manual (BRE, 2024)
- PAS 2035:2023 (BSI)
- TrustMark Framework Operating Requirements
- GOV.UK: energy efficiency policy, MEES guidance
- CIBSE TM guides
- Elmhurst/Quidos technical bulletins (publicly available)

**Course structure (every course):**
```
# [Title]
Course ID: [ID] | CPD Hours: [X] | Published: [Month Year]
© Meridian CPD 2026. All rights reserved.

## Learning Objectives
[3-5 bullet points]

## Introduction
[~300 words]

## Section 1: [Title]
[~400 words]

## Section 2: [Title]
[~400 words]

## Section 3: [Title]
[~400 words]

[Additional sections as needed]

## Key Takeaways
[5-7 bullet points]

## Self-Assessment Questions
[5 multiple choice questions with answers]

## Further Reading
[3-5 references to primary sources]

---
© Meridian CPD 2026. All rights reserved. Unauthorised reproduction prohibited.
This course material is licensed to individual subscribers only.
```

---

### [ ] PRIORITY 5 — Automated Content Engine

**What:** Twice-monthly cron that monitors industry sources, generates BRAND NEW courses
from fresh material, adds them to the ever-growing library, notifies subscribers.
The library compounds — every course ever created stays permanently available for purchase.
Nothing is repeated or recycled. Each run produces 1 new course from current source material.

**Build location:** `/Users/mac/Documents/meridian-cpd/content-engine/`

**Schedule:** GitHub Actions — 1st and 15th of each month

**Files:**
- `content_engine.py` — source monitor + Claude content generator
- `course_publisher.py` — PDF build + Supabase upload + member email
- `sources.json` — list of URLs to monitor

**Sources to monitor:**
```json
[
  "https://www.gov.uk/search/policy-papers-and-consultations?keywords=energy+efficiency",
  "https://www.trustmark.org.uk/news",
  "https://www.elmhurstenergy.co.uk/news",
  "https://www.quidos.co.uk/news",
  "https://www.ecmk.co.uk/news",
  "https://www.bre.co.uk/news",
  "https://www.ofgem.gov.uk/check-if-energy-price-cap-affects-you",
  "https://www.cibse.org/news"
]
```

---

### [ ] PRIORITY 6 — Member CPD Dashboard

**What:** meridiancpd.co.uk/dashboard — members log in, see CPD hours, download certs.

**Auth:** Magic link email (no password). Supabase Auth.

**Build:** Next.js (reuse Supabase setup from RetroTrack — different project/tables).

**Defer until:** Priorities 1-4 are complete and first paying customers exist.

---

## NotebookLM Integration

Notebook: "Meridian CPD — Research & Content"
Sources to add:
- MERIDIAN_SYSTEM.md
- MER-DEA-001 PowerPoint (once PDF exported)
- RdSAP 10 Technical Manual (upload when available)
- PAS 2035:2023 summary

Use for: research queries when generating course content. Not for automation.

---

## What Matt Needs to Do (Touchpoints Only)

| # | Task | When |
|---|------|------|
| 1 | Export MER-DEA-001 PowerPoint → PDF (File → Export as PDF on Mac) | Now |
| 2 | Create Railway account at railway.app | When webhook is built |
| 3 | Add webhook URL to Stripe → Developers → Webhooks | After Railway deploy |
| 4 | Add CNAME DNS record in GoDaddy for GitHub Pages | When landing page is built |
| 5 | Complete Stripe identity verification (to go live) | Before campaigns fire |

---

## Safety Rules

- NEVER delete Instantly campaigns without Matt's explicit confirmation
- NEVER overwrite data/active_experiments.json or results/results.log
- NEVER push to GitHub without checking .gitignore excludes .env files
- All course content must be based on primary regulatory sources — never fabricated
- Certificates must only be issued for courses the member has actually purchased
