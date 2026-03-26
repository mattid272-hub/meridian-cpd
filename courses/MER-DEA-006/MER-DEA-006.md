# Heating Systems Secondary: Storage Heaters, Direct Electric and Room Heaters in RdSAP 10
**Course ID:** MER-DEA-006 | **CPD Hours:** 1.0 | **Published:** March 2026
*© Meridian CPD 2026. All rights reserved.*

---

## Learning Objectives

- Correctly classify and distinguish high heat retention storage heaters from standard (older) storage heaters in RdSAP 10, understanding why the distinction is material to the calculation.
- Apply the correct RdSAP 10 input conventions for direct electric heating, electric panel heaters, and portable electric room heaters.
- Accurately assess and record mixed heating systems where a primary system is supplemented by secondary electric heating in different rooms.
- Identify the efficiency defaults, input parameters, and evidence requirements for electric heating systems in RdSAP 10.
- Recognise the most common audit failure points for electric heating assessments.

---

## Introduction

Properties heated primarily or partially by electric systems represent a significant and often underestimated challenge for DEAs. While gas-fired central heating dominates the overall housing stock, electric heating — in its various forms — is prevalent in a distinct subset of properties: purpose-built flats, local authority and housing association stock from the 1960s–1980s, rural properties without gas access, and an increasing number of retrofit cases where heat pumps interact with or replace older electric systems.

Getting electric heating data entry right matters more in RdSAP 10 than it did in previous iterations of the methodology. The updated treatment of storage heater types — particularly the introduction of more nuanced differentiation between high heat retention storage heaters and older standard designs — means that classification errors have a larger impact on calculated energy performance than before. Simultaneously, the carbon intensity of grid electricity (now lower than in previous SAP editions, reflecting decarbonisation) changes the relative performance of electric heating in the EPC rating in ways that may surprise assessors who have not reviewed the updated methodology.

This course covers the full range of electric primary and secondary heating types in RdSAP 10: storage heaters (old and new), direct electric (panel heaters, convectors, radiant heaters), room heaters (electric fire, fan heater), and the treatment of mixed systems where electric provides secondary heating in rooms not served by the primary system. For each, we address the classification criteria, RdSAP 10 input conventions, applicable defaults, and the evidence that distinguishes a defensible assessment from an auditable failure.

---

## Section 1: Storage Heaters — Standard vs High Heat Retention

Storage heaters are the defining electric heating type for pre-1990 non-gas housing stock, and their correct classification in RdSAP 10 is one of the more consequential judgements an assessor makes on an all-electric property.

**The fundamental distinction.** RdSAP 10 recognises two principal categories of storage heater: old (standard/manual) storage heaters and high heat retention (HHR) storage heaters. The distinction is not merely aesthetic — it reflects substantially different thermal performance characteristics that have a material impact on the calculated space heating energy demand.

Standard storage heaters — the type found in the vast majority of older all-electric properties — use relatively simple resistive elements to charge overnight on cheap-rate electricity, with manual or basic automatic controls for heat release during the day. Their heat retention is poor: they release a significant proportion of stored heat regardless of demand, leading to overheating in mild weather and being discharged too early on cold days. In RdSAP 10, these are assigned an efficiency value (as a responsiveness and heat retention factor) that reflects this poor controllability.

High heat retention storage heaters — modern units typically installed under the HHRS (High Heat Retention Storage Heater) or equivalent scheme, and more recently under ECO4 — use improved insulation cores and electronic controls to retain heat more effectively and release it on demand. They typically incorporate fan-assisted output, room thermostats, and seven-day programmers. Their performance in RdSAP 10 is substantially better, reflecting their superior controllability.

**Classification criteria.** The key on-site distinguishing features:

- *Age:* Standard storage heaters dominate pre-1990 installations; HHR heaters are generally post-2010 products, though the category does not have a fixed installation year threshold in RdSAP 10.
- *Physical characteristics:* HHR heaters are typically slimmer in profile, have a digital display or electronic controls panel, and often include a fan outlet grille. Standard heaters are bulkier, heavier (due to dense storage core), and have simpler manual controls.
- *Controls:* An input dial (input/boost) and an output dial (room temperature or vent position) are characteristic of older standard heaters. An electronic programmer with temperature set-point and boost function indicates HHR.
- *Product label:* Manufacturers such as Dimplex, Elnur, and Electrorad produce HHR heaters under product names that include the HHR designation. The product label or specification plate should confirm the category.

