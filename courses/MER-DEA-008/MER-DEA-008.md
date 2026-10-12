# Insulation in RdSAP 10: Walls, Roofs, Floors and Common Errors
**Course ID:** MER-DEA-008 | **CPD Hours:** 1.0 | **Published:** October 2026
*© Meridian CPD 2026. All rights reserved.*

---

## Learning Objectives
- Choose between "as built", "unknown" and an added insulation entry using conventions 3.03a, 3.03b and 3.03c.
- Record wall construction, wall thickness and alternative walls under conventions 2.13, 2.22, 3.01, 3.02 and 3.14.
- Apply the thickness rules in convention 3.07 and explain when a U-value may be entered under convention 3.08.
- Record roof insulation under convention 3.04, including lofts that cannot be inspected.
- Record floor construction and insulation, and recognise where the conventions and the specification disagree.

---

## Introduction

This course covers how wall, roof and floor construction and insulation are recorded for RdSAP 10. Every rule comes from the Conventions (v12.2) for RdSAP 10, applicable from 6 August 2026, or the RdSAP10 Specification of 9 June 2025, with the reference in brackets. Where the two conflict, the convention takes precedence (Conventions v12.2, opening statement). This edition replaces the March 2026 edition; where they differ, rely on this one.

The course uses the data item names in specification Table 31, not software screens. Roof rooms are covered in MER-DEA-004.

---

## Section 1: As built, unknown, or added insulation

### What "as built" delivers

RdSAP assigns default insulation from the age band of the part of the property concerned (specification section 5.1), so "as built" does not mean "uninsulated". In England, a cavity wall as built is 1.5 W/m2K in age bands A to E and 0.26 in band M (specification Table 6). A wall that has only the insulation that was part of its original construction is "as built" (Table 31 item 4-4).

Assume "as built" if there is no evidence of retro-fitted insulation (convention 3.03a). The convention applies this expressly to roof rooms where there is no access and no documentary evidence, and to the roof cases in Section 3.

### "Unknown" is for exceptional circumstances

Selecting "unknown" automatically suppresses any insulation recommendation, so it must not be used inappropriately, and it must be explained in site notes (convention 3.03b). The convention's examples are:
- conflicting evidence (inspection and/or documentary) of added insulation whose presence cannot be ascertained conclusively
- a fully boarded or obstructed loft, unless the householder has documentary evidence or is prepared to lift the boards
- a pitched roof with no access to the loft space, or access prevented, and no documentary evidence

"Unknown insulation thickness" is for exceptional circumstances: conflicting evidence of thickness, or insulation you can see but cannot measure (convention 3.03c).

### Evidence for added insulation

Where there is evidence of additional insulation you can give its thickness, give the U-value of the element, or select unknown thickness and let RdSAP default (specification section 5.1). Thickness and U-value are mutually exclusive (Table 31 items 3-4, 4-7 and 5-6).

In England, Wales and Northern Ireland, acceptable documentary evidence includes, but is not limited to, official correspondence from the applicable Registered Social Landlord, certificates, warranties, guarantees, or any documents verifying that work has been carried out (convention 9.02). You must be confident, and able to demonstrate, that it relates to the actual property being assessed and/or that the work has been carried out, and that there is no physical or other documentary evidence to the contrary. Evidence of intent to install does not qualify on its own, but:
- (a) where both an intention to upgrade the element (in planning documents, for example) and Building Control oversight can be demonstrated, the element can be treated as upgraded as the planning documents indicate
- (b) where only one of those can be demonstrated, but it can also be seen that an upgrade has occurred, the element can be treated as upgraded using the minimum selectable upgrade of the relevant type, with "unknown insulation thickness" if there is no evidence of thickness; for roof insulation between joists, use 100 mm as the lowest selectable thickness

The Scotland-only wording of convention 9.02 does not contain rules (a) and (b): there, evidence of intent to install does not qualify.

### Entering a U-value

Default U-values must not be overwritten unless there is specific documentary evidence of the thermal conductivity of the individual materials of the element in the property being assessed, calculated in accordance with BR 443 (convention 3.08). The evidence is either building control approval that correctly defines the construction and states the calculated U-value, or a U-value calculation produced or verified by a person with suitable expertise and experience. Knowing the product and its thickness leads to a thickness entry under convention 3.07, not a U-value.

### Conversions

For a conversion of a building originally intended to be heated, or a sub-divided dwelling, use the original construction date and specify upgraded elements only with documentary or visual evidence (convention 3.05a; Scotland has its own version, tied to the building warrant application date). For a conversion of an unheated building, such as a barn, use the conversion date, based on documentary evidence (convention 3.05b).

---

## Section 2: Walls

### Construction type

