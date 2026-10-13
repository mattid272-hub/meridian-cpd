# Hot Water Systems in RdSAP 10: Cylinders, Combis and Immersions
**Course ID:** MER-DEA-007 | **CPD Hours:** 1.0 | **Published:** October 2026
*© Meridian CPD 2026. All rights reserved.*

---

## Learning Objectives
- Identify the water heating source, including a boiler or heat pump that heats water only, a system that is fitted but not working, and a dwelling with no water heater.
- Apply the single tariff rules to a dual immersion and an electric CPSU, and know when Addendum 6 is included.
- Record cylinder size, insulation and cylinderstat using conventions 6.05 to 6.07, and tell a site default from a software default.
- Enter instantaneous water heaters, electric combi boilers and electric showers using conventions 6.08, 6.09 and 4.22.
- Count baths and showers, and decide whether waste water heat recovery, solar water heating and flue gas heat recovery can be included.

---

## Introduction

The hot water rules in RdSAP 10 are short. Most of the conventions in section 6 are one or two sentences long. Short rules are easy to half remember.

This revised edition has been rebuilt from the two governing documents: the Conventions (v12.2) for RdSAP 10, applicable from 6 August 2026, and the RdSAP10 Specification version 4.0 (7 June 2026). Every rule carries a reference so that you can check it. Where the two documents disagree, the convention takes precedence (conventions, front page).

Three of the v12.2 changes touch hot water (conventions, revision history). Convention 4.03 now covers a hot water system that is incomplete or not working, as well as heating. Convention 4.22 on electric combi boilers is new. Convention 9.08 on waste water heat recovery has gained a list of bath and shower items.

This edition replaces the March 2026 edition. That edition taught rules for a combi boiler "keep-hot" facility. Neither the conventions nor the specification's water heating data items (Table 31, items 7-9 to 7-20) mention a combi boiler "keep-hot" facility, so those rules have been removed. Where the sources are silent on something you need, that is said plainly and you are pointed to your accreditation scheme.

---

## Section 1: Identifying the Water Heating Source

### The choices in the data set

The specification lists where the hot water can come from: the main heating system, the second main system, the secondary system, another water heater from the hot-water-only part of SAP 10.2 Table 4a, or no hot water system present. If the water is not heated by the main system, the fuel is needed as well (specification Table 31, item 7-9).

### A separate boiler or heat pump for hot water only

Sometimes a boiler or heat pump does nothing except heat the water. Convention 6.04 tells you to use the two main heating system entries:
- Main system 1 is the one providing space heating, with 100% of the heat.
- Main system 2 is the one providing the hot water, with 0% of the heat.

The specification gives the same instruction (section 10.5.1, and Table 31, item 7-5). If both main heating systems supply space heating only, so that neither entry is available for the water heater, a generic DHW-only boiler can be selected from the water heating options (convention 6.04).

### Fitted but not working, and not fitted at all

Convention 4.03 was amended in v12.2 to refer to hot water as well as heating. A fixed hot water source that is fitted but not working, or that has been condemned, is still taken into account when you decide the hot water type (convention 4.03). You record what is installed, not what currently runs.

Where there is no water heating system at all, the calculation is done for an electric immersion heater. The immersion is taken as dual if the electricity meter is dual and as single otherwise, including where the meter is unknown. The cylinder is taken from the first rows of Tables 28 and 29, which are the rows for an inaccessible cylinder (specification section 10.7).

### Dual immersion on a single tariff

If the cylinder has a dual immersion but the dwelling has a single electricity tariff, enter a single immersion and include Addendum 6 (convention 6.03). The specification agrees: a dual electric immersion is one of the systems that needs an off-peak tariff for its intended operation, and with a single meter the immersion is entered as single with Addendum 6 (specification sections 10.5 and 12).

Addendum 6 tells the reader of the EPC that a dual rate appliance is present with a single-rate supply, and that a single-rate appliance was used for the assessment (specification Table 30).

### Electric CPSU

Convention 4.15 deals with the electric CPSU in three steps. It uses a 10-hour or 18-hour tariff. On a 7-hour tariff it is treated as a water storage boiler. On a single tariff it is recorded as a direct-acting electric boiler.

Specification section 12 words the single meter case differently (heating entered as panel heaters, with Addendum 6), so the two documents do not match. The convention takes precedence, but it does not mention Addendum 6, so check with your accreditation scheme whether to include it.

