# Ventilation in RdSAP 10: PIV, MVHR and Natural Ventilation
**Course ID:** MER-DEA-003 | **CPD Hours:** 1.0 | **Published:** October 2026
*© Meridian CPD 2026. All rights reserved.*

---

## Learning Objectives
- List the chimney, flue, fan and vent counts in the RdSAP 10 ventilation calculation and the flow rate attached to each.
- Apply convention 9.01 to tell an open chimney from a blocked chimney, a flue and a chimney that is not counted.
- Decide when mechanical ventilation is entered from the product database, when by defaults, and when vents are entered as passive stack.
- Set wet rooms, duct type and duct insulation under conventions 7.03b to 7.03d, and choose between two systems under convention 7.03e.
- Record draught lobbies and draught proofing correctly, and know when an air pressure test result may be entered.

---

## Introduction

Ventilation is one of the areas the RdSAP10 Specification lists as changed from RdSAP 2012: mechanical ventilation is treated as in full SAP with database entry (default values still allowed), the ventilation algorithm allows more options, and an air pressure test result can be used if available (specification, Introduction).

This edition has been rebuilt from two documents: the Conventions v12.2 for RdSAP 10, applicable from 6 August 2026, and the RdSAP10 Specification version 4.0 (7 June 2026). Each rule carries a reference in brackets so you can check it. Where the two conflict, the convention takes precedence (conventions v12.2, front page). Where they are silent, the course says so and points you to your accreditation scheme.

The March 2026 edition taught rules on trickle vents, cooker hoods, a default duct type, commissioning evidence and default air permeability by age band. None could be found in either document, and they have been removed.

---

## Section 1: What the Calculation Takes From Your Survey

**In short:** Count chimneys, flues, intermittent extract fans, passive vents and flueless gas fires carefully, because each one counted carries a set flow rate: an open chimney is 80 m3 per hour. Treat ventilation as natural with intermittent extract fans unless a mechanical system is clearly identified. Without a pressure test result, your draught lobby and draught proofing entries also feed the infiltration rate. Neither document says whether a cooker hood counts as an extract fan, so ask your scheme.

Specification section 4.1 says the parameters for the ventilation rate come from its Table 5 and that the calculation follows the SAP 10.2 worksheet. The first part of Table 5 is a list of openings. Each one counted is multiplied by a fixed flow rate in m3 per hour:
- Open chimneys: 80
- Open flues: 20
- Chimneys or flues attached to a closed fire: 10
- Flues attached to a solid fuel boiler: 20
- Flues attached to other heater: 35
- Blocked chimneys: 20
- Intermittent extract fans: 10
- Passive vents: 10
- Flueless gas fires: 40

The total is converted to air changes per hour and carried into the infiltration rate (specification section 4.1, Table 5).

Table 5 also says how the counts are made. Chimneys are the number of open fireplaces for main and for secondary heating. The flue rows are counted the same way, and a flue for a solid fuel boiler in an unheated space is not counted. Extract fans, passive stack vents and flueless gas fires are the number if known. The ventilation system is natural with intermittent extract fans unless a mechanical ventilation system is clearly identified (specification section 4.1, Table 5). Where the number of extract fans is unknown, Table 5 supplies a default; the printed table is badly aligned, so its figures are not reproduced here. Neither document says whether a cooker hood counts as an extract fan, and trickle vents appear in neither; ask your scheme.

When there is no pressure test result, two more items come straight from your survey. Having no draught lobby adds 0.05 to the infiltration rate. Window infiltration is 0.25 minus 0.2 times the fraction of windows and doors draught proofed (specification section 4.1, Table 5).

For a park home, open fireplaces are always none and ventilation is always natural (specification section 1.18).

---

## Section 2: Chimneys, Blocked Chimneys and Flues

**In short:** Count an open chimney, 200 mm diameter or more or a rectangular duct of equivalent area, only when it is unrestricted and suitable for use. For a decommissioned chimney, check the ventilation: sealed completely with no air bricks, it is not counted; under 30,000 mm2 it is a blocked chimney; at 30,000 mm2 or more it is open. A chimney with a flexible gas flue liner sealed into it is a flue. For temporary blocking, ask your scheme.

