

# Room in Roof: Type 1 and Type 2 in RdSAP 10
**Course ID:** MER-DEA-004 | **CPD Hours:** 1.0 | **Published:** March 2026
*© Meridian CPD 2026. All rights reserved.*

---

## Learning Objectives

- Correctly distinguish between Type 1 (integral) and Type 2 (connected) room-in-roof constructions as defined in the RdSAP 10 specification and apply the appropriate classification during data input.
- Identify the discrete thermal elements — gable walls, stud walls, sloping ceiling sections, and residual ceiling — that comprise each room-in-roof type and assign the correct insulation parameters to each element.
- Apply the revised dimensional conventions in RdSAP 10 for measuring and apportioning room-in-roof heat-loss areas, including the updated treatment of knee-wall height and collar tie position.
- Recognise common survey errors and lodgement rejections associated with room-in-roof entries and implement field-level quality assurance checks to prevent them.
- Evaluate the impact of room-in-roof insulation retrofit measures on the dwelling's SAP rating and fabric energy efficiency, with reference to PAS 2035:2023 medium-term improvement considerations.

---

## Introduction

Room-in-roof constructions remain one of the most frequently mis-recorded building elements in domestic energy assessments. Scheme audits consistently flag room-in-roof entries as a leading cause of lodgement queries, rating discrepancies, and — in retrofit contexts — incorrectly scoped insulation measures that fail to deliver projected energy savings. The transition to RdSAP 10 has sharpened the distinctions that assessors must make at the point of survey, and getting this wrong now carries greater consequence than it did under RdSAP 9.94.

RdSAP 10 retains the two-type classification system — Type 1 and Type 2 — but refines how each type's sub-elements are dimensioned, how insulation thickness assumptions are applied in the absence of evidence, and how the software handles the thermal bridging at junctions between insulated and uninsulated zones. The changes are not cosmetic. A Type 1 room-in-roof incorrectly entered as Type 2, or vice versa, will produce materially different heat-loss calculations because the two types model fundamentally different geometric and thermal relationships between the habitable loft space and the rest of the dwelling.

For assessors working within the retrofit supply chain — particularly those producing pre- and post-measure assessments under PAS 2035:2023 — accuracy in room-in-roof classification directly affects the medium-term improvement plan. An incorrectly baselined roof element can result in overstated improvement recommendations, which in turn creates compliance risk for the retrofit coordinator and, ultimately, the installer. The TrustMark framework and ECO4 verification processes are now cross-referencing lodged EPC data with measure installation reports; inconsistencies are being flagged algorithmically.

This course assumes you already understand basic roof construction typologies and the general principles of heat-loss calculation in RdSAP. It does not revisit first principles. The focus is on the specific, technical distinctions between Type 1 and Type 2, the dimensional and insulation conventions that apply to each, and the practical survey and data-entry discipline required to get the lodgement right first time.

---

## Section 1: Defining Type 1 and Type 2 — Geometry, Thermal Envelope, and Classification Criteria

The classification of a room-in-roof as Type 1 or Type 2 is determined by the structural and thermal relationship between the converted loft space and the storey immediately below it.

**Type 1: Integral room in roof.** The habitable loft space is open to the room below — that is, there is no thermally separating ceiling between the lower storey and the loft room. The most common example is a mezzanine or open-plan vaulted arrangement where the upper area is accessed via an open stairwell and shares the same air volume as the room beneath. In a Type 1, the dwelling's thermal envelope extends continuously from the ground floor up through the loft room's sloping ceilings and gable walls. There is no residual horizontal ceiling element at collar-tie level acting as part of the thermal envelope between the two volumes; the sloping sections run from the eaves knee wall to the ridge or to a flat ceiling section at or near the ridge.

**Type 2: Connected room in roof.** The habitable loft space is separated from the storey below by a distinct ceiling. The loft room is accessed through a doorway, staircase enclosure, or hatch — but critically, there is a horizontal ceiling plane that thermally separates the two zones. In a Type 2, the thermal sub-elements are: the sloping ceiling sections (typically two), the knee walls (typically two), the gable walls (one or two depending on dwelling position), and the flat ceiling at collar-tie level. Additionally, the residual ceiling — the portion of the original ceiling plane that remains between the knee wall and the eaves on each side — must be accounted for as a separate horizontal element.

The classification test is therefore straightforward in principle: **does a thermally separating horizontal ceiling exist between the lower storey and the loft room?** If yes, Type 2. If no, Type 1.

