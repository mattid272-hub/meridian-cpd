# Heating Systems Primary: Boilers, Controls and Data Entry in RdSAP 10
**Course ID:** MER-DEA-005 | **CPD Hours:** 1.0 | **Published:** March 2026, revised October 2026 (Conventions v12.2)
*© Meridian CPD 2026. All rights reserved.*

---

## Learning Objectives
- Identify the main heating system from the Product Characteristics Database wherever possible, and apply the defaults when a boiler, heat pump or micro-CHP unit is not listed.
- Apply the heat emitter rules for systems serving both radiators and underfloor heating, and the design flow temperature rule for condensing boilers and heat pumps.
- Decide which system is main system 1 when a dwelling has two main heating systems, and record the proportions, using convention 4.09.
- Recognise community heating and Heat as a Service arrangements and select the correct heat source and fuel.
- Record TRVs, zone control, app-based control, central heating pump age and flue gas heat recovery as the conventions require.

---

## Introduction

This course covers how the main heating system is identified and entered in an RdSAP 10 assessment: boilers, heat pumps, community heating and their controls. This October 2026 rewrite replaces the March 2026 edition. Every rule is referenced to the Conventions (v12.2) for RdSAP 10, applicable from 6 August 2026, or to the RdSAP10 Specification of 9 June 2025, so you can check it.

Where a convention conflicts with the specification, the convention takes precedence (conventions, opening statement), and where the two differ on this topic the course says so. The specification does not itself list the heating systems or the controls. It refers to SAP 10.2 Tables 4a, 4b and 4e for them (specification sections 10.1 and 10.3). Those tables sit outside the two documents this course is built on, so no efficiency figures or control adjustments are quoted here.

Version 12.2 added conventions 4.05b on Heat as a Service and 4.22 on electric combi boilers (conventions, revision history). Storage heaters, room heaters and secondary heating are covered in MER-DEA-006 and water heating in MER-DEA-007.

---

## Section 1: Identifying the Main Heating System and Its Fuel

The main heating system is the one that heats the largest proportion of the dwelling. It is not usually based on individual room heaters, unless room heaters are all there is (specification section 10.1).

### Database first, default second

Main heating systems are either identified through the Product Characteristics Database (PCDB) or categorised using the generic types in SAP 10.2 Tables 4a and 4b. For gas or oil boilers, micro-CHP and heat pumps the database is to be used whenever possible (specification section 10.1).

Where the product cannot be found:
- A boiler or heat pump that is not in the PCDB is entered using the default (convention 4.07). The convention does not say which default; the specification's fallback is the generic system types just mentioned.
- Micro-CHP that cannot be found in the database is entered as a default condensing boiler, with Addendum 5 included (convention 4.04).

If there is no heating system, "none" is recorded and the calculation is done for portable electric heaters with no controls (specification section 17, Table 31 item 7-3).

Alongside the system, Table 31 item 7-4 collects the flue type (open or room-sealed), the heat emitter type (radiators, underfloor or, for heat pumps only, fan coil units) and, for heat pumps, whether it is an MCS installation, which is "yes" only if documentary evidence is available.

### Cases the conventions settle
- Electric combi boiler. Space heating is recorded manually as a standard boiler, direct acting, with electricity as the fuel (convention 4.22, new in v12.2). Its water heating is specified as "instantaneous at point of use" (convention 6.08).
- Range cooker boiler. Where a cast iron range-style cooker boiler is present, the cooker is treated as a radiator (convention 4.01a).

### Not working, not fitted or not accessible

Convention 4.03 separates three situations:
- Fitted but not working, or condemned. Any fixed heating or hot water source, or heat emitters, that are installed are still taken into account when deciding the main and secondary heating and the hot water type.
- Not fitted. If the heating source or the heat emitters are not installed, enter no heating system, or do another survey when the system is installed.
- Present but not accessible. If the heating source or emitters cannot be inspected and no documentary evidence is made available, the assessment cannot be completed until access has been provided. Community heating is excluded from this rule.

