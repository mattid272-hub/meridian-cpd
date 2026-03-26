# Heating Systems Primary: Boilers, Controls and Data Entry in RdSAP 10
**Course ID:** MER-DEA-005 | **CPD Hours:** 1.0 | **Published:** March 2026
*© Meridian CPD 2026. All rights reserved.*

---

## Learning Objectives

- Correctly classify boiler types (combi, regular, system) and assign appropriate efficiency values in RdSAP 10, distinguishing between manufacturer data, PCDB defaults and age-band defaults.
- Apply the RdSAP 10 controls hierarchy accurately, understanding how TRVs, programmers, room thermostats, weather compensation and load compensation each affect the heating efficiency multiplier.
- Identify the data entry conventions for fuel type, flue type, and boiler age that influence the RdSAP 10 calculation outcome.
- Recognise the top audit failure categories for primary heating data and apply the evidence standards required to defend a lodged EPC.

---

## Introduction

Boilers remain the primary heating system in the overwhelming majority of dwellings assessed in England and Wales. Gas-fired central heating, with a range of boiler configurations and control arrangements, dominates the housing stock from the 1960s through to the present. Despite this familiarity, heating system data entry generates a disproportionate share of EPC audit failures — not because assessors do not know what a boiler is, but because the RdSAP 10 input conventions are more nuanced than they appear, the controls hierarchy is frequently misapplied, and the interaction between efficiency data sources is poorly understood.

RdSAP 10 introduced meaningful changes to how heating system efficiency is determined and how controls are entered. The Product Characteristics Database (PCDB) is now the primary efficiency source for qualifying products, and its use is not optional where a product is listed. The controls multiplier — the factor applied to the base efficiency to reflect how well the system is controlled — has been restructured, with clearer differentiation between control types and more material consequences for getting the hierarchy wrong.

This course works through the complete heating data entry workflow for gas, oil, and LPG boilers: boiler classification, efficiency determination (PCDB versus default), flue type, fuel type, age, and the controls hierarchy in full. It addresses the specific data entry conventions that trip up experienced assessors and the evidence standards required to defend each input. The goal is not theoretical knowledge of SAP methodology — you have that. The goal is accurate, audit-ready data entry every time.

---

## Section 1: Boiler Classification — Combi, Regular and System Boilers in RdSAP 10

The first input decision for any gas, oil, or LPG central heating system is boiler type. RdSAP 10 recognises three principal configurations, and the classification affects not only efficiency defaults but also how hot water provision is treated in the overall dwelling assessment.

**Combination (combi) boilers** heat space and provide domestic hot water on demand from a single unit, with no stored hot water cylinder. In RdSAP 10, selecting a combi boiler eliminates the need for a separate DHW cylinder input — the hot water section of the assessment is handled through the combi's hot water performance parameters (instantaneous or storage combi, keep-hot function, standby losses). The key classification decision for combis is whether they are truly instantaneous or whether they incorporate an internal stored hot water volume (typically 10–50 litres). This distinction matters: storage combis have different standby loss profiles to instantaneous units. If the boiler model is in the PCDB, the software will pull the correct parameters automatically; if not, the assessor must determine the configuration from the boiler data plate or installation manual.

**Regular (open-flued or room-sealed heat-only) boilers** supply heat to the central heating circuit and, via a coil, to a separate hot water cylinder. They require a feed and expansion cistern in the loft and a hot water cylinder elsewhere in the property. The cylinder must be assessed separately as part of the DHW system input. Under RdSAP 10, the regular boiler classification triggers the cylinder assessment workflow. Confusingly, older boilers are sometimes labelled as "conventional" or "traditional" boilers rather than "regular" — the classification should be based on the system configuration, not the label.

**System boilers** supply heat to a sealed central heating circuit and incorporate a separate hot water cylinder. Unlike regular boilers, they do not require a separate feed and expansion cistern. System boilers are common in post-2000 gas-fired installations. The distinction from a regular boiler matters principally because of the sealed versus vented system designation, which affects certain efficiency assumptions in the calculation.