In RdSAP 10, this classification drives the software's treatment of the heat-loss elements. A Type 1 construction will not generate residual ceiling areas or a separating ceiling in the model; the heat-loss calculation runs through the sloping and vertical elements only. A Type 2 will generate both the sub-elements of the loft room envelope and the residual loft floor areas — the cold-side triangular sections either side of the knee walls that sit above the heated space below.

Assessors must make this determination on site. It cannot be reliably inferred from floor plans or estate-agent photographs. The presence of a closed staircase enclosure is a strong indicator of Type 2 but is not conclusive on its own; the thermal separation at ceiling level is the determinant, not the access arrangement.

---

## Section 2: Thermal Sub-Elements — Measurement Conventions and Insulation Inputs in RdSAP 10

Once classification is established, the assessor must identify, measure, and characterise each thermal sub-element. RdSAP 10 requires specific dimensional inputs that differ from the simplified approach in earlier versions.

**Knee walls.** These are the short vertical stud walls that run from the floor of the loft room to the point where the sloping ceiling begins. RdSAP 10 measures knee-wall height from the finished floor level of the loft room to the underside of the rafter or sloping ceiling lining at the junction point. Default knee-wall height, where measurement is not possible, is 1.2 m. Insulation assessment follows the standard convention: the assessor must determine whether insulation is present between the studs, the thickness and type (where ascertainable), and whether there is any secondary layer on the cold side. In practice, knee-wall insulation is frequently absent in older conversions — this should be recorded as "no insulation" rather than defaulted to an assumed level.

**Sloping ceiling sections.** Measured from the top of the knee wall to the underside of the collar tie (Type 2) or to the ridge (Type 1, where no collar tie forms a flat ceiling). The slope length is the rafter length along the surface, not the horizontal projection. RdSAP 10 expects the assessor to record whether insulation is between rafters only, between and above, or absent. Where insulation is present between rafters, the maximum insulation thickness that can be recorded is limited to the rafter depth — any compression must be accounted for. Rafter depths of 100 mm and 150 mm are most common in UK housing stock; recording 200 mm of mineral wool in a 100 mm rafter void is a data-quality error that will correctly be flagged.

**Flat ceiling (collar-tie level) — Type 2 only.** The horizontal ceiling at the top of the loft room. Width is measured internally wall-to-wall; length follows the room dimension. Insulation above the collar tie is recorded if present and accessible for inspection.

**Residual ceiling — Type 2 only.** The triangular or trapezoidal loft-floor sections between the knee wall and the eaves, sitting above the heated room on the storey below. These areas are part of the original ceiling plane. RdSAP 10 calculates them from the dimensional inputs; the assessor does not enter a separate area but must ensure the storey-below ceiling dimensions and the knee-wall position are consistent so the software correctly derives the residual area. Insulation here is typically the original loft insulation — 100 mm mineral wool in many pre-2000 conversions — and should be recorded at the thickness observed, not assumed to match the loft room elements.

**Gable walls.** Recorded as the exposed gable area within the room-in-roof zone. Construction type follows normal wall conventions. In mid-terrace properties there are no exposed gables; in semi-detached or end-terrace, one gable is exposed; in detached, typically two.

---

## Section 3: Common Errors, Audit Failures, and Quality Assurance at Survey

Accreditation scheme audit data consistently identifies room-in-roof entries among the highest-frequency error categories. Understanding where assessors routinely go wrong is essential to avoiding costly re-lodgements and the reputational risk of scheme sanctions.

**Error 1: Misclassification of Type 1 vs Type 2.** The most consequential error. It typically arises when the assessor encounters an enclosed staircase leading to a loft room and assumes Type 2 without confirming a thermally separating ceiling exists. In some conversions, the staircase is enclosed but the ceiling between the lower room and loft void has been removed to create a partial double-height space. This is Type 1. Conversely, an open-tread staircase with a plasterboard ceiling intact at first-floor level is Type 2. **Always verify the ceiling plane, not the staircase.**

**Error 2: Omitting the residual ceiling (Type 2).** If the assessor enters a Type 2 room-in-roof but provides dimensional data that implies the entire first-floor ceiling is accounted for by the room-in-roof footprint, the residual ceiling areas are lost from the model. This under-reports heat loss. The software in RdSAP 10 cross-checks these areas, but only if the dwelling dimensions and room-in-roof dimensions are internally consistent. Inaccurate room dimensions propagate into incorrect residual areas. Measure carefully.