Wall construction is one of: stone (granite or whinstone), stone (sandstone or limestone), solid brick, cob, cavity, timber frame, park home wall, system build, basement wall or curtain wall (Table 31 item 4-2). These rules decide the choice:
- A cavity wall is entered as such irrespective of the width of the cavity; record its insulation level, any dry-lining and the wall thickness (convention 3.01).
- Timber frame is recorded as timber frame, not system build, irrespective of the external cladding (convention 3.02).
- A system built wall is a wall other than masonry or timber framed (specification section 5.2.2).
- If no option corresponds closely, select the nearest equivalent and include Addendum 1 (specification section 5.2).
- For flats, record the construction of the heat loss walls of the dwelling being assessed, not the overall superstructure, and select Addendum 1 (convention 3.14).

### Wall thickness

Measure wall thickness in mm for each building part and any alternative wall within it; evidence is required for each different thickness (convention 2.22). Measure at door or window reveals, or compare internal and external measurements. Where thickness varies a little for the same construction, use the average.

For solid brick in age bands A to E the default is 2.5 W/m2K up to 200 mm, 1.7 from 200 to 280 mm, and lower again for thicker walls (specification Table 13); for stone it is calculated from the thickness (specification Table 12), except that band E takes a fixed value, 1.7 in England, unless the calculated value is lower (specification Table 6, note a).

### Alternative walls

An alternative wall is a sheltered wall, a wall whose construction type or U-value differs from the main external wall, or both (convention 2.13). Each building part can have two, only one of them sheltered. The rules are:
- Always include a sheltered alternative wall, irrespective of size.
- Disregard a non-sheltered alternative wall of less than 10% of the total exposed wall area of the building part, including windows and doors. On 90 m2, a 6 m2 panel (6.7%) is disregarded and a 12 m2 section (13.3%) is entered.
- For stone walls, assess thickness at each external elevation and each storey, and use an alternative wall if it varies by more than 100 mm. Specification section 3.2.2 words this rule as covering stone or solid brick walls in age bands A to E.

### Wall insulation type and dry lining

The options are as built, external, filled cavity, internal, cavity plus external, cavity plus internal, and unknown; external, cavity or internal insulation is indicated only if it was added after the original construction and evidence exists (Table 31 item 4-4). Table 31 has no item for cavity fill material or installation date. The sources do not say which visual signs of cavity fill are sufficient; convention 3.03b describes evidence as inspection and/or documentary, so if in doubt ask your accreditation scheme. Three specific cases:
- A system built wall with evidence of retro cavity fill is recorded as system build with internal insulation, thickness unknown, with Addendum 1 (convention 3.02).
- A timber framed wall with external brick or block work and added external wall insulation is treated "as built", with Addendum 1 (convention 3.02a).
- Where there is both internal and external insulation, add the thicknesses together and enter as external (convention 3.07).

Dry lining is any internal lining that creates an airspace behind it, such as plasterboard on dabs or lath and plaster (convention 3.06). Use a tap test; if inconclusive, regard the wall as not dry-lined. Dry lining alone does not confirm the presence of insulation. The item applies only to stone, solid brick and cavity walls in age bands A to E.

### Insulation thickness and thermal conductivity

Convention 3.07 adjusts the thickness you enter. It applies only where a thickness is specified, not where a U-value is calculated.
- Multi-foil (a blanket with at least three layers of foil-type material) is entered at twice its actual thickness.
- Any insulation, except on solid brick and stone walls in age bands A to E, can be doubled if there is documentary evidence of the insulation type and manufacturer's information that its thermal conductivity is 0.025 W/mK or less.
- If the thermal conductivity is more than 0.08 W/mK (vermiculite, for example), halve the thickness.

For solid brick and stone walls in age bands A to E the doubling for low thermal conductivity does not apply. You enter the thickness and select a thermal conductivity of 0.040, 0.030 or 0.025 W/mK (convention 3.07). A documented value between these is rounded to the closest: 0.019 is entered as 0.025, and 0.044 as 0.040. Where insulation is confirmed but its conductivity is not available, use 0.040 for mineral wool, rock wool, fibre glass or EPS, 0.030 for XPS, and 0.025 for PUR, PIR or phenolic foam. Table 31 item 4-6 says to assume 0.04 where there is no documentary evidence of the thermal property; where you can identify the material, the convention's list is the more specific rule.

Worked examples:
- 50 mm of PIR on a cavity wall, with documentary evidence of the type and a manufacturer's conductivity of 0.022 W/mK, can be entered as 100 mm.
- The same PIR on a solid brick wall in age band B is entered as 50 mm at 0.025 W/mK.

### Hard to treat cavities and basement walls