**Back boilers** — gas boilers installed behind a fire grate, common in 1960s–1980s housing — are a separate classification in RdSAP 10. Their efficiency defaults are significantly lower than modern boilers and their treatment in the PCDB is limited because most are no longer manufactured. If you encounter a back boiler, the age-band default efficiency applies unless a PCDB listing exists.

**Oil and LPG boilers** follow the same classification framework but use different fuel type inputs. The key practical distinction is that oil boilers almost always have a flue through the external wall (balanced flue or open flue to a conventional flue) rather than through the roof. LPG boilers behave identically to gas boilers in RdSAP 10 terms — the fuel input is changed, not the boiler classification or control hierarchy.

---

## Section 2: Efficiency Values — PCDB, Manufacturer Data and Age-Band Defaults

The efficiency value assigned to a boiler in RdSAP 10 is the most consequential single data entry decision for the heating system assessment. It drives the primary energy demand calculation for space heating and, for regular and system boilers, interacts with the DHW cylinder losses.

**The PCDB hierarchy.** RdSAP 10 mandates use of the Product Characteristics Database where a boiler model is listed. The PCDB is maintained by BRE and contains seasonal efficiency data (SEDBUK — Seasonal Efficiency of Domestic Boilers in the UK, now expressed as SAP efficiency) for gas, oil, and LPG boilers tested under standardised conditions. Assessors should search for the boiler model by brand and model number using the boiler registration number from the data plate. Where the exact model is found, the PCDB value is used directly; where only a family entry exists, the family default applies. Using an age-band default when a PCDB listing exists is a methodology failure and a common audit finding.

**PCDB search practice.** The data plate on a boiler — typically inside the casing, behind the front panel — contains the model number, GC number (for gas appliances), and installation year. These are the search terms for PCDB lookup. The GC number (Gas Council number) is the most reliable identifier for older gas boilers. For very old boilers (pre-1990), PCDB listings may not exist; for these, the age-band default is applied.

**Age-band defaults.** Where no PCDB listing is available, RdSAP 10 applies efficiency defaults by fuel type and age band. The age band is determined by the installation date if known, or estimated from the boiler model era if the exact date cannot be established. Current age-band defaults for gas boilers range from approximately 70% seasonal efficiency for pre-1979 boilers to 89–90% for post-2005 condensing boilers. Non-condensing gas boilers installed post-2005 are rare (Building Regulations required condensing from 2005) but do exist as replacement units in heritage properties with planning restrictions. Oil boiler defaults follow similar bands with slightly lower efficiency values at older age bands.

**Condensing versus non-condensing.** RdSAP 10 requires explicit identification of whether a boiler is condensing or non-condensing. A condensing boiler has a visible plastic (typically white or grey) flue pipe exhausting at low level, often near the base of an external wall, and a condensate drain pipe. The flue exhaust temperature is low enough to condense water vapour, which is a visual indicator. A non-condensing boiler will have a metal flue pipe exhausting at high level or via a chimney. Misclassifying a non-condensing boiler as condensing assigns it an erroneously high efficiency and is a hard audit fail.

**Manufacturer-declared efficiency.** Where a boiler is not listed in the PCDB but manufacturer documentation is available giving a SEDBUK or seasonal efficiency figure, this may be used subject to scheme-specific rules. The documentation must be retained. Most scheme guidance requires the figure to be a certified SEDBUK value, not a marketing efficiency claim. Net and gross efficiency distinctions also apply — RdSAP 10 uses gross efficiency for gas and oil; manufacturer data expressed on a net basis must be converted using the appropriate calorific value ratio (approximately ÷ 1.11 for gas).

---

## Section 3: Controls Hierarchy — TRVs, Programmers, Room Stats, Weather and Load Compensation

The controls multiplier in RdSAP 10 adjusts the effective efficiency of the heating system to reflect the quality of system control. A well-controlled system wastes less energy because it delivers heat more precisely — reducing overheating, cycling losses, and unnecessary operation. RdSAP 10 uses a structured controls hierarchy with defined efficiency multipliers for each combination of control types.

