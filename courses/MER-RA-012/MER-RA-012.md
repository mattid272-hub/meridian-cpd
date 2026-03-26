

# TrustMark Data Requirements: What Retrofit Assessors Must Submit
**Course ID:** MER-RA-012 | **CPD Hours:** 1.0 | **Published:** March 2026
*© Meridian CPD 2026. All rights reserved.*

---

## Learning Objectives

- Identify the mandatory data fields required for a PAS 2035:2023 Retrofit Assessment submission to TrustMark and explain the consequences of omissions.
- Apply the correct data formats and reference standards (UPRN, RRN, exposure zone codes) required for TrustMark submission.
- Recognise the most common TrustMark lodgement rejection reasons and implement preventive practices for each.
- Understand the TrustMark quality assurance framework and how Retrofit Assessment data quality is monitored after submission.
- Explain the relationship between the Retrofit Assessment submission, the Improvement Pathway record, and the subsequent installation notification in the TrustMark data ecosystem.

---

## Introduction

TrustMark is the government-endorsed quality scheme for domestic retrofit in England. For publicly funded retrofit projects — ECO4, Great British Insulation Scheme (GBIS), Social Housing Decarbonisation Fund, Local Authority Delivery, and related programmes — TrustMark registration and data submission are mandatory requirements for all parties in the retrofit chain, including Retrofit Assessors.

The TrustMark data warehouse receives Retrofit Assessment data, Improvement Pathway records, installation notifications, and post-installation documentation. Data quality in this system is a shared responsibility: the assessor's submission forms the foundation of the project record, and errors or omissions at the assessment stage propagate through to the installation record and ultimately to the programme's quality assurance outcomes.

Understanding TrustMark's data requirements in detail is not optional for assessors working in funded retrofit. This course covers what TrustMark requires, how the submission works, what gets rejected and why, and how the quality framework operates after submission.

---

## Section 1: The TrustMark Data Ecosystem for Retrofit Projects

TrustMark's data infrastructure for retrofit projects was substantially enhanced for the PAS 2035:2023 era. The key components are:

**The Retrofit Assessment record.** Submitted by the Retrofit Assessor (or by the Retrofit Coordinator on the assessor's behalf, depending on programme structure). Contains the PAS 2035:2023 Annex A data — property identification, construction, energy systems, occupancy, moisture, and current EPC data.

**The Improvement Pathway record.** Submitted by the Retrofit Coordinator following assessment. Identifies the proposed measures, the risk pathway, and the design and monitoring arrangements. It is built on the foundation of the assessment data — if the assessment is incomplete, the Improvement Pathway cannot be completed.

**The Installation Notification.** Submitted by the TrustMark-registered installer on completion of each measure. References the project record established at assessment and Improvement Pathway stages. Includes installation date, product specifications, and installer certification references.

**The Post-Installation Assessment record.** For higher-risk projects (Path B and C), a post-installation assessment is required to confirm the measures have been installed as designed and that no post-installation defects are apparent.

**The project chain.** Every step is linked. A missing field in the assessment record creates a gap that blocks the Improvement Pathway submission, which blocks the installation notification, which blocks the programme payment. Getting the assessment right is not just a quality issue — it is a project delivery issue.

---

## Section 2: Mandatory Data Fields for TrustMark Submission

The following fields must be complete and correctly formatted for a TrustMark Retrofit Assessment submission to be accepted:

**Property identification:**
- Full postal address
- UPRN (Unique Property Reference Number) — from the OS AddressBase dataset, searchable at findmyaddress.co.uk. Must be the specific UPRN for the exact address, not a neighbouring property or a postcode centroid.
- Tenure: owner-occupied, private rented, social rented, or other
- EPC Report Reference Number (RRN) — the 24-character reference from the EPC Register for the current or most recent EPC. Must be current within the programme's required currency period (typically 2 years).

**Construction data (for each element):**
- Wall: construction type, age band, insulation status and type (or confirmed uninsulated), U-value (calculated/declared/default — basis must be stated)
- Roof: construction type, age band, insulation depth or type if present, U-value
- Floor: construction type, insulation status, U-value
- Windows: glazing type, approximate installation period

**Energy systems:**
- Primary heating: fuel type, system type, manufacturer/model (or age-band identifier if not identifiable), installation year, efficiency (SEDBUK/ErP or age-band default)
- Secondary heating (if present): type and fuel
- Hot water: system type (combi, cylinder — volume if applicable)
- Ventilation: system type and extract fan locations

**Occupancy:**
- Total occupant count
- Age distribution (under 5, 5–16, 17–60, 61–74, 75+)
- Health/vulnerability flags (with consent recorded)
- Fuel poverty indicators

**Moisture (all six mandatory indicators):**
- Rising damp evidence (positive/negative finding)
- Penetrating damp evidence (positive/negative finding)
- Condensation evidence (positive/negative finding)
- Ventilation adequacy assessment
- Exposure zone (BREDEM/BS 8104 zone code)
- Rainwater goods condition

**Photographic evidence pack:** All elevations, boiler data plate, consumer unit, loft space (if accessed), and any specific feature photographs required by the programme.

---

## Section 3: Most Common Rejection Reasons and How to Prevent Them

TrustMark quality review data identifies the following as the most frequent submission rejection reasons:

**1. Incorrect or missing UPRN.** The UPRN is the primary linking field for the property record across all datasets. A wrong UPRN creates a project record for the wrong property, which contaminates the dataset and may result in the wrong property being attributed with a completed retrofit. Prevention: always look up the UPRN using the OS tool or the programme's property search tool and verify it against the full address before submission. Do not accept a UPRN from the client or installer without independent verification.

**2. EPC reference expired or incorrect.** Most programmes require an EPC lodged within a specified period (typically 24 months) prior to the Retrofit Assessment. An EPC lodged more than 24 months ago is typically expired for programme purposes even if it is technically valid on the EPC Register. The RRN must match the EPC on the EPC Register — mistyped RRNs are a frequent error. Prevention: copy the RRN directly from the EPC Register entry for the property; do not transcribe it from a printed certificate.

**3. Incomplete fabric element records.** Wall type without insulation status, or roof without insulation depth, are the most common partial entries. Prevention: use a structured site checklist that requires both construction type and insulation status for each element before the survey is considered complete.

**4. Moisture indicators incomplete.** Any of the six mandatory moisture indicator fields missing from the submission triggers rejection. Prevention: treat the moisture assessment as a standalone module with its own checklist, completed for every survey regardless of the proposed measures.

**5. Photographic evidence insufficient.** The minimum photographic pack requirements vary by programme, but all programmes require a minimum set. Missing elevation photographs or a missing boiler data plate photograph are the most common gaps. Prevention: a standardised site photography protocol with a signed-off list of required images for each survey type.

**6. Occupancy data missing.** Total occupant count absent, or age distribution not completed. Prevention: occupancy data should be the first thing recorded at the start of the survey — while the occupant is present and before the assessor begins the physical survey.

---

## Section 4: The TrustMark Quality Framework — After Submission

Submission of a Retrofit Assessment record to TrustMark is not the end of the quality process — it is the beginning of it.

**Automated data quality checks.** TrustMark's system performs automated checks on submission: UPRN validity, RRN format and currency, field completeness, and consistency between related data fields (e.g., a solid wall construction age dated post-1970 without cavity fill explanation would flag as anomalous). Automated rejections return a specific rejection reason code that identifies the failing field.

**Manual quality reviews.** TrustMark's quality team conducts manual reviews of a sample of submitted assessment records. These reviews check for plausibility, consistency between data fields, and compliance with PAS 2035:2023 requirements. A manual review failure results in a quality finding — this is escalated to the TrustMark-registered business responsible for the project (typically the Retrofit Coordinator or main contractor) and, where systematic, to the assessor's scheme.

**Programme-level audit.** Individual retrofit programmes (ECO4, GBIS, SHDF) conduct their own quality audits of TrustMark data. Programme auditors can request original assessment documentation, site photographs, and supporting evidence for any submission. The audit file requirement (retain for 6 years, as discussed in MER-DEA-014) applies equally to Retrofit Assessment records.

**The consequences of quality failures.** For individual submissions: rejection requires correction and resubmission, delaying project progress. For repeated failures: the TrustMark-registered business is flagged in the quality system, attracting higher audit rates and potentially suspension. For seriously deficient data: programme funders (Ofgem for ECO4 and GBIS) can seek repayment of funded measures where the assessment data does not support the installation claimed.

**Keeping records.** Every Retrofit Assessment submitted to TrustMark must have a corresponding local record maintained by the assessor or their organisation. This includes the completed assessment data, the photographic evidence pack, any occupant consent records, and any specialist investigation reports. The local record must be available for production within the specified period on request from TrustMark, the programme auditor, or the accreditation scheme.

---

## Key Takeaways

- TrustMark data submission is mandatory for all PAS 2035:2023 retrofit projects in funded programmes; assessment data quality determines whether the project record can proceed to installation.
- The UPRN is the primary linking field — it must be verified independently for every submission, not taken on trust from any other party.
- The EPC RRN must be current within the programme's required period and copied exactly from the EPC Register — transcription errors are a frequent rejection cause.
- The six mandatory moisture indicator fields must all be present; any omission triggers rejection.
- TrustMark performs both automated and manual quality checks after submission; systematic data quality failures escalate to the TrustMark-registered business and the assessor's accreditation scheme.
- Local records must be maintained for 6 years and produced on request — a photographic evidence pack is part of the mandatory record for every submission.

---

## Self-Assessment Questions

**Q1.** A Retrofit Assessor submits a PAS 2035:2023 assessment for a 1962 semi-detached house. The submission is automatically rejected with the code "UPRN_INVALID." What is the most likely cause and the correct action?

A) The UPRN format is wrong — it should be 12 digits. The assessor should check the format.
B) The UPRN entered does not match any valid record in the OS AddressBase dataset — likely a transcription error or the wrong property's UPRN was entered. The assessor should look up the correct UPRN using the OS tool and resubmit.
C) UPRNs are not yet available for pre-1970 properties — the assessor should use the postcode
D) The submission should be escalated to TrustMark support immediately

