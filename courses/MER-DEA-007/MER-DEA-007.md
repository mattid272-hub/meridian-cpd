# Hot Water Systems in RdSAP 10: Cylinders, Combis and Immersions
**Course ID:** MER-DEA-007 | **CPD Hours:** 1.0 | **Published:** March 2026
*© Meridian CPD 2026. All rights reserved.*

---

## Learning Objectives

- Apply the RdSAP 10 DHW assessment methodology correctly for the main cylinder types, distinguishing between insulated and uninsulated cylinders, jacket types, and factory-insulated foam cylinders.
- Correctly classify and enter combi boiler DHW provision in RdSAP 10, including the distinction between instantaneous and storage combis and the keep-hot function.
- Assess immersion heaters as primary and secondary DHW systems and determine the correct RdSAP 10 inputs for each configuration.
- Understand how solar thermal systems interact with DHW assessment in RdSAP 10 and the evidence required to claim solar DHW contribution.
- Recognise the most common audit failures in DHW data entry and apply the evidence standards required.

---

## Introduction

Domestic hot water accounts for a significant proportion of total energy demand in most dwellings — typically 20–30% of total space and water heating energy, rising to a larger proportion in well-insulated homes where space heating demand has been reduced. Despite this, DHW data entry is one of the areas where assessors most frequently make systematic errors, often because the DHW section of the RdSAP 10 software workflow is completed quickly after the more complex heating section.

RdSAP 10 has brought meaningful changes to the DHW methodology. Cylinder thermal performance — particularly the treatment of insulation type, thickness, and the distinction between factory foam-insulated cylinders and site-applied jacket insulation — is more granular. The interaction between hot water provision, boiler type, and solar thermal is more explicitly modelled. And the default assumptions for immersion heater-primary systems have been updated to reflect contemporary usage patterns.

The DHW system in a dwelling is also an increasingly important component of retrofit assessment. The interaction between DHW provision and heat pump installation — particularly heat pump water heaters and air source heat pumps with DHW capability — is an area where EPC data will increasingly feed into retrofit design decisions. Getting the DHW section right is therefore important not just for the EPC but for downstream retrofit pathway accuracy.

This course covers the full DHW assessment workflow in RdSAP 10: cylinder classification (insulated vs uninsulated, jacket vs foam, thermostat), combi boiler DHW (instantaneous vs storage combi, keep-hot), immersion heater configurations, solar thermal interaction, heat pump DHW, and the evidence requirements for each input. We conclude with the specific audit failure patterns that affect DHW data.

---

## Section 1: Hot Water Cylinders — Classification, Insulation and Thermostat

The hot water cylinder is the central DHW assessment object for properties with a regular or system boiler, and for properties with immersion heater primary DHW. RdSAP 10 requires assessment of the cylinder volume, insulation type, insulation thickness, and the presence of a cylinder thermostat.

**Cylinder location and access.** Before assessing a cylinder, confirm it is the active DHW cylinder for the dwelling. In some properties (particularly converted or extended homes), there may be a redundant cylinder alongside the active one, or an active cylinder in an unexpected location (under-stair cupboard, bedroom built-in, garage). Always confirm the cylinder is connected to the primary hot water circuit.

**Insulated versus uninsulated cylinders.** The most fundamental classification is whether the cylinder has insulation. An uninsulated copper cylinder — found in pre-1970s housing where the hot water cupboard was designed to provide an element of space heating from standing losses — has high standing heat losses and attracts a severe energy penalty in RdSAP 10. An insulated cylinder reduces these standing losses substantially. The insulation type determines how well.

**Jacket insulation.** A cylindrical foam or mineral wool jacket, typically 80 mm thick when British Standard compliant (BS 5615), is the most common retro-fitted insulation type. In RdSAP 10, the jacket thickness must be recorded. The assessment options are typically: 25 mm, 38 mm, 50 mm, 80 mm (BS compliant), or 'thick' (equivalent to BS). A jacket that has slipped, is torn, or does not cover the crown of the cylinder is less effective and should be noted. For RdSAP 10 purposes, assess what you see — if the jacket clearly does not cover the top of the cylinder, the effective insulation is compromised.

**Factory foam insulation.** Modern cylinders manufactured since the mid-1990s are typically factory-insulated with rigid polyurethane (PU) foam, integrated into the cylinder outer casing. These cylinders are visually identifiable by their smooth outer surface (often white or off-white plastic outer jacket) and their significantly lower standing losses. In RdSAP 10, a factory foam-insulated cylinder is classified separately from a jacketed cylinder, and the standing losses assigned to it are substantially lower. The typical minimum foam insulation thickness for compliant modern cylinders is 35–50 mm, though this varies by manufacturer. The data plate on the cylinder should confirm the insulation specification.

