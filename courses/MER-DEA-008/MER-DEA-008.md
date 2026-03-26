

# Insulation in RdSAP 10: Walls, Roofs, Floors and Common Errors
**Course ID:** MER-DEA-008 | **CPD Hours:** 1.0 | **Published:** March 2026
*© Meridian CPD 2026. All rights reserved.*

---

## Learning Objectives

- Apply the correct wall construction classification and insulation input conventions in RdSAP 10, distinguishing between evidenced and default U-values across all wall types.
- Record roof and loft insulation data accurately under RdSAP 10 conventions, including accessible and inaccessible configurations and the treatment of room-in-roof constructions.
- Identify the floor insulation input requirements for suspended timber, solid, and insulated slab floors, and correctly apply default and evidenced U-values.
- Recognise the top audit failure categories for fabric insulation data and implement site practices that prevent them.
- Determine the correct evidence standard required to claim insulation performance above the age-band default for each element type.

---

## Introduction

Fabric insulation is the largest single determinant of a dwelling's space-heating energy demand in RdSAP 10. Walls, roofs, and floors account collectively for the majority of calculated heat loss in most UK housing stock, and errors in insulation inputs propagate directly into the EPC rating, the improvement recommendations, and — where the assessment feeds into a retrofit project — the specification and budget for any fabric measures.

RdSAP 10 has tightened the input conventions, updated the default U-value tables, and clarified what constitutes acceptable evidence for above-default claims. The changes are incremental rather than revolutionary, but they are changes you need to apply consistently. The most common audit failures in insulation data are not exotic edge cases — they are systematic errors: wrong construction type classification, failure to identify insulation that is present, and overclaiming insulation performance without adequate evidence.

This course covers walls, roofs, and floors in sequence. For each element, the focus is on the RdSAP 10 input logic, the default and override mechanism, the evidence requirements, and the specific failure points that scheme auditors flag most frequently. Throughout, references are to the RdSAP 10 specification and current accreditation scheme guidance.

---

## Section 1: Wall Insulation — Construction Types, Defaults and the Evidence Hierarchy

**Construction type classification.** RdSAP 10 organises wall construction into the following main categories: masonry cavity wall, masonry solid wall, timber frame, system build (concrete panel, prefabricated), and stone wall (sandstone or limestone; granite). The correct classification is the starting point for everything else — the wrong construction type produces incorrect default U-values and incorrect insulation options in the software.

The most common misclassification is between cavity wall and solid wall in properties built between 1920 and 1945. Not all interwar housing has a cavity: many properties of this era are solid 9-inch brick. The test is not age alone — it is construction evidence. Check the external wall at the DPC level or at any exposed return (corner, window reveal, door frame). A brick bond with through-headers visible (Flemish or English bond) indicates solid construction. A stretcher bond throughout, with no visible through-headers, is consistent with cavity construction. Where evidence is genuinely ambiguous and the property predates 1935, the conservative default is solid wall.

**Cavity wall insulation.** For unfilled cavities, RdSAP 10 applies a default U-value based on wall construction type and age. For filled cavities (CWI), the assessor must enter the insulation type (blown mineral fibre, EPS beads, polyurethane foam, or other) and the approximate installation date. RdSAP 10 uses this to apply an appropriate insulated U-value. Critically, you must not enter CWI unless you have evidence that the cavity is filled. Acceptable evidence includes: a CIGA guarantee (Cavity Insulation Guarantee Agency), a BBA certificate on file, a CO2 registration certificate, a building control completion certificate, or a formal declaration from the property owner confirmed by documentary trail. Visual inspection from outside is insufficient — a cavity can appear undisturbed while being filled, and vice versa. If in doubt, the unfilled default applies.

**Solid wall insulation.** For solid walls with IWI (internal wall insulation) or EWI (external wall insulation), the assessor must identify whether insulation is present and, if so, record the insulation type and thickness. IWI is identifiable by a reduced room depth compared with external dimensions, or by the presence of a plasterboard lining with an obvious depth addition at reveals and junctions. EWI is identifiable externally by the tell-tale signs: render over a different texture to the original walling, thickened reveals, recessed windows, or a visible edge detail at the DPC. Both are frequently missed by assessors who do not look carefully at reveals and junctions. Missed insulation is a direct audit failure — you have recorded a worse performance than the property actually has.

**Default versus evidenced U-values.** RdSAP 10 provides age-band default U-values for all construction types. An assessor may override the default only where the actual insulation specification is known and evidenced. For CWI, the insulation type is the override trigger — the software derives the insulated U-value from the construction and insulation combination. For IWI and EWI on solid walls, if you have the insulation thickness and type (rigid PIR, mineral wool, EPS), you can enter a calculated or manufacturer-declared U-value. Without evidence of the specification, you must use the appropriate insulated default, which RdSAP 10 provides for each combination.

---

## Section 2: Roof Insulation — Accessible Loft, Inaccessible, and Room-in-Roof

