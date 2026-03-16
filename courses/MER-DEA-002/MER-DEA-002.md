

# Measuring Windows in RdSAP 10
**Course ID:** MER-DEA-002 | **CPD Hours:** 1.0 | **Published:** March 2026
*© Meridian CPD 2026. All rights reserved.*

---

## Learning Objectives

- Apply the revised RdSAP 10 window measurement conventions correctly, distinguishing between the frame opening method and the previous RdSAP 9.94 approach.
- Identify when default window areas apply and calculate the threshold conditions that trigger their use within the RdSAP 10 methodology.
- Correctly assign glazing types, frame types, and gap sizes to measured windows using the RdSAP 10 input conventions, including the updated treatment of secondary glazing.
- Recognise and avoid the most common audit failure points related to window measurement, orientation assignment, and data entry as identified in recent Elmhurst and Stroma scheme auditor bulletins.
- Determine the appropriate evidence standard for window age, specification, and U-value claims in both EPC and retrofit (PAS 2035:2023) contexts.

---

## Introduction

Window measurement has always been a disproportionate source of audit failures, lodgement queries, and — more consequentially — inaccurate EPC ratings. With the transition to RdSAP 10, the conventions governing how we measure, record, and characterise windows have been refined in ways that are subtle but materially significant to calculated energy performance.

The shift matters now for three reasons. First, the RdSAP 10 calculation engine treats solar gain, thermal bridging at openings, and ventilation heat loss with greater granularity than its predecessor. Inaccurate window data therefore propagates more aggressively through the calculation than it did under RdSAP 9.94. Second, the convergence of EPC and retrofit assessment pathways — formalised through PAS 2035:2023 and the updated TrustMark data requirements — means that window data captured during an EPC survey increasingly feeds directly into medium-term retrofit plans. Getting it wrong has downstream consequences beyond the certificate itself. Third, scheme auditors have tightened tolerances. Recent bulletins from accreditation bodies have made clear that window measurement discrepancies exceeding defined thresholds will be treated as methodology failures, not minor variances.

This course is not a primer on what a window is. You measure windows regularly. The purpose here is to nail the specific RdSAP 10 conventions — where they differ from what you may have been doing for years, where the tolerances sit, and where the methodology gives you discretion versus where it does not. We will address the measurement protocol itself, the classification and specification inputs, the default and override mechanisms, and the practical application of all of this on site.

Throughout, references are to the RdSAP 10 specification document (BEIS/DESNZ), the SAP 10.2 conventions it derives from, and current scheme guidance. Where PAS 2035:2023 imposes additional or different requirements for retrofit assessments, these are noted explicitly.

If you are still measuring windows the way you were taught in 2013, parts of this course will require you to change your practice. That is the point.

---

## Section 1: The RdSAP 10 Measurement Convention — What Has Actually Changed

The foundational rule in RdSAP 10 remains consistent with SAP convention: windows are measured as the total area of the opening in the wall, including the frame. You are measuring the structural opening, not the glazed area alone. This has not changed. What has changed is the rigour with which this principle is now expected to be applied and the way the methodology handles situations where direct measurement is not possible.

**Frame opening versus reveal-to-reveal.** Under RdSAP 9.94, common practice among many assessors was to measure reveal-to-reveal internally — the visible opening from inside the room. RdSAP 10 makes explicit that the correct measurement is the full structural opening as seen from the external face of the wall. In cavity wall construction, this typically adds 25–50 mm per side compared with an internal reveal measurement, depending on reveal depth and plaster thickness. On a standard 1200 × 1050 mm window, this can represent a 5–8% increase in recorded area. Across a dwelling with 15–20 openings, the cumulative effect on total glazed area — and therefore on fabric heat loss, solar gain, and the balance between the two — is not trivial.

In practice, direct external measurement of every opening is not always feasible (access constraints, height, extensions built to boundary). The RdSAP 10 conventions permit internal measurement with an addition for the reveal depth on each side where external measurement cannot be taken. The convention specifies that where reveal depth cannot be determined, a default addition is applied based on wall construction type. For standard masonry cavity walls, this is 25 mm per reveal side and 25 mm at the cill. For solid walls (stone or brick), the default is larger — typically 50 mm per side — reflecting deeper reveals. Timber frame constructions assume minimal reveal depth and no default addition is required beyond the measured internal dimension.