Convention 9.10 defines three items:
- Access issue: any facade where it is not possible to pitch a 5 metre ladder considering health and safety requirements.
- Narrow cavity: indicated by a stretcher bond brick pattern with wall thickness 220 to 250 mm.
- Possible high exposure: any dwelling in exposure zones 3 or 4 (Appendix 1 of the conventions); if in doubt, record it.

For a flat on the third storey or above where cavity construction is identified (and retro-fit cavity insulation is therefore recommended), select "Access issues" (convention 3.14).

Basement walls are those adjacent to earth, and are only included when the basement is heated (convention 3.17). Basement walls above ground level are treated as a different wall construction (convention 2.05).

---

## Section 3: Roofs

### What is above the building part

Table 31 item 2-3 lists what can be above a building part: four pitched roof options, a flat roof, non-residential or other unheated space, the same dwelling, or another dwelling. The sources conflict on commercial premises above: convention 2.21 says non-residential/other unheated space, specification section 5.2.5 says another dwelling above. The convention takes precedence.

### Loft access

Where safe and practicable access is possible, measure the loft insulation and provide photographic evidence of the measured thickness (convention 3.04). Otherwise:
- "No access" means there is no loft hatch or other means of gaining access to the loft space.
- If there is a hatch or other means of access that could not be used on the day (painted over, or an obstruction preventing access for health and safety reasons), record "access, loft insulation unknown".
- If the insulation is fully obstructed, by boarding or stored items, enter "pitched, access, loft insulation unknown" unless the householder has documentary evidence (maximum thickness is the depth of the joists), lifts the boards or removes the obstructions.
- If you can establish and evidence the insulation under boards at multiple locations, through gaps or extending in from the edges, treat the boarded area as insulated to the thickness the evidence proves.

With no access, or insulation unknown, the U-value comes from the age band: 0.40 W/m2K, equivalent to 100 mm, for bands A to G (specification section 5.11.2 and Table 18, column 1). "None" is 2.3 W/m2K (specification Table 16), so keep it for a loft seen to be uninsulated.

### Loft insulation thickness

Thickness at joists is selected from fixed values between 12 mm and 400+ mm (Table 31 item 5-2). The rules in convention 3.04 are:
- If the level of insulation varies, use an area-weighted average thickness.
- If there is an area with no insulation, split the dwelling into building parts so that each roof insulation scenario can be entered.
- If joist and rafter insulation are both present, base the assessment on the joist insulation only.
- Multi-foil or foam insulation at joists or rafters is entered under convention 3.07, which also halves the thickness of materials such as vermiculite: 100 mm is entered as 50 mm.

Worked example: a 40 m2 loft has 30 m2 insulated to 300 mm and 10 m2 to 100 mm. The average is ((30 x 300) + (10 x 100)) divided by 40, which is 250 mm. The sources do not say what to do when the average falls between two listed thicknesses, so ask your accreditation scheme.

The U-values behind the thicknesses are 0.40 W/m2K at 100 mm, 0.21 at 200 mm and 0.16 at 270 mm (specification Table 16, column 1).

### Rafters, sloping ceilings and flat roofs

Rafter, flat roof and sloping ceiling insulation each take "unknown", "as built" or a known thickness (Table 31 items 5-3 to 5-5). "None" does not apply to a flat roof or a pitched roof with sloping ceiling (Table 31 item 5-1). Assume "as built" for a flat roof or sloping ceiling without documentary evidence, and for rafter insulation with no evidence of retro-fitting (convention 3.03a). The comment on Table 31 item 5-1 says that without evidence the entry is "unknown"; the convention takes precedence. The U-value is the same either way (specification Table 18, note 1), but "unknown" loses the recommendation (convention 3.03b). A conservatory recorded as an extension because its roof has been replaced or a false ceiling added has its own roof entries (convention 2.28).

The age band of a roof room is the same as the building part unless evidence, such as planning applications or dated photographs, proves otherwise (convention 3.13).

---

## Section 4: Floors

### What is below, and the floor construction

Table 31 item 2-2 records what is below each building part. Commercial premises below are recorded as partially heated space below (convention 2.21).

Floor construction is unknown, solid, basement floor, suspended timber, or suspended not timber, recorded for the lowest floor of the building part (Table 31 item 3-1). If the floor construction cannot be determined, "unknown" is appropriate (convention 3.03b). The software then assumes suspended timber for age bands A and B, or solid if there is underfloor heating, and solid from band C onwards (specification Table 19).

### Floor insulation

Floor insulation is unknown, as built, or retro-fitted, and there must be evidence for retro-fitted insulation (Table 31 item 3-2). Thickness is entered only if the insulation is retro-fitted: unknown, or 25 to 200 mm in 25 mm steps (Table 31 item 3-3). A known floor U-value is the alternative (Table 31 item 3-4) and needs the evidence in convention 3.08.

