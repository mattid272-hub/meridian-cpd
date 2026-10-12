# Solar PV, Battery Storage and PV Diverters in RdSAP 10
**Course ID:** MER-DEA-011 | **CPD Hours:** 1.0 | **Published:** March 2026, revised October 2026 (Conventions v12.2)
*© Meridian CPD 2026. All rights reserved.*

---

## Learning Objectives
- Identify the capacity figure RdSAP 10 needs for a PV array: kWp first, declared net capacity second, and percentage of roof area only in one defined case.
- Enter panels on different roof planes as separate systems and apportion a single total kWp or DNC between them.
- Apply the generation meter and connection rules, including what to record when connection to the dwelling's meter cannot be determined.
- Allocate a PV array that serves more than one building or dwelling on an area-weighted basis.
- State the evidence required for PV batteries and PV diverters, the battery default, and how a battery above the default is entered.

---

## Introduction

This course covers how photovoltaics, PV batteries and PV diverters are identified, evidenced and entered in an RdSAP 10 assessment. Almost all of the rules sit in one place: convention 9.05 of the RdSAP 10 Conventions, version 12.2, applicable from 6 August 2026. The RdSAP10 Specification of 9 June 2025 adds the list of data items (section 17, Table 31), a short section on photovoltaics (section 11.1) and another on diverters and batteries (section 11.2).

This revised edition replaces the March 2026 edition and is written directly from those two documents. Where it differs from the earlier edition, follow this one. Every rule carries a reference in brackets so you can check it. Where a convention conflicts with the specification, the convention takes precedence (conventions, opening statement).

The course does not describe software screens, which differ between schemes and are not in the sources. It says little about how the calculation credits these technologies, because the specification largely refers to SAP 10.2 for that. Where the sources are silent, it says so and points you to your accreditation scheme.

---

## Section 1: Capacity: kWp, DNC and the percentage of roof route

### The figure you are looking for

When photovoltaics are present, the peak power of the array in kWp is required (convention 9.05). The convention names where you might find it: the system specification documents, or the schematic wiring diagram, which may be next to the electricity meter or the consumer unit (convention 9.05).

If the kWp cannot be found, the declared net capacity (DNC) stated on the MCS certificate may be used instead (convention 9.05).

Paperwork you rely on has to meet the general test for documentary evidence. Acceptable evidence includes certificates, warranties, guarantees or any documents verifying that work has been carried out. You must be confident, and able to demonstrate, that it relates to the actual property and that there is no physical or other documentary evidence to the contrary (convention 9.02). Evidence of intent to install does not on its own qualify, and under the separate wording for Scotland it does not qualify at all (convention 9.02).

### What goes in with the kWp

Where the kWp or DNC is known, the data set holds these details for the array (specification section 17, Table 31, item 11-1):
- kWp.
- Pitch, as one of horizontal, 30 degrees, 45 degrees, 60 degrees or vertical.
- Orientation, if not horizontal, as one of S, SE, E, NE, N, NW, W or SW.
- Overshading, as one of very little, modest, significant or heavy.
- Whether the PVs are connected to the dwelling's electricity meter.

Up to three separate PV arrays are allowed for, each with its own kWp, tilt, orientation and overshading (specification section 11.1). The specification rounds kWp to two decimal places before the calculation (specification section 15).

Neither the conventions nor the specification sections covered here say how to choose between the four overshading categories for a PV array. If you are unsure which applies, check your scheme's guidance.

### When neither kWp nor DNC can be found

If the kWp or DNC cannot be ascertained, the instruction is not to allocate the PV, with one exception: where it is connected to a meter serving a single dwelling (convention 9.05). In that case you record the percentage of the total roof area occupied by PVs, and the total roof area includes the main dwelling and all extensions where present (convention 9.05).

The percentage is therefore of the whole roof of the dwelling, extensions included, not of the slope the panels sit on.

The specification explains what is done with the percentage (specification section 11.1):
- PV area is the roof area used for heat loss, before any amendment for a room in roof, multiplied by the percentage of roof area covered by PVs.
- For a pitched roof that area is divided by the cosine of 35 degrees. Where there is an extension, the cosine factor is applied only to the parts with a pitched roof.
- kWp is taken as 0.12 multiplied by the PV area, on the stated basis that mainstream panels produce around 120 Wp per square metre.
- If orientation, pitch and overshading are not provided in the data set, the array is taken as facing south, at 30 degrees pitch, with modest overshading.

