

# Solar PV, Battery Storage and PV Diverters in RdSAP 10
**Course ID:** MER-DEA-011 | **CPD Hours:** 1.0 | **Published:** March 2026
*© Meridian CPD 2026. All rights reserved.*

---

## Learning Objectives

- Correctly identify and record all required solar PV input parameters in RdSAP 10, including array orientation, tilt, overshading, peak kilowatt capacity and MCS certification status.
- Distinguish between the RdSAP 10 treatment of battery storage systems and explain when and how battery storage modifies the dwelling's energy performance calculation.
- Apply the correct methodology for logging PV diverters (solar-to-hot-water switches) within RdSAP 10, including eligibility criteria and the interaction with the domestic hot water circuit.
- Identify common site-assessment errors related to PV, battery and diverter installations and apply appropriate evidence-gathering procedures consistent with Conventions and current scheme guidance.
- Evaluate the combined impact of PV generation, battery storage and PV diverters on the dwelling emission rate (DER), primary energy rate and EPC band, and explain the limitations of the modelled assumptions to clients and stakeholders.

---

## Introduction

RdSAP 10 represents the most significant revision to the reduced data Standard Assessment Procedure since its inception. For solar technologies in particular, the changes are substantial. The previous RdSAP 9.94 framework treated photovoltaic arrays in a relatively simplified manner, offered no pathway for battery storage and handled PV diverters through a narrow appendix mechanism that many assessors either misunderstood or overlooked entirely. RdSAP 10 addresses all three technologies with materially revised input logic, new data fields and a more granular calculation engine that better reflects real-world energy flows.

The timing matters. As of early 2026, DESNZ deployment statistics indicate that over 1.4 million homes in England and Wales now have solar PV, with battery retrofit rates accelerating sharply since 2024. PV diverter installations, once a niche product, have become a routine addition to PV systems, particularly in off-gas dwellings where immersion heaters are present. Assessors are encountering these technologies on a daily basis, and the consequences of incorrect data entry are no longer trivial. Under the reformed compliance and enforcement framework, lodgement errors relating to renewable technologies are flagged by automated audit rules within the central register. An incorrectly recorded PV array can shift an EPC by one or even two bands, with direct implications for MEES compliance, Green Deal eligibility, ECO4 and Great British Insulation Scheme funding, and property transactions under the Home Energy Model roadmap.

This course is built for working DEAs who already hold a Level 3 or equivalent qualification and are active on a recognised accreditation scheme. It assumes familiarity with RdSAP conventions, the structure of the SAP 10.2 calculation and the general principles of on-site evidence gathering. The objective is not to teach you what solar PV is; it is to ensure you record it correctly, understand what the software does with your inputs, and know where the methodological boundaries lie. We will work through the PV, battery and diverter input fields in sequence, examine their interaction within the calculation, address the most common convention and evidence pitfalls, and then consolidate with practical scenarios.

---

## Section 1: Solar PV in RdSAP 10 — Inputs, Conventions and Calculation Logic

The RdSAP 10 PV input set is expanded relative to 9.94 and demands more precise site observation. The core parameters you are required to record are as follows:

**Peak kilowatt capacity (kWp).** This is the declared peak output of the array under standard test conditions. The primary evidence source is the MCS certificate or the manufacturer's datasheet. Where neither is available on site and the homeowner cannot provide documentation, you must estimate kWp from the panel count and a default wattage per panel as specified in the prevailing conventions. RdSAP 10 conventions currently default to 350 Wp per panel where the panel wattage is unknown and the installation post-dates 2020, and 250 Wp for installations pre-dating 2014. For installations between those dates, 300 Wp applies. These defaults are deliberately conservative. Always use the documented figure where available — it will almost always produce a more favourable result for the homeowner.

**Orientation and tilt.** RdSAP 10 uses the same eight-point compass segmentation as before (N, NE, E, SE, S, SW, W, NW) plus a horizontal option for flat-roof or near-flat installations. Tilt is recorded in degrees from horizontal. The most common error remains assessors recording roof pitch rather than array tilt on systems with mounting frames that alter the effective angle. If the panels are flush-mounted on a pitched roof, array tilt equals roof pitch. If they are mounted on an A-frame on a flat roof, you must estimate the frame angle. The SAP 10.2 solar irradiance tables are sensitive to tilt in 15-degree bands; getting this wrong by one band can shift annual yield by 5–8%.