The specification refers you to the conventions for chimney and fireplace definitions and count (specification section 4.1). The governing text is convention 9.01, amended in v12.2.

### Open chimney

An open chimney is a vertical duct for combustion gases with a diameter of 200 mm or more, or a rectangular duct of equivalent area. The convention prints that area as 125,000 mm2; use the published figure and raise any borderline rectangular duct with your scheme. Count all open chimneys and fireplaces, upstairs and downstairs, but only when they are unrestricted and suitable for use. An open chimney is modelled at 80 m3 per hour. A chimney attached to a decorative gas fire and a chimney fitted with a damper are also treated as open chimneys (convention 9.01).

### Decommissioned chimneys and the 30,000 mm2 test

A chimney or fireplace can be decommissioned by filling in the fireplace and capping or removing the stack. Convention 9.01 then gives three outcomes:
- Sealed completely, with no air bricks: it does not need to be counted as a chimney.
- Air bricks installed, ventilation area less than 30,000 mm2: a blocked chimney, modelled at 20 m3 per hour.
- Ventilation area greater than or equal to 30,000 mm2: treated as an open chimney, at 80 m3 per hour.

Exactly 30,000 mm2 is therefore an open chimney under v12.2. The convention does not say how the ventilation area is measured (overall vent size or free open area), so check your scheme's guidance.

### Flues

A vertical duct with a diameter of less than 200 mm is counted as a flue. That includes a chimney with a flexible gas flue liner sealed into it, because the liner reduces the diameter to less than 200 mm. The convention lists the cases considered (convention 9.01):
- An open flue gas fire with the flue products outlet sealed to the chimney, including radiant gas fires and ILFE (insert live fuel effect) fires.
- A chimney or open flue attached to a wood or solid fuel boiler.
- A chimney or open flue attached to a wood or solid fuel stove or appliance with a controlled air supply.

Table 5 has four flue rows, at 10, 20 or 35 m3 per hour. Neither document states in words which row each of these cases belongs to, so follow your scheme's guidance on the flue categories.

### Open fires and the heating assessment

An open fire is considered in the heating assessment if the fireplace is capable of supporting an open fire, which includes having a grate suitable for holding fuel, even if no fuel is present. The number of open fireplaces is used in the calculation as the number of open chimneys for ventilation (convention 5.02). Convention 9.01 adds that its count affects only the ventilation rate; other rules decide the choice of main or secondary heating.

### A change in v12.2

Version 12.1 listed a chimney temporarily blocked with cardboard, newspaper bungs, chimney balloons and similar as an open chimney. Version 12.2 no longer contains that line and says nothing else about temporary blocking, though a chimney is still counted only when unrestricted and suitable for use (convention 9.01). Ask your scheme how to record one.

### Worked example

A house has four chimney positions (conventions 5.02 and 9.01):
- Front room: a fireplace with a grate, no fuel, and an unrestricted chimney of 200 mm or more. An open chimney.
- Rear room: a gas fire with a flexible flue liner sealed into the chimney. A flue.
- Front bedroom: fireplace filled in and stack capped, with an air brick giving a ventilation area under 30,000 mm2. A blocked chimney.
- Rear bedroom: fireplace filled in and sealed completely, no air brick. Not counted.

---

## Section 3: Natural, Mechanical and Passive Stack

**In short:** Intermittent kitchen and bathroom fans are not a mechanical ventilation system, and if you cannot identify the type of ventilation, assume natural. Where make and model details are available, a mechanical system should be entered from the product database; with no evidence of them, it must be entered using the defaults. If vents, excluding air bricks, are present and you cannot confirm mechanical ventilation, enter the number of vents as passive stack.

### The names the sources use

Convention 7.03a defines mechanical ventilation systems as those that circulate fresh air via ducts and vents and use continually running fans when in operation. They can be input-only, extract-only or balanced (input and extract).