**Measurement tolerance.** RdSAP 10 does not define an explicit percentage tolerance for window measurement in the specification document itself, but scheme auditor guidance — most recently updated by Elmhurst Energy (Auditor Technical Bulletin 2025-07) and Quidos — applies a ±10% tolerance on individual window areas and a ±5% tolerance on total glazed area for the dwelling. Exceeding these thresholds on audit constitutes a methodology failure. This is tighter than the informal tolerances many assessors were working to previously.

**Rounding.** Individual window dimensions should be recorded to the nearest 10 mm. Areas should be calculated in square metres to two decimal places. Do not round individual window areas before summing.

---

## Section 2: Glazing Classification, Frame Types, and the Updated Input Matrix

Measuring the opening accurately is only half the task. The energy impact of a window in RdSAP 10 depends on the interplay between area, orientation, glazing type, frame material, gas fill, gap size, and — now more prominently — the window energy rating (WER) or declared U-value where available.

**Glazing type hierarchy.** RdSAP 10 maintains the hierarchy: single glazed, double glazed, triple glazed, secondary glazing. Within double and triple glazing, the methodology differentiates by gap size (6 mm, 12 mm, 16 mm or more) and gas fill (air, argon, krypton). The critical change in RdSAP 10 is the updated default U-values assigned to each combination. These have been recalculated using EN 673:2011 conventions and are marginally different from the RdSAP 9.94 defaults — in most cases slightly worse for older air-filled units and slightly better for modern argon-filled 16 mm+ units. The net effect is a wider spread between good and poor glazing in the calculation, which amplifies the importance of correct classification.

**Window Energy Rating (WER) and manufacturer data.** Where a window carries a BFRC (British Fenestration Rating Council) rating, this can be entered directly into RdSAP 10 using the WER band (A++ through E) or, preferably, the specific declared U-value and g-value from the BFRC certificate or datasheet. The RdSAP 10 software interface now requires assessors to declare the basis for any claimed performance — WER band, declared U-value, or default. This declaration is auditable. Claiming a WER band without supporting evidence (FENSA certificate, BFRC label, building control sign-off, or manufacturer documentation) is a fail point. In the absence of evidence, you must use the appropriate default for the assessed age and type.

**Frame types.** RdSAP 10 classifies frames as wood, PVC-U, metal (with and without thermal break), and composite. The frame type affects both the U-value (through frame factor adjustments) and the solar gain (through the frame-to-glazing ratio assumed in the calculation). The frame factor defaults are: wood 0.70, PVC-U 0.70, metal with thermal break 0.70, metal without thermal break 0.80, composite per manufacturer data or 0.70. These frame factors represent the fraction of the opening area that is glazed. Note that metal frames without thermal breaks — still common in pre-1990s local authority housing — have a meaningfully different frame factor that reduces effective glazed area while simultaneously having a higher frame U-value.

**Secondary glazing.** RdSAP 10 retains secondary glazing as a separate input category but now requires the gap between primary and secondary panes to be estimated and recorded (less than 20 mm or 20 mm and above). The effective U-value calculation for secondary glazing is significantly more favourable with a gap of 20 mm or more. If you cannot determine the gap, the default is less than 20 mm.

**Curtain walling and non-standard glazing.** Full-height glazed elements, structural glazing, and curtain walling systems are entered as windows in RdSAP but must be measured to the full extent of the glazed structural opening. Where curtain walling extends below floor level or into non-heated zones, only the portion bounding the heated envelope is measured.

---

## Section 3: Defaults, Overrides, and the Age-Based Fallback Logic

RdSAP 10, like its predecessors, is a reduced-data methodology. Its entire architecture is built around the principle that where measured or evidenced data is not available, a defensible default is applied. For windows, the default logic is more layered than many assessors appreciate, and misapplication of defaults is a persistent audit issue.

**When defaults apply.** You use default window areas when you genuinely cannot measure the windows — the classic example being an inaccessible elevation, or a survey conducted under conditions where measurement is physically impossible (rare, and requiring justification in site notes). Under RdSAP 10, the default total window area is calculated as a percentage of total floor area, varying by dwelling age band. For dwellings in age band A–B (pre-1900), the default is approximately 15% of total floor area. For age bands up to and including J (2003–2006), it increases progressively to around 22%. Post-2006 bands reflect the larger glazed areas typical of modern construction standards and Building Regulations Part L requirements. These percentages are applied to total floor area, and the resulting area is distributed across orientations using a standard split unless the assessor specifies otherwise.