**The basic control suite.** The RdSAP 10 controls matrix is built around four primary control types: time control (programmer or time switch), temperature control (room thermostat), zone control (thermostatic radiator valves or separate zone controls), and enhanced control (weather compensation, load compensation). The multiplier applied to the boiler efficiency reflects the combination present.

**Programmer or time switch.** A basic time switch provides on/off control with no temperature modulation. A full programmer provides separate time control for heating and hot water. The distinction matters in RdSAP 10: a full programmer (separate timing for CH and DHW) attracts a better multiplier than a basic time switch. On-site, the difference is visible: a programmer with two channel controls (two rocker switches or two sets of time segments) is a full programmer. A single-channel time switch is not.

**Room thermostat.** A fixed room thermostat provides a set-point temperature for the whole dwelling. Its presence is required for the standard multiplier for a room thermostat-controlled system. The thermostat must be functional — a broken or disconnected thermostat does not count. The location matters for audit purposes: a thermostat buried behind furniture or in an unheated hallway may be present but functionally compromised. Record what you see; the methodology does not require you to verify function beyond visual inspection.

**Thermostatic radiator valves (TRVs).** TRVs on radiators provide room-by-room temperature control in addition to the whole-house room thermostat. RdSAP 10 requires TRVs on all or most radiators (typically defined as at least 50% of radiators in heated rooms) to qualify for the TRV multiplier benefit. One radiator in the dwelling must be left without a TRV (typically the one in the room containing the thermostat — this is a heating best-practice requirement to ensure the thermostat circuit remains open). If all radiators have TRVs with no bypass arrangement, this is a controls deficiency, but it does not change the RdSAP classification. TRVs present only on some radiators do not qualify for the full multiplier.

**Programmer + room stat + TRVs.** This combination — the standard for a reasonably well-controlled gas central heating system — gives the best multiplier available without enhanced controls. It represents the majority of post-2000 domestic installations.

**Weather compensation.** A weather compensation controller modulates boiler flow temperature based on external air temperature — lowering output temperature in mild weather and increasing it in cold weather. This significantly reduces cycling losses and is particularly beneficial for condensing boilers (which operate more efficiently at lower flow temperatures). Weather compensation requires a weather sensor and a compatible boiler. Its presence in the controls input in RdSAP 10 attracts a meaningful additional multiplier. Evidence: a weather sensor visible on an external wall, wired to the boiler or controller.

**Load compensation.** Load compensation modulates boiler output based on the difference between set-point and actual room temperature. It is similar in effect to weather compensation but uses internal signals rather than external temperature. Less common in practice. The same evidential standard applies.

**Smart and connected controls.** Smart thermostats (Nest, Hive, Honeywell Evohome, Drayton Wiser etc.) introduce complexity. RdSAP 10 guidance does not have a dedicated "smart thermostat" classification; instead, these systems are classified based on what control functions they actually provide. A smart thermostat providing time and temperature control with load compensation logic qualifies for the load compensation multiplier; one providing basic time and temperature control is classified as programmer + room thermostat. Assessors should record the functionality present, not the product brand.

---

## Section 4: Flue Type, Fuel Type, and Common Audit Failures

Beyond boiler type and efficiency, RdSAP 10 requires correct entry of flue configuration and fuel type. These inputs influence combustion efficiency assumptions and interact with the controls and building fabric data.

**Flue type.** RdSAP 10 recognises four main flue types: open flue (conventional chimney or flue liner), balanced flue (room-sealed with air supply and exhaust via a co-axial or twin-pipe arrangement through the external wall or roof), open-flued with a draught diverter, and fan-assisted flue (most modern boilers). The flue type affects thermal performance because an open flue draws air from the heated space for combustion, increasing ventilation heat loss. A balanced flue (room-sealed) uses external air only. Modern fan-assisted balanced flue boilers represent the vast majority of post-1990 gas installations and are the default classification for any boiler with a plastic horizontal flue through an external wall.