**Error 3: Over-stating insulation in sloping sections.** Assessors record insulation thickness without accounting for rafter depth constraints. If the void between rafters is 100 mm deep and is fully filled with mineral wool, the insulation thickness is 100 mm — not the thickness of the batt before compression. Where insulation is between and above rafters (e.g., rigid board below the rafter with mineral wool between), each layer must be separately justifiable. If you cannot see behind the plasterboard lining, the convention is "as built" with reference to the age of the conversion and the building regulations applicable at the time — not a best-case assumption.

**Error 4: Treating a dormer as a room-in-roof.** A dormer window changes the geometry of the roof but does not automatically create a room-in-roof construction. Where the dormer is a small projection within an otherwise unconverted loft, the roof is recorded as a standard pitched roof with the dormer treated as a wall and window element. A room-in-roof classification is only appropriate where the loft space is a habitable room.

**Error 5: Ignoring thermal bridging at junctions.** RdSAP 10 applies y-values at the junctions between room-in-roof sub-elements. If elements are mis-measured or omitted, the junction lengths are incorrect and the thermal bridging contribution to the heat-loss calculation is wrong. This is silent — the software does not flag it — but it affects the final SAP score.

**Field QA protocol.** Before leaving site, cross-check: (1) Type classification is based on observed ceiling plane; (2) all sub-elements are identified and measured; (3) insulation thicknesses are evidence-based or conservatively defaulted; (4) dwelling dimensions are consistent with room-in-roof dimensions; (5) photographic evidence covers knee wall, sloping section, flat ceiling, and any visible insulation.

---

## Section 4: Retrofit Context — Room-in-Roof Insulation Under PAS 2035:2023 and ECO4

Room-in-roof insulation is one of the most cost-effective fabric improvement measures in the domestic retrofit landscape. Under ECO4, it qualifies as a primary measure when included in a whole-house retrofit plan developed by a PAS 2035:2023-compliant retrofit coordinator. Getting the baseline assessment right is not optional — it is the foundation of the entire measure specification.

When a DEA produces a pre-measure RdSAP assessment for a property with an uninsulated room in roof, the correct classification (Type 1 or Type 2), accurate dimensions, and honest recording of existing insulation levels determine the projected SAP improvement. The retrofit coordinator uses this data to scope the measure, the installer uses it to specify materials, and the post-measure assessment must demonstrate a credible uplift. If the pre-measure assessment over-states existing insulation or misclassifies the type, the projected uplift is compressed and may fall below the threshold for ECO4 funding eligibility. If it under-states, the measure may appear to deliver an implausibly large improvement at post-measure, triggering a TrustMark verification flag.

PAS 2035:2023 requires that room-in-roof insulation retrofit addresses all sub-elements — knee walls, sloping sections, flat ceiling (Type 2), and residual ceiling (Type 2) — as a complete package. Partial treatment (e.g., insulating knee walls but not sloping sections) creates condensation risk at the thermal discontinuity and is non-compliant. The DEA's post-measure assessment must reflect the complete intervention, and each sub-element's insulation must be individually verified and recorded.

Moisture risk is a particular concern. PAS 2035:2023 requires a moisture risk assessment before room-in-roof insulation is installed. The DEA is not responsible for the moisture risk assessment itself, but should be aware that the ventilation provisions recorded in the RdSAP assessment — particularly the presence or absence of mechanical extract ventilation serving the loft room — form part of the retrofit coordinator's risk evaluation. Accurate recording of ventilation at the point of survey contributes to safe retrofit delivery.

---

## Key Takeaways

- **Type 1 = no thermally separating ceiling** between the loft room and the storey below; **Type 2 = separating ceiling present.** Classification is based on the ceiling plane, not the staircase arrangement.
- Every room-in-roof comprises multiple discrete thermal sub-elements; each must be individually identified, measured, and characterised for insulation — there is no single "room-in-roof insulation" input.
- Insulation thickness in sloping sections is constrained by rafter depth; never record a thickness that exceeds the available void without evidence of a secondary insulation layer.
- Type 2 constructions generate residual ceiling areas that must be captured through consistent dimensional data — if your room-in-roof footprint and dwelling dimensions do not reconcile, the heat-loss calculation is wrong.
- Photographic evidence of each sub-element and any visible insulation is essential for audit defence and should be captured before leaving site.
- In retrofit contexts, the accuracy of the pre-measure room-in-roof data directly determines ECO4 funding eligibility, measure specification, and TrustMark compliance — errors propagate through the entire retrofit chain.
- RdSAP 10's junction thermal bridging calculations depend on correct element dimensions; mis-measured or omitted sub-elements produce silent errors in the SAP score that will not be flagged by the software.