**Overshading.** The four-tier overshading classification (none or very little / modest / significant / heavy) applies to the PV array specifically, not to the dwelling generally. Assess overshading as it affects the panels, considering nearby buildings, trees, roof features such as dormers and chimneys, and adjacent array sections on complex roofs. RdSAP 10 retains the percentage-reduction factors applied to annual generation: none or very little applies a 1.0 factor, modest 0.8, significant 0.65, and heavy 0.5. There is no partial shading model within RdSAP — the factor applies uniformly to the entire declared array.

**MCS certification.** A new explicit Boolean field in RdSAP 10 records whether the installation holds a valid MCS certificate (or equivalent, such as a legacy Microgeneration Certification Scheme certificate under the predecessor framework). This affects the assumed system loss factor. MCS-certified systems attract a lower default system loss, reflecting that the installation met design standards at commissioning. Non-MCS systems attract a higher loss factor. This is not a trivial difference — the loss adjustment can alter modelled annual generation by approximately 5%.

**Multiple arrays.** Where a dwelling has panels on more than one roof plane, each array must be entered separately with its own orientation, tilt, kWp and overshading. RdSAP 10 permits up to three distinct PV arrays per dwelling. If a dwelling genuinely has panels across four or more orientations, the conventions require you to combine the two closest-oriented arrays into a single entry using the capacity-weighted average orientation and tilt. Document this in your site notes.

The calculation engine takes these inputs and applies the regional solar irradiance data from SAP 10.2 Table H4 (updated from the older tables in SAP 2012), applies the tilt and orientation correction, the overshading reduction and the system loss factor, and produces an annual electricity generation figure in kWh/year. That figure is then split between electricity used on-site and electricity exported, using a default on-site usage fraction. In SAP 10.2, the assumed on-site usage fraction for PV without battery storage is 0.50 for systems up to 2.5 kWp and reduces for larger systems — a material change from the flat 0.50 used in earlier SAP versions.

---

## Section 2: Battery Storage — The New RdSAP 10 Framework

The treatment of battery storage is one of the headline changes in RdSAP 10. Under RdSAP 9.94, there was no mechanism to record or credit domestic battery storage at all. The SAP 10.2 methodology, which RdSAP 10 now implements in reduced-data form, introduces a defined approach.

**What qualifies.** The battery must be a dedicated electrical energy storage system connected to the PV array (AC- or DC-coupled) and configured to store surplus PV generation for later use within the dwelling. Vehicle-to-grid (V2G) systems are not currently eligible. Portable or plug-in battery units without a fixed electrical connection to the consumer unit do not qualify. The system must be permanently installed and, ideally, evidenced through an installer's commissioning certificate, an MCS battery certificate, or the manufacturer's documentation. Where no documentation is available, the assessor may record the battery based on visual inspection and identification of the unit, but must note the evidence limitation.

**Input parameters.** RdSAP 10 requires the following battery inputs:

- **Usable storage capacity (kWh).** This is the manufacturer's declared usable capacity, not the total cell capacity. For example, a Tesla Powerwall 2 has a usable capacity of 13.5 kWh. If the exact figure is unavailable, the conventions provide a default of 4.0 kWh, which is deliberately conservative and will understate the benefit.
- **Battery present (Boolean).** A simple yes/no flag that activates the battery calculation pathway.

That is it. RdSAP 10 does not require you to record battery chemistry, round-trip efficiency, charge/discharge rate or degradation state. The methodology applies fixed default assumptions for these: a round-trip efficiency of 0.85 and no degradation adjustment. The rationale, as set out in the SAP 10.2 accompanying notes, is that real-world battery efficiency variations are smaller than the uncertainty already inherent in the occupancy-independent SAP model, and introducing additional inputs would add assessment burden without proportionate accuracy gain.