---

## Section 2: Cylinders: Size, Insulation and Cylinderstat

### Cylinder size

Use the actual size if it can be obtained from the label on the cylinder; an exact volume can be entered where known (specification section 10.5, and Table 31, item 7-10). If the actual size is not determined, choose a descriptor, and the calculation uses a fixed size for it (specification Table 28):
- Normal, up to 130 litres: calculated as 110 litres.
- Medium, 131 to 170 litres: calculated as 160 litres.
- Large, over 170 litres: calculated as 210 litres.
- Inaccessible: 210 litres with an off-peak electric dual immersion, 160 litres if heated from a solid fuel boiler, otherwise 110 litres.

"No cylinder" is also an option (specification Table 31, item 7-10). A hot water thermal store that is physically separate is treated as a cylinder (convention 6.06).

### Insulation type and thickness

The insulation type, unless there is no access, is one of none, loose jacket or factory-applied, and the thickness is one of 0, 12, 25, 38, 50, 80, 120 or 160 mm (specification Table 31, items 7-11 and 7-13). The alternative to a thickness is the cylinder's measured loss in kWh per day; the two are mutually exclusive (specification Table 31, items 7-12 and 7-13). Neither document says what evidence is needed for a measured loss figure, so ask your accreditation scheme before using one.

Convention 6.05 gives four rules for what you find on site:
- A modern unvented pressurised cylinder, steel or plastic encased (the convention's example is a Megaflo), or one with a factory fitted jacket: treat the insulation as 50 mm of factory-applied foam and assume a cylinderstat is present.
- An Elson (wooden box) type: record the actual thickness as factory-applied insulation and check for a cylinderstat, "otherwise record as no access" in the convention's words.
- Factory insulation plus a jacket: enter the thickness of the foam plus one third of the thickness of the jacket.
- Thickness that cannot be measured: assume 25 mm for spray foam and 12 mm for a jacket.

### Worked example: foam plus jacket

A cylinder has 25 mm of factory-applied foam with a 75 mm loose jacket fitted over it. One third of the jacket is 25 mm, so the thickness to enter is 25 + 25 = 50 mm (convention 6.05).

Had the jacket been 80 mm, the sum would be 25 + 26.7 = 51.7 mm, which is not one of the eight listed thicknesses. Neither document says how to round, so ask your accreditation scheme.

### Two different kinds of default

Keep these apart, because they apply in different situations:
- The convention's figures (25 mm for spray foam, 12 mm for a jacket) are for insulation whose thickness cannot be measured (convention 6.05).
- The specification's figures are for a cylinder that is not accessible. They depend on the age band of the main property: 12 mm loose jacket for age bands A to F, 25 mm foam for G and H, 38 mm foam for I to M (specification Table 29).

### Cylinderstat

Include a cylinderstat only when it is mounted on the side of the cylinder and has an electric connection (convention 6.07). The exception is the Megaflo-type cylinder in convention 6.05, where a cylinderstat is assumed present.

The item is yes or no, unless there is no access (specification Table 31, item 7-15). With no access the assumption is no cylinder thermostat, but one is assumed present when the hot water is from a heat network, an immersion heater, a thermal store, a combi boiler or a CPSU (specification Table 29).

The entry has a second effect. Boiler interlock is assumed present if there is a room thermostat and, for stored hot water heated by the boiler, a cylinder thermostat; otherwise the system is not interlocked (specification Table 29).

---

## Section 3: Instantaneous Heaters, Electric Combis and Electric Showers

### Instantaneous water heaters and the 55 litre test

An instantaneous water heater may contain a small store. Convention 6.08 says to disregard a small water storage volume, and defines small as less than or equal to 55 litres. If the storage volume exceeds 55 litres, the heater is specified as an electric immersion or a gas boiler for water heating only (convention 6.08). Exactly 55 litres is still small and is disregarded.

### Electric combi boilers

Convention 4.22 is new in v12.2. Space heating from an electric combi boiler is recorded manually as a standard boiler, direct acting, with the fuel type electricity (convention 4.22). For the hot water it sends you to convention 6.08: where water is heated by an electric combi, the water heater is specified as "instantaneous at point of use".

### An electric shower as the only water heater

If the only water heater in the dwelling is an electric shower, specify the water heating as "electric instant water heating" (convention 6.09).

### Water heated by PV

Convention 6.10, which dealt with water heated by PV, is deleted. A PV diverter for water heating is a yes or no item in the data set (specification Table 31, item 11-2), and it can be entered only with written evidence of the manufacturer and model of the diverter (convention 9.05).

---

## Section 4: Baths, Showers, Heat Recovery and Solar

### Baths and showers are always counted

The data set includes the number of showers, mixer showers and baths (specification Table 31, items 7-18 to 7-20). The number of baths with waste water heat recovery, and the number and type of showers with it, are always collected so that a recommendation can be made (specification Table 31, item 9-1).

The v12.2 addition to convention 9.08 spells this out. For instantaneous and storage types, and when no system or an unknown system is present, record the total number of baths in the property, the number of baths connected to the system if there is one, and the type and number of non-electric showers. A shower must be permanent, meaning not temporarily attached to bath taps when in use (convention 9.08).

### When waste water heat recovery can be included

Include a system only if its brand name and model are found in the PCDB. If the model cannot be found there is no default: the device is left out of the assessment and its presence is recorded in site notes (convention 9.08).

### Instantaneous systems

For instantaneous types, convention 9.08 sets these rules:
- The number of rooms with a bath and/or shower includes rooms with only an electric shower. Two showers in a single room count as one.
- Only mixer showers count. A mixer shower is one where the hot water is provided by a boiler (combi or regular), a heat pump or an immersion heater.
- A shower that is integral with the bath taps, designed as a unit switchable between shower and taps, counts as a mixer shower only if there is a shower bracket at least 1.5 m above the plughole and a shower curtain or screen is present. Both conditions are needed.

### Storage systems

For storage types the convention says to record the total number of baths and showers of any type, and the total number connected to the system (convention 9.08). The specification's data table says instead that a storage type is disregarded, because the details needed for the calculation cannot be identified at survey (specification Table 31, item 9-2). The two do not match. The convention takes precedence, so record the counts, and ask your accreditation scheme if you cannot enter the system.

### Worked example: counting for an instantaneous system

A house has three rooms with a bath or shower. The bathroom has a bath with a switchable bath and shower unit fed from the combi boiler, a bracket 1.7 m above the plughole and a glass screen. The en-suite has an electric shower only. The ground floor shower room has a fixed shower fed from the combi.
- Rooms with a bath and/or shower: three. The en-suite counts even though it has only an electric shower.
- Baths: one.
- Mixer showers: two. The shower room shower is fed by a boiler, and the bath unit passes both the bracket test and the screen test.
- The electric shower is not a mixer shower: its hot water is not provided by a boiler, heat pump or immersion heater.

Take away the screen and the bath unit no longer counts, leaving one mixer shower (convention 9.08).

### Solar water heating

The first item is whether a solar panel is present. If details are known, the items are tilt, orientation, overshading, the type of solar water pump and the type of showers in the property; collector details and solar store details are further sets (specification Table 31, items 8-1 to 8-4). Convention 9.09 governs what you can change:
- Documentary evidence is required to overwrite collector or solar store values. Orientation, tilt and overshading can be overwritten.
- If collector details are available but solar store information is not, default values can be used for the store.
- If the solar store is combined and its details are being recorded, the volume of the combined cylinder must be recorded too.
- Shower type is required when solar water heating details are known. Here "electric shower" means a shower where the water is heated by electricity as the shower runs. A shower supplied from a hot water cylinder is non-electric, and the specification adds that this holds even though the cylinder is electrically heated (convention 9.09; specification Table 31, item 8-2).

If a panel is present and details are not known, the defaults include a flat panel with an aperture area of 3 square metres, facing south at a 30 degree pitch with modest overshading (specification Table 29).

### Flue gas heat recovery

Include a flue gas heat recovery system only if it is found in the PCDB, identified in the same way as a heating system. If the model is not there, there is no default: leave it out and record its presence in site notes (convention 9.06).

---

## Key Takeaways
- A boiler or heat pump that heats water only is main system 2 with 0% of the space heating (convention 6.04).
- A hot water source that is fitted but not working or condemned is still recorded (convention 4.03).
- A dual immersion on a single tariff is entered as a single immersion with Addendum 6 (convention 6.03).
- A Megaflo-type cylinder is 50 mm factory-applied foam with a cylinderstat assumed. Foam plus a jacket is the foam thickness plus one third of the jacket (convention 6.05).
- Otherwise a cylinderstat counts only if it is mounted on the side of the cylinder and has an electric connection (convention 6.07).
- A store of 55 litres or less in an instantaneous water heater is disregarded. An electric combi is a direct acting electric standard boiler for heating and "instantaneous at point of use" for water (conventions 6.08 and 4.22).
- Waste water and flue gas heat recovery are included only if found in the PCDB (conventions 9.08 and 9.06).
- A shower integral with bath taps is a mixer shower only with a bracket at least 1.5 m above the plughole and a curtain or screen (convention 9.08).

---

## Self-Assessment Questions

**Q1.** A cylinder has a dual immersion heater, and the dwelling has a single electricity tariff. How is the immersion entered?

A) As a dual immersion, with the off-peak tariff it was designed for
B) As a single immersion, with Addendum 6 included
C) As a dual immersion on the single tariff, with no addendum
D) As no water heating system, because the immersion cannot work as intended