The specification lists seven methods of providing ventilation (specification section 4.2):
- Natural ventilation
- Positive input, from loft (treated as natural)
- Positive input, from outside
- Mechanical extract, centralised
- Mechanical extract, decentralised
- Whole House Mechanical Ventilation, no heat recovery
- Whole House Mechanical Ventilation, with heat recovery

The conventions use "PIV" only in convention 7.03e, and neither document uses "MVHR". The specification is not tidy about positive input from the loft: the list labels it "treated as natural", and the next sentence says every method except natural ventilation is treated as mechanical ventilation (specification section 4.2). If the distinction matters for an entry, ask your scheme.

### Intermittent fans are not a system

The comments against the mechanical ventilation data item settle several points (specification Table 31, item 10-1):
- If the type of ventilation cannot be identified, assume natural ventilation.
- The item applies to a whole house ventilation system only; otherwise assume natural ventilation.
- Intermittent extract fans in kitchens and bathrooms are not a mechanical ventilation system for the calculation.
- Continuously running extract fans in wet rooms are treated as mechanical extract ventilation.

### Database entry or defaults

Where make and model details are available, the system should be entered via the product database (written PCDF in conventions 7.03a to 7.03d, and PCDB in 7.03e and the specification). Where there is no evidence of the make and model, it must be entered using the defaults (convention 7.03a). The specification agrees: with details and documentary evidence, select the system by brand name and model; otherwise use the default data (specification section 4.2).

The default data are (specification section 4.1, Table 5):
- Mechanical extract ventilation (centralised or decentralised), or positive input ventilation from outside: specific fan power 0.8 W per litre per second.
- Balanced whole house mechanical ventilation without heat recovery: specific fan power 2.0.
- Balanced whole house mechanical ventilation with heat recovery: specific fan power 2.0 and heat recovery efficiency 66%.
- Default in-use factors: 2.5 for specific fan power and 0.70 for heat recovery efficiency.

### Vents with no confirmed system

If vents, excluding air bricks, are present in the property and the presence of mechanical ventilation cannot be confirmed, enter the number of vents as passive stack (convention 7.03a).

Worked example: a flat has ceiling vents in the kitchen and bathroom. You cannot find a fan unit and there is no documentation. Mechanical ventilation is not confirmed, so the two vents are entered as passive stack (convention 7.03a), each carrying 10 m3 per hour (specification section 4.1, Table 5).

---

## Section 4: Wet Rooms, Ducts and Two Systems

**In short:** For a system chosen from the product database, set the wet room count for a balanced whole house or centralised system, excluding bedrooms with hand basins, and identify the duct type for a decentralised system. With two mechanical ventilation systems, enter one: if identical, with half the wet rooms; if different, the one selectable from the database; if both or neither are selectable, follow the order of precedence. Ask your scheme about an odd number of wet rooms.

Conventions 7.03b, 7.03c and 7.03d apply when a system is chosen from the product database.

### Wet rooms

When a balanced whole house system or a centralised system is chosen from the database, the number of wet rooms must be set for the dwelling being assessed. Wet rooms are kitchens, utility rooms, rooms with one or more flush toilets or urinals, bathrooms and shower rooms. Bedrooms with hand basins are not included (convention 7.03b).

Worked example: a house has a kitchen, a utility room, a ground floor WC, a family bathroom, an en-suite shower room and a bedroom with a hand basin. The wet room count is five; the bedroom is not a wet room (convention 7.03b).

### Duct type

The duct type has to be identified and entered for decentralised systems. Rigid ducting is solid ductwork made from a rigid material, likely plastic, with no movement at all. Flexible ducting is typically flexible plastic over a metal wire coil forming a tube (convention 7.03c). Neither document gives a default for ductwork you cannot see, so ask your scheme.

### Duct insulation

For balanced whole house mechanical ventilation, an insulation level is required where the ducting is inside the heated envelope. Establish the length of the supply or extract duct, whichever is longer. Level 1 is met where (convention 7.03d):
- The length is less than or equal to 2 m and the duct system is continuously insulated throughout to at least 25 mm, with a thermal conductivity of 0.04 W/m.K or less.
- The length is greater than or equal to 2 m and the duct system is continuously insulated throughout to at least 50 mm, with a thermal conductivity of 0.04 W/m.K or less.