---

## Self-Assessment Questions

**Q1.** A loft room is accessed via an enclosed staircase. The original first-floor ceiling has been retained and is intact. How should this room in roof be classified?

A) Type 1, because the staircase is enclosed
B) Type 2, because a thermally separating ceiling exists between the loft room and the storey below
C) Type 1, because the loft space is habitable
D) It depends on whether the staircase has a door at the top

**Correct answer: B.** The classification is determined by the presence of a thermally separating horizontal ceiling between the loft room and the lower storey, not by the staircase configuration. An intact ceiling means Type 2.

---

**Q2.** In a Type 2 room-in-roof construction, what is the "residual ceiling"?

A) The flat ceiling at collar-tie level within the loft room
B) The portion of the original ceiling plane between the knee wall and the eaves, above the heated space below
C) The underside of the sloping rafter section
D) The ceiling of the storey below the room in roof, measured wall-to-wall

**Correct answer: B.** The residual ceiling is the section of original loft floor either side of the knee walls that remains above the heated room on the lower storey. It is a horizontal heat-loss element and its insulation level (typically original loft insulation) must be accurately recorded.

---

**Q3.** An assessor records 200 mm of mineral wool insulation between rafters in the sloping section of a room in roof. The rafter depth is 100 mm. What is the correct approach?

A) Record 200 mm — the assessor observed the insulation
B) Record 100 mm — the maximum insulation thickness between rafters cannot exceed the rafter depth
C) Record 150 mm as a compromise
D) Record 200 mm and add a note explaining the compression

**Correct answer: B.** Insulation between rafters is limited to the rafter depth. If a 200 mm batt has been compressed into a 100 mm void, the effective insulation thickness recorded is 100 mm. Any additional insulation on the room side of the rafters would be a separate layer.

---

**Q4.** Under PAS 2035:2023, which of the following is compliant when retrofitting insulation to a Type 2 room-in-roof?

A) Insulating the knee walls only, as this is the most cost-effective sub-element
B) Insulating the knee walls and sloping sections but leaving the residual ceiling untreated
C) Insulating all sub-elements — knee walls, sloping sections, flat ceiling, and residual ceiling — as a complete package
D) Insulating whichever sub-elements the installer considers most accessible

**Correct answer: C.** PAS 2035:2023 requires that room-in-roof insulation addresses all sub-elements to avoid thermal discontinuities and associated condensation risk. Partial treatment is non-compliant.

---

**Q5.** In RdSAP 10, which factor determines the thermal bridging contribution at room-in-roof junctions?

A) The U-values of the adjacent elements only
B) The junction lengths, which are derived from the dimensional inputs for each sub-element
C) A fixed allowance applied per room-in-roof type regardless of geometry
D) The age of the loft conversion

**Correct answer: B.** RdSAP 10 calculates thermal bridging at room-in-roof junctions using y-values applied to junction lengths derived from the assessor's dimensional inputs. Inaccurate or missing sub-element dimensions produce incorrect junction lengths and therefore incorrect thermal bridging values.

---

## Further Reading

1. **BRE. *Reduced Data Standard Assessment Procedure 10 (RdSAP 10): Specification*.** Building Research Establishment, 2025. Available via the BRE SAP website: [https://www.bregroup.com/sap/](https://www.bregroup.com/sap/)

2. **BSI. *PAS 2035:2023 — Retrofitting dwellings for improved energy efficiency. Specification and guidance*.** British Standards Institution, 2023. Available via the BSI Shop: [https://www.bsigroup.com/](https://www.bsigroup.com/)

3. **DESNZ. *ECO4 Guidance: Measures and Technical Requirements*.** Department for Energy Security and Net Zero, 2023 (updated 2025). Available at: [https://www.gov.uk/government/publications/energy-company-obligation-eco4-guidance](https://www.gov.uk/government/publications/energy-company-obligation-eco4-guidance)

4. **BRE. *Conventions for RdSAP 10: Room-in-Roof (Appendix S)*.** Building Research Establishment, 2025. Published as part of the RdSAP 10 conventions document suite. Available via: [https://www.bregroup.com/sap/](https://www.bregroup.com/sap/)

---

*© Meridian CPD 2026. All rights reserved. Unauthorised reproduction prohibited.*
*This course material is licensed to individual subscribers only.*