**Correct answer: B.** A dual immersion with a single electricity tariff is entered as a single immersion and Addendum 6 is included (convention 6.03).

---

**Q2.** A cylinder has 25 mm of factory-applied foam and a 75 mm loose jacket fitted over the foam. What insulation thickness is entered?

A) 100 mm, the foam plus the full jacket
B) 25 mm, because a jacket over foam is ignored
C) 75 mm, because the thicker layer is used
D) 50 mm, the foam plus one third of the jacket

**Correct answer: D.** For a factory insulated cylinder with a jacket, enter the foam thickness plus one third of the jacket thickness, here 25 + 25 = 50 mm (convention 6.05).

---

**Q3.** An electric combi boiler provides the heating and the hot water. How is it recorded?

A) Heating as a standard boiler, direct acting, fuel electricity; water heater as "instantaneous at point of use"
B) Heating as an electric CPSU; water heating from the main system
C) Heating as a water storage boiler; water heating as an electric immersion
D) Heating as panel heaters with Addendum 6; water heating as a single immersion

**Correct answer: A.** Space heating from an electric combi is recorded manually as a standard boiler, direct acting, fuel type electricity (convention 4.22), and its water heating is specified as "instantaneous at point of use" (convention 6.08).

---

**Q4.** An instantaneous waste water heat recovery system is found in the PCDB. The bath has a shower integral with the bath taps, fed from a combi, with a bracket 1.6 m above the plughole and no curtain or screen. Does it count as a mixer shower?

