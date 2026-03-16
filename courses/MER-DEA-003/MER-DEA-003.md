

# Ventilation in RdSAP 10: PIV, MVHR and Natural Ventilation
**Course ID:** MER-DEA-003 | **CPD Hours:** 1.0 | **Published:** March 2026
*© Meridian CPD 2026. All rights reserved.*

---

## Learning Objectives

- Identify how RdSAP 10 categorises and models the three principal ventilation strategies—natural, positive input ventilation (PIV), and mechanical ventilation with heat recovery (MVHR)—and distinguish the specific input parameters each requires at data entry.
- Explain the relationship between air permeability, ventilation heat loss, and the infiltration assumptions embedded in the RdSAP 10 calculation, including the default values applied when no pressure test result is available.
- Correctly record ventilation system type, ductwork configuration, and commissioning evidence during a domestic energy assessment, applying the conventions set out in RdSAP 10 and its accompanying conventions document.
- Evaluate the impact of each ventilation strategy on the dwelling's Energy Efficiency Rating (EER) and Environmental Impact Rating (EIR), and articulate why that impact can vary significantly with fabric performance and heating fuel type.
- Apply PAS 2035:2023 ventilation safeguarding principles when recommending fabric improvements on an EPC, recognising the assessor's duty-of-care boundary and when to flag referral to a retrofit coordinator.

---

## Introduction

Ventilation has always been the orphan topic in domestic energy assessment. Most DEAs can recite U-values in their sleep but hesitate over ductwork insulation classes. RdSAP 10 makes that hesitation costly. The revised methodology—live since its phased rollout began under SAP 10.2 and now fully embedded in lodgement software—treats ventilation heat loss with considerably more granularity than its predecessor. Input errors that once nudged a rating by a single point can now shift it by five or six, enough to move a dwelling across an EPC band boundary and, in a rental market shaped by Minimum Energy Efficiency Standards (MEES), enough to determine whether a property can be legally let.

Three things have changed the landscape. First, RdSAP 10 applies updated wind-speed and shielding factors drawn from revised climate data, which alter the background infiltration calculation for every dwelling regardless of ventilation system. Second, the Product Characteristics Database (PCDB) now holds performance records for a far wider range of mechanical ventilation units, including most mainstream PIV systems, meaning the days of lumping all positive input ventilation under a single generic entry are ending. Third, PAS 2035:2023 has hardened the expectation that anyone recommending fabric measures on a retrofit path must consider ventilation adequacy—a principle that directly touches the improvement recommendations section of every EPC.

This course is not a primer. It assumes you already hold a Level 3 DEA qualification, that you are actively lodging EPCs, and that you understand the broad architecture of an RdSAP calculation. What it offers is a focused, one-hour examination of how ventilation inputs flow through the RdSAP 10 model, where the common errors lie, and what the regulatory framework now expects of you when ventilation and fabric interact. We will work through natural ventilation, PIV, and MVHR in turn, then close with practical guidance on site recording and EPC recommendations.

Throughout, references to specific RdSAP conventions relate to the version current at the date of publication. Always verify against the latest edition of the RdSAP conventions document and PCDB before lodging.

---

## Section 1: Ventilation Heat Loss in the RdSAP 10 Model — What Actually Changed

The RdSAP calculation estimates total ventilation heat loss using an effective air change rate, expressed in air changes per hour (ach). That rate is built from two components: infiltration (uncontrolled air leakage through the fabric) and purposeful ventilation (deliberate airflow via trickle vents, extract fans, or a mechanical system). RdSAP 10 did not reinvent this framework, but it recalibrated several of the numbers inside it, and the cumulative effect is significant.

**Infiltration assumptions.** Where no air pressure test result is entered, RdSAP 10 assigns a default air permeability based on dwelling age band, construction type, and the number of storeys. These defaults were revised upward for some pre-1976 archetypes following post-occupancy monitoring data, meaning untested older dwellings may now show higher infiltration rates than they did under RdSAP 2012. Where a valid pressure test is available, the measured value at 50 Pa is divided by 20 (the standard convention for converting to an approximate ach at ambient conditions) and then adjusted by shelter and wind factors. Those shelter and wind factors now use updated regional climate datasets aligned with SAP 10.2 weather files, which shifts results modestly for exposed and heavily sheltered sites alike.

**Purposeful ventilation.** For naturally ventilated dwellings, RdSAP 10 accounts for the number of open flues, intermittent extract fans, and passive stack vents. Each carries an associated airflow rate in litres per second (l/s) that feeds into the effective air change rate. The l/s values themselves have not changed dramatically, but the way the model balances infiltration against purposeful ventilation has been tightened: the "greater of" rule—where the effective rate is the higher of infiltration alone or a minimum whole-dwelling ventilation rate—still applies, but the minimum rate has been nudged upward in line with Approved Document F Volume 1 (2021 edition) background ventilation provisions.