**The critical point: defaults are a fallback, not a shortcut.** If you can measure the windows, you must measure the windows. Entering default areas because measurement is tedious or time-consuming is a methodology violation. Scheme auditors will check site photographs against recorded areas and, increasingly, use satellite and street-level imagery to verify that measured areas are broadly consistent with the visible fenestration.

**Age-based glazing type defaults.** Where the glazing type cannot be determined (sealed unit with no markings, no FENSA certificate, no Building Control record, and visual inspection is inconclusive), RdSAP 10 assigns a default based on the window installation date — which is often, but not always, the same as the dwelling age band. If there is evidence that windows have been replaced (different style from originals, FENSA sticker, visible trickle vents on a property where originals would not have had them), the assessor must estimate the replacement date and apply the corresponding default. For replacements where the date cannot be determined but post-2002 installation is evident (trickle vents present, modern PVC-U profile), the default is double glazed, air-filled, 12 mm gap, PVC-U frame. For known post-April 2006 installations, the default shifts to double glazed, low-E hard coat, argon-filled, 16 mm gap.

**Override with evidence.** An assessor may override the defaults with better performance data only where documentary evidence exists and can be retained. Acceptable evidence under RdSAP 10 conventions includes: FENSA or CERTASS certificate, Building Control completion certificate, BFRC rating label or certificate, manufacturer's declaration with U-value data, or a GGF (Glass and Glazing Federation) data sheet referencing the specific installation. Anecdotal evidence from the occupant ("we had them done about five years ago, they're triple glazed") is not acceptable as the sole basis for an override, though it can support a reasonable assessment of installation age where combined with visual evidence.

**Mixing window types.** Most dwellings contain a mix of window ages and types. RdSAP 10 allows multiple window groups to be defined, each with its own glazing type, frame type, orientation, and area. There is no limit on the number of window groups. Best practice is to group windows by common specification — for example, all original single-glazed timber sash windows as one group, all replacement PVC-U double-glazed units as another. Avoid defining excessive groups where the specification is identical; this increases data entry time without improving accuracy and can introduce rounding discrepancies.

---

## Section 4: On-Site Best Practice and Common Audit Failures

Knowing the conventions is necessary. Applying them reliably on a wet Tuesday afternoon in a terraced house with an uncooperative occupant is the actual skill. This section addresses the practical workflow.

**Kit.** A laser measure is now effectively mandatory for defensible window measurement. Tape measures remain acceptable under scheme rules, but the accuracy and speed of a laser measure — particularly for heights and for windows above ground floor — make it the professional standard. Record all measurements in your site notes contemporaneously. Photograph every window group with the laser measure display visible in the shot where possible.

**Orientation.** RdSAP 10 assigns solar gain by orientation. Compass bearings must be taken on site (phone compass is acceptable if calibrated). A common audit failure is to assign orientation based on assumed north from the surveyor's mental model of the property rather than measured bearing. If the front of the property faces, say, 280° (west-north-west), all window orientations must be derived from this measured reference, not from "front = north" shorthand. RdSAP 10 uses eight compass points. Assign each window group to the nearest.

**Documenting evidence.** Photograph FENSA certificates, BFRC labels, and any visible manufacturer stamps on spacer bars or frame profiles. Where you are claiming a specification above the age-band default, the audit file must contain the supporting evidence. No photo, no claim.

**The top five audit failure points for windows, per scheme auditor data (2024–2025):**

1. Total glazed area outside ±5% tolerance due to inconsistent measurement method (internal vs. external).
2. Glazing specification claimed without retained evidence.
3. Orientation misassigned by one or more compass points.
4. Secondary glazing gap not recorded or incorrectly defaulted.
5. Replacement windows recorded at dwelling age-band default instead of estimated replacement date default.

Each of these is avoidable with disciplined site practice. None of them require additional time on site — they require attention to the correct convention applied consistently.

---

## Key Takeaways

