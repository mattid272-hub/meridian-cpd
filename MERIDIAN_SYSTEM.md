# Meridian CPD — System Design & Curriculum Map
**Version 1.0 · March 2026 · Confidential**

---

## The Brand

**Meridian CPD**

A meridian is a precise line of measurement — exactly what DEAs and retrofit assessors do. It implies precision, professional standards, navigation, and direction. It is short, memorable, and credible.

- **Domain to register:** meridiancpd.co.uk
- **Tagline:** *Stay Sharp. Stay Certified.*
- **Tone:** Expert-to-expert. Not patronising, not corporate. This is a professional talking to professionals.
- **Positioning:** The independent CPD resource for energy assessors and retrofit professionals. Not an accreditation body. Not a training college. The specialist, always-current subscription service that keeps you compliant and ahead.

---

## The Market

| Segment | Estimated UK Numbers | CPD Requirement | Priority |
|---|---|---|---|
| Active DEAs (Domestic Energy Assessors) | ~18,000–20,000 | 10 hours/year mandatory | ⚡ Primary |
| Retrofit Assessors | ~3,000–5,000 (growing) | 10 hours/year mandatory | ⚡ Primary |
| Retrofit Coordinators | ~1,500–2,500 | 25 hours/year mandatory | High |
| Non-Domestic Energy Assessors (NDEAs) | ~3,000 | 10 hours/year | Secondary |
| Display Energy Certificate Assessors | ~2,000 | 10 hours/year | Secondary |

**Total addressable market:** ~27,000–32,000 professionals with mandatory CPD requirements.

**The hook:** RdSAP 10 launched June 2025 — the biggest methodology change in 13 years. Every active DEA in the UK needs to understand it. New EPC reform consultation is ongoing. The sector never stops changing. That change is Meridian's fuel.

---

## Pricing Model

| Tier | Price | What's Included |
|---|---|---|
| **Pay Per Course** | £12–£25 per course | Single course download + certificate on completion |
| **Annual Subscription — Assessor** | £79/year | Unlimited DEA/RA course library + monthly new releases + certificate tracking |
| **Annual Subscription — Professional** | £129/year | Full library (all strands) + priority access to new courses + downloadable CPD log |
| **Team / Organisation** | £POA | Bulk licences for accreditation bodies, training providers, employers |

**Revenue projection at modest penetration:**
- 500 subscribers at £79/year = £39,500 ARR
- 1,000 subscribers at average £95/year = £95,000 ARR
- Add pay-per-course revenue on top

---

## Content Ownership & Protection

### What We Are Building

All Meridian CPD course content is **original intellectual property**. Content is:
- Informed by the existing curriculum landscape (ECMK, Elmhurst, Quidos, TrustMark, BRE, DESNZ publications)
- Written from primary regulatory and technical sources (PAS 2035, RdSAP documentation, TrustMark Framework Operating Requirements)
- Never copied or reproduced from third-party materials
- Produced by qualified practitioners (Seren Surveying credentials)

This makes the content both legally clean and more valuable — it reflects real-world professional experience, not just rehashed course notes.

### Protection Mechanisms

| Layer | Method |
|---|---|
| **Legal** | Copyright notice on every slide and document. "© Meridian CPD [Year]. All rights reserved. Unauthorised reproduction or redistribution is prohibited." |
| **Technical — PDF** | Export all courses as PDF with password protection, print restriction, and no-copy flags |
| **Technical — PPTX** | Watermark every slide with subscriber name + unique licence ID (mail-merge approach) |
| **Technical — Delivery** | Courses delivered via a subscriber portal, not as open downloads. Link-based with expiry. |
| **Certificate Control** | Certificates issued only from Meridian — not included in the course file itself. Issued separately on completion verification. |
| **Marking** | Each course file contains a unique subscriber-specific tracking ID embedded in metadata |

### What Redistribution Protection Does NOT Require

- DRM software (overkill for this market, adds friction)
- Blockchain certificates (unnecessary complexity)
- Video-only format (PDFs are fine — assessors are used to reading technical material)

---

## The Content Engine — Weekly Refresh Cycle

### How New Content Is Generated