A) Yes, because the bracket is more than 1.5 m above the plughole
B) Yes, because any shower fed from a combi boiler is a mixer shower
C) No, because there is no shower curtain or screen
D) No, because a shower over a bath is never counted

**Correct answer: C.** A shower integral with bath taps counts as a mixer shower only if the bracket is at least 1.5 m above the plughole and a shower curtain or screen is present; both are required (convention 9.08).

---

**Q5.** Solar water heating details are known. The only shower in the dwelling is supplied from a hot water cylinder heated by an electric immersion. What shower type is recorded?

A) Electric, because the water is heated by electricity
B) Non-electric, because the shower is supplied from a hot water cylinder
C) No shower, because it is not connected to the solar panel
D) Both electric and non-electric, to cover both possibilities

**Correct answer: B.** "Electric shower" means the water is heated by electricity as the shower runs; a shower supplied from a hot water cylinder is non-electric, even where the cylinder is electrically heated (convention 9.09; specification Table 31, item 8-2).

---

## Further Reading
- **Conventions (v12.2) for RdSAP 10.** Applicable from 6 August 2026. Read section 6 (water heating), then conventions 4.03, 4.15, 4.22, 9.05, 9.06, 9.08 and 9.09.
- **RdSAP10 Specification.** BRE, version 4.0 (7 June 2026). See sections 10.5 to 10.11 and 12, Tables 28, 29 and 30, and Table 31 items 7-9 to 7-20, 8-1 to 8-6, 9-1, 9-2 and 11-2.
- **BRE Technical Notes.** https://www.bregroup.com/sap/bre-technical-notes/ Convention 9.16 requires you to check this list when you find a technology that might be the subject of a Technical Note.

---

*© Meridian CPD 2026. All rights reserved. Unauthorised reproduction prohibited.*
*This course material is licensed to individual subscribers only.*