**Identifying flue type on site.** The distinguishing features: a metal flue liner in a chimney = open flue; a co-axial pipe (pipe within a pipe) through the wall = balanced flue; a single plastic pipe through the wall at low level = fan-assisted balanced flue. For older back boilers with a conventional chimney flue, the open-flue classification applies and its efficiency penalties are built into the age-band default.

**Fuel type.** Gas, oil, and LPG are the three fossil fuel inputs. Mains gas uses the OFGEM/SAP standard calorific value. Oil defaults to standard heating oil (kerosene/28-second oil for domestic use). LPG covers both bulk tank and bottled supplies — the distinction does not change the RdSAP calculation outcome. Bottled gas (butane or propane cylinders with no fixed distribution pipework) is a separate fuel category in RdSAP 10. Dual-fuel systems (e.g., gas boiler with electric immersion backup) require both heating and DHW fuel inputs to be captured correctly.

**Top audit failure categories for primary heating data (scheme auditor data, 2024–2025):**

1. PCDB not consulted — age-band default applied where a PCDB listing exists for the boiler model. This is the single most common heating-related audit finding across multiple scheme bulletins.

2. Boiler type misclassified — regular boiler entered as system boiler (or vice versa), leading to incorrect cylinder assessment in DHW section.

3. Controls over-credited — programmer + TRVs entered without a functioning room thermostat (e.g., room stat missing, unplugged, or clearly non-functional).

4. Non-condensing boiler classified as condensing — usually resulting from unfamiliarity with flue identification. If the flue is metal and exits via the roof or chimney, it is almost certainly non-condensing.

5. Fuel type wrong — LPG boilers entered as mains gas (a common error on rural properties where mains gas is assumed). Always confirm mains supply at the meter: a regulator cabinet or LPG tank on the property indicates off-grid supply.

6. Controls data inconsistent with photographs — site photographs show TRVs absent or room thermostat not visible, but controls data claims programmer + room stat + TRVs.

**Evidence retention for heating data.** Photograph the data plate, the flue terminal, the controls panel (programmer/thermostat), and a representative radiator for TRV presence. Note the boiler model number and GC number in site records. If PCDB was consulted, retain a screenshot or record the database entry used. This evidence pack is the defence against audit queries.

---

## Key Takeaways

- Combi, regular, and system boilers each trigger different assessment workflows in RdSAP 10; correct classification is the foundation of accurate heating data entry.
- The PCDB must be consulted for every boiler — age-band defaults apply only where no PCDB listing exists; bypassing PCDB when a listing is available is a methodology failure.
- Condensing versus non-condensing classification is determined by flue type and exit temperature, not by boiler age alone; misclassification is the most consequential single efficiency error.
- The controls hierarchy (time + temperature + zone + enhanced) must be assessed against what is actually present and functional on site; over-crediting controls is a persistent audit failure.
- Weather compensation and load compensation attract meaningful multiplier benefits but require hardware evidence (external sensor, compatible controller); do not credit these without photographic evidence.
- Fuel type must be verified at the meter or supply — do not assume mains gas without confirming the supply method, particularly on rural properties.
- Evidence retention for heating data should include: data plate photograph, GC/model number recorded, flue terminal photograph, controls panel photograph, TRV presence on radiators.

---

## Self-Assessment Questions

**Q1.** A 2008 gas boiler is found on site. The data plate shows a model number. What is the correct first step for determining the efficiency value to enter in RdSAP 10?

A) Apply the post-2005 condensing boiler age-band default (approximately 89–90%)
B) Search the PCDB using the model number or GC number from the data plate
C) Ask the occupant for the installation manual
D) Apply the ErP regulation minimum efficiency for that installation year

**Correct answer: B**
*RdSAP 10 mandates PCDB consultation where a listing may exist. Age-band defaults are a fallback only when the PCDB confirms no listing. The post-2005 age-band default should never be applied without first checking the PCDB.*

---

**Q2.** An assessor identifies a boiler with a white plastic horizontal pipe exiting through an external wall at low level, with a visible condensate drain pipe running to a nearby drain. How should the boiler be classified?