**Cylinder volume.** The cylinder volume must be estimated or recorded. RdSAP 10 uses cylinder volume (in litres) to calculate stored DHW energy. The standard range for domestic cylinders is approximately 90–210 litres, with most single-dwelling cylinders between 120 and 180 litres. The cylinder data plate or manufacturer markings typically state the nominal volume. If the cylinder has no readable data plate, volume can be estimated from the external dimensions (height × cross-sectional area × approximately 0.85 to account for irregular internal geometry), but this is a fallback requiring justification in site notes.

**Cylinder thermostat.** A cylinder thermostat — typically a clip-on or strap thermostat mounted to the lower third of the cylinder body — controls the temperature at which the immersion element or boiler coil heats the stored water. Its presence reduces energy wastage from overheating the stored water. In RdSAP 10, the cylinder thermostat input directly affects calculated DHW efficiency. Its absence (which is common in older installations where cylinder temperature was controlled only by the boiler thermostat) attracts an efficiency penalty. Confirm presence visually and record whether it appears functional (wired in, not visibly disconnected).

---

## Section 2: Combi Boilers and Instantaneous DHW Systems

**Combi boiler DHW.** When a combi boiler is selected as the primary heating system, the DHW cylinder assessment is replaced by the combi's DHW performance parameters. The key decisions are: instantaneous combi versus storage combi, and whether a keep-hot function is present.

**Instantaneous combi.** An instantaneous combi boiler heats water on demand from the mains supply, with no stored hot water volume. It produces no standing losses but has a higher peak demand when hot water is drawn. In RdSAP 10, an instantaneous combi is assessed using the boiler's PCDB data (where listed) or the appropriate default efficiency parameters. The critical input is the combi boiler type confirmation in the heating section — selecting combi automatically routes the software to the appropriate DHW input screens.

**Storage combi.** A storage combi incorporates an internal hot water volume (typically 10–50 litres), pre-heated and maintained at temperature within the boiler casing. This provides faster initial hot water delivery than a fully instantaneous unit but introduces standing losses from the stored volume. In RdSAP 10, the storage volume and standing loss characteristics are captured (via PCDB data for listed models, or defaults for unlisted ones). Identifying a storage combi on site: the boiler casing is typically larger than an equivalent instantaneous combi, and the product label or installation manual will describe the internal store volume.

**Keep-hot function.** Some combi boilers include an electric keep-hot element that maintains a small volume of water at temperature between draws, improving the hot water draw experience. This element consumes electricity continuously when active. In RdSAP 10, the keep-hot function — if present and active — must be declared. Its standing electricity consumption adds to the assessed DHW energy use. Evidence: the keep-hot mode must be clearly available from the boiler controls panel (typically a dedicated button or setting), and the occupant's confirmation that it is active. If there is no keep-hot mode or it is disabled, do not enter it.

**Instantaneous electric water heaters.** Single-point (over-sink or under-sink electric water heaters) and multi-point instantaneous electric water heaters are a separate input category from immersion heaters. These are common in commercial-to-residential conversions and some older properties. They provide DHW on demand from an electric element without a cylinder. In RdSAP 10, instantaneous electric water heaters are assessed differently from cylinder-based immersion systems: their losses are primarily electrical draw on demand rather than standing cylinder losses.

---

## Section 3: Immersion Heaters — Primary and Secondary DHW

**Immersion heater as primary DHW.** On all-electric properties and some properties with gas boilers but no boiler coil to the cylinder, the immersion heater is the primary DHW heat source. An immersion heater is a resistive electrical element inserted into the cylinder through a boss (typically at the top, occasionally on the side), controlled by a thermostat. The cylinder is otherwise identical to a boiler-heated cylinder.

**Primary immersion — RdSAP 10 inputs.** For immersion heater primary DHW, the RdSAP 10 inputs are: cylinder volume, insulation type and thickness, cylinder thermostat present/absent, and whether the immersion is on standard or off-peak (Economy 7) tariff. The tariff input is critical: an immersion heater on Economy 7 tariff uses cheap-rate electricity to heat the cylinder overnight, reducing fuel cost significantly compared with standard-rate operation. As with storage heaters, Economy 7 must be confirmed at the meter.

**Primary immersion without a thermostat.** A cylinder immersion heater operated without a cylinder thermostat (controlled only by a manual switch or timer without a temperature set-point) has higher energy wastage due to overheating and cycling. This configuration is identified on site by the absence of a cylinder thermostat clip-on unit. The RdSAP 10 input for "no cylinder thermostat" applies the appropriate efficiency penalty.

**Immersion heater as secondary DHW.** On most properties with a boiler-heated cylinder, a secondary immersion heater is present as a backup or for summer use (when the boiler is not running). In RdSAP 10, the secondary immersion heater is an input that may or may not be entered depending on its usage. The convention: if there is a secondary immersion present but it is clearly not in use as a regular supplement (no timer on it, occupant confirms it is emergency only), it does not need to be entered as a secondary DHW system. If it has a dedicated timer or is clearly regularly used, it should be entered.