Level 2 applies where Level 1 is not satisfied or the insulation specification is not known. Where the ducting is outside the heated envelope, establish whether it is insulated or uninsulated. Convention 3.07 is cited for insulation types and equivalent thermal conductivity values (convention 7.03d).

As printed, both Level 1 conditions include a length of exactly 2 m, and the convention does not say which applies. Table 31 shows duct insulation only as yes or no (specification Table 31, item 10-1); the convention is more detailed and takes precedence.

### Two mechanical ventilation systems

Convention 7.03e was added in v12.2. Where two mechanical ventilation systems are present, one is entered:
- If the systems are identical, choose this system and input it with half the number of wet rooms.
- If the systems are different, input the system which can be selected from the database.
- If both can be selected from the database, or both are default systems, use this order of precedence: mechanical ventilation with heat recovery, then mechanical ventilation, then mechanical extract ventilation, then PIV from outside, then PIV from loft.

The notes give the reasoning. Halving the wet rooms reflects two systems in effect halving the load. Entering the database system means entering the system you can physically evidence, which the note accepts differs from a worst-case approach. The order of precedence is a sliding scale of functionality, with centralised and decentralised extract bundled together (convention 7.03e, notes 1 to 3).

Worked examples (convention 7.03e):
- Two identical units in a dwelling with six wet rooms: enter that system with three wet rooms.
- A heat recovery system and a positive input system from outside, neither with make and model evidence: both are default systems, so enter the heat recovery system.

The convention does not say what to do when the wet room count is an odd number; ask your scheme.

---

## Section 5: Draught Lobby, Draught Proofing, Air Tightness and Cooling

**In short:** A draught lobby must meet every condition in convention 2.09b, including covering the Main Entrance and at least 2 m2 of floor area, although a flat reached through an enclosed corridor or stairwell should be classified as having one. Keep the RdSAP default pressure test result unless you have a pressure test certificate that meets convention 10.01, which becomes invalid for RdSAP entry after material changes since the test. For cooling, include fixed systems only, not reversible heat pumps.

### Draught lobby

A draught lobby is an arrangement of two doors that forms an airlock on the Main Entrance to the dwelling. It may be heated or unheated. To be included, the enclosed space must (convention 2.09b):
- Cover the Main Entrance to the dwelling.
- Have a floor area of at least 2 m2.
- Have a door arrangement that lets a person with a pushchair or similar close the outer door before opening the inner door.
- Lead into a further circulation area and not directly into any other room type, although it may also give access to a cloakroom, with or without a WC.

The Main Entrance is the one designed as the main entrance, which may not be the one the occupier uses most. Flats with access via an enclosed heated or unheated corridor or stairwell should be classified as having a draught lobby (convention 2.09b). For a house, bungalow or park home, assume no draught lobby if it cannot be determined (specification section 4.1, Table 5).

Worked example: an enclosed porch covers the main entrance and has an inner and an outer door, but its floor area is 1.6 m2. It fails the 2 m2 test, so no draught lobby is recorded (convention 2.09b).

### Draught proofing

All external doors and openable windows in each building part should be examined for draught proofing (specification section 8.1). If the state of the draught proofing cannot be determined, take triple, double or secondary glazed as draught proofed, and single glazed windows and doors as not draught proofed, unless there is contrary evidence. Include glazing in a non-separated conservatory (convention 3.11a). The percentage is the number of draught proofed openable windows and doors divided by the total number of openable windows and doors, times 100 (specification section 8.1).

### Air tightness

The pressure test result stays at the RdSAP default unless specific documentary evidence is available. That evidence is a pressure test certificate giving the measured air permeability from a blower door test at 50 Pa or a low-pressure pulse test at 4 Pa, produced by a person with suitable expertise and experience, which can be shown by membership of a recognised air tightness Competent Persons Scheme (EAS or ATTMA) approved by Government. If material changes have been made to the property since the test, the certificate becomes invalid for RdSAP entry. Results from background ventilation tests are not included (convention 10.01). Course MER-DEA-021 covers this convention in full.