A) Open flue, non-condensing
B) Balanced flue, non-condensing
C) Fan-assisted balanced flue, condensing
D) Open flue, condensing

**Correct answer: C**
*A plastic horizontal flue through an external wall indicates a fan-assisted balanced flue (room-sealed). The visible condensate drain confirms condensing operation. This combination is standard for modern domestic gas boilers installed post-2005.*

---

**Q3.** A dwelling has a full programmer (separate time channels for CH and DHW), a room thermostat in the hallway, and TRVs on all radiators including the one in the room containing the thermostat. What is the correct assessment of this controls arrangement for RdSAP 10 purposes?

A) Full controls credit — programmer + room stat + TRVs with full multiplier
B) Reduced controls credit — TRV on thermostat radiator is a minor deficiency but does not affect RdSAP 10 classification
C) No controls credit — the absence of a free radiator bypasses the thermostat circuit, invalidating the entire controls credit
D) Weather compensation credit applies automatically

**Correct answer: B**
*The TRV on the thermostat radiator is a heating best-practice issue but does not change the RdSAP 10 controls classification. The assessor records the controls present (programmer + room stat + TRVs) and applies the corresponding multiplier. The best-practice advisory may be noted in the recommendations, but it does not invalidate the classification.*

---

**Q4.** What is the defining visual difference between a regular boiler and a system boiler installation?

A) Regular boilers are always older than system boilers
B) Regular boilers require a feed and expansion cistern in the loft; system boilers use a sealed pressurised circuit without one
C) System boilers always have weather compensation fitted
D) Regular boilers use LPG; system boilers use mains gas only

**Correct answer: B**
*The presence of a feed and expansion cistern (typically a small rectangular tank in the loft connected to the boiler circuit) is the diagnostic indicator of a regular (vented) boiler installation. System boilers use a sealed pressurised circuit with a pressure gauge and filling loop but no cistern.*

---

**Q5.** A Nest Learning Thermostat is installed, connected to a gas boiler. The system has no separate TRVs and no weather sensor. How should this be classified in RdSAP 10?

A) Weather compensation, because the Nest uses predictive algorithms
B) Load compensation + programmer, because the Nest adjusts based on room temperature and time scheduling
C) Room thermostat + programmer equivalent, with load compensation if the Nest's load compensation mode is active and documented
D) No controls credit — smart thermostats are not recognised in RdSAP 10

**Correct answer: C**
*Smart thermostats are classified by the functions they perform, not by brand. A Nest providing time programming and temperature set-point equates to programmer + room thermostat. If the Nest's load compensation mode (Home/Away adjustment, True Radiant learning) is documented as active, load compensation credit may apply. Weather compensation requires a physical external sensor — algorithmic weather response does not qualify.*

---

## Further Reading

- **RdSAP 10 Specification Document** — Department for Energy Security and Net Zero (DESNZ) / BRE. Available at: [https://www.bregroup.com/sap/](https://www.bregroup.com/sap/)

- **Product Characteristics Database (PCDB)** — BRE. Boiler efficiency lookup tool. Available at: [https://www.ncm-pcdb.org.uk/](https://www.ncm-pcdb.org.uk/)

- **SEDBUK Database and Boiler Efficiency Database** — Boiler efficiency ratings for gas and oil appliances. Available at: [https://www.boilers.org.uk/](https://www.boilers.org.uk/)

- **SAP 10.2: The Government's Standard Assessment Procedure** — DESNZ. Full methodology document including controls tables. Available at: [https://www.gov.uk/guidance/standard-assessment-procedure](https://www.gov.uk/guidance/standard-assessment-procedure)

- **Elmhurst Energy Auditor Technical Bulletins** — Scheme-specific guidance on heating data entry and common audit failures. Available via Elmhurst member portal: [https://www.elmhurstenergy.co.uk/](https://www.elmhurstenergy.co.uk/)

---

*© Meridian CPD 2026. All rights reserved. Unauthorised reproduction prohibited.*
*This course material is licensed to individual subscribers only.*