**Calculation impact.** The presence of a battery modifies the on-site usage fraction for PV-generated electricity. Without a battery, SAP 10.2 assumes that a proportion of PV generation is exported because it is generated when demand is low. With a battery, more of that surplus is retained. The methodology uses a lookup relationship between battery capacity, PV array size and the dwelling's annual electricity demand to determine a revised on-site usage fraction. In practical terms, for a typical 3–4 kWp system with a 5+ kWh battery in a medium-demand dwelling, the on-site usage fraction increases from approximately 0.45–0.50 to 0.70–0.80. This is significant. On-site consumption of PV electricity displaces grid electricity at the full grid carbon intensity and fuel cost, whereas exported electricity receives only a partial credit. A battery therefore improves both the DER and the energy cost rating, and can shift the EPC band.

**Common pitfalls.** The most frequent error is recording a battery that is not connected to the PV system. Some dwellings have standalone batteries installed for tariff arbitrage (charging from the grid at off-peak rates). These do not qualify under the SAP methodology because they are not storing PV generation — they are storing grid electricity. The SAP 10.2 model only credits battery storage in the context of PV self-consumption. If the battery is connected to the grid but there is no PV system on the dwelling, the battery field should not be activated. Similarly, hybrid inverter systems that combine PV and grid charging should still be recorded as battery present, because the SAP model does not distinguish — it simply adjusts the PV self-consumption fraction upward. The methodology inherently assumes the battery is used to maximise PV self-consumption regardless of real-world dispatch logic.

A second pitfall relates to shared systems in converted flats. Where a PV array and battery serve multiple dwellings, you must apportion the kWp and battery capacity to the individual dwelling using the same approach as for shared PV — typically by floor area fraction — and record only the apportioned share. The conventions are explicit on this point. Do not record the total system capacity for each flat.

---

## Section 3: PV Diverters — Eligibility, Input Requirements and Hot Water Interaction

PV diverters — also known as solar PV diverters, immersion optimisers, or power diverters — redirect surplus PV-generated electricity to an immersion heater in the hot water cylinder rather than exporting it to the grid. Common products include the Eddi (myenergi), iBoost and Solar iBoost. In RdSAP 10, these devices have a defined input pathway that differs from both the PV and battery treatments.

**Eligibility criteria.** For a PV diverter to be recorded in RdSAP 10, all of the following must be true:

1. The dwelling must have a solar PV array (already recorded).
2. The dwelling must have a hot water storage cylinder with an electric immersion heater. Combi boiler systems and unvented direct systems without a cylinder do not qualify, because there is no thermal store to receive the diverted electricity.
3. The diverter must be a permanently installed, hardwired device that automatically routes surplus PV generation to the immersion element. A manual timer switch or a smart plug does not meet the definition. The device must sense export and divert in real time.

**What to record.** RdSAP 10 introduces a single Boolean field: PV diverter present (yes/no). There is no requirement to record the make, model, capacity or rated power of the diverter. The methodology applies a fixed set of assumptions about diverter behaviour.

**Calculation logic.** The PV diverter modifies the domestic hot water (DHW) energy calculation. SAP 10.2 models the diverter as providing a fraction of the dwelling's annual DHW demand from diverted PV electricity, reducing the fuel consumption attributed to the primary DHW heating system. The fraction is derived from the PV array size, the dwelling's DHW demand and a seasonal availability curve that reflects the correlation between PV surplus and hot water demand. In summer months, a larger fraction of DHW can be met by the diverter; in winter, the contribution is minimal.

The key point for assessors to understand is this: the PV diverter credit is applied to the hot water energy demand, not to the electrical self-consumption fraction. This means the diverter and the battery are modelled through different pathways in the calculation and their benefits are partially additive. A dwelling with PV, a battery and a diverter will see the battery increase the electrical self-consumption fraction (reducing lighting and appliance grid electricity consumption) and the diverter reduce the modelled fuel input for DHW. However, there is an interaction cap — the total PV generation cannot be double-counted. The SAP 10.2 algorithm ensures that the electricity allocated to the diverter is deducted from the electricity available for self-consumption or export. In effect, the model partitions annual PV generation into three streams: on-site electrical use (enhanced by the battery), diverted-to-DHW (via the diverter) and exported.

**Interaction with solar thermal.** If the dwelling also has a solar thermal panel contributing to DHW, the PV diverter credit is applied after the solar thermal contribution. The combined solar thermal and PV diverter benefit is capped so that the modelled renewable DHW contribution does not exceed the total DHW demand. In practice, this cap is rarely reached — but in a well-insulated, low-occupancy dwelling with a large PV array and solar thermal panels, it is theoretically possible.

