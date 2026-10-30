# Airtightness Testing in RdSAP 10
**Course ID:** MER-DEA-021 | **CPD Hours:** 1.0 | **Published:** October 2026
*© Meridian CPD 2026. All rights reserved.*

---

## Learning Objectives
- State what convention 10.01 requires before a pressure test result can replace the RdSAP default, and what makes a certificate invalid.
- Explain how the specification uses a 50 Pa or 4 Pa test result, and which parts of the infiltration estimate it replaces.
- Classify a chimney as open, blocked, a flue or not counted, using the 200 mm, 125,000 mm2 and 30,000 mm2 tests in convention 9.01.
- Apply the draught lobby definition in convention 2.09b and the draught proofing rule in 3.11a.
- Identify the other recorded items that feed the infiltration estimate: storeys, wall and floor construction, vents, fans and built form.

---

## Introduction

Despite the title, nothing in RdSAP 10 asks a DEA to test a dwelling. Convention 10.01 asks for something narrower: decide whether a pressure test certificate you are handed can go into the assessment, and otherwise leave the default alone. Where there is no certificate, infiltration is estimated from things you record anyway: fireplaces and flues, vents and fans, the main entrance, draught proofing, wall and floor construction, storeys and built form.

The specification lists "air pressure test result can be used if available" among its significant changes from RdSAP 2012 (specification, introduction). This course covers the certificate rules first, then the recorded items.

Everything here comes from the Conventions v12.2 for RdSAP 10, applicable from 6 August 2026, and the RdSAP10 Specification version 4.0 (7 June 2026). Where the two conflict, the convention takes precedence (conventions v12.2, front page). Statements about what v12.2 changed come from comparing the v12.1 and v12.2 texts.

This edition replaces the March 2026 edition. That edition gave a three-year limit on the age of a certificate and named testing standards. Neither is in the conventions or the specification, and both have been removed. The sources say nothing about how a pressure test is carried out, what result to expect or what it costs, so nor does this course. Where they are silent on something you need on site, it says so.

---

## Section 1: The pressure test result and convention 10.01

**In short:** Leave the default unless you have a pressure test certificate giving a measured air permeability at 50 Pa or 4 Pa, and know which; do not estimate or enter a design figure. Confirm it relates to this dwelling and comes from a person with suitable expertise and experience. Material changes since the test make it invalid; the sources do not define them, so compare the test date with later works, record what you find and ask your scheme if unsure.

### The default comes first

The pressure test result must be the RdSAP default and must not be overwritten unless specific documentary evidence is available (convention 10.01). The specification agrees: the infiltration rate is calculated when a pressure test result is not available, and when one is available it can be used (specification section 4.1, Table 5). No certificate, no entry: you do not estimate a figure.

### What the figure is

The figure is the measured air permeability, which the convention writes as m3/m2/hr, from a blower door test at 50 Pa or a low-pressure pulse test at 4 Pa (convention 10.01). The specification applies a different formula to each (specification section 4.1, Table 5), so you need to know which test the certificate reports.

Note the word "measured". The worksheet text reproduced in the specification notes that an air permeability value applies if a pressurisation test has been done "or a design or specified air permeability is being used" (specification section 4.1, Table 5). Convention 10.01 describes only a measured figure evidenced by a certificate. The convention takes precedence, so a design or target figure is not evidence for an RdSAP entry.

### Who produced the certificate

The evidence is a pressure test certificate produced by a person with suitable expertise and experience. That can be demonstrated by membership of a recognised air tightness Competent Persons Scheme that is approved by Government; the convention names EAS or ATTMA (convention 10.01). It does not expand those abbreviations or say how to confirm a tester's membership; ask your accreditation scheme.

### Does it relate to this dwelling

You must be confident, and able to demonstrate, that the documentation relates to the actual property being assessed and that there is no physical or other documentary evidence to the contrary (convention 9.02; the Scotland text refers only to physical evidence to the contrary). A certificate for another flat in the block does not meet that test.