**PCDB for storage heaters.** The PCDB includes entries for some storage heater models, particularly newer HHR units. Where a PCDB listing exists, use it. Where the heater is too old or obscure for PCDB listing, the age-band default for the appropriate category applies.

**Fan-assisted storage heaters.** Fan-assisted storage heaters (which use a fan to draw air over the storage core for on-demand output) are a sub-category that predates the HHR classification. Some older fan-assisted heaters exist from the 1990s and early 2000s. These are generally classified as fan-assisted storage heaters (not HHR) in RdSAP 10 unless they specifically meet the HHR specification.

---

## Section 2: Direct Electric Heating — Panel Heaters, Convectors and Radiant Systems

Direct electric heating converts electrical energy to heat in real time with no storage element. It is a simpler assessment category than storage heaters but still requires careful classification of the type and configuration.

**Panel heaters and electric convectors.** Slimline electric panel heaters — wall-mounted units that heat via convection — are common in modern flats and in rooms supplementary to a primary system. They typically incorporate a simple thermostat and sometimes a timer. In RdSAP 10, these are entered as direct electric heating with 100% efficiency (all electrical energy is converted to heat in the conditioned space — there are no flue or distribution losses). The assessment task is determining whether they are the primary system or a secondary/supplementary system.

**Radiant electric heaters.** Radiant heaters (infrared panels, electric bar heaters, ceiling radiant panels) convert electricity to radiant heat. Their RdSAP 10 treatment is the same as panel convectors — 100% efficiency — but the responsiveness factor differs. Radiant heaters are highly responsive (immediate heat output); convectors slightly less so. RdSAP 10 uses responsiveness as a factor in the controls multiplier for electric heating systems.

**Underfloor electric heating.** Electric underfloor heating (resistive element in the floor build-up) is common in bathrooms and occasionally as primary heating in newer or renovated flats. In RdSAP 10, it is classified as electric underfloor — a specific input category. It is assessed at 100% efficiency with a responsiveness factor reflecting the thermal mass of the floor construction (slower to respond than panel heaters, faster than storage heaters). The key data entry decision is whether the underfloor element runs on standard or off-peak (Economy 7 or Economy 10) tariff — this affects the fuel cost calculation.

**Ceiling heating.** Electric ceiling heating elements (resistive cables or mats in the ceiling structure) are a rarer configuration but still encountered in commercial-to-residential conversions and some post-war social housing. Classification follows the same logic as underfloor electric: 100% efficiency, with responsiveness reflecting the thermal mass of the ceiling construction.

**Evidence requirements.** For direct electric heating, the key evidence is confirmation of the system type (panel, radiant, underfloor, ceiling), the tariff (standard rate or off-peak), and whether the system serves the whole dwelling or only specific rooms. Photograph the heaters and any visible thermostat or control panel. For underfloor heating, photograph the thermostat and confirm whether it serves the whole ground floor or specific rooms only.

---

## Section 3: Room Heaters, Portable Appliances and Mixed Systems

**Room heaters.** RdSAP 10 includes an input category for electric room heaters — standalone units not permanently installed. This category covers electric fires (mock fireplace units with electric elements), portable fan heaters, and similar appliances. Room heaters are characterised by their portability and lack of permanent installation, though some are semi-permanent. Their efficiency in RdSAP 10 is the same as direct electric (100% conversion), but their controls characteristics differ — they are typically poorly controlled (no programmer, no room thermostat except a basic safety stat).

**The primary/secondary distinction in mixed systems.** Many dwellings have a primary central heating system that does not serve all rooms — most commonly, a gas boiler serving the main living rooms and bedrooms, with electric heating (storage or panel) in a converted loft, a rear extension, or a conservatory. In RdSAP 10, these are assessed as mixed systems: one primary system and, where appropriate, a secondary system for the rooms not served.

The input convention is: the primary system is the one that heats the main habitable rooms (living room, main bedrooms). Secondary heating covers rooms outside the primary system's distribution. If a room is accessible from the primary system's pipework but has no radiator, it is treated as unheated, not as a secondary heated room.

**Percentage of heat from secondary system.** RdSAP 10 requires the assessor to estimate the percentage of heat provided by the secondary system. This is one of the more subjective inputs in the assessment. The convention is to estimate based on the floor area served by secondary heating as a proportion of the total heated floor area. Scheme guidance typically advises a maximum of 10–15% secondary heating for a single room in an extension, rising to 30%+ where a significant proportion of the dwelling has no primary heating.