### Fuel
- Mains gas available. This is "yes" only if a mains gas meter is present or a mains gas burning appliance is fixed within the property (convention 8.02). The specification adds that a closed-off gas pipe does not count (Table 31 item 10-3).
- LPG at mains gas prices. If documentary evidence such as billing information confirms that the property receives LPG at mains gas prices, enter the fuel as "LPG subject to special condition 18" (convention 4.11). The specification's fuel table names it "LPG subject to Special Condition 11F" (specification Table 32).
- LNG. Liquefied Natural Gas networks are treated as mains gas (convention 4.11).
- Straw bales and other biomass fuels not available in RdSAP. Select wood logs and include addendum 12 (convention 4.12).
- Biogas. The convention says to specify "mains bulk LPG" and include addendum 12 (convention 4.21).
- Biodiesel, and appliances able to use mineral oil or liquid biofuel. Specify oil and include addendum 12 (convention 4.21).

Convention 4.21 adds a note: if the boiler model is in the database with mains gas as its fuel type but not bulk LPG, the database entry must not be used. The note's final words, on how to specify the boiler instead, are incomplete in the published text, so ask your accreditation scheme. Convention 4.10 on liquid biofuels has been deleted.

---

## Section 2: Heat Pumps, Heat Emitters and Design Flow Temperature

A heat pump is identified from the database whenever possible and entered as a default if it is not listed (convention 4.07). A reversible heat pump is not recorded as a cooling system (convention 9.04).

### One system serving radiators and underfloor

Convention 4.01a gives two treatments, depending on the heat source.

For anything other than a heat pump, specify the same heat source as main heating 1 and main heating 2, following the two main systems rules in convention 4.09. Specification section 10.1 repeats this.

For a heat pump there is a single entry. Enter radiators when they serve 50% or more of the total floor area. The convention then says that where the proportion is the same the emitters are entered as underfloor. Read literally, those two sentences overlap at an exact 50/50 split, and the case where radiators serve less than half is not spelled out, although underfloor is the evident reading. For an even split, check with your accreditation scheme.

The specification's data table carries a comment that reads differently: if underfloor downstairs and radiators upstairs, select radiators (Table 31 item 7-4). That does not match convention 4.01a, and the convention takes precedence.

### Worked example

A two-storey house has a gas boiler feeding underfloor heating on the ground floor and radiators upstairs. The ground floor includes the living area and is 60% of the floor area.
- Convention 4.01a: this is not a heat pump, so the boiler is entered as both main heating 1 and main heating 2, one entry for each emitter type.
- Convention 4.09 rule a): system 1 always heats the living area, so the underfloor entry is main system 1.
- Convention 4.09: the two entries serve different spaces, so the proportion is based on floor area served. The second system serves 40%.

With a heat pump instead there would be one entry. Radiators serve 40% of the floor area, below the 50% test, so on the evident reading of convention 4.01a the emitter is underfloor.

### Design flow temperature

For condensing boilers and heat pumps, the design flow temperature is recorded as unknown unless there is documentary evidence that the system has been designed and commissioned as a low temperature one (convention 4.01b). The options are unknown, over 45°C, 45°C or below but over 35°C, and 35°C or below (Table 31 item 7-4). Where the entry is unknown, the calculation takes radiators as over 45°C and underfloor heating as 35°C or below (specification section 10.11, Table 29).

Neither document describes what that evidence should look like, so ask your accreditation scheme what it accepts.

---

## Section 3: Two Main Heating Systems

RdSAP allows for two main heating systems, to cover different systems heating different parts of the dwelling. If main system 1 heats all habitable rooms there is no main system 2, unless the second system serves hot water only (specification section 10.2). Main systems 1 and 2 cannot be room heaters unless the dwelling's heating consists solely of room heaters, and a second main system is not to be confused with a secondary heater (convention 4.09).

### Which is main system 1

Convention 4.09 gives four rules, each applying when the one before does not settle it:
- a) System 1 always heats the living area.
- b) When both systems heat the living area, main system 1 is the one that heats the most habitable rooms.
- c) When both heat the same number of habitable rooms, main system 1 is the system that provides water heating.
- d) When neither or both heat water, main system 1 is the system that is cheapest to run: the fuel cost from specification Table 32 divided by the efficiency of the heating system.

Habitable rooms are as defined in convention 2.04a, so a room used solely as a kitchen, a bathroom or a hallway does not add to either system's count.