### Material changes

Version 12.2 added one sentence: if material changes have been made to the property since the original test, the certificate becomes invalid for RdSAP entry (convention 10.01). It is not in the v12.1 text; the rest of 10.01 is unchanged.

Neither the convention nor the specification defines a material change or gives examples. Compare the test date with what you see and are told about works since then, record it, and if unsure ask your accreditation scheme. The default remains available when a certificate cannot be relied on (convention 10.01).

### Background ventilation tests and other gaps

Results from background ventilation tests are not included in the assessment (convention 10.01). Three other things the sources do not say:
- They give no maximum age for a certificate, only the material changes rule.
- They do not settle whether you must enter a valid certificate when one is offered. The specification says a result "can be used" in one line and "is used" in another.
- They do not set out what a certificate must contain. Check what your scheme asks for.

---

## Section 2: What the calculation does with a test, and without one

**In short:** Get the chimney, flue, fan and vent counts right whether or not there is a test, because a test replaces only the fabric allowances and those counts are still added. The 50 Pa and 4 Pa results use different formulas, so do not enter one as the other. Built form sets the shelter factor on either route, and the sources do not say any recorded item can be skipped when a test is entered, so collect it all.

The specification takes the infiltration calculation from the SAP 10.2 worksheet and reproduces the relevant lines in Table 5 (specification section 4.1). Every figure in this section comes from that table. There are two parts: openings you count, and fabric allowances that follow from what you record.

### Counted openings

Each counted item is given a flow in m3 per hour:
- Open chimneys: 80
- Open flues: 20
- Chimneys or flues attached to a closed fire: 10
- Flues attached to a solid fuel boiler: 20
- Flues attached to another heater: 35
- Blocked chimneys: 20
- Intermittent extract fans: 10
- Passive vents: 10
- Flueless gas fires: 40

The total is divided by worksheet item (5) to give air changes per hour, which is item (8). Item (5) is not defined in the part of the worksheet the specification reproduces.

### Fabric allowances, used when there is no test

With no pressure test the worksheet adds these, in air changes per hour:
- Storeys: the number of storeys minus one, multiplied by 0.1. The number is the greater of that in the main part and in any extension.
- Structural infiltration: 0.25 for steel or timber frame, 0.35 for masonry.
- Floor: 0.2 for an unsealed suspended wooden ground floor, 0.1 for a sealed one, otherwise 0.
- Draught lobby: 0.05 if there is none, otherwise 0.
- Window infiltration: 0.25, less 0.2 multiplied by the percentage of windows and doors draught proofed and divided by 100.

Those are added to item (8) to give the infiltration rate.

### With a test result

A test result replaces the fabric allowances but keeps item (8):
- Test at 50 Pa: the air permeability divided by 20, plus item (8).
- Test at 4 Pa: 0.263 multiplied by the air permeability raised to the power 0.924, plus item (8).

A certificate does not switch off the chimney, flue, fan and vent counts: they are added to the tested figure, so they must be right either way. And because the 50 Pa and 4 Pa figures use different formulas, one must not be entered as the other. The sources do not say any recorded item can be skipped when a test is entered, so collect it all.

### Shelter

On either route the result is multiplied by a shelter factor: 1 minus 0.075 multiplied by the number of sheltered sides. That number is 0 for detached, 1 for semi-detached or end terraced, 3 for enclosed mid-terraced and 2 in other cases such as mid-terraced, including flats. So the built form you record feeds infiltration too.

### Worked example

Take a two-storey masonry semi-detached house with an unsealed suspended timber ground floor, no draught lobby and every openable window and door draught proofed. The allowances are 0.1 for the second storey, 0.35 for masonry, 0.2 for the floor, 0.05 for the missing lobby and 0.05 for the windows (0.25 minus 0.2). They total 0.75 air changes per hour, to which item (8) is added. The shelter factor for one sheltered side is 0.925.

