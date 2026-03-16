

# Airtightness Testing in RdSAP 10
**Course ID:** MER-DEA-021 | **CPD Hours:** 1.0 | **Published:** March 2026
*© Meridian CPD 2026. All rights reserved.*

---

## Learning Objectives

- Explain how RdSAP 10 treats measured airtightness data differently from RdSAP 9.94, including the revised default assumptions and their impact on dwelling energy ratings.
- Identify the circumstances under which a measured air permeability value can and should be entered into RdSAP 10 for an existing dwelling EPC assessment.
- Apply the correct ATTMA TSL1 / CIBSE TM23 testing protocols and determine whether a test certificate is compliant for RdSAP 10 input.
- Evaluate the effect of airtightness improvements on SAP ratings within the context of PAS 2035:2023 retrofit pathways and medium-term improvement recommendations.
- Distinguish between the regulatory treatment of airtightness for new-build SAP calculations (Part L1A / Part L1) and existing dwelling assessments under RdSAP 10, avoiding common data entry errors.

---

## Introduction

Airtightness has always been a significant variable in domestic energy modelling, but for most of RdSAP's operational life it has been functionally invisible to DEAs working on existing dwellings. RdSAP 9.94 assigned a default air permeability derived from dwelling age, construction type, and a set of proxy assumptions about draught-stripping and flue presence. The assessor had no facility to enter a measured value. The model simply estimated infiltration and moved on.

RdSAP 10 changes this. The updated methodology, aligned with the 2025 iteration of SAP 10.2 and deployed through the Home Energy Model framework, now permits — and in certain retrofit scenarios, actively encourages — the entry of a measured air permeability result for existing dwellings. This is not a marginal technical adjustment. Airtightness directly influences space heating demand, which dominates the energy balance in the vast majority of the UK's 29 million existing homes. A dwelling tested at 5 m³/(h·m²) at 50 Pa versus one defaulting to 15 m³/(h·m²) at 50 Pa will show materially different fabric heat loss calculations and, consequently, a different EPC band.

For DEAs, this creates both an opportunity and a compliance obligation. Where a valid test result exists — for example, from a PAS 2035 retrofit project or a post-installation verification under a government-funded scheme — the assessor must understand when to use it, what constitutes a valid certificate, and how the software processes the input. Getting it wrong means an inaccurate EPC, potential enforcement action from the accreditation scheme, and a disservice to the homeowner or landlord relying on the rating.

This course walks through the mechanics: what RdSAP 10 actually does with the airtightness input, how the defaults have been recalibrated, the testing standards that underpin valid data, and the practical interface with PAS 2035 retrofit coordination. It assumes you are already producing EPCs and are familiar with the RdSAP conventions. The focus is on what has changed, what it means for your workflow, and where the errors are most likely to occur.

---

## Section 1: How RdSAP 10 Models Infiltration — What Has Actually Changed

RdSAP has always calculated an infiltration rate as part of its heat loss computation. The methodology converts air permeability (measured in m³/(h·m²) at 50 Pa pressure difference) into an effective infiltration rate in air changes per hour (ach) using a shelter factor and a division factor (typically ÷20 under SAP convention, though the precise treatment is more nuanced in the background calculations). That infiltration rate feeds into the ventilation heat loss coefficient, which combines with purposeful ventilation to produce total ventilation loss.

Under RdSAP 9.94, the air permeability for existing dwellings was purely algorithmic. The model assigned a base value according to a matrix of wall construction type (masonry cavity, solid brick, timber frame, system-built, etc.) and age band. A pre-1900 solid-walled dwelling might default to approximately 15 m³/(h·m²) at 50 Pa; a post-2006 cavity masonry home to around 7–10 m³/(h·m²) at 50 Pa. These defaults were then adjusted by whether draught-stripping was recorded on windows and doors, whether open flues or chimneys were present, and the number and type of extract fans. The assessor had no override.

RdSAP 10 retains the default pathway — you are not required to have a test for every EPC — but it introduces an explicit data entry field for measured air permeability. When a valid measured value is entered, it replaces the age-band default entirely. The software then adjusts for the ventilation strategy and purposeful ventilation provisions as before, but the baseline infiltration starts from a tested figure rather than a statistical proxy.