### Proportions and other rules
- Different spaces. Record the heating proportion based on the floor area served by each system (convention 4.09). The specification asks for the percentage served by the second system, estimated to the nearest 10% (Table 31 item 7-5).
- Same heating circuit. The default is a 50/50 split. A different ratio can be used only with clear documentary evidence (convention 4.09).
- Hot water only. Where a separate boiler or heat pump provides hot water only, main system 1 is the one providing space heating, at 100%, and main system 2 is the one providing hot water, at 0% (convention 6.04; specification section 10.5.1).
- More than two main systems. Use the rules above to determine main systems 1 and 2 and disregard the third (convention 4.09).
- A single system with multiple outputs, such as warm air and radiators. Treat it as two main systems, with the option that heats most floor area as main system 1 (convention 4.09a).
- Addendum 9. When there are two main systems and a heating system upgrade is recommended, include addendum 9 (convention 4.09).

Convention 4.09a also says that any system that has a heat pump must be main system 1. It does not say how that sits with rule a) of convention 4.09 when a different system heats the living area, so confirm that arrangement with your accreditation scheme.

### Worked example

Two gas boilers both feed radiators in a large living room. Boiler A also heats three other habitable rooms and boiler B heats two. Rule a) does not separate them, because both heat the living area. Under rule b) boiler A heats more habitable rooms, so it is main system 1. Had the counts been equal, rule c) would give it to whichever boiler provides the hot water.

---

## Section 4: Community Heating and Heat as a Service

### What counts as community heating

Community heating is a system in which a heat generator provides heat, hot water or both to more than one premises. Each dwelling is assessed individually. If the heat generator is in the dwelling, it is the heating system for that dwelling. If it is not in the dwelling, treat it as community heating (convention 4.05a).

### Heat source and fuel
- Where the community scheme can be identified in the community network database, it is to be selected. If there is more than one data record, only the current record can be used (convention 4.06).
- Otherwise, try to find out what the fuel is. If it cannot be ascertained, select mains gas (convention 4.06).
- For a network that is not in the database, the specification asks for the fuel and the heat generator type: boilers, CHP and boilers, or heat pump (Table 31 item 7-6).

### Heat as a Service

Convention 4.05b is new in v12.2. A Heat-as-a-Service system is treated as community heating where the service provider owns and/or operates the heat generator, regardless of whether the generator is inside or outside the dwelling. It is therefore an exception to the location test in convention 4.05a.
- Specific documentary evidence must be provided to confirm the presence of a Heat-as-a-Service installation.
- Where the service is powered by electricity, use community heat pump.
- In other circumstances, use community boiler.

The convention does not say what form the evidence must take, so confirm with your accreditation scheme what it will accept.

---

## Section 5: Controls, Pump Age and Flue Gas Heat Recovery

### Where the control options come from

Space heating controls are those marked "rd" in SAP 10.2 Table 4e (specification section 10.3). The control item is chosen from that table according to the main system type, for both main systems if there are two, and a compensating controller, if present, is taken from the PCDB (Table 31 item 7-7). The conventions do not define a programmer or a room thermostat. They add the rules below.

### TRVs

Include TRVs when they are present on 50% or more of the radiators. For this purpose count all radiators, including those not in a habitable room, such as one in a hallway (convention 4.13).

Example. A house has ten radiators, seven in habitable rooms and three elsewhere. TRVs are fitted to four. Four out of ten is below 50%, so TRVs are not included, even though four is more than half of the seven in habitable rooms. With TRVs on five of the ten, the test is met.

### Zone control and app control

Time and Temperature Zone Control (TTZC) is a system of controls that allows the heating times of at least two zones to be programmed independently, as well as having independent temperature control. It includes wired or wireless remote or mobile control systems (convention 4.17).

Heating control from a mobile application can be included only where a fixed receiver is present and there is evidence of the type of controls: time, temperature, zone (convention 4.19).

Convention 4.16 on weather compensators has been deleted, so there is no current convention on them.

### Central heating pump age

Convention 4.18 sets the test:
- Separate pump, not within the boiler. Record the age as unknown if the pump cannot be seen. The age is 2013 or later if the pump has a label stating the EEI (energy efficiency index), or if the date of manufacture on the ID plate indicates it. Otherwise it is 2012 or earlier.
- Integral pump. If supporting information is available for the presence of an integral pump to the EEI standard, treat it as 2013 or later.

The convention does not say what to record for an integral pump with no supporting information, so check with your accreditation scheme.

### Flue gas heat recovery