**Why it matters at the keyboard.** If you under-record extract fans in a naturally ventilated dwelling, you may inadvertently trigger the minimum ventilation rate floor instead of the fan-based calculation, producing a lower heat loss figure and an artificially generous rating. Conversely, recording an open flue that has been sealed without updating the combustion appliance entry creates a phantom air path. Accuracy here is not pedantic—it is the difference between a defensible EPC and a lodgement that will not survive audit.

---

## Section 2: Natural Ventilation — Defaults, Overrides, and the Flue Problem

The majority of EPCs lodged in England and Wales are for naturally ventilated dwellings. RdSAP 10 treats natural ventilation as the baseline: no mechanical supply, no mechanical extract beyond intermittent fans in wet rooms. The model's effective air change rate for these properties is dominated by infiltration and modified by chimneys, flues, fans, and vents.

**Chimneys and flues remain disproportionately influential.** An open fireplace chimney adds approximately 40 l/s equivalent airflow to the calculation—a figure drawn from established conventions that RdSAP 10 carries forward. A blocked chimney with no ventilation provision registers zero. Between those extremes sit partially blocked chimneys, chimney breasts with ventilated caps, and decommissioned gas flue terminals. The conventions document distinguishes between an "open flue" (serving a working appliance or genuinely open to the room) and a "blocked" or "sealed" chimney. A chimney with a capped pot and no room vent is treated as blocked; a chimney with a cowl but an open register plate is not. This is site-observation territory: you must physically verify the register plate or closure state. Photographs of chimney breast configuration should be standard practice in your evidence pack.

**Intermittent extract fans.** RdSAP 10 requires you to record the number of intermittent extract fans. Each is assigned a default airflow contribution. A common audit finding is under-counting—assessors record the extractor in the bathroom but miss the one in the utility room or en suite. Walk the dwelling systematically. Open every door. Check above hobs: a recirculating cooker hood is not an extract fan and should not be recorded; a ducted-to-outside hood is.

**Trickle vents.** RdSAP 10 asks whether trickle vents are present. This is a binary input (present/absent) rather than a count. Where trickle vents are fitted to all habitable room windows and wet room windows, record them as present. Partial provision—a handful of vents in a dwelling where many windows lack them—should be recorded as absent per the conventions. This input modifies the infiltration offset within the calculation.

**Passive stack ventilation (PSV).** PSV systems—vertical ducts running from wet rooms to roof terminals using buoyancy-driven airflow—are treated separately. They are not common in new-build since the rise of continuous mechanical extract, but they persist in 1990s and early 2000s housing stock. Record the number of PSV ducts. Each replaces one intermittent extract fan in the calculation and carries its own default airflow rate.

Accuracy in this section pays compound dividends: every litre per second of ventilation airflow affects the space heating demand, which propagates through fuel cost, CO₂ emissions, and both EPC ratings.

---

## Section 3: Mechanical Systems — PIV and MVHR in the RdSAP 10 Framework

**Positive Input Ventilation (PIV).** PIV units supply filtered, tempered air into the dwelling—typically from the loft space via a ceiling diffuser—creating a slight positive pressure that displaces moist, stale air through the fabric's natural leakage paths. In energy terms, the critical question is whether the incoming air is pre-warmed (loft-mounted units benefit from residual loft heat) and how much electrical energy the fan consumes.

RdSAP 10 treats PIV as a sub-category of mechanical supply ventilation. If the specific unit is listed on the PCDB, the assessor enters the PCDB reference and the software draws the tested specific fan power (SFP) in W/(l/s) and any associated heat contribution factor. If the unit is not on the PCDB, the software applies a default SFP that is considerably less favourable. This is a practical issue: PIV is one of the most commonly retro-fitted ventilation systems in the UK social housing sector, yet many older units have never been submitted to the PCDB. Where you encounter a PIV unit without a PCDB entry, record the manufacturer and model in your notes and apply the default—do not guess an SFP.

The interaction between PIV and air permeability is important. PIV assumes leakage paths exist for air to escape; in a very airtight dwelling, it can pressurise the structure and drive moist air into interstitial spaces. RdSAP 10 does not model moisture risk, but PAS 2035:2023 requires that any retrofit measure which changes the ventilation regime must be assessed for moisture safety. If you are generating an EPC that will feed into a retrofit programme—PAS 2035 medium-term improvement plan territory—flagging existing PIV and its interaction with proposed fabric tightening is a professional obligation.