The defaults themselves have also been recalibrated. BRE's supporting research, drawing on an expanded dataset of blower door tests conducted across the English Housing Survey and devolved-nation equivalents, revised several age-band assumptions. Notably, mid-century dwellings (1950–1975) saw their defaults tightened modestly, reflecting field evidence that these properties — often with smaller window areas and simpler construction — were somewhat less leaky than the previous assumptions suggested. Pre-1919 defaults remained broadly unchanged, reflecting the persistent leakiness of older solid-walled stock.

Critically, the division factor and shelter model have been refined in line with SAP 10.2. Wind exposure is treated with greater regional granularity, meaning that two identical dwellings with identical air permeability values will show different infiltration rates depending on location and shielding — a change from the relatively blunt treatment in SAP 2012/RdSAP 9.94. For the DEA, this means the measured value you enter interacts more sensitively with the site context than it would have under the old methodology.

---

## Section 2: When Measured Data Is Valid — Test Standards, Certificates, and Compliance

A measured air permeability value can only be entered into RdSAP 10 if it is supported by a compliant test certificate. The relevant testing standards are ATTMA Technical Standard L1 (Measuring Air Permeability of Building Envelopes — Dwellings) and CIBSE TM23, both of which align with BS EN ISO 9972:2015 (the international standard for fan pressurisation testing). For RdSAP 10 purposes, the test must have been conducted in accordance with one of these frameworks, and the certificate must be issued by a tester holding UKAS-accredited certification or registered with ATTMA's Lodgement Scheme.

The test result recorded on the certificate is the air permeability at 50 Pa in m³/(h·m²), referenced to the total envelope area of the dwelling. This is the figure that enters the software. Do not confuse it with air changes per hour at 50 Pa (n₅₀), which is referenced to dwelling volume rather than envelope area. The two are related by a geometric ratio but are numerically different. Entering n₅₀ where the software expects q₅₀ (air permeability) will produce an incorrect result, and this is one of the most common data entry errors flagged in audits of new-build SAP calculations — there is no reason to import that error into existing dwelling assessments now that the field is available.

For the certificate to be accepted, the test must have been conducted under appropriate conditions: the dwelling sealed as per the testing protocol (temporary sealing of intentional openings such as trickle vents, extract fans, and flues), wind speed below the threshold specified in BS EN ISO 9972 (generally ≤6 m/s, though the standard specifies Beaufort force 3 or a product-specific limit), and both pressurisation and depressurisation results recorded. The mean of the two is the reported result.

There is a temporal dimension. RdSAP 10 software conventions, as specified in the associated conventions document, require that the test was conducted no more than three years prior to the date of the EPC assessment, unless the test was conducted as part of a completed PAS 2035 retrofit project and the measures have not been materially altered since. This prevents reliance on stale data in a dwelling that may have undergone changes — new windows, additional penetrations, removed draught-stripping — that would have altered the envelope's performance.

DEAs should also be aware that they are not being asked to conduct the test themselves. Your role is to verify the certificate's validity, confirm it relates to the dwelling in question (address, UPRN where available, and envelope area should be cross-referenced), and enter the figure into the software with the appropriate source flag. If anything on the certificate appears inconsistent — for instance, an envelope area that differs significantly from what you would calculate from your survey — you should default to the algorithmic value and note the discrepancy.

---

## Section 3: Interaction with PAS 2035:2023 Retrofit Pathways and Improvement Recommendations

The introduction of a measured airtightness input in RdSAP 10 is not coincidental to the maturation of PAS 2035. The 2023 revision of PAS 2035 (published by BSI and mandated for publicly funded retrofit under ECO4, the Great British Insulation Scheme, and their successor programmes) places significant emphasis on a fabric-first hierarchy, with airtightness identified as a key performance metric for both pre- and post-intervention assessment.

Under PAS 2035:2023, a Retrofit Coordinator developing a Medium Term Improvement Plan for a dwelling in Pathway B or C is expected to consider airtightness improvement as part of the ventilation strategy. The standard explicitly warns against improving airtightness without addressing ventilation adequacy — the so-called "seal tight, ventilate right" principle. Where airtightness measures are installed (draught-stripping, sealing of service penetrations, floor sealing, chimney draught excluders), a post-works blower door test is strongly recommended at Assessment Risk Level 3 and may be mandated by scheme requirements.

This is where the DEA's work intersects directly. When producing a post-retrofit EPC — which is required to demonstrate the energy improvement resulting from funded measures — the assessor now has the ability to enter the post-works measured air permeability. This can substantially improve the calculated energy rating compared to leaving the default in place, because the default assumes a statistically average dwelling of that age and type, not a dwelling that has just had its envelope systematically sealed.