An illustration using those rules: a dwelling has 50 square metres of roof area for heat loss and you record 20% covered, which gives 10 square metres. The roof is pitched, so 10 divided by 0.819 gives 12.2 square metres of PV area, and 0.12 multiplied by 12.2 gives 1.46 kWp. The specification's own example reaches the same 1.46 kWp from 10 square metres, although it prints the multiplier as 1.2 where the rule says 0.12. You record only the percentage; the conversion is part of the calculation.

---

## Section 2: Roof planes, the generation meter and connection

### Panels on different roof planes

If there are PV panels on different planes of the roof, enter them as separate systems (convention 9.05). If only a total kWp or DNC is provided, estimate the relative area of each and apportion the value accordingly (convention 9.05).

Worked example. The paperwork gives a single figure of 4.00 kWp. You estimate about 15 square metres of panels on the south-east plane and about 10 on the north-west plane, 25 in total. The south-east system is 15 divided by 25, or 60%, so it is entered as 2.40 kWp. The north-west system takes the remaining 40%, entered as 1.60 kWp. Each system then carries its own pitch, orientation and overshading (specification section 11.1).

The sources do not say what to do where panels sit on more planes than the three arrays the specification allows for (specification section 11.1). If you meet that, ask your accreditation scheme.

### Verifying connection

The data set asks, whichever way the array is entered, whether the PVs are connected to the dwelling's electricity meter (specification section 17, Table 31, item 11-1). Convention 9.05 sets out how that is established, in two sentences that need reading together:
- PV connection to the dwelling's meter must be verified by the presence of a PV generation meter or documentary evidence.
- In all cases, the PV-generated electricity is included in the assessment of a dwelling only if the dwelling has a PV generation meter serving it.

The first sentence accepts either a generation meter or documents as verification. The second makes a generation meter serving the dwelling the condition in every case. The convention does not explain how to treat documentary evidence of connection where no generation meter can be found. If that is your situation, ask your accreditation scheme before lodging. The conventions also do not describe what a PV generation meter looks like.

Where it cannot be determined that the PV supply is feeding into a meter serving the dwelling being assessed, the PV panels are still allocated to the dwelling but should not be specified as being connected (convention 9.05).

### The four outcomes

Putting the paragraphs of convention 9.05 side by side gives four outcomes:
- kWp or DNC known, and connection to a meter serving the dwelling verified: enter the system or systems as connected.
- kWp or DNC known, but connection cannot be determined: the panels are still allocated to the dwelling, but not specified as connected.
- Neither can be ascertained, and the PV is connected to a meter serving a single dwelling: record the percentage of the total roof area occupied by PVs.
- Neither can be ascertained, and there is no such connection: do not allocate the PV.

### Electricity meters, smart meters and export

The dwelling's electricity meter type is a separate entry, covered by convention 9.13. Smart meters are defined there as meters that communicate wirelessly with the meter network. They do not have to be functioning at the time of the visit, but the evidence must be either a smart meter unit or a portable display that shows meter readings (convention 9.13). The smart meter items do not affect the calculation and are used for statistical reasons only (specification section 17, Table 31, items 1-17 and 1-18).

The data set also asks whether the dwelling is export-capable, yes or no, because the savings from generated electricity depend on whether it is used within the dwelling or exported (specification section 17, Table 31, item 1-16). The conventions give no rule on how export capability is identified or evidenced, so follow your scheme's guidance.

---

## Section 3: PV shared between buildings or dwellings

### The rule

Where the PV supply is serving more than one building, or multiple dwellings within the building, the total capacity of the PV is allocated between the buildings on an area-weighted basis, based on an estimate of the total floor area of all of the buildings or dwellings served by the PV (convention 9.05).

This applies in all scenarios where the PV supplies more than one building or multiple dwellings within a building, including where the other buildings are all dwellings, a mix of dwellings and non-domestic buildings, or all non-domestic buildings (convention 9.05). The floor area used is an estimate of everything served, not only the dwelling you are assessing.

### Worked example: flats sharing one array