**Accessible loft insulation.** For standard pitched roofs with an accessible loft space, RdSAP 10 requires the assessor to record the insulation position (at ceiling joist level), the insulation type, and the depth. The assessor must physically access the loft to measure insulation depth — or, where access is genuinely impossible, apply the age-band default. The depth measurement should be taken at the centre of the loft, not at the eaves where insulation typically compresses or thins. Where the depth varies significantly across the loft, record the average. RdSAP 10 defines minimum depth categories (the software maps depth to a U-value using construction-specific thermal conductivity assumptions), so exact depth matters — the difference between 100 mm and 150 mm is a step change in calculated U-value.

Do not record loft insulation that the occupant claims is present without visual confirmation. The most common fraud vector in EPC data is overclaimed loft insulation. If you cannot access the loft, you cannot confirm depth, and the default applies.

**Inaccessible pitched roof.** Where the loft is inaccessible (hatch sealed or absent, storage rammed to the apex, health and safety concern), RdSAP 10 requires the assessor to use the appropriate default. This should be clearly documented in site notes with the reason for inaccessibility. "Occupant said it is insulated" is not a basis for an override.

**Flat roofs.** For flat roofs, RdSAP 10 distinguishes between insulated and uninsulated. An insulated flat roof has insulation either above the structural deck (warm roof) or below it (cold roof with insulation at ceiling level). The key input is whether insulation is confirmed present and, where the specification is known, the type and thickness. Age-band defaults apply where specification is unknown. Many flat roofs have had insulation added retrospectively — a sudden step in the internal ceiling height visible from the room below, or a thickness increase at the roof edge, can indicate this.

**Room-in-roof.** Room-in-roof construction requires the assessor to classify the element as Type 1 (separate room-in-roof construction, insulated at the sloping ceiling and knee walls) or Type 2 (integrated room-in-roof where the roof slope forms the room envelope). The insulation inputs for each type differ — this is covered in detail in MER-DEA-004. For this course, the key point is that room-in-roof elements are not entered as loft insulation; they are a separate construction category.

---

## Section 3: Floor Insulation — Solid, Suspended Timber, and Insulated Slab

Floor insulation is the element type most frequently recorded incorrectly in RdSAP 10 assessments, both through over-claim (recording insulation that is not present) and under-claim (missing insulation added during renovation works).

**Solid ground floors.** For solid concrete slab ground floors, the default assumption in RdSAP 10 is uninsulated for most age bands. Where insulation is present below the slab, above the slab (screed insulation), or at the perimeter (edge insulation only), this must be identifiable from the construction. Below-slab insulation is not visible during a survey and cannot be confirmed without documentation (building regulations completion certificate, thermal specification drawings, or a renovation record from the owner). Perimeter insulation only (edge insulation) has a different effect on calculated U-value than full below-slab insulation and is entered separately in the software.

**Suspended timber floors.** For suspended timber ground floors, the default is uninsulated. Insulation in a suspended floor (typically mineral wool batts between the joists) is visible either by lifting a loose board, looking through a vent opening, or — in many cases — by a marked change in the underfloor draught characteristics when the vent is opened. Where the floor is carpeted and boards are not accessible, the default applies unless documentary evidence exists. Do not enter suspended floor insulation based on an occupant claim without visual or documentary confirmation.

**Underfloor heating as a proxy.** Properties with underfloor heating (particularly wet UFH in a screed) are sometimes assumed to have floor insulation by assessors. This is not necessarily true — the installation of UFH does not mandate insulation, though good practice requires it. Unless the installation specification or building control sign-off confirms the insulation layer, the default applies.

**Upper floors.** Floors above unheated spaces (garages, unheated utility rooms, basement areas) are treated as exposed floor elements in RdSAP 10. The insulation inputs follow the same logic — evidenced or default — but the exposure condition (floor over unheated space) must be correctly identified. A floor entered as ground floor when it is actually over an unheated garage will produce a materially incorrect U-value.

---

## Section 4: Common Audit Failures in Fabric Data

Scheme auditor data from 2024 and 2025 shows a consistent set of fabric-related audit failure categories. These are not isolated incidents — they represent systematic errors made by a significant proportion of assessors across all scheme providers.

**Failure 1: Wrong wall construction type.** Solid walls recorded as cavity, or vice versa. Most common in interwar stock (1920–1939) and system-built properties (1950s–1970s). The fix is to check brick bond visually and consult construction databases (the BRE's English Housing Survey data, Historic England's guidance on interwar housing construction) where the external evidence is ambiguous.

**Failure 2: CWI claimed without evidence.** Cavity wall insulation entered where no evidence is available. This is the most frequently challenged failure because it inflates the EPC rating, which can affect renewable heat incentive eligibility and mortgage valuations. The fix is to record unfilled cavity and note "no CWI evidence available" in site notes.

**Failure 3: Loft insulation depth overclaimed.** The most common depth error is recording 200 mm when the measured depth is 100–150 mm. This is a significant error — the difference in U-value between 100 mm and 200 mm of mineral wool is approximately 0.08 W/m²K, which translates directly into space heating demand and rating. Measure, do not estimate.