With a valid 50 Pa certificate, the 0.75 is replaced by the certificate figure divided by 20. A figure of 10 would give 0.5; a figure of 20 would give 1.0. Those are arithmetic illustrations, not typical results: a tested figure can sit below or above the default.

---

## Section 3: Chimneys, fireplaces and flues

**In short:** Count chimneys of 200 mm diameter or more, or 125,000 mm2, as open where unrestricted and suitable for use, plus the other cases listed; a duct under 200 mm in diameter, including a sealed flexible gas flue liner, is a flue. A decommissioned chimney with a ventilation area below 30,000 mm2 is blocked, at 30,000 mm2 or more is open, and one sealed completely with no air bricks need not be counted. Where the sources are silent, ask your scheme.

The specification refers you to the conventions for the chimney and fireplace definitions and count (specification section 4.1). Everything in this section comes from convention 9.01 unless another source is cited.

### Open chimneys

An open chimney is a vertical duct for combustion gases with a diameter of 200 mm or more, or a rectangular duct of equivalent area, given as 125,000 mm2. Count all open chimneys and fireplaces, downstairs and upstairs, but only when they are unrestricted and suitable for use. An open chimney is modelled at 80 m3 per hour. Three other cases are treated as open chimneys:
- A chimney attached to a decorative gas fire
- A chimney fitted with a damper
- A decommissioned chimney with a ventilation area greater than or equal to 30,000 mm2

### Decommissioned chimneys

A chimney can be decommissioned with the fireplace filled in and the stack capped or removed completely. It may still need air bricks to manage moisture, for example on an external wall. Three outcomes follow:
- Sealed completely, with no air bricks required: it does not need to be counted as a chimney.
- Ventilation area less than 30,000 mm2: a blocked chimney, modelled at 20 m3 per hour.
- Ventilation area of 30,000 mm2 or more: treated as an open chimney.

The convention does not say how the ventilation area is measured, for example the overall size of the air brick or its free open area. For a vent near the threshold, ask your scheme.

### Flues

A vertical duct with a diameter of less than 200 mm is counted as a flue. That includes a flexible gas flue liner sealed into a chimney, because the liner reduces the diameter to less than 200 mm. The convention lists three cases as considered in SAP:
- An open flue gas fire with the flue products outlet sealed to the chimney, including radiant gas fires and ILFE (insert live fuel effect) fires
- A chimney or open flue attached to a wood or solid fuel boiler
- A chimney or open flue attached to a wood or solid fuel stove or appliance with a controlled air supply

The worksheet has four flue lines, listed with their flow rates in Section 2. Neither document states which line each of the convention's cases belongs to, so follow your scheme's guidance on the flue categories. A flue for a solid fuel boiler in an unheated space is not counted (specification section 4.1, Table 5).

### Ventilation and heating are separate questions

Convention 9.01 notes that it relates only to the number of open fireplaces for ventilation, and that other rules apply to the choice of main or secondary heating. Under convention 5.02 an open fire is considered in the heating assessment if the fireplace is capable of supporting an open fire, which includes having a grate suitable for holding fuel, even if no fuel is present. The number of open fireplaces is then used as the number of open chimneys for ventilation (convention 5.02). Neither convention says in terms whether an open chimney with no grate still counts for ventilation. If you meet one, ask your scheme.

### What changed in v12.2

Comparing the v12.1 and v12.2 texts of convention 9.01:
- The passage on decommissioned chimneys is new, with its flow rates of 80 and 20 m3 per hour and the sealed chimney that need not be counted.
- In v12.1 a decommissioned chimney was open with a ventilation area "greater than" 30,000 mm2. It is now "greater than or equal to".
- The v12.1 text listed a chimney temporarily blocked with cardboard, newspaper bungs, chimney balloons and similar as an open chimney. That bullet is not in v12.2.