**Mechanical Ventilation with Heat Recovery (MVHR).** MVHR systems supply fresh air to habitable rooms and extract from wet rooms through a ducted network, passing both streams through a heat exchanger. RdSAP 10 models the heat recovery efficiency (as a percentage of the temperature difference recovered) and the SFP for the combined supply-and-extract fans.

For MVHR, the PCDB entry is even more consequential. A well-commissioned system with tested efficiency of 90% or above at a low SFP can dramatically reduce ventilation heat loss in an airtight dwelling, producing EPC improvements of 5–10 SAP points compared with natural ventilation, depending on fuel type and climate zone. A system entered with defaults—because the PCDB reference is missing or the unit is unrecognisable on site—will be modelled at a generic, far less favourable efficiency.

**Ductwork.** RdSAP 10 distinguishes between rigid and flexible ductwork for MVHR, because flexible duct carries higher pressure drops and thus higher in-use SFP. If you cannot determine ductwork type—for instance in a dwelling where ducts are concealed within the building fabric—the convention is to assume flexible, which produces the more conservative result.

**Commissioning evidence.** Where an MVHR system has been commissioned and the commissioning certificate is available, this should inform your assessment. Uncommissioned MVHR receives a penalty in the calculation, reflecting real-world evidence that poorly balanced systems underperform significantly. Ask the householder. Check the document pack. Note the presence or absence of commissioning records in your site notes.

---

## Section 4: Site Practice, EPC Recommendations, and PAS 2035 Boundaries

**On-site recording.** Ventilation assessment begins at the front door. Before you enter data, you need answers to a clear checklist:

1. What is the primary ventilation strategy? (Natural / MEV / MVHR / PIV / PSV)
2. How many intermittent extract fans are present, and where?
3. Are trickle vents fitted to all or most windows?
4. Are there open chimneys or flues? What is the state of each?
5. If mechanical, what is the make, model, and PCDB reference of the unit?
6. For MVHR, is the ductwork rigid or flexible? Is there a commissioning certificate?
7. Is an air pressure test result available?

Photograph every ventilation-relevant feature: fan grilles, MVHR unit labels, chimney breast states, trickle vents (or their absence). Auditors are increasingly requesting photographic evidence for ventilation inputs specifically because error rates are high.

**EPC improvement recommendations.** RdSAP 10 software generates recommended measures. Where ventilation features, exercise professional judgement. Recommending cavity wall insulation or internal wall insulation on a naturally ventilated dwelling with no trickle vents and open flues may improve the notional EPC rating, but it tightens the fabric without addressing ventilation adequacy. Since PAS 2035:2023 Section 8 requires that retrofit projects must not degrade indoor air quality, your recommendation narrative should note where ventilation upgrades are a necessary companion to fabric measures.

You are not a retrofit coordinator. You do not design the ventilation strategy. But as the assessor generating the data that triggers funding and compliance pathways, you sit at the front of the information chain. A note in the assessor comments field—"dwelling has no mechanical ventilation; fabric measures should be accompanied by ventilation review per PAS 2035:2023"—costs you ten seconds and may prevent a significant moisture and IAQ problem downstream.

**MEES and the rating boundary.** For rental properties, the difference between an E and a D can determine legal lettability under current and anticipated MEES thresholds. Ventilation inputs can tip that boundary. This is not a reason to manipulate data—it is a reason to get data right. An accurate ventilation entry is your defence in any compliance challenge.

---

## Key Takeaways

- RdSAP 10 applies revised default air permeability values and updated wind and shelter factors; untested older dwellings may now model with higher infiltration than under previous versions.
- Every open chimney or flue adds substantial ventilation heat loss—verify register plate and closure state on site and photograph the evidence.
- PIV and MVHR performance in RdSAP 10 is heavily dependent on whether a valid PCDB entry is available; default values are significantly less favourable than tested product data.
- For MVHR, record ductwork type (rigid vs flexible) and commissioning status—both directly modify the calculation and both are common audit failure points.
- Trickle vent presence is a binary input in RdSAP 10; partial provision should be recorded as absent per conventions.
- PAS 2035:2023 requires ventilation adequacy to be safeguarded during retrofit; your EPC recommendations should flag where fabric measures need to be accompanied by ventilation review.
- Photograph all ventilation features systematically—audit scrutiny of ventilation inputs is increasing, and photographic evidence is your primary defence.

---

## Self-Assessment Questions

**Question 1.** In RdSAP 10, where no air pressure test result is available for a pre-1976 masonry dwelling, the software applies:

A) A default air permeability of 5 m³/(h·m²) at 50 Pa for all age bands
B) An age-band and construction-type specific default air permeability, which may be higher than the equivalent default under RdSAP 2012
C) Zero infiltration, on the assumption that untested dwellings cannot be modelled
D) The Building Regulations Part F minimum ventilation rate as a proxy for infiltration

**Correct answer: B.** RdSAP 10 assigns default air permeability values by dwelling age band and construction type. These defaults were revised using post-occupancy monitoring data, and for some pre-1976 archetypes the values increased compared with RdSAP 2012.

---

**Question 2.** A dwelling has an MVHR system installed, but the assessor cannot determine whether the ductwork is rigid or flexible. Under RdSAP 10 conventions, the assessor should:

A) Record the ductwork as rigid, as this is the most common type
B) Record the ductwork as flexible, as this produces the more conservative result
C) Omit the MVHR system from the assessment entirely
D) Enter a 50/50 split between rigid and flexible

**Correct answer: B.** The convention is to assume flexible ductwork where the type cannot be determined, because flexible duct is associated with higher pressure drops and a less favourable SFP, producing the more conservative modelled outcome.

---

**Question 3.** A recirculating cooker hood is installed above the hob. How should this be recorded in RdSAP 10?

A) As one intermittent extract fan
B) As a continuous mechanical extract ventilation (MEV) system
C) It should not be recorded as an extract fan, because it does not exhaust air to outside
D) As a passive stack vent

**Correct answer: C.** A recirculating cooker hood filters and returns air to the kitchen; it does not extract air from the dwelling. Only fans or hoods ducted to outside should be recorded as intermittent extract fans.

---

**Question 4.** A PIV unit is installed in the loft space of a dwelling, but the unit does not have a PCDB entry. What is the correct approach under RdSAP 10?

A) Estimate the specific fan power from the manufacturer's marketing literature and enter it manually
B) Enter the system using the PCDB reference for the closest equivalent product from the same manufacturer
C) Record the system as PIV and allow the software to apply the default (generic) specific fan power
D) Record the dwelling as naturally ventilated, since the PIV unit cannot be verified

**Correct answer: C.** Where a mechanical ventilation product does not have a PCDB entry, the assessor records the system type and the software applies generic default values. Estimating performance data or substituting another product's PCDB reference is not permitted.

---

**Question 5.** Under PAS 2035:2023, when an EPC recommends fabric insulation measures for a naturally ventilated dwelling, the assessor should:

A) Design and specify a replacement mechanical ventilation system as part of the EPC recommendation
B) Note in the assessor's comments that fabric measures should be accompanied by a ventilation adequacy review, as ventilation must be safeguarded during retrofit
C) Suppress the insulation recommendation if no mechanical ventilation is present
D) Assume that Building Control will address ventilation at the point of installation

**Correct answer: B.** The assessor's role is to flag the interaction between fabric tightening and ventilation adequacy, not to design the ventilation solution. PAS 2035:2023 requires that retrofit does not degrade indoor air quality; a note in the assessor comments ensures this consideration enters the retrofit decision chain.

---

## Further Reading

1. **BRE — RdSAP 10 Conventions Document (current edition).** The primary reference for all data entry conventions, including ventilation inputs, defaults, and PCDB lookup requirements. Available via the BRE SAP website: [https://www.bregroup.com/sap/](https://www.bregroup.com/sap/)

2. **HM Government — Approved Document F: Ventilation, Volume 1: Dwellings (2021 edition, as amended).** Sets the statutory ventilation provisions for new and existing dwellings in England. Essential context for understanding minimum ventilation rates referenced in the RdSAP model. Available at: [https://www.gov.uk/government/publications/ventilation-approved-document-f](https://www.gov.uk/government/publications/ventilation-approved-document-f)

3. **BSI — PAS 2035:2023 Retrofitting Dwellings for Improved Energy Efficiency — Specification and Guidance.** The overarching retrofit specification for publicly funded energy efficiency schemes. Section 8 addresses ventilation safeguarding. Available for purchase from the BSI shop: [https://www.bsigroup.com/](https://www.bsigroup.com/)

4. **PCDB — SAP Product Characteristics Database.** The authoritative database of tested mechanical ventilation products, including SFP and heat recovery efficiency data used by RdSAP 10 software. Searchable online at: [https://www.ncm-pcdb.org.uk/sap/](https://www.ncm-pcdb.org.uk/sap/)

---

*© Meridian CPD 2026. All rights reserved. Unauthorised reproduction prohibited.*
*This course material is licensed to individual subscribers only.*