### Cooling

For a cooling system, include fixed systems only and do not include reversible heat pumps (convention 9.04).

---

## Key Takeaways
- An open chimney is a vertical duct of 200 mm diameter or more, counted only when unrestricted and suitable for use, at 80 m3 per hour (convention 9.01).
- A decommissioned chimney with a ventilation area under 30,000 mm2 is a blocked chimney at 20 m3 per hour; at 30,000 mm2 or more it is an open chimney; sealed completely it is not counted (convention 9.01).
- Intermittent kitchen and bathroom fans are not a mechanical ventilation system (specification Table 31, item 10-1).
- Mechanical ventilation is entered from the database where make and model are evidenced, otherwise by defaults; vents (excluding air bricks) with no confirmed system are passive stack (convention 7.03a).
- Wet rooms are kitchens, utility rooms, rooms with a flush toilet or urinal, bathrooms and shower rooms (convention 7.03b).
- Two identical mechanical ventilation systems are entered once with half the wet rooms; otherwise the database system, then the order of precedence, decides (convention 7.03e).
- A draught lobby must cover the Main Entrance, be at least 2 m2, work as an airlock and lead into a circulation area (convention 2.09b).

---

## Self-Assessment Questions

**Q1.** A decommissioned chimney has air bricks giving a ventilation area of less than 30,000 mm2. How is it treated?

A) As an open chimney, modelled at 80 m3 per hour
B) As a blocked chimney, modelled at 20 m3 per hour
C) It is not counted at all
D) As a flue

**Correct answer: B.** Convention 9.01 treats it as a blocked chimney at 20 m3 per hour; only a chimney sealed completely with no air bricks is left out of the count.

---

**Q2.** Vents (not air bricks) are present in a dwelling, but the presence of mechanical ventilation cannot be confirmed. What is entered?

A) Mechanical extract ventilation using the default data
B) Nothing, because the vents are disregarded
C) The vents, counted as intermittent extract fans
D) The number of vents, as passive stack

**Correct answer: D.** Convention 7.03a says the number of vents (excluding air bricks) is entered as passive stack when mechanical ventilation cannot be confirmed.

---

**Q3.** Two identical mechanical ventilation systems are present in one dwelling. How are they entered?

A) Choose this system and input it with half the number of wet rooms
B) Choose this system and input it with the full number of wet rooms
C) Choose this system and input it with double the number of wet rooms
D) Enter the dwelling as naturally ventilated

**Correct answer: A.** Convention 7.03e says identical systems are entered as one system with half the number of wet rooms.

---

**Q4.** An enclosed porch covers the Main Entrance of a house, has an inner and an outer door, leads into a hallway and has a floor area of 1.6 m2. Is it recorded as a draught lobby?

A) Yes, any two-door arrangement on the Main Entrance counts
B) Yes, but only if the porch is heated
C) No, because the enclosed space must be at least 2 m2
D) No, because a house can never have a draught lobby

**Correct answer: C.** Convention 2.09b requires a floor area of at least 2 m2, and says a draught lobby may be heated or unheated.

---

**Q5.** Which of these is not a wet room when setting the wet room count for a system chosen from the product database?

A) A utility room
B) A bedroom with a hand basin
C) A room with a flush toilet
D) A shower room

**Correct answer: B.** Convention 7.03b states that bedrooms with hand basins are not included; the other three are in its list of wet rooms.

---

## Further Reading
- **Conventions (v 12.2) for RdSAP 10.** Applicable from 6 August 2026. Read conventions 7.03a to 7.03e, 9.01, 5.02, 2.09b, 3.11a, 9.04 and 10.01 in full.
- **RdSAP10 Specification.** BRE, version 4.0 (7 June 2026). See section 4 (Table 5 and the list of ventilation methods), section 8.1 and Table 31 item 10-1.

---

*© Meridian CPD 2026. All rights reserved. Unauthorised reproduction prohibited.*
*This course material is licensed to individual subscribers only.*