**Weekly monitoring sources:**
1. GOV.UK energy efficiency policy updates (DESNZ, MHCLG)
2. TrustMark scheme update bulletins
3. Ofgem ECO4/GBIS scheme changes
4. ECMK, Elmhurst, Quidos technical bulletins (publicly available)
5. BRE / SAP/RdSAP documentation updates
6. Gas Safe Register technical notices
7. MCS (Microgeneration Certification Scheme) updates
8. PAS 2035 / BSI standard revisions
9. MEES enforcement guidance updates
10. Retrofit Academy updates

**Weekly workflow:**
1. Monitor sources (automated alerts on GOV.UK, TrustMark, Ofgem)
2. Flag any changes with curriculum impact
3. Draft new or updated course content
4. QA against primary source
5. Build in PowerPoint using master template
6. Add watermark layer and copyright notice
7. Export as PDF and PPTX
8. Upload to subscriber library with release notes
9. Email subscribers with "What's New This Week" update

**Monthly release rhythm:**
- 2–4 new courses per month minimum
- 1 "In Depth" extended course (multi-hour) per month
- Monthly CPD digest email (1 CPD hour claimable for reading)

---

## The Library Architecture

### File Structure

```
meridian-library/
  active/                    ← Current live courses
    dea/                     ← DEA strand courses
    retrofit-assessor/       ← Retrofit Assessor courses
    retrofit-coordinator/    ← RC courses
    ndea/                    ← Non-domestic strand
    all-strands/             ← Applicable to all
  archive/                   ← Retired versions (still saleable)
    2025/
    2026/
  certificates/              ← Certificate templates + issued log
  templates/                 ← Branded PPTX and PDF templates
  release-log/               ← Version history for every course
```

### Course Metadata (every course)

| Field | Example |
|---|---|
| Course ID | MER-DEA-045 |
| Title | RdSAP 10: Ventilation Changes in Detail |
| Strand | DEA / Retrofit Assessor |
| CPD Hours | 1 |
| Version | 2.1 |
| Published | March 2026 |
| Last updated | March 2026 |
| Supersedes | MER-DEA-039 |
| Regulatory source | RdSAP 10 Technical Manual, Section 9 |
| Keywords | ventilation, RdSAP 10, PIV, MVHR, natural ventilation |
| Status | Active |

---

## Certificate System

### Certificate Design
- Meridian CPD logo and branding
- Recipient name
- Course title and Course ID
- CPD hours awarded
- Completion date
- Accreditation strand (DEA / Retrofit Assessor / RC)
- Unique certificate number
- Issuer signature block: *Issued by Meridian CPD. This certificate confirms successful completion of the above course. It is the learner's responsibility to ensure CPD is accepted by their accreditation scheme.*

### Issuance Process
- Certificates issued once per month in batch (or on-demand for subscribers)
- Delivered as PDF via email — not included in course download
- Certificate log maintained: name, certificate number, date, course, CPD hours
- Subscriber CPD log available to download from portal — shows all completed courses, dates, hours

### Important disclaimer on all certificates
*Meridian CPD is an independent CPD provider. This certificate is not issued by or on behalf of any accreditation scheme (ECMK, Elmhurst, Quidos, Sterling, or others). Acceptance of CPD hours is at the discretion of the subscriber's accreditation body. Subscribers are responsible for verifying their scheme's CPD acceptance criteria.*

---

## The Curriculum Map

### STRAND A — Domestic Energy Assessor (DEA) Core