**All-electric with two systems.** In properties where Economy 7 storage heaters provide the bulk of space heating but there are also electric panel heaters in some rooms, both are entered as separate heating systems with proportional heat shares estimated from the areas served.

**Economy 7 and Economy 10 tariffs.** Storage heaters and some underfloor systems are specifically designed to charge on off-peak tariff. RdSAP 10 requires correct tariff identification because the fuel cost calculation uses tariff-specific unit rates. Economy 7 properties have a two-rate electricity meter (standard and off-peak). Evidence: the meter itself (two registers visible) or the occupant's electricity bill showing two unit rates. Do not assume Economy 7 for all storage heater properties — some have been rewired to standard tariff.

---

## Section 4: Input Conventions and Common Audit Failures

**Input sequence for all-electric properties.** The RdSAP 10 data entry workflow for an all-electric property differs meaningfully from a gas-heated property. The main inputs are: heating system type (from the electric heating categories), controls (thermostat, programmer, boost), fuel type (electricity — standard or off-peak), and secondary systems where applicable. The DHW section requires separate treatment: most all-electric properties use an immersion heater for hot water, with or without a cylinder thermostat.

**Controls for electric heating.** The controls multiplier for electric heating is simpler than for gas systems but still matters. A storage heater with no thermostat and no programmer (basic manual controls only) receives minimal controls credit. A modern HHR storage heater with a room thermostat and seven-day programmer receives full controls credit. Panel heaters with thermostats receive an intermediate credit. Assess what is actually present and functional.

**The responsiveness factor.** Electric heating systems have a responsiveness factor in RdSAP 10 that reflects how quickly the system responds to a demand for heat — and therefore how effectively it can avoid overheating. HHR storage heaters score better here than standard storage heaters. Direct electric panel heaters score best (most responsive). The responsiveness factor interacts with the intermittency factor (how often the dwelling is occupied and heating demanded) to determine the calculated space heating energy.

**Top audit failure categories for electric heating (scheme auditor data, 2024–2025):**

1. Standard storage heaters classified as HHR — the single most common error on all-electric properties. Assessors must inspect controls and product labels, not assume HHR because heaters are modern-looking.

2. Economy 7 assumed without meter verification — particularly on properties that have been refurbished. If the storage heaters are present but the meter has been replaced with a single-rate smart meter, Economy 7 no longer applies.

3. Secondary electric heating not captured — panel heaters in extensions or converted rooms omitted, underrepresenting total heat demand.

4. Mixed system proportions not evidenced — the 20% secondary heat share is entered without a supporting floor area calculation in site notes.

5. Underfloor electric entered as direct electric — the responsiveness and thermal mass corrections are different; UHF electric is a specific input category.

**Practical site workflow.** For an all-electric property: (a) identify all heating appliances room by room; (b) photograph each unit and its controls; (c) record the product label and any model number; (d) check the electricity meter type (single-rate or two-rate); (e) estimate the floor area served by each heating type; (f) check for any immersion heater and cylinder arrangement. This workflow, consistently applied, produces audit-ready data for every all-electric assessment.

---

## Key Takeaways

- The distinction between standard (old) and high heat retention storage heaters is a classification decision with material impact on calculated energy performance — inspect controls, product labels, and physical characteristics on site.
- High heat retention storage heaters have electronic controls, fan-assisted output, and digital programming; standard storage heaters have manual input/output dials and bulkier insulation cores.
- Direct electric heating (panel heaters, radiant panels, electric underfloor) is assessed at 100% conversion efficiency; the performance differences lie in responsiveness and controls, not conversion efficiency.
- Economy 7 tariff must be verified at the meter — a two-register electricity meter is the physical evidence; do not assume off-peak tariff for storage heater properties that may have been rewired.
- Mixed primary/secondary systems require the percentage heat share from each system to be estimated and documented, typically based on proportion of heated floor area served.
- The controls assessment for electric heating must reflect what is actually present and functional — do not credit a programmer or room thermostat that is absent or non-functional.
- Photograph every electric heater, its controls panel, and the electricity meter to provide the audit evidence base for all electric heating inputs.

---

## Self-Assessment Questions

**Q1.** An assessor visits a 1970s all-electric flat. The storage heaters are large, heavy units with manual input and output dials and no visible digital display or fan outlet. How should these be classified in RdSAP 10?