There is no single default floor U-value: it is calculated from the floor area, exposed perimeter and wall thickness of each building part, the floor construction and the thickness of all-over floor insulation (specification section 5.12). Where no thickness is given, the insulation assumed depends on age band and country: in the England and Wales column, none up to band H, 25 mm for I, 75 mm for J, 100 mm for K and L, and 140 mm for M (specification Table 19). For retro-fitted insulation of unknown thickness, the greater of 50 mm and the age band thickness is used (Table 19, note 2).

### Exposed floors and basements

An exposed floor has external air below and a semi-exposed floor has an unheated space below, such as an integral garage (specification section 3.11); no distinction is made between them for U-value (specification section 5.13).

A basement that meets the criteria in convention 2.05 becomes the lowest occupied floor. Where it does not, the sources conflict: convention 2.05 says to treat the floor above it as a suspended floor above unheated space, while specification section 5.17 says a floor above a basement is treated as a ground floor for heat loss. The convention takes precedence.

---

## Key Takeaways
- "As built" delivers the age band default; assume it wherever there is no evidence of retro-fitted insulation (convention 3.03a).
- "Unknown" is for exceptional circumstances and suppresses the insulation recommendation (convention 3.03b).
- A U-value entry needs the evidence in convention 3.08; product and thickness alone lead to a thickness entry under convention 3.07.
- Solid brick and stone walls in age bands A to E take a conductivity of 0.040, 0.030 or 0.025 W/mK, with no doubling of thickness for low conductivity (convention 3.07).
- "No access" means no hatch or other means of access; a hatch you could not use, or insulation fully obstructed, is "access, loft insulation unknown" (convention 3.04).
- Varying loft insulation is an area-weighted average; an area with none means splitting into building parts (convention 3.04).

---

## Self-Assessment Questions

**Q1.** A house has a loft hatch, but on the day of the visit it is painted over and cannot be opened, and there is no documentary evidence. How is the roof recorded?

A) Pitched roof, no access
B) Access, loft insulation unknown
C) Roof insulation "none"
D) Insulation at joists, 100 mm

**Correct answer: B.** Under convention 3.04, "no access" means no hatch or other means of access; a hatch that could not be used on the day is "access, loft insulation unknown".

---

**Q2.** A 40 m2 loft is fully insulated at joist level: 30 m2 at 300 mm and 10 m2 at 100 mm. What thickness is entered?

A) 300 mm, the thickness over most of the loft
B) 100 mm, the lowest thickness found
C) The thickness measured at the centre of the loft
D) 250 mm, the area-weighted average

**Correct answer: D.** Convention 3.04 requires an area-weighted average where insulation varies: ((30 x 300) + (10 x 100)) divided by 40 is 250 mm.

---

**Q3.** A solid brick wall in age band C has 50 mm of PIR internal insulation, with documentary evidence of a thermal conductivity of 0.022 W/mK. How is it entered?

A) 50 mm, with thermal conductivity 0.025 W/mK
B) 100 mm, because the conductivity is 0.025 W/mK or less
C) 25 mm, because the thickness is halved
D) As a U-value worked out by the assessor from the product and thickness

**Correct answer: A.** Convention 3.07 excludes solid brick and stone walls in age bands A to E from the doubling for a conductivity of 0.025 W/mK or less; the thickness is entered with the closest of 0.040, 0.030 or 0.025 W/mK.

---

**Q4.** A flat roof extension has no documentary evidence of insulation, and none is visible. What is the insulation entry?

A) "None"
B) Flat roof insulation, 100 mm
C) "As built"
D) A U-value of 2.3 W/m2K

**Correct answer: C.** Convention 3.03a says to assume "as built" for a flat roof with no documentary evidence; "none" does not apply to a flat roof (Table 31 item 5-1).

---

**Q5.** A cavity wall in age band D shows no evidence, from inspection or documents, that insulation has been added. What is the wall insulation entry?

A) "Unknown"
B) "As built"
C) Filled cavity
D) Internal insulation, thickness unknown

**Correct answer: B.** Convention 3.03a says to assume "as built" if there is no evidence of retro-fitted insulation; "unknown" is for exceptional circumstances such as conflicting evidence (convention 3.03b).

---

## Further Reading
- **Conventions (v12.2) for RdSAP 10.** Applicable from 6 August 2026. Read section 3 and conventions 2.13, 2.22, 9.02 and 9.10.
- **RdSAP10 Specification.** BRE, 9 June 2025. See section 5 for the U-value tables and Table 31 for the floor, wall and roof data items.

---

*© Meridian CPD 2026. All rights reserved. Unauthorised reproduction prohibited.*
*This course material is licensed to individual subscribers only.*