- Measure the full structural opening from the exterior face where accessible; apply the wall-type-specific reveal addition when measuring internally.
- Record dimensions to the nearest 10 mm; calculate areas to two decimal places; do not round individual areas before summing.
- The ±5% tolerance on total glazed area is an audit hard line — cumulative small errors across many windows will breach it.
- Always declare the basis for glazing performance claims (WER, declared U-value, or default) and retain photographic or documentary evidence for any claim above the age-band default.
- Measure compass orientation on site for every property; assign window groups to the nearest of eight compass points based on the measured bearing of the elevation, not assumed orientation.
- Use replacement-date defaults for windows that have clearly been replaced, even where the exact date is unknown — do not default to the dwelling age band for visibly modern fenestration.
- Secondary glazing gap size (below or above 20 mm) now affects the calculated U-value materially; estimate and record it.

---

## Self-Assessment Questions

**Q1.** Under RdSAP 10 conventions, what is the correct measurement basis for a window opening?

A) The visible glazed area only, excluding frame
B) The internal reveal-to-reveal dimension
C) The full structural opening as seen from the external face of the wall, including the frame
D) The manufacturer's nominal frame size from the order specification

**Correct answer: C**
*RdSAP 10 specifies the full structural opening measured externally. Where external measurement is not possible, internal measurement with a construction-type-specific reveal addition is applied.*

---

**Q2.** An assessor measures all windows internally on a standard cavity-wall dwelling and applies no reveal depth addition. The total recorded glazed area is 18.5 m². Approximately what total area might more accurately reflect the RdSAP 10 convention, assuming a 25 mm addition per reveal side and cill across all openings?

A) 18.5 m² — no difference expected
B) 19.4–19.9 m²
C) 22.0 m²
D) 17.0 m²

**Correct answer: B**
*A 25 mm addition per side and cill on typical window dimensions adds approximately 5–8% to total recorded area. On 18.5 m², this equates broadly to 19.4–19.9 m². The exact figure depends on the number and size distribution of openings.*

---

**Q3.** The occupant states their windows were replaced "about eight years ago" and are triple glazed with argon fill. No FENSA certificate, BFRC label, or Building Control record is available. What should the assessor enter?

A) Triple glazed, argon-filled, based on the occupant's statement
B) The dwelling age-band default glazing type
C) Double glazed, low-E, argon-filled, 16 mm gap — the post-2006 replacement default — supported by visual evidence of modern installation
D) Single glazed, as no documentary evidence is available

**Correct answer: C**
*Occupant statements alone are insufficient to claim triple glazing. However, the assessor should apply the appropriate replacement-date default (not the dwelling age-band default) where visual evidence confirms modern replacement. If the replacement is clearly post-April 2006 but the triple-glazing claim cannot be evidenced, the post-2006 double-glazed default applies.*

---

**Q4.** In RdSAP 10, what is the default frame factor applied to PVC-U frames?

A) 0.60
B) 0.70
C) 0.80
D) 0.90

**Correct answer: B**
*PVC-U frames have a default frame factor of 0.70, meaning 70% of the measured opening area is assumed to be glazed. This is the same default as wood frames and metal frames with a thermal break.*

---

**Q5.** An assessor records secondary glazing but does not determine or record the gap between primary and secondary panes. What gap default does RdSAP 10 apply?

A) 20 mm or more
B) Less than 20 mm
C) 12 mm (same as standard double-glazing default)
D) No default is applied; the software rejects the entry

**Correct answer: B**
*Where the gap cannot be determined, RdSAP 10 applies the less favourable default of less than 20 mm. This produces a higher (worse) effective U-value than the 20 mm or more category. Assessors should attempt to estimate the gap where possible.*

---

## Further Reading

- **RdSAP 10 Specification Document** — Department for Energy Security and Net Zero (DESNZ). Available via the BRE SAP website: [https://www.bregroup.com/sap/](https://www.bregroup.com/sap/)

- **SAP 10.2: The Government's Standard Assessment Procedure for Energy Rating of Dwellings (2022 edition)** — DESNZ. Available at: [https://www.gov.uk/guidance/standard-assessment-procedure](https://www.gov.uk/guidance/standard-assessment-procedure)

- **PAS 2035:2023 — Retrofitting Dwellings for Improved Energy Efficiency: Specification and Guidance** — British Standards Institution (BSI). Available via BSI Shop: [https://www.bsigroup.com/](https://www.bsigroup.com/)

- **BFRC (British Fenestration Rating Council) — Window Energy Rating Scheme Documentation and Rated Product Directory.** Available at: [https://www.bfrc.org/](https://www.bfrc.org/)

---

*© Meridian CPD 2026. All rights reserved. Unauthorised reproduction prohibited.*
*This course material is licensed to individual subscribers only.*