Consider a 1960s semi-detached house with solid concrete floors, cavity walls (now insulated), and replacement double-glazed windows. The RdSAP 10 age-band default air permeability for this archetype might sit around 11–13 m³/(h·m²) at 50 Pa. If post-retrofit testing demonstrates an achieved permeability of 6 m³/(h·m²) at 50 Pa, entering the measured value will reduce the ventilation heat loss significantly, potentially contributing one or more SAP points and, in borderline cases, shifting the EPC band.

However, the assessor must exercise caution. Entering a measured airtightness value without confirming that the ventilation provision is adequate creates a theoretical risk that the modelled ventilation heat loss will be unrealistically low. RdSAP 10 handles this through its ventilation algorithm — if the dwelling has no mechanical ventilation and no trickle vents, the model applies a minimum ventilation rate floor regardless of how tight the envelope tests. But the assessor should be aware that where airtightness improvements have been made, the PAS 2035 Retrofit Coordinator should have addressed ventilation. If the EPC is being produced and there is evidence of airtightness works but no corresponding ventilation upgrade, the DEA should record the measured value (if the certificate is valid) but may wish to flag the ventilation concern to the scheme provider or lodgement body.

The practical upshot: measured airtightness data from PAS 2035 projects is likely to become the most common source of valid test certificates for existing dwelling EPCs. DEAs working on post-retrofit assessments should proactively request the airtightness test certificate from the Retrofit Coordinator or installer at the same time as they collect details of the installed measures.

---

## Section 4: Practical Workflow — Data Entry, Audit Risk, and Common Errors

When you encounter a measured airtightness value in the field, the workflow is straightforward but demands attention to detail.

**Step 1: Verify the certificate.** Confirm the testing body's accreditation (ATTMA or equivalent UKAS scope). Match the address and envelope area to the dwelling you are assessing. Check the date against the three-year validity window. Confirm both pressurisation and depressurisation results are recorded and that the mean is the stated result.

**Step 2: Enter the data.** In your RdSAP 10 software, select "measured" as the airtightness data source and enter the q₅₀ value from the certificate. Do not convert, round aggressively, or estimate. Enter the figure as stated to one decimal place.

**Step 3: Retain the evidence.** The test certificate must be retained in your assessment file for audit purposes. Accreditation scheme audit protocols now include specific checks for measured airtightness entries — this is a flagged field because it has a material impact on the rating and is therefore a target for manipulation or error. If audited, you will need to produce the certificate.

**Common errors to avoid:**

- Entering n₅₀ (air changes per hour at 50 Pa) instead of q₅₀ (air permeability in m³/(h·m²) at 50 Pa). The certificate should clearly label which is which. If in doubt, check the units.
- Using a test certificate from a different dwelling in a block of similar properties. Each certificate applies to a specific tested unit.
- Entering a measured value for a dwelling where the test was conducted before significant alteration works (e.g., new windows installed after the test). The value no longer represents the dwelling's current state.
- Assuming that a measured value will always improve the rating. In some cases — particularly well-built post-2000 homes — the age-band default may already assume reasonable airtightness, and a measured result could be higher (leakier) than the default, reducing the SAP score.

Where no valid test certificate is available, leave the software on its default setting. Do not estimate or guess at a value. The default pathway remains the correct and compliant approach for the majority of existing dwelling assessments.

---

## Key Takeaways

- RdSAP 10 introduces, for the first time, a data entry field for measured air permeability in existing dwelling assessments, replacing the default-only approach of RdSAP 9.94.
- The age-band default air permeability values have been recalibrated using updated field data, with notable adjustments for mid-20th century dwelling archetypes.
- A measured value may only be entered when supported by a compliant test certificate (ATTMA TSL1, CIBSE TM23, or BS EN ISO 9972:2015) from an accredited tester, dated within three years of assessment or linked to a completed PAS 2035 retrofit.
- The correct unit for data entry is air permeability q₅₀ in m³/(h·m²) at 50 Pa — not air changes per hour (n₅₀). Confusing these is the single most common input error.
- Post-retrofit EPCs following PAS 2035 projects represent the primary use case for measured airtightness data; DEAs should routinely request the test certificate from the Retrofit Coordinator.
- A measured airtightness result will not always improve the SAP rating — it depends on how the measured value compares to the age-band default for that dwelling type.
- The test certificate must be retained in the assessment evidence file; measured airtightness entries are specifically flagged in accreditation scheme audit protocols.