| Course ID | Title | Hours | Priority |
|---|---|---|---|
| MER-DEA-001 | Introduction to RdSAP 10: What's Changed and Why | 2 | ⚡ Launch |
| MER-DEA-002 | Measuring Windows in RdSAP 10: The New Requirements | 1 | ⚡ Launch |
| MER-DEA-003 | Ventilation in RdSAP 10: PIV, MVHR, and Natural Systems | 1 | ⚡ Launch |
| MER-DEA-004 | Room in Roof: Type 1 and Type 2 in RdSAP 10 | 1 | ⚡ Launch |
| MER-DEA-005 | Heating Systems Primary: Boilers, Controls and Data Entry | 1 | Core |
| MER-DEA-006 | Heating Systems Secondary: Storage Heaters, Direct Electric and Room Heaters | 1 | Core |
| MER-DEA-007 | Hot Water Systems: Cylinders, Combis, and Immersions | 1 | Core |
| MER-DEA-008 | Insulation: Walls, Roofs, Floors and Common Errors | 1 | Core |
| MER-DEA-009 | Floors and Extensions: Modelling Split Properties Correctly | 1 | Core |
| MER-DEA-010 | Lighting and Renewables in RdSAP 10: What's New | 1 | ⚡ Launch |
| MER-DEA-011 | Solar PV, Battery Storage and PV Diverters in RdSAP 10 | 1 | ⚡ Launch |
| MER-DEA-012 | Heat Pumps: Assessment, Recommendations and Data Entry | 1 | Core |
| MER-DEA-013 | Older and Traditional Properties: Solid Walls, Suspended Floors, Sash Windows | 2 | Core |
| MER-DEA-014 | EPC Audit Preparation: How to Pass Your Annual Audit | 1 | Core |
| MER-DEA-015 | Common DEA Mistakes and How to Avoid Them | 1 | Core |
| MER-DEA-016 | Floorplans and Measuring: Conventions, Accuracy and Evidence | 1 | Core |
| MER-DEA-017 | Photography Evidence: What Auditors Need and Why | 1 | Core |
| MER-DEA-018 | EPC Recommendations: Understanding the Improvement Measure Logic | 1 | Core |
| MER-DEA-019 | MEES 2028–2030: What Private Landlords Need to Know (Client Comms) | 1 | Core |
| MER-DEA-020 | Annexes, HMOs and Multi-Unit Properties | 1 | Core |
| MER-DEA-021 | Airtightness Testing in RdSAP 10: Data Entry and Evidence | 1 | ⚡ Launch |
| MER-DEA-022 | Thermal Bridging: Understanding Y-Values and Psi-Values | 1 | Advanced |
| MER-DEA-023 | Data Protection and GDPR for Energy Assessors | 1 | Core |
| MER-DEA-024 | Professional Indemnity Insurance: What You Need and Why | 1 | Core |
| MER-DEA-025 | Client Communication Skills for DEAs | 1 | Core |

---

### STRAND B — Retrofit Assessor

| Course ID | Title | Hours | Priority |
|---|---|---|---|
| MER-RA-001 | PAS 2035:2023 Overview: The Retrofit Standard Explained | 2 | ⚡ Launch |
| MER-RA-002 | The Retrofit Assessment: Process, Documentation and Sign-Off | 1 | Core |
| MER-RA-003 | Occupancy Assessment (OA): Methodology and Client Interaction | 1 | Core |
| MER-RA-004 | Condition Assessment: Identifying Site Constraints and Defects | 1 | Core |
| MER-RA-005 | Energy Performance Reports (EPRs): Pre and Post Assessment | 2 | Core |
| MER-RA-006 | EPR Variation Conventions: RdSAP 10 Transition Update | 1 | ⚡ Launch |
| MER-RA-007 | Ventilation Strategy in Retrofit Assessments: PAS 2035 Requirements | 1.5 | Core |
| MER-RA-008 | Internal Wall Insulation (IWI): Assessment, Risks and Best Practice | 1 | Core |
| MER-RA-009 | External Wall Insulation (EWI): Planning Permission, Fire Risk and Assessment | 1 | ⚡ Launch |
| MER-RA-010 | Solid Wall Properties: Assessment Considerations and Common Issues | 1 | Core |
| MER-RA-011 | Underfloor Insulation: Types, Assessment and Contraindications | 1 | Core |
| MER-RA-012 | Loft and Roof Insulation: Assessment for Retrofit Programmes | 1 | Core |
| MER-RA-013 | Heat Pumps in Retrofit: Suitability Assessment and Fabric-First Principles | 1.5 | Core |
| MER-RA-014 | Solar PV in Retrofit: Assessment, Battery Storage and Diverters | 1 | Core |
| MER-RA-015 | TrustMark Framework: Retrofit Assessor Obligations | 1 | Core |
| MER-RA-016 | ECO4 and GBIS: Scheme Rules for Retrofit Assessors | 1 | Core |
| MER-RA-017 | Warm Homes Social Housing Fund: Delivering Wave 3 Programmes | 1 | ⚡ Launch |
| MER-RA-018 | Working with Traditional Buildings in Retrofit Programmes | 1.5 | Core |
| MER-RA-019 | Risk Factors and Contraindications in Retrofit Assessment | 1 | Core |
| MER-RA-020 | Welsh Optimised Retrofit Programme (ORP): What Assessors Need to Know | 1 | ⚡ Launch |