**Evidence requirements.** Visual identification of the diverter unit (typically mounted near the consumer unit or the hot water cylinder) is the primary evidence. Photograph the unit and its wiring. If you can see a branded unit with a clear label (e.g., "myenergi eddi"), that is sufficient. If the homeowner claims a diverter is installed but you cannot identify the device, you cannot record it. The conventions are clear: if it cannot be evidenced, it is not recorded. A receipt or invoice without physical verification is insufficient.

**Common error.** Some assessors confuse PV diverters with solar thermal diverter valves (motorised valves in solar thermal plumbing). These are entirely different technologies. A PV diverter is an electrical device. A solar thermal diverter valve is a plumbing component. Ensure you are identifying the correct technology.

---

## Section 4: Combined Scenarios and Practical Auditing Considerations

In practice, you will increasingly encounter dwellings with all three technologies — PV, battery and diverter — installed together, often as part of a single package from an MCS-certified installer. Getting the inputs right for the combination requires a systematic approach.

**Recommended site workflow:**

1. **Identify the PV array first.** Count panels, record orientation and tilt per array plane, assess overshading at panel level, and collect the MCS certificate or datasheet. Record kWp per array.
2. **Identify the inverter.** Check whether it is a hybrid (battery-compatible) inverter. This often indicates a battery is present or was planned. Note the inverter's rated capacity — if it is significantly larger than the PV array, a battery may be connected.
3. **Locate the battery.** Check the garage, utility room, or adjacent to the consumer unit. Record the make, model and usable capacity from the unit label or commissioning documentation.
4. **Locate the PV diverter.** Check near the consumer unit and near the hot water cylinder. Confirm the cylinder has an immersion heater (check for an immersion boss and wiring). Confirm the diverter is wired to the immersion.
5. **Photograph everything.** MCS certificate, panel array, inverter nameplate, battery nameplate, diverter unit, cylinder with immersion wiring. These photographs form your audit trail.

**Audit exposure.** Under the reformed quality assurance framework, renewable technology inputs are high-priority audit items. A desk-based audit can cross-reference your declared kWp against the MCS installation database. If the figures diverge, your lodgement will be flagged. Ensure your recorded kWp matches the MCS register entry, not an approximation.

**Impact on EPC outcomes.** For a typical mid-terrace, gas-heated dwelling (SAP band D), adding a 4 kWp PV system alone may lift the rating by 8–14 SAP points. Adding a 5 kWh battery may add a further 3–6 points. Adding a PV diverter may add 1–3 points, depending on DHW demand and existing heating system. These are indicative ranges — actual outcomes depend on dwelling geometry, demand profile and existing efficiency measures. Do not quote specific point improvements to clients; run the calculation.

---

## Key Takeaways

- Always use documented kWp from the MCS certificate or datasheet; only fall back to convention defaults when no evidence exists, and select the correct era-based default wattage per panel.
- Record PV array tilt as the actual panel angle from horizontal, not the roof pitch, where mounting frames alter the effective angle.
- Battery storage in RdSAP 10 requires only two inputs (present and usable capacity in kWh) and modifies the PV on-site usage fraction — do not record batteries that are not connected to a PV system.
- PV diverters are recorded as a Boolean field and require a hot water cylinder with an immersion heater to be present; the benefit flows through the DHW calculation pathway, not the electrical self-consumption pathway.
- The battery and diverter benefits are partially additive but the SAP 10.2 algorithm prevents double-counting of PV-generated electricity across the three output streams.
- Photograph and document all renewable technology components — MCS certificates, nameplates and wiring configurations — as your primary audit defence.
- Do not extrapolate SAP point improvements to clients without running the specific calculation; modelled outcomes depend on the full dwelling dataset, not isolated technology inputs.

---

## Self-Assessment Questions

**Question 1.** A dwelling has a PV array installed in 2022 but the homeowner cannot provide the MCS certificate or any panel documentation. You count 12 panels. Under RdSAP 10 conventions, what kWp should you record?

A) 12 × 250 Wp = 3.0 kWp
B) 12 × 300 Wp = 3.6 kWp
C) 12 × 350 Wp = 4.2 kWp
D) You cannot record the PV array without documentation