An array on the roof of a small block has a documented capacity of 6.00 kWp and serves three flats. You are assessing the middle flat. You estimate the floor areas as 50, 70 and 80 square metres, 200 square metres in total.
- Share for the flat being assessed: 70 divided by 200, which is 0.35.
- Capacity allocated to it: 6.00 kWp multiplied by 0.35, which is 2.10 kWp.

Entering the full 6.00 kWp against one flat, or an equal three-way split of 2.00 kWp, would not follow the convention, which requires area weighting (convention 9.05).

### Where the sources stop

Two points are not answered by the sources:
- Area weighting needs a total capacity to share out. The convention does not explain how the percentage of roof route would work for a shared array whose kWp and DNC cannot be ascertained.
- The sharing rule speaks only of the capacity of the PV. It does not say how a battery shared between dwellings should be treated.

On either, ask your accreditation scheme.

---

## Section 4: Batteries, diverters and related entries

### PV batteries: what is recorded

The data set has an item for PV batteries, yes or no, and an item for the number of batteries, from 1 to a maximum of 4, used only if battery storage is present (specification section 17, Table 31, items 11-3 and 11-4). The assessor needs to collect the number of batteries and the capacity of each (specification section 11.2).

### Battery evidence and the default

For PV batteries, photographic or written evidence of the manufacturer and model of the battery unit, and of its usable capacity in kWh, is required. If this cannot be obtained, use a default of 5 kWh per battery (convention 9.05). The specification agrees: if the capacity is unknown or cannot be determined, assume 5 kWh (specification section 17, Table 31, item 11-4).

### A battery above the default

Version 12.2 added a paragraph to convention 9.05 that was not in version 12.1. It says that where an individual battery has a storage capacity greater than 5, the PV battery shall be entered as two separate batteries: the first entry shall be 5, with the excess entered as a second battery (convention 9.05).

The units in that paragraph are not consistent. The default in the preceding sentence is given as 5kWh, but the new paragraph says "5Kw" and "5kW". The specification has the same mix: section 11.2 gives the default as 5kW, while Table 31 item 11-4 gives 5kWh and says that a known capacity of 10 kWh is specified as 2 batteries. If the difference matters for a unit you are assessing, ask your scheme.

Worked example. A single battery has documented usable capacity of 8 kWh. Following convention 9.05, it is entered as two batteries: the first at 5 and the second carrying the excess of 3.

The convention does not say what to do when the excess is itself more than 5, for example a single 12 kWh unit, where the excess would be 7. The specification allows up to 4 batteries (specification section 17, Table 31, item 11-4) but does not settle the point either. Ask your scheme.

At least one accreditation scheme bulletin states that no more than three batteries can be recorded, and that a diverter is ignored where batteries are present. Neither statement appears in the conventions or the specification. Treat them as that scheme's practice and check what your own scheme says.

### Batteries that are not PV batteries

Convention 9.05 and the data set both speak of PV batteries. The specification's list of EPC addenda, from which the assessor selects, includes one for "PV-independent battery storage present". Its text says the assessment does not include PV-independent battery storage (specification section 13, Table 30, addendum 16).

### PV diverters

The data set has a yes or no item, PV diverter for water heating, described as for when PV is used for water heating (specification section 17, Table 31, item 11-2). If the answer is yes, the specification says only that the calculation follows SAP 10.2 section G4 (specification section 11.2).

For PV diverters, written evidence of the manufacturer and model of the diverter system installed is required, and if this cannot be obtained the diverter cannot be entered (convention 9.05). Compare the two rules:
- Battery: photographic or written evidence, with a 5 kWh default if it cannot be obtained.
- Diverter: written evidence, with no default. Without it there is no entry.

The former convention on water heated by PV is shown as deleted (convention 6.10), so convention 9.05 is where the diverter rule sits. Neither document sets out further eligibility tests for a diverter, such as the type of hot water system it must serve. If you are unsure whether a device counts, ask your scheme.

### Related addenda and other technologies

Two more addenda are relevant (specification section 13, Table 30):
- Addendum 8, for PVs or a wind turbine present on the property in England, Wales or Scotland. Its text says the assessment does not include any feed-in tariffs but may include a benefit for the export of excess generation to the grid.
- Addendum 15, for when PV is recommended. Its text suggests considering a PV battery and a PV diverter for water heating.

If you meet a technology that does not fit these entries and might be the subject of a BRE Technical Note, check the published list and, if a note applies to RdSAP, follow its instructions (convention 9.16).