---

## Self-Assessment Questions

**Q1.** Under RdSAP 10, what is the correct unit for entering a measured airtightness result?

A) Air changes per hour at 50 Pa (n₅₀)
B) Air permeability in m³/(h·m²) at 50 Pa (q₅₀)
C) Litres per second per square metre at 4 Pa
D) Cubic metres per hour at 25 Pa

**Correct answer: B**
*RdSAP 10 requires the air permeability value q₅₀, measured in m³/(h·m²) at 50 Pa, which is referenced to the total envelope area. This is distinct from n₅₀, which is referenced to dwelling volume.*

---

**Q2.** What is the maximum age of an airtightness test certificate for it to be valid for entry into an RdSAP 10 existing dwelling assessment (under standard conditions)?

A) 12 months
B) 2 years
C) 3 years
D) 5 years

**Correct answer: C**
*The RdSAP 10 conventions specify that the test must have been conducted no more than three years prior to the assessment date, unless it is linked to a PAS 2035 project where the measures remain unaltered.*

---

**Q3.** A DEA is producing a post-retrofit EPC for a 1950s semi-detached house. The PAS 2035 Retrofit Coordinator provides an airtightness test certificate showing a q₅₀ of 7.2 m³/(h·m²) at 50 Pa. The RdSAP 10 age-band default for this dwelling type is approximately 12 m³/(h·m²) at 50 Pa. What is the most likely impact of entering the measured value?

A) No impact — measured and default values are treated identically
B) The SAP rating will decrease because a lower permeability increases overheating risk
C) The ventilation heat loss will reduce, likely improving the SAP rating
D) The software will reject the value because it is below the default

**Correct answer: C**
*A measured permeability significantly lower than the default reduces calculated infiltration and therefore ventilation heat loss. This will improve the fabric energy efficiency and likely improve the overall SAP rating.*

---

**Q4.** Which of the following would be a valid reason for a DEA to decline to enter a measured airtightness value from a test certificate?

A) The result is higher (leakier) than the RdSAP 10 default
B) The test was conducted by an ATTMA-registered tester
C) The certificate's envelope area differs significantly from the assessor's calculated envelope area
D) The test was conducted using depressurisation only

**Correct answer: C**
*A significant discrepancy between the certificate's envelope area and the assessor's own calculation suggests the test may not relate to the dwelling as currently configured. Option D is also a concern (both pressurisation and depressurisation are required), but Option C is the clearest basis for rejecting the certificate's applicability to this specific assessment.*

---

**Q5.** Under PAS 2035:2023, what principle governs the relationship between airtightness improvement and ventilation?

A) "Build tight, ventilate later"
B) "Seal tight, ventilate right"
C) "Fabric first, services second"
D) "Insulate before you ventilate"

**Correct answer: B**
*PAS 2035:2023 explicitly adopts the "seal tight, ventilate right" principle, requiring that any airtightness improvements are accompanied by adequate ventilation provision to maintain indoor air quality.*

---

## Further Reading

- **BRE: RdSAP 10 Specification and Conventions Document** — Available via the BRE SAP website. The definitive technical reference for all RdSAP 10 input conventions, including the treatment of measured and default airtightness.
  [https://www.bregroup.com/sap/](https://www.bregroup.com/sap/)

- **BSI PAS 2035:2023 — Retrofitting Dwellings for Improved Energy Efficiency: Specification and Guidance** — The current retrofit standard mandating fabric-first approaches and ventilation adequacy in publicly funded schemes.
  [https://knowledge.bsigroup.com/products/retrofitting-dwellings-for-improved-energy-efficiency-specification-and-guidance](https://knowledge.bsigroup.com/products/retrofitting-dwellings-for-improved-energy-efficiency-specification-and-guidance)

- **ATTMA Technical Standard L1: Measuring Air Permeability of Building Envelopes (Dwellings)** — The testing protocol and certificate requirements for domestic airtightness testing in the UK.
  [https://www.attma.org/technical-standards/](https://www.attma.org/technical-standards/)

- **BS EN ISO 9972:2015 — Thermal Performance of Buildings: Determination of Air Permeability of Buildings — Fan Pressurization Method** — The underlying international standard for blower door test methodology.
  [https://www.iso.org/standard/55718.html](https://www.iso.org/standard/55718.html)

---

*© Meridian CPD 2026. All rights reserved. Unauthorised reproduction prohibited.*
*This course material is licensed to individual subscribers only.*