**Correct answer: B**
*UPRN_INVALID typically means the entered UPRN is not in the OS AddressBase dataset — either a transcription error, a wrong property's UPRN, or (rarely) a UPRN not yet issued. The assessor looks up the correct UPRN via the OS tool, verifies it against the full address, and resubmits.*

---

**Q2.** The EPC for a property was lodged 28 months ago. The programme requires an EPC current within 24 months of the Retrofit Assessment date. What must the assessor do?

A) Use the existing EPC — 28 months is within the 30-month tolerance
B) A new EPC must be lodged before the Retrofit Assessment can be submitted to TrustMark for this programme
C) Submit with a note explaining the EPC date — TrustMark will accept this with a waiver
D) Use the EPC from the previous retrofit project on the same address

**Correct answer: B**
*A new EPC must be lodged to meet the programme's currency requirement. The assessor cannot submit with an out-of-currency EPC; the submission will be rejected. The new EPC must be lodged and the new RRN used in the assessment submission.*

---

**Q3.** A TrustMark quality reviewer flags a submitted assessment as "moisture indicators incomplete — exposure zone not recorded." The assessor believes the field was completed but left as "not applicable" because the property had no moisture issues. What is the error?

A) "Not applicable" is an acceptable entry — the assessor was correct
B) The exposure zone is not condition-dependent — it is always mandatory regardless of whether moisture issues are present. "Not applicable" is not a valid entry; the zone must be determined and recorded for every assessment.
C) The exposure zone only needs to be recorded for EWI or IWI projects
D) The reviewer has made an error — the field is recommended, not mandatory

**Correct answer: B**
*The external exposure zone is a mandatory field in all PAS 2035:2023 assessments — it is not conditional on moisture issues being present. "Not applicable" is not a valid entry. The assessor must determine the zone from the BREDEM/BS 8104 dataset for the property postcode and record it.*

---

**Q4.** An assessor submits a Retrofit Assessment and it is accepted by TrustMark's automated checks. Three months later, a manual quality review flags the assessment as having implausible wall construction data — a "1930s cavity wall fully filled with CWI, no CIGA certificate in evidence pack." What action does TrustMark take?

A) No action — the assessment was accepted automatically
B) A quality finding is raised and escalated to the TrustMark-registered business responsible for the project; if systematic, it may also be escalated to the assessor's accreditation scheme; the assessor may be required to produce the original evidence or re-survey the property
C) The CWI installation is automatically reversed
D) The assessor is immediately decertified

**Correct answer: B**
*Manual quality reviews can raise findings on previously accepted submissions. The finding is escalated to the responsible business (typically the main contractor or Retrofit Coordinator) and, where systematic quality failures are identified, to the assessor's accreditation scheme. The assessor may be required to produce the original evidence or re-survey. Decertification is a last resort that requires a formal process.*

---

**Q5.** How long must Retrofit Assessment records and supporting evidence be retained by the assessor or their organisation?

A) 1 year from lodgement
B) Until the TrustMark project record is closed
C) 6 years from lodgement — the standard audit trail retention period for retrofit programme data
D) Indefinitely — there is no defined retention period

**Correct answer: C**
*The standard record retention requirement for TrustMark-related retrofit programme data is 6 years from lodgement. This covers programme audit requirements, potential dispute resolution, and warranty periods for installed measures. Records must be available for production within the specified period on request from TrustMark, programme auditors, or the accreditation scheme.*

---

## Further Reading

- **TrustMark — Retrofit Assessment Data Requirements and Submission Guidance.** Available at: https://www.trustmark.org.uk/
- **PAS 2035:2023 — Retrofitting Dwellings for Improved Energy Efficiency** — BSI. Available at: https://www.bsigroup.com/
- **Ordnance Survey — AddressBase and UPRN Lookup.** Available at: https://www.findmyaddress.co.uk/
- **EPC Register — Report Reference Number (RRN) Search.** Available at: https://www.epcregister.com/
- **Ofgem — ECO4 and GBIS Quality Framework and Audit Requirements.** Available at: https://www.ofgem.gov.uk/

---

*© Meridian CPD 2026. All rights reserved. Unauthorised reproduction prohibited.*
*This course material is licensed to individual subscribers only.*