---

## Key Takeaways
- The array's kWp is required; if it cannot be found, the DNC stated on the MCS certificate may be used instead (convention 9.05).
- If neither can be ascertained, do not allocate the PV unless it is connected to a meter serving a single dwelling; then record the percentage of the total roof area occupied by PVs (convention 9.05).
- Panels on different roof planes are separate systems; a single total kWp or DNC is apportioned by the estimated relative area of each (convention 9.05).
- Connection must be verified by a PV generation meter or documentary evidence; if it cannot be determined, the panels are still allocated but not specified as connected (convention 9.05).
- PV serving more than one building or dwelling is allocated by area weighting on estimated total floor area (convention 9.05).
- Batteries need photographic or written evidence of manufacturer, model and usable capacity; without it the default is 5 kWh per battery, and a battery above that is entered as two (convention 9.05).
- A PV diverter needs written evidence of manufacturer and model; without it the diverter cannot be entered (convention 9.05).

---

## Self-Assessment Questions

**Q1.** The kWp of a PV array cannot be found in any document or on the wiring diagram, but the MCS certificate states the declared net capacity. What does convention 9.05 allow?

A) Record the percentage of roof area covered
B) Use the DNC stated on the MCS certificate instead of the kWp
C) Do not allocate the PV to the dwelling
D) Enter three arrays of equal size

**Correct answer: B.** Convention 9.05 says that if the kWp cannot be found, the DNC stated on the MCS certificate may be used instead; the percentage of roof route is only for when neither can be ascertained.

---

**Q2.** The kWp of an array is documented, but it cannot be determined that the PV supply is feeding into a meter serving the dwelling being assessed. How are the panels treated?

A) They are left out of the assessment altogether
B) They are entered as connected, because the kWp is known
C) They are replaced by a percentage of roof area entry
D) They are still allocated to the dwelling but not specified as being connected

**Correct answer: D.** Convention 9.05 says that in this case the PV panels are still allocated to the dwelling but should not be specified as being connected.

---

**Q3.** A PV battery is present. You can photograph the unit, but neither the photographs nor any paperwork give its usable capacity. What capacity applies?

A) A default of 5 kWh per battery
B) A default of 4 kWh per battery
C) No battery can be entered without the capacity
D) A default of 10 kWh, entered as two batteries

**Correct answer: A.** Convention 9.05 says that if evidence of manufacturer, model and usable capacity cannot be obtained, a default of 5kWh per battery is used.

---

**Q4.** A 6.00 kWp array serves three flats with estimated floor areas of 50, 70 and 80 square metres. What capacity is allocated to the 70 square metre flat?

A) 6.00 kWp, because the array is on the building
B) 2.00 kWp, an equal share between three flats
C) 2.10 kWp, by area weighting
D) None, because shared arrays are not allocated

**Correct answer: C.** Convention 9.05 allocates the total capacity by area weighting on the estimated total floor area served: 70 divided by 200 is 0.35, and 0.35 of 6.00 kWp is 2.10 kWp.

---

**Q5.** A householder tells you a PV diverter is installed, but no written evidence of the manufacturer and model of the diverter system can be obtained. What does convention 9.05 require?

A) Enter the diverter using a default
B) The diverter cannot be entered
C) Enter it as a second PV battery of 5 kWh
D) Enter it under convention 6.10, water heated by PV

**Correct answer: B.** Convention 9.05 requires written evidence of manufacturer and model and says that if this cannot be obtained the diverter cannot be entered; convention 6.10 is deleted.

---

## Further Reading
- **Conventions (v12.2) for RdSAP 10.** Applicable from 6 August 2026. Read convention 9.05 in full, with 9.02 for documentary evidence, 9.13 for meters and 9.16 for technologies outside the standard entries.
- **RdSAP10 Specification.** 9 June 2025. See sections 11.1 and 11.2, section 13 Table 30 (addenda 8, 15 and 16) and section 17 Table 31 (items 1-16 to 1-18 and 11-1 to 11-4).
- **BRE Technical Notes.** BRE, https://www.bregroup.com/sap/bre-technical-notes/. The list that convention 9.16 requires you to check.

---

*© Meridian CPD 2026. All rights reserved. Unauthorised reproduction prohibited.*
*This course material is licensed to individual subscribers only.*