**Correct answer: B.** The installation post-dates 2014 but pre-dates the post-2020 threshold. The convention default for installations between 2014 and 2020 is 300 Wp per panel. However, note the installation date is 2022 — this falls into the post-2020 bracket, making the answer **C) 3.6 kWp at 300 Wp** only if the assessor misidentifies the date band. Re-reading the convention: installations post-dating 2020 use 350 Wp. The correct answer is **C) 12 × 350 Wp = 4.2 kWp.**

**Correct answer: C.** The 2022 installation date falls into the post-2020 convention default of 350 Wp per panel. 12 × 350 Wp = 4.2 kWp.

---

**Question 2.** A dwelling has a 5.0 kWh battery storage system installed, but no solar PV array. Should the battery be recorded in RdSAP 10?

A) Yes — battery storage is recorded regardless of PV presence
B) Yes — but with the kWp field left at zero
C) No — the battery calculation pathway is only activated when a PV array is also recorded
D) No — batteries are not recognised in RdSAP 10

**Correct answer: C.** The SAP 10.2 battery methodology modifies the PV self-consumption fraction. Without a PV array, there is no self-consumption to modify. The battery field should not be activated.

---

**Question 3.** An assessor records a PV diverter as present on a dwelling with a 3.5 kWp PV array. The dwelling has a combi boiler and no hot water cylinder. Is this correct?

A) Yes — the PV diverter can heat water at the point of use
B) Yes — the diverter will be credited against space heating instead
C) No — a PV diverter requires a hot water cylinder with an immersion heater
D) No — PV diverters are only valid with systems above 4.0 kWp

**Correct answer: C.** A PV diverter requires a DHW cylinder with an immersion heater as the thermal store receiving the diverted electricity. A combi boiler system has no cylinder, so the diverter cannot function as modelled and must not be recorded.

---

**Question 4.** A dwelling has PV panels flush-mounted on a roof pitched at 35 degrees from horizontal, facing south-west. An adjacent chimney stack casts a shadow across approximately one-third of the array during winter mornings. What overshading category is most likely appropriate?

A) None or very little
B) Modest
C) Significant
D) Heavy

**Correct answer: B.** Shadow from a chimney affecting approximately one-third of the array during a limited period (winter mornings) is consistent with the "modest" overshading category. "Significant" would apply if the obstruction affected a larger proportion of the array for a greater part of the year. Assessors should apply professional judgement within the four-tier classification framework, considering annual rather than worst-case seasonal shading.

---

**Question 5.** In RdSAP 10, what is the assumed round-trip efficiency applied to battery storage systems in the SAP 10.2 calculation?

A) 0.80
B) 0.85
C) 0.90
D) It varies depending on the battery chemistry recorded

**Correct answer: B.** SAP 10.2 applies a fixed default round-trip efficiency of 0.85 for all battery storage systems. Battery chemistry is not a recorded input in RdSAP 10.

---

## Further Reading

- **SAP 10.2: The Government's Standard Assessment Procedure for Energy Rating of Dwellings (2022 edition with 2025 amendments)** — BRE on behalf of DESNZ. Full methodology including Appendix H (solar PV), Appendix M (battery storage) and Appendix Q (PV diverters).
  https://www.bregroup.com/sap/standard-assessment-procedure-sap-2012/

- **RdSAP 10 Conventions** — Published by the scheme operators under licence from DESNZ. The definitive source for evidence hierarchies, default values and assessment rules for reduced data applications.
  https://www.nher.co.uk/sap-rd-sap/

- **MCS Installation Standards: MIS 3002 (Solar PV) and MIS 3012 (Battery Storage)** — Microgeneration Certification Scheme. Relevant for understanding the installation standards that underpin MCS certification and the evidence documents assessors should expect to encounter.
  https://mcscertified.com/standards-tools-library/

- **PAS 2035:2023 — Retrofitting dwellings for improved energy efficiency. Specification and guidance** — BSI. Relevant where PV, battery and diverter installations form part of a whole-house retrofit under ECO4 or the Great British Insulation Scheme, particularly regarding the role of the DEA in the pre-assessment process.
  https://knowledge.bsigroup.com/products/retrofitting-dwellings-for-improved-energy-efficiency-specification-and-guidance

---

*© Meridian CP