Include a flue gas heat recovery system only if it is found in the PCDB, identified in the same way as for heating systems. When the model cannot be found there is no default option: the device is not included in the assessment, but its presence should be recorded in site notes (convention 9.06). The specification makes it an option only where the main heating is a condensing boiler fired by mains gas, LPG or oil (Table 31 item 8-5).

---

## Key Takeaways
- Use the PCDB whenever possible. An unlisted boiler or heat pump is entered as a default (convention 4.07), and unlisted micro-CHP as a default condensing boiler with Addendum 5 (convention 4.04).
- Radiators and underfloor from one system: a boiler is entered as main heating 1 and 2, while a heat pump has one entry, with radiators when they serve 50% or more of the floor area (convention 4.01a).
- Installed but not working still counts (convention 4.03). Design flow temperature is unknown unless there is documentary evidence of low temperature design and commissioning (convention 4.01b).
- Main system 1 is settled by living area, then most habitable rooms, then water heating, then cheapest to run. Proportions follow floor area, with 50/50 the default on a shared circuit (convention 4.09).
- Community heating applies when the heat generator is not in the dwelling (convention 4.05a), and to an evidenced Heat-as-a-Service system wherever the generator sits (convention 4.05b).
- TRVs count when on 50% or more of all radiators (convention 4.13). TTZC needs at least two zones with independent time and temperature control (convention 4.17).

---

## Self-Assessment Questions

**Q1.** When are TRVs included in the assessment?

A) Only when fitted to every radiator in the dwelling
B) When present on 50% or more of the radiators, counting all radiators including those not in habitable rooms
C) When present on 50% or more of the radiators in habitable rooms, ignoring radiators elsewhere
D) When at least one radiator has one

**Correct answer: B.** Convention 4.13 says to include TRVs when present on 50% or more of the radiators, counting all radiators including those not in a habitable room.

---

**Q2.** Two main heating systems both heat the living area and the same number of habitable rooms, but only one provides water heating. Which is main system 1?

A) The system that is cheapest to run
B) The system that was installed most recently
C) The system that serves the larger floor area
D) The system that provides water heating

**Correct answer: D.** Under convention 4.09 rule c), when both systems heat the same number of habitable rooms, main system 1 is the one that provides water heating. Rule d), cheapest to run, applies only when neither or both heat water.

---

**Q3.** A house is heated by an air source heat pump owned and operated by a Heat-as-a-Service provider, and specific documentary evidence is provided. How is the main heating treated?

A) As community heating, using community heat pump
B) As an individual heat pump, because the heat generator serves only this dwelling
C) As community heating, using community boiler
D) As no heating system, because the occupier does not own the heat generator

**Correct answer: A.** Convention 4.05b treats a Heat-as-a-Service system as community heating where the provider owns and/or operates the heat generator, and says to use community heat pump where the service is powered by electricity.

---

**Q4.** A condensing boiler serves radiators and there is no documentary evidence about how the system was designed or commissioned. What is recorded for design flow temperature?

A) 35°C or below, because the boiler is a condensing type
B) Over 45°C, because the emitters are radiators
C) Unknown
D) Whatever temperature is currently set on the boiler

**Correct answer: C.** Convention 4.01b says the design flow temperature is recorded as unknown unless there is documentary evidence that the system has been designed and commissioned as a low temperature one.

---

**Q5.** How is the space heating from an electric combi boiler recorded?

A) Manually, as a standard boiler, direct acting, with electricity as the fuel
B) As an electric CPSU
C) As electric storage heaters
D) As no heating system, with the calculation done for portable electric heaters

**Correct answer: A.** Convention 4.22, added in v12.2, says space heating provided by an electric combi boiler should be recorded manually as a standard boiler, direct acting, fuel type electricity.

---

## Further Reading
- **Conventions (v12.2) for RdSAP 10.** Applicable from 6 August 2026. Read section 4 (Main heating) in full, with conventions 6.04, 6.08, 8.02 and 9.06.
- **RdSAP10 Specification.** BRE, 9 June 2025. See section 10 (Space and water heating), Table 29, Table 30 (addenda) and the heating items in Table 31 (data to be collected).
- **BRE Technical Notes.** BRE, https://www.bregroup.com/sap/bre-technical-notes/. Convention 9.16 requires you to check this list when a technology on site might be the subject of a Technical Note.

---

*© Meridian CPD 2026. All rights reserved. Unauthorised reproduction prohibited.*
*This course material is licensed to individual subscribers only.*