**Dual immersion heaters.** Some older cylinders have two immersion elements: a long element heating the full cylinder volume and a short upper element heating only the top portion of the cylinder for small-draw situations. The presence of dual elements does not change the RdSAP 10 assessment significantly — record the cylinder and insulation characteristics as for any cylinder installation.

**Heat pump DHW.** Air source heat pump installations increasingly incorporate DHW heating, either via a dedicated heat pump water heater (HPWH — a standalone cylinder with an integrated heat pump) or via the space heating heat pump with a hot water cylinder coil. In RdSAP 10, heat pump DHW is assessed using the PCDB data for the specific system where available, or the relevant default COP (coefficient of performance) and stored energy parameters. This is a growing area as retrofit heat pump installations become more common and the EPC data for these properties must accurately reflect the DHW source.

---

## Section 4: Solar Thermal Interaction and Common DHW Audit Failures

**Solar thermal in RdSAP 10.** Solar thermal collectors — roof-mounted panels that heat water using solar energy, typically supplementing a gas boiler or immersion cylinder — are a specific DHW input in RdSAP 10. The methodology models the solar contribution based on collector area, orientation, tilt, overshading, and collector type (evacuated tube or flat plate).

The RdSAP 10 solar thermal input requires: collector type, aperture area (m²), orientation, tilt, overshading level, and the presence of a dedicated solar cylinder or combined cylinder with solar coil. The aperture area is the active collector area (not the total panel size including frame). For flat plate collectors, aperture area is typically 85–95% of overall panel dimensions; for evacuated tube collectors, it is the total cross-sectional area of the tubes. The data plate or installation certificate should state the aperture area.

**Evidence for solar thermal claims.** Claiming a solar thermal contribution requires evidence that the system is operational. An MCS (Microgeneration Certification Scheme) installation certificate is the primary evidence for post-2010 installations. For older systems, a commissioning record or an installation invoice stating the collector specification. A solar thermal system that is visually present but clearly decommissioned (disconnected pipes, empty or leaking header tank, inoperative pump) should not be entered as a functioning system.

**Common DHW audit failures (scheme auditor data, 2024–2025):**

1. Cylinder insulation overstated — a heavily compressed or partially displaced jacket entered as a full 80 mm BS-compliant jacket.

2. Factory foam cylinder not distinguished from jacketed cylinder — the standing loss defaults are very different; misclassifying a foam-insulated cylinder as a jacket cylinder understates performance.

3. Cylinder thermostat absent but entered as present — one of the most common single-field errors in the DHW section.

4. Combi keep-hot entered without evidence — keep-hot function credited when the boiler has no such facility, or when the occupant has never enabled it.

5. Solar thermal aperture area overstated — total panel area (including frame) used instead of aperture area, overstating the solar contribution.

6. Immersion on standard rate entered as Economy 7 — the reverse of the storage heater tariff error, but equally common; always confirm at the meter.

**Evidence retention for DHW.** Photograph the cylinder (including the data plate where readable), the jacket or outer casing, the cylinder thermostat (or confirm its absence), the immersion element boss and any timer, and — for solar — the collector array and any visible MCS or commissioning documentation. For combi boilers, the photograph of the boiler data plate (already required for heating) also supports the DHW assessment.

---

## Key Takeaways

- Factory foam-insulated cylinders have substantially lower standing losses than jacket-insulated cylinders; the two must not be confused — inspect the cylinder casing carefully and check the data plate.
- Cylinder thermostat presence or absence must be confirmed visually; it is one of the most-failed individual DHW fields on audit.
- For combi boilers, the keep-hot function adds to assessed DHW energy only when it is present on the boiler, enabled, and actively used.
- Immersion heater tariff (standard vs Economy 7) must be confirmed at the electricity meter, not assumed from the presence of a timer or the occupant's belief.
- Solar thermal input requires aperture area (not total panel area), confirmed orientation and tilt, and evidence of an operational installation — an MCS certificate is the primary evidence.
- Heat pump DHW systems require PCDB lookup or applicable default COP; they should not be assessed as immersion heater systems.
- The DHW section accounts for 20–30% of total assessed energy — systematic errors here have a material impact on the EPC rating, not just a minor rounding issue.

---

## Self-Assessment Questions

**Q1.** A 1960s property has a copper hot water cylinder in the airing cupboard with no visible insulation — bare metal exterior, clearly no jacket. What is the correct RdSAP 10 input?