---

### STRAND C — Retrofit Coordinator (RC)

| Course ID | Title | Hours | Priority |
|---|---|---|---|
| MER-RC-001 | PAS 2035 Coordinator Role: Responsibilities and Competence | 2 | Core |
| MER-RC-002 | The Whole House Plan (WHP): Structure, Content and Compliance | 2 | Core |
| MER-RC-003 | Retrofit Measure Design: Fabric-First Principles and Sequencing | 2 | Core |
| MER-RC-004 | Ventilation Strategy Design: MVHR, MEV and Natural Ventilation | 2 | Core |
| MER-RC-005 | Managing Installers and Contractors: TrustMark Requirements | 1 | Core |
| MER-RC-006 | Pre and Post-Retrofit EPCs: Coordinator Oversight and Sign-Off | 1 | Core |
| MER-RC-007 | Programme Management for RCs: Wave 3 SHF at Scale | 2 | ⚡ Launch |
| MER-RC-008 | Client Care and Vulnerability: Working with Social Housing Residents | 1 | Core |
| MER-RC-009 | Dispute Resolution and Complaints: RC Obligations | 1 | Core |
| MER-RC-010 | CPD Requirements for Retrofit Coordinators: 25 Hours and How to Meet Them | 1 | Core |

---

### STRAND D — All Strands (Cross-Cutting)

| Course ID | Title | Hours | Priority |
|---|---|---|---|
| MER-ALL-001 | UK Energy Policy 2026: Warm Homes Plan, MEES, and What Comes Next | 1 | ⚡ Launch |
| MER-ALL-002 | Building Physics for Assessors: U-Values, Heat Loss and Thermal Bridging | 2 | Core |
| MER-ALL-003 | Understanding SAP and RdSAP: Methodology Fundamentals | 2 | Core |
| MER-ALL-004 | Fire Safety in Retrofit: EWI Planning, Cladding and Current Guidance | 1 | ⚡ Launch |
| MER-ALL-005 | Condensation Risk and Damp: Assessment and Advice | 1 | Core |
| MER-ALL-006 | Running Your Assessor Business: Pricing, Contracts and PI Insurance | 1 | Core |
| MER-ALL-007 | Social Housing Decarbonisation: Policy, Programmes and Opportunities | 1 | Core |
| MER-ALL-008 | Smart Meters and In-Home Displays: Understanding Measured Data | 1 | Core |
| MER-ALL-009 | Fuel Poverty and Vulnerability: Assessor Responsibilities | 1 | Core |
| MER-ALL-010 | Hydrogen-Ready Boilers and Future Heating Technologies | 1 | Future |

---

## Launch Sequence

**Month 1 — Launch Pack (12 courses, all ⚡ flagged above)**
Lead with RdSAP 10 content — this is the immediate market need. Every active DEA needs it.

Priority launch titles:
1. RdSAP 10: What's Changed and Why (2hr) — flagship course
2. Ventilation in RdSAP 10
3. Solar PV and Battery Storage in RdSAP 10
4. Windows in RdSAP 10
5. PAS 2035:2023 Overview
6. EPR Variation Conventions: RdSAP 10 Update
7. EWI: Planning Permission and Fire Risk (topical — TrustMark issued recent guidance)
8. Warm Homes SHF Wave 3 (directly relevant to social housing market)
9. Welsh ORP for Assessors
10. UK Energy Policy 2026
11. Fire Safety in Retrofit
12. Room in Roof Type 1 and Type 2

**Month 2 — Core Library**
Add the foundation courses — heating systems, insulation, floorplans, audit prep.

**Month 3 onwards — Subscription rhythm**
2–4 new courses per month. Monthly digest email = 1 CPD hour.

---

## Outreach Engine — Targeting Active DEAs

### The Target List

**Source:** EPC Register at epcregister.com / Landmark Hive public listings.