On the last point, v12.2 does not say how such a chimney is now treated, although the test of unrestricted and suitable for use remains. Ask your scheme and record what you found.

### Worked example: four fireplaces

Applying convention 9.01 to one house:
- Fireplace A has a grate and an unrestricted, usable chimney duct of 200 mm or more. It is an open chimney, and an open fire for heating (convention 5.02).
- Fireplace B has a gas fire with a flexible flue liner sealed into the chimney. It is a flue, not a chimney.
- Fireplace C is filled in, the stack is capped and an air brick gives a ventilation area of 15,000 mm2. It is a blocked chimney.
- Fireplace D is as C, but the ventilation area is exactly 30,000 mm2. It is treated as an open chimney.

That gives two open chimneys at 80 and one blocked chimney at 20: 180 m3 per hour before the flue is added.

---

## Section 4: Draught lobby, draught proofing, vents and construction

**In short:** A draught lobby counts only if it meets all four tests, including covering the entrance designed as the Main Entrance, which may not be the one used most, but a flat reached by an enclosed corridor or stairwell should be classified as having one. Examine every external door and openable window for draught proofing, using the glazing-type rule only where its state cannot be determined. Record timber frame as timber frame whatever the cladding; retro-fitted floor insulation must be evidenced.

### Draught lobby

A draught lobby is an arrangement of two doors that forms an airlock on the Main Entrance to the dwelling. It may be heated or unheated. To be included, the enclosed space must meet all of these (convention 2.09b):
- It covers the Main Entrance to the dwelling.
- It has a floor area of at least 2 m2.
- A person with a push-chair or similar can close the outer door before opening the inner door.
- It leads into a further circulation area and not directly into any other room type. It may additionally give access to a cloakroom, with or without a WC.

The Main Entrance is the one designed to be the main entrance, which may not be the one the occupier uses most (convention 2.09b). So a lobby on a door not designed as the main entrance does not count, and a porch opening straight into the living room fails the fourth test.

A flat with access via an enclosed heated or unheated corridor or stairwell should be classified as having a draught lobby (convention 2.09b). For a house, bungalow or park home, assume no draught lobby if it cannot be determined (specification section 4.1, Table 5).

### Draught proofing

All external doors and openable windows in each building part should be examined for draught proofing. The percentage is the number draught proofed divided by the total number of openable windows and doors, multiplied by 100 (specification section 8.1).

If the state of the draught proofing cannot be determined, take triple, double or secondary glazed as draught proofed, and single glazed windows and doors as not draught proofed unless there is contrary evidence of draught proofing. Include glazing in a non-separated conservatory (convention 3.11a).

### Vents and fans

If vents, excluding air bricks, are present in the property and the presence of mechanical ventilation cannot be confirmed, enter the number of vents as passive stack (convention 7.03a). Air bricks are left out of this count, but under 9.01 those serving a decommissioned chimney decide between blocked and open.

Enter the number of extract fans if known; the specification gives defaults by age band and number of habitable rooms for when it is not (specification section 4.1, Table 5).

### Wall construction

The wall construction you record sets the structural infiltration when there is no test (specification section 4.1, Table 5):
- System build is treated as masonry.
- Where both frame and masonry are present, use the value for the greater wall area after deducting openings, and 0.35 if the areas are equal.
- Walls of roof rooms are not included.
- A park home uses the timber frame value.

Timber frame should be recorded as timber frame and not as system build, irrespective of the external cladding (convention 3.02). For a flat, record the construction of the heat loss walls of the dwelling being assessed, not the overall superstructure (convention 3.14).

### Floor construction

Only a suspended timber ground floor adds floor infiltration; solid floors and suspended floors that are not timber add nothing. Whether a suspended timber floor counts as sealed follows from other entries (specification section 4.1, Table 5):
- Main dwelling age band A to E: sealed if the floor U-value is below 0.5, or if the floor insulation is retro-fitted and no U-value is supplied. Otherwise unsealed.
- Main dwelling age band F to M: sealed.
- Park home: unsealed suspended timber.