A) High heat retention storage heaters — age alone determines classification
B) Standard (old) storage heaters with manual controls
C) Direct electric panel heaters, as they are wall-mounted
D) Fan-assisted storage heaters

**Correct answer: B**
*Manual input and output dials, no digital display, no fan outlet, and bulky construction are all characteristic of standard (old) storage heaters. HHR classification requires electronic controls and typically a fan-assisted output. Age alone does not determine the classification — the controls and construction must be inspected.*

---

**Q2.** A modern all-electric flat has electric panel heaters in the living room and bedroom (served by a wall-mounted thermostat in each room) and electric underfloor heating in the bathroom. How should the bathroom be treated in RdSAP 10?

A) Ignored — bathrooms are excluded from the heated floor area calculation
B) Entered as a secondary electric heating system (electric underfloor) serving the bathroom floor area
C) Entered as a separate primary system
D) Treated as an unheated space

**Correct answer: B**
*The bathroom with electric underfloor heating is captured as a secondary electric heating system in RdSAP 10, with the underfloor heating category selected and the proportion of heat from this system estimated relative to the panel heaters. Bathrooms are included in the heated floor area if heated.*

---

**Q3.** An assessor assumes a property has Economy 7 tariff because storage heaters are present. On closer inspection, the electricity meter is a single-register smart meter with no off-peak register. What is the correct assessment?

A) Economy 7 still applies — storage heaters always run on off-peak tariff
B) Standard rate electricity applies — the meter confirms no off-peak supply; Economy 7 must not be entered
C) The assessor should ask the occupant, and if they believe it is Economy 7, enter it as such
D) Economy 10 applies as an alternative to Economy 7

**Correct answer: B**
*Economy 7 requires a two-rate supply confirmed by a two-register meter or dual-rate supply agreement. A single-register smart meter confirms standard rate supply regardless of what appliances are present. Entering Economy 7 without meter evidence is a methodology failure.*

---

**Q4.** A gas-fired central heating system serves the living room, kitchen-diner, and two bedrooms. A rear extension (single bedroom) has two electric panel heaters with individual thermostats. How is the secondary heat share estimated for RdSAP 10 purposes?

A) 50% — the extension is a separate room, so half the heat comes from each system
B) Based on the floor area of the extension as a proportion of total heated floor area
C) 10% fixed default for any single secondary heated room
D) Secondary heating is only recorded if it covers more than one room

**Correct answer: B**
*The percentage of heat provided by the secondary system is estimated from the floor area served by secondary heating relative to the total heated floor area of the dwelling. If the extension is, say, 15 m² out of a total 85 m² heated floor area, the secondary heat share is approximately 18%.*

---

**Q5.** Which of the following is NOT a distinguishing feature of a high heat retention (HHR) storage heater compared with a standard storage heater?

A) Electronic digital controls with seven-day programming
B) Fan-assisted heat output grille
C) Large, heavy insulation core (dense storage bricks)
D) Room temperature set-point function

**Correct answer: C**
*A large, heavy insulation core with dense storage bricks is characteristic of STANDARD (old) storage heaters, not HHR units. HHR heaters are typically slimmer in profile due to improved insulation materials. The distinguishing features of HHR heaters are electronic controls, fan-assisted output, and room temperature programming — not a heavy core.*

---

## Further Reading

- **RdSAP 10 Specification Document** — Department for Energy Security and Net Zero (DESNZ) / BRE. Full methodology including electric heating system tables. Available at: [https://www.bregroup.com/sap/](https://www.bregroup.com/sap/)

- **SAP 10.2: The Government's Standard Assessment Procedure** — DESNZ. Electric heating system efficiency and responsiveness data. Available at: [https://www.gov.uk/guidance/standard-assessment-procedure](https://www.gov.uk/guidance/standard-assessment-procedure)

- **Ofgem — Electricity Meter Types and Tariff Guidance** — Consumer and technical guidance on single and multi-rate meters. Available at: [https://www.ofgem.gov.uk/](https://www.ofgem.gov.uk/)

- **Elmhurst Energy — Technical Bulletin: Electric Heating Assessment (2024)** — Scheme-specific guidance on storage heater classification and common audit failures. Available via Elmhurst member portal: [https://www.elmhurstenergy.co.uk/](https://www.elmhurstenergy.co.uk/)

---

*© Meridian CPD 2026. All rights reserved. Unauthorised reproduction prohibited.*
*This course material is licensed to individual subscribers only.*