A) Factory foam-insulated cylinder — all modern cylinders are foam-insulated
B) Uninsulated cylinder
C) Jacket-insulated cylinder at 25 mm (minimum default)
D) Cylinder with no standing losses — the airing cupboard provides thermal mass

**Correct answer: B**
*A bare copper cylinder with no jacket or foam insulation is an uninsulated cylinder. This is the highest-loss category and the RdSAP 10 default standing loss for an uninsulated cylinder applies. It should not be entered as a jacketed cylinder simply to avoid the energy penalty.*

---

**Q2.** A combi boiler is found to have a keep-hot button on its controls panel. The occupant states they always have it switched on. How should this be entered in RdSAP 10?

A) Do not enter keep-hot — the occupant's statement is not sufficient evidence
B) Enter keep-hot as active — the occupant's confirmation, combined with the presence of the function, is sufficient
C) Enter keep-hot only if an MCS certificate for the boiler is available
D) Enter the boiler as a storage combi instead

**Correct answer: B**
*The presence of the keep-hot function on the boiler controls panel combined with the occupant's confirmation that it is active is sufficient to enter it in RdSAP 10. The occupant's confirmation of actively used features is an acceptable evidence basis; what the assessor must not do is credit keep-hot in the absence of the physical function on the boiler.*

---

**Q3.** A flat plate solar thermal system is installed on a south-facing roof at approximately 35° tilt. The installation certificate states a gross collector area of 4.0 m² and an aperture area of 3.6 m². What area should be entered in RdSAP 10?

A) 4.0 m² — the total panel area
B) 3.6 m² — the aperture area as stated on the installation certificate
C) 2.0 m² — a 50% deduction for shading must always be applied
D) 3.0 m² — an average between gross and aperture area

**Correct answer: B**
*RdSAP 10 requires aperture area (the active collector area), not gross or overall panel area. The installation certificate value of 3.6 m² is the correct input. No blanket shading deduction is applied — overshading is a separate input based on the assessed level from site observation.*

---

**Q4.** A property has a gas boiler-heated hot water cylinder. The cylinder has a factory foam outer casing (smooth white plastic jacket, no retrofitted insulation wrap). It has a cylinder thermostat. How should this be entered in RdSAP 10?

A) Jacket-insulated cylinder at 80 mm (BS standard) — foam and jacket have equivalent performance
B) Factory foam-insulated cylinder with cylinder thermostat present
C) Uninsulated cylinder — factory foam is not recognised in RdSAP 10
D) No cylinder input is required because the boiler is a regular boiler

**Correct answer: B**
*A factory foam-insulated cylinder is a specific input category in RdSAP 10 with lower standing losses than a jacketed cylinder. It must be selected correctly to avoid understating the cylinder's thermal performance. The cylinder thermostat present/absent input is separate and must also be recorded.*

---

**Q5.** An immersion heater is the sole DHW source on an all-electric property. The occupant believes they are on Economy 7. The electricity meter is a single-register smart meter showing one tariff. What should the assessor enter?

A) Economy 7 — the occupant's belief is sufficient
B) Standard rate electricity — the single-register meter confirms no off-peak supply is active
C) Economy 10 as a conservative alternative to Economy 7
D) The assessor should defer and ask the supplier before lodging

**Correct answer: B**
*A single-register meter confirms standard rate supply regardless of the occupant's belief. Economy 7 must be confirmed by a two-register meter or equivalent off-peak supply evidence. The occupant may believe they are on Economy 7 because storage heaters were originally installed with that tariff, but subsequent meter replacement may have changed the supply.*

---

## Further Reading

- **RdSAP 10 Specification Document** — Department for Energy Security and Net Zero (DESNZ) / BRE. DHW system tables and solar thermal methodology. Available at: [https://www.bregroup.com/sap/](https://www.bregroup.com/sap/)

- **SAP 10.2: The Government's Standard Assessment Procedure** — DESNZ. Hot water cylinder default data and solar thermal calculation methodology. Available at: [https://www.gov.uk/guidance/standard-assessment-procedure](https://www.gov.uk/guidance/standard-assessment-procedure)

- **MCS (Microgeneration Certification Scheme) — Solar Thermal Installation Standards** — MCS 001 and MCS 024. Available at: [https://mcscertified.com/](https://mcscertified.com/)

- **British Standards Institution — BS 1566: Copper Indirect Cylinders** and **BS 3198: Combination Hot Water Storage Units** — Standards governing cylinder manufacture. Available via BSI Shop: [https://www.bsigroup.com/](https://www.bsigroup.com/)

- **Product Characteristics Database (PCDB)** — BRE. Combi boiler and hot water system data. Available at: [https://www.ncm-pcdb.org.uk/](https://www.ncm-pcdb.org.uk/)

---

*© Meridian CPD 2026. All rights reserved. Unauthorised reproduction prohibited.*
*This course material is licensed to individual subscribers only.*