The floor infiltration for the whole dwelling is determined by the floor type of the main dwelling. There must be evidence for retro-fitted floor insulation (specification section 17, Table 31, item 3-2).

---

## Key Takeaways
- The pressure test result stays at the RdSAP default unless a certificate from a person with suitable expertise and experience gives the measured air permeability at 50 Pa or 4 Pa (convention 10.01).
- Material changes since the test make the certificate invalid for RdSAP entry. The sources do not define a material change (convention 10.01).
- A test result replaces the fabric allowances, but the chimney, flue, fan and vent counts are still added (specification section 4.1, Table 5).
- An open chimney is an unrestricted, usable duct of 200 mm diameter or more, or 125,000 mm2. Smaller ducts are flues (convention 9.01).
- A decommissioned chimney with a ventilation area below 30,000 mm2 is blocked and one at 30,000 mm2 or more is open; one sealed completely, with no air bricks required, need not be counted (convention 9.01).
- A draught lobby must meet all four tests in convention 2.09b. Flats reached by an enclosed corridor or stairwell are classified as having one.

---

## Self-Assessment Questions

**Q1.** Under convention 10.01, which of these allows the default pressure test result to be overwritten?

A) A design air permeability figure
B) A pressure test certificate produced by a person with suitable expertise and experience
C) A background ventilation test result
D) The householder's word that a test was done

**Correct answer: B.** Convention 10.01 requires a pressure test certificate from a person with suitable expertise and experience, and excludes background ventilation test results.

---

**Q2.** A decommissioned chimney has air bricks giving a ventilation area of exactly 30,000 mm2. How does convention 9.01 treat it?

A) It is not counted
B) As a blocked chimney
C) As a flue
D) As an open chimney

**Correct answer: D.** Convention 9.01 treats a ventilation area greater than or equal to 30,000 mm2 as an open chimney; only less than 30,000 mm2 is blocked.

---

**Q3.** A valid 50 Pa test result is entered. Which of these still contributes to the infiltration rate in the specification's calculation?

A) The count of chimneys, flues, fans and vents
B) The structural infiltration allowance
C) The 0.05 allowance for having no draught lobby
D) The window infiltration allowance

**Correct answer: A.** Specification section 4.1, Table 5 gives the rate as the air permeability divided by 20 plus item (8), the openings total, so only the fabric allowances are replaced.

---

**Q4.** A flat is entered from an enclosed, unheated communal stairwell. What does convention 2.09b say about a draught lobby?

A) There is none, because the stairwell is unheated
B) Only if the flat has its own lobby of at least 2 m2
C) The flat should be classified as having a draught lobby
D) It cannot be determined, so assume none

**Correct answer: C.** Convention 2.09b says flats with access via an enclosed heated or unheated corridor or stairwell are classified as having a draught lobby.

---

**Q5.** Material changes have been made to a property since its pressure test. What does convention 10.01 say about the certificate?

A) It can be used if it is less than three years old
B) It becomes invalid for RdSAP entry
C) Enter the figure with a note of the changes
D) It can be used if the tester is a scheme member

**Correct answer: B.** Convention 10.01 says the certificate becomes invalid for RdSAP entry if material changes have been made since the original test; it sets no age limit.

---

## Further Reading
- **Conventions (v12.2) for RdSAP 10.** Applicable from 6 August 2026. Read conventions 10.01, 9.01, 9.02, 5.02, 2.09b, 3.11a, 7.03a, 3.02 and 3.14 in full.
- **RdSAP10 Specification.** Version 4.0 (7 June 2026). Section 4.1 and Table 5 for infiltration, section 8.1 for draught proofing, Table 31 for the data items.

---

*© Meridian CPD 2026. All rights reserved. Unauthorised reproduction prohibited.*
*This course material is licensed to individual subscribers only.*