The EPC register lists all lodged certificates with the assessor's name and accreditation scheme. Assessor contact details are available through the accreditation bodies' public-facing find-an-assessor tools.

**Build approach:**
1. Scrape find-an-assessor pages (ECMK, Elmhurst, Quidos, Sterling, Stroma) for publicly listed assessor names and emails
2. Cross-reference against EPC register lodgement data to confirm active status (lodged within last 12 months)
3. Build segmented list: DEA-only, DEA+RA, RC

**GDPR compliance:**
- All contact data from public, professional directories
- Legitimate interest basis: CPD services are directly relevant to the assessed professional's mandatory regulatory requirements
- Privacy notice published on meridiancpd.co.uk before any outreach
- Every email contains: clear sender identity, reason for contact, unsubscribe link
- Suppression list maintained from day one
- Maximum 2 cold emails before moving to suppressed

---

### Email Outreach Sequence

**Email 1 — The Introduction**
Subject: *RdSAP 10 CPD — ready for you*

> Hi [Name],
>
> RdSAP 10 is the biggest change to energy assessment in over a decade — and the CPD requirement doesn't go away just because the deadline passed.
>
> We've built a full library of CPD courses specifically for DEAs and retrofit assessors. All written by practising professionals. All available as downloadable PDFs with certificates issued monthly.
>
> Annual subscription: £79. Pay per course from £12.
>
> Your first course is on us — use code MERIDIAN10 for a free RdSAP 10 overview module.
>
> [Explore the library → meridiancpd.co.uk]
>
> Meridian CPD | Stay Sharp. Stay Certified.
> Unsubscribe

---

**Email 2 — The Follow-Up (5 working days later, non-responders only)**
Subject: *Free RdSAP 10 module — still available*

> Hi [Name],
>
> Just a quick follow-up — your free RdSAP 10 course is still available with code MERIDIAN10.
>
> This 2-hour module covers every key change from version 9.94 to RdSAP 10 — windows, ventilation, room in roof, solar PV and battery storage, and airtightness testing.
>
> Counts as 2 CPD hours. Certificate issued the same month.
>
> [Claim it here → meridiancpd.co.uk]
>
> Meridian CPD
> Unsubscribe | This email was sent because your details appear on a public DEA accreditation register.

---

**Email 3 — Monthly subscriber newsletter (subscribers only)**
Subject: *What's new at Meridian CPD — [Month Year]*

> New this month: [3 new course titles with one-line descriptions]
>
> Your CPD log shows [X] hours completed so far this year. You need [Y] hours by your renewal date.
>
> [See your CPD log → meridiancpd.co.uk/my-cpd]
>
> [Browse new courses →]
>
> Meridian CPD | Stay Sharp. Stay Certified.

---

## Technical Platform Requirements (Future Build)

This is the roadmap for building the subscriber platform. In the short term, courses can be sold manually via email + payment link. The platform comes once revenue justifies it.

| Phase | Component | Description |
|---|---|---|
| 0 (Now) | Manual | Email delivery + Stripe payment link + PDF course + monthly certificate email |
| 1 | Simple website | Landing page + course catalogue + Stripe checkout + automated PDF delivery |
| 2 | Subscriber portal | Login + CPD log + library access + certificate download |
| 3 | Admin panel | Course upload + subscriber management + certificate batch issue + revenue tracking |
| 4 | Automation | Weekly source monitoring + draft content flagging + release workflow |

---

## The First Action

Before anything else is built, one thing generates revenue immediately:

1. Build the flagship course: **RdSAP 10: What's Changed and Why** — 2 hours, full PowerPoint, PDF export
2. Set up a Stripe payment link at £19.99
3. Set up a simple landing page (can be Fistral-built)
4. Email 50 DEAs you can reach through your existing network or LinkedIn
5. Use code MERIDIAN10 for a free download to the first wave

That's a test of whether people will pay. They will — because they have to. But verify it before building the full platform.

---

*Meridian CPD · meridiancpd.co.uk · © 2026 All rights reserved.*
*Content produced by qualified PAS 2035 professionals. Not affiliated with ECMK, Elmhurst, Quidos, Sterling, TrustMark, or any government body.*