**Failure 4: Floor construction not verified.** Suspended timber floors recorded as solid, or floors over unheated spaces recorded as ground floors. The fix is to check floor construction at the accessible perimeter (under stairs, at a threshold, through a vent).

**Failure 5: Insulation claimed on the basis of age alone.** Entering insulated values for elements because the property was "built after Building Regulations required it" without confirming the insulation is actually present. Regulations require it; that does not mean it was done.

---

## Key Takeaways

- Classify wall construction from visual evidence (brick bond, reveals, wall thickness), not from age alone — interwar and system-build properties are frequently misclassified.
- Do not enter CWI without documentary evidence: CIGA guarantee, BBA certificate, CO2 registration, or building control sign-off.
- Measure loft insulation depth physically and at the centre of the loft — do not accept occupant claims without visual confirmation.
- Floor construction type and insulation must be confirmed from the accessible perimeter or from documentation — carpet is not an obstacle to inquiry.
- Floors above unheated spaces are exposed floor elements and must be identified as such, not entered as ground floors.
- Any insulation claim above the age-band default requires retained evidence — the audit file must support the claim.
- The five most common fabric audit failures are wall type misclassification, uncertified CWI claims, loft depth overclaim, floor type error, and age-based insulation assumptions. All are avoidable.

---

## Self-Assessment Questions

**Q1.** A 1932 semi-detached property has external walls laid entirely in stretcher bond with no visible through-headers. The wall appears to be approximately 275 mm thick externally. What is the most likely construction?

A) 9-inch solid brick
B) Cavity masonry wall
C) Timber frame with brick cladding
D) Concrete panel system build

**Correct answer: B**
*Stretcher bond throughout with no visible through-headers is consistent with cavity wall construction. The 275 mm thickness is also consistent with a standard cavity wall. Solid brick in English or Flemish bond would show alternating header courses.*

---

**Q2.** An assessor visits a 1960s semi-detached property. The occupant states the cavity was insulated "about ten years ago" but cannot produce any paperwork. What should the assessor record?

A) CWI present — occupant verbal confirmation is acceptable evidence
B) Unfilled cavity — no documentary evidence available
C) CWI present, type unknown, estimated date 2015
D) The assessor should decline to survey until documentation is provided

**Correct answer: B**
*Verbal confirmation from the occupant is not acceptable evidence for CWI under RdSAP 10 conventions. The assessor records unfilled cavity and notes in the site file that the occupant claimed CWI but no documentation was available.*

---

**Q3.** A loft space contains variable mineral wool insulation: 180 mm at the centre, thinning to approximately 50 mm at the eaves. What depth should be entered in RdSAP 10?

A) 50 mm — the minimum depth governs
B) 180 mm — the depth at the centre governs
C) 115 mm — the average of 180 mm and 50 mm
D) The depth measured at the loft hatch

**Correct answer: B**
*RdSAP 10 convention is to record the depth at the centre of the loft. Thinning at the eaves is normal and is not used to reduce the recorded depth. The centre measurement represents the thermally significant zone.*

---

**Q4.** A 1970s terraced property has a solid concrete ground floor throughout the ground level. No renovation records are available. The occupant says the floor "feels warm." What should the assessor enter?

A) Insulated solid floor — occupant perception suggests insulation
B) Uninsulated solid floor — age-band default applies, no documentary evidence of insulation
C) Suspended timber floor — common in 1970s terraces
D) Insulated floor, screed over insulation, as the 1970s Building Regulations required it

**Correct answer: B**
*1970s Building Regulations did not mandate floor insulation. Occupant perception of warmth is not evidence of insulation. Without a building control completion certificate, renovation record, or visible evidence of an insulation layer, the uninsulated default applies.*

---

**Q5.** A property has a room above an integral unheated garage. The assessor enters this floor as a standard ground floor. What is the likely audit outcome?

A) No issue — ground floor and floor over unheated space have the same default U-value
B) Audit failure — the floor should be classified as an exposed floor over unheated space, producing a different U-value
C) Minor discrepancy — acceptable within tolerance
D) No issue if the floor is carpeted

**Correct answer: B**
*A floor above an unheated space is an exposed floor element in RdSAP 10 with its own U-value calculation, not a ground floor. Entering it as a ground floor produces an incorrect (and typically better) U-value, which is a methodology failure on audit.*

---

## Further Reading

- **RdSAP 10 Specification Document** — Department for Energy Security and Net Zero (DESNZ). Available via: https://www.bregroup.com/sap/
- **BRE Housing Stock Data — Construction Type Reference** — BRE Group. Available at: https://www.bregroup.com/
- **CIGA (Cavity Insulation Guarantee Agency) — Guarantee and Installation Standards.** Available at: https://www.ciga.co.uk/
- **Historic England — Thermal Improvements to Traditional Buildings.** Available at: https://historicengland.org.uk/
- **PAS 2035:2023 — Retrofitting Dwellings for Improved Energy Efficiency** — BSI. Available at: https://www.bsigroup.com/

---

*© Meridian CPD 2026. All rights reserved. Unauthorised reproduction prohibited.*
*This course material is licensed to individual subscribers only.*
