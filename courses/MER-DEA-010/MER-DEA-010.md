

# Lighting and Renewables in RdSAP 10
**Course ID:** MER-DEA-010 | **CPD Hours:** 1.0 | **Published:** March 2026
*© Meridian CPD 2026. All rights reserved.*

---

## Learning Objectives

- Accurately record fixed lighting installations in RdSAP 10, including the revised efficacy thresholds and the treatment of smart lighting controls.
- Correctly input solar photovoltaic systems using the updated RdSAP 10 methodology, including the handling of battery storage, diverters, and export assumptions.
- Apply the RdSAP 10 framework for solar thermal, wind turbines, and micro-CHP, identifying where input conventions have changed from RdSAP 9.94.
- Recognise the interaction between renewable technologies and fabric performance within the SAP energy balance, and how this affects the EPC rating output.
- Identify common lodgement errors associated with lighting and renewables data and apply appropriate evidence-gathering strategies to withstand audit scrutiny.

---

## Introduction

RdSAP 10 is the most substantial revision to the reduced data Standard Assessment Procedure since its original introduction. For working DEAs, the changes to how lighting and renewable technologies are handled are not cosmetic — they alter rating outcomes, recommendation reports, and the defensibility of your lodgements under the Accreditation Scheme's audit regime.

On the lighting side, the long-overdue update to efficacy thresholds reflects the near-total market shift to LED. The old binary of "low energy yes/no" is gone. RdSAP 10 introduces a more granular treatment of lighting efficacy, recognising that not all LEDs are equal and that lighting controls — particularly occupancy sensors and smart dimming — can now be factored into the energy calculation. This matters because lighting remains a meaningful contributor to the dwelling emission rate and primary energy metric, and getting it wrong is one of the most common audit findings.

On renewables, the changes are more consequential. The UK's installed domestic PV capacity has grown enormously since RdSAP 9.94 was drafted, and battery storage is now a mainstream addition. RdSAP 10 introduces explicit methodologies for battery systems, hot water diverters, and revised self-consumption assumptions that better reflect real-world usage patterns. Solar thermal inputs have been refined, wind turbine calculations updated, and the treatment of micro-CHP brought in line with current product data.

For assessors working in the retrofit space, these changes intersect directly with PAS 2035:2023. Medium-term improvement plans frequently include renewable installations, and the accuracy of your baseline EPC — and any projected post-improvement rating — depends on getting these inputs right. Incorrect renewable data does not just produce a wrong rating; it can undermine a retrofit coordinator's whole-house approach and distort projected carbon savings used to justify public funding.

This course assumes you are already competent with RdSAP conventions. The aim is to get you technically current, audit-ready, and confident with the specific inputs that have changed.

---

## Section 1: Lighting in RdSAP 10 — Revised Efficacy Framework and Controls

RdSAP 9.94 used a simple count: how many fixed lighting outlets exist, and how many of those have "low-energy" fittings. The threshold was crude — any fitting with a lamp efficacy above 45 lumens per watt qualified. In a market now saturated with LED, this binary approach had become almost meaningless, with the vast majority of dwellings scoring 100% low-energy lighting regardless of actual installed quality.

RdSAP 10 replaces this with a tiered efficacy model. Fixed lighting outlets are still counted, but the assessor now records the predominant lamp type across the dwelling and, where identifiable, assigns an efficacy band. The three bands currently defined in the RdSAP 10 specification are:

- **Standard LED (≥80 lm/W to <120 lm/W):** The default assumption for most modern retrofit and new-build LED fittings.
- **High-efficacy LED (≥120 lm/W):** Premium-grade LED panels, integrated downlights from major manufacturers with documented efficacy data, and certain smart bulb systems operating in white mode.
- **Sub-LED / legacy low-energy (<80 lm/W):** Compact fluorescent lamps (CFLs), older T8/T5 fluorescent tubes, and early-generation LED lamps that fall below the 80 lm/W threshold but above the halogen/incandescent baseline.

Incandescent and halogen fittings remain in the calculation as the baseline case, though in practice you will encounter these increasingly rarely.

**Lighting controls** are the genuinely new element. RdSAP 10 allows an adjustment factor where the dwelling has hardwired occupancy-sensing or daylight-sensing controls installed on fixed lighting circuits. Note the critical distinction: smart bulbs controlled via an app or voice assistant do **not** qualify unless the control function is integrated into the fixed wiring or a hardwired sensor. A Philips Hue bulb on a standard bayonet fitting is not a qualifying control. A PIR sensor hardwired into a bathroom lighting circuit is.

The practical evidence requirement has tightened accordingly. You must be able to justify the efficacy band claimed. Where integrated LED downlights are installed and no product data is accessible, the convention is to default to the Standard LED band. Only claim high-efficacy where you have visible labelling, manufacturer documentation, or the homeowner can provide product specifications. Photograph everything. Auditors are specifically targeting lighting claims in the early phase of RdSAP 10 lodgements — this has been confirmed in Scheme communications from both Elmhurst and Stroma.

---

## Section 2: Solar PV in RdSAP 10 — Battery Storage, Diverters, and Self-Consumption

The PV methodology in RdSAP 10 represents a significant departure from 9.94. The core generation calculation — based on peak kilowatt capacity (kWp), orientation, tilt, and overshading — remains structurally similar, using regional irradiance data from the SAP 10.2 climate dataset. However, what happens to that generated electricity within the dwelling energy balance has been substantially reworked.

**Self-consumption assumptions** have been updated. RdSAP 9.94 applied a flat assumption that approximately 50% of PV generation was used on-site for systems without battery storage or diverter. RdSAP 10 uses a more sophisticated algorithm that scales the self-consumption fraction based on the PV array size relative to estimated electrical demand, the presence of battery storage, and whether a hot water diverter is installed. For a typical 4 kWp system on a three-bedroom semi-detached dwelling with no storage, the self-consumption fraction under RdSAP 10 will typically fall in the range of 25–35%, reflecting real-world monitoring data more accurately. This is lower than the old 50% assumption and will in some cases produce a marginally less favourable EPC rating for PV-only installations than the same dwelling would have received under 9.94.

**Battery storage** is now an explicit input. You record the usable capacity in kWh. The software uses this to adjust the self-consumption fraction upward according to the SAP 10.2 battery model. A typical 5 kWh domestic battery paired with a 4 kWp array will push self-consumption toward 55–65%, recovering and exceeding the benefit that was previously over-estimated for PV-only systems. You must verify the battery is installed and operational — a battery that is on order or physically present but not commissioned does not qualify.

**Hot water diverters** (solar PV diverters / immersion optimisers) are also now a defined input. Where a diverter is installed and connected to the domestic hot water immersion heater, RdSAP 10 applies a separate credit to the water heating energy calculation rather than simply inflating the electrical self-consumption fraction. This is methodologically cleaner and avoids the double-counting issues that some assessors were inadvertently creating under 9.94 workarounds.

**Evidence requirements** are critical. Record the kWp from the MCS certificate or inverter nameplate. Record battery usable capacity from the product label or commissioning documentation. Note the diverter make and model. Photograph the generation meter, inverter, battery unit, and diverter. If the homeowner cannot evidence the kWp and no nameplate is accessible, the convention is to count panels, measure dimensions, and use the RdSAP 10 default assumption of 0.35 kWp per panel for crystalline silicon — but document your reasoning.

---

## Section 3: Solar Thermal, Wind, and Micro-CHP — Updated Input Conventions

**Solar thermal** systems retain their dedicated input pathway in RdSAP 10, but the calculation methodology now aligns fully with BS EN ISO 9806 test data where available. You continue to record collector type (flat plate or evacuated tube), aperture area, orientation, tilt, and overshading. The change is in the default performance parameters: where the assessor cannot obtain the specific collector performance data (zero-loss efficiency, heat loss coefficients), RdSAP 10 applies revised default values that are less generous than those used in 9.94 for flat plate systems and slightly more favourable for evacuated tubes. This reflects updated test evidence from the Solar Keymark database.

The critical convention change concerns **combined PV and solar thermal systems** (PV-T). RdSAP 10 now includes a specific input pathway for PV-T panels, which were previously not handled within the reduced data methodology. If you encounter a PV-T installation, you record the electrical kWp and the thermal aperture area separately, and the software applies appropriate generation and contribution factors for each function. Do not double-enter PV-T as both a PV system and a separate solar thermal system — this is explicitly flagged as an error in the RdSAP 10 conventions document.

**Wind turbines** remain relatively rare in domestic settings, but the input methodology has been updated. RdSAP 9.94 used a simplified wind speed correction that was widely acknowledged to over-estimate generation in urban and suburban contexts. RdSAP 10 applies a more conservative terrain roughness factor and requires the assessor to categorise the site environment as rural open, rural sheltered, suburban, or urban. For a typical building-mounted 1.5 kW micro-wind turbine in a suburban location, the estimated annual generation under RdSAP 10 will be substantially lower than the same system would have produced under 9.94. Mast-mounted systems on rural properties will see less change. Record the rated power output from the manufacturer's nameplate and the hub height or mounting position. Photograph the installation and any MCS documentation.

**Micro-CHP** (micro combined heat and power) is treated as both a heating system and an electricity generator in SAP. RdSAP 10 updates the Appendix N product database entries and adjusts the electrical efficiency credits based on current Stirling engine and fuel cell product test data. In practice, domestic micro-CHP installations are uncommon and concentrated in specific new-build developments and trial schemes. If you encounter one, the product index number from the PCDB (Product Characteristics Database) drives the calculation. Your role is to correctly identify the unit, record its index number, and confirm it is operational. Do not attempt to manually input performance data — the PCDB entry contains all required parameters.

---

## Section 4: Practical Application — Evidence, Audit Defence, and Common Errors

The Accreditation Schemes have signalled clearly that the transition to RdSAP 10 will be accompanied by increased audit sampling rates, particularly during the first 12 months of mandatory adoption. Lighting and renewables are among the areas specifically identified as high-risk for input errors. Your audit defence strategy should be built around three principles: **photograph comprehensively, record model numbers, and default conservatively where evidence is ambiguous.**

**Common lighting errors to avoid:**
- Claiming high-efficacy LED without product evidence. Default to Standard LED if uncertain.
- Recording smart bulbs as qualifying lighting controls. Only hardwired controls qualify.
- Miscounting fixed outlets. Remember: a fixed outlet is a ceiling rose, wall-mounted fitting, or recessed downlight connected to the fixed wiring. A plug-in floor lamp is not a fixed outlet, regardless of bulb type.

**Common renewable errors to avoid:**
- Entering PV kWp from the panel nameplate total rather than the system kWp. A system with 10 × 400W panels is 4.0 kWp, not 0.4 kWp per panel entered ten times. Confirm how your software expects the input.
- Failing to record battery storage when present, or recording total capacity rather than usable capacity. Most lithium batteries advertise total capacity; usable capacity is typically 90–95% of this figure, and the product datasheet will specify.
- Recording a hot water diverter when one is present but not connected — physically trace the connection to the immersion heater or confirm with the occupier.
- Entering solar thermal for a system that has been decommissioned or drained down. If the system is not functioning, it should not be recorded.

**PAS 2035:2023 interface:** Where you are producing an EPC that will serve as a baseline for a publicly funded retrofit scheme (ECO4, Great British Insulation Scheme, Warm Homes Plan), accuracy in renewable inputs directly affects the projected improvement. A retrofit coordinator relying on your EPC to model post-improvement performance needs the baseline to be correct. Over-stating existing renewable contribution means the improvement uplift will be under-estimated, potentially disqualifying the property from funding thresholds.

---

## Key Takeaways

- RdSAP 10 replaces the binary low-energy lighting classification with a tiered efficacy band system — know the thresholds (sub-LED, Standard LED, High-efficacy LED) and default conservatively.
- Lighting controls are now a defined input, but only hardwired occupancy or daylight sensors qualify — not smart bulbs or app-controlled systems.
- PV self-consumption assumptions are lower in RdSAP 10 for systems without storage; battery and diverter inputs are now explicit and must be evidenced separately.
- Battery storage is recorded as usable capacity, not total capacity — check the product datasheet, not the marketing material.
- Solar thermal defaults have been revised, and PV-T panels now have a dedicated input pathway — do not double-enter as separate PV and solar thermal systems.
- Wind turbine generation estimates are significantly lower in suburban and urban contexts under the revised terrain roughness methodology.
- Photograph all renewable installations, nameplates, MCS certificates, and battery/diverter units — your audit file should tell the full story without requiring additional explanation.

---

## Self-Assessment Questions

**Q1.** Under RdSAP 10, what is the minimum efficacy threshold for the "High-efficacy LED" lighting band?

A) 80 lm/W
B) 100 lm/W
C) 120 lm/W
D) 150 lm/W

**Correct answer: C**
*The High-efficacy LED band in RdSAP 10 is defined as ≥120 lm/W. The Standard LED band covers ≥80 lm/W to <120 lm/W.*

---

**Q2.** A dwelling has a 4 kWp PV array with no battery storage and no hot water diverter. Under RdSAP 10, what is the approximate self-consumption fraction the methodology is likely to calculate for a typical three-bedroom semi-detached house?

A) 50%
B) 70–80%
C) 25–35%
D) 10–15%

**Correct answer: C**
*RdSAP 10 uses a dynamic self-consumption algorithm that typically produces 25–35% for a PV-only system of this size on a dwelling of this type, lower than the flat 50% assumption used in RdSAP 9.94.*

---

**Q3.** An assessor encounters a Philips Hue smart lighting system controlled via a smartphone app, installed on standard bayonet fittings throughout a dwelling. Should this be recorded as a qualifying lighting control in RdSAP 10?

A) Yes — smart lighting systems always qualify as lighting controls.
B) Yes — but only if the system includes a dimming function.
C) No — only hardwired occupancy or daylight sensors on fixed wiring qualify.
D) No — lighting controls are not part of the RdSAP 10 methodology.

**Correct answer: C**
*RdSAP 10 requires lighting controls to be hardwired into the fixed lighting circuit. App-controlled smart bulbs on standard fittings do not meet this requirement.*

---

**Q4.** When recording battery storage capacity for a PV system in RdSAP 10, which figure should the assessor input?

A) The total (gross) battery capacity from the marketing literature.
B) The usable (net) battery capacity from the product datasheet.
C) The inverter AC output rating.
D) The PV array kWp multiplied by a storage factor.

**Correct answer: B**
*RdSAP 10 requires the usable (net) capacity in kWh. This is typically 90–95% of the total capacity and is specified on the product technical datasheet.*

---

**Q5.** A dwelling has a PV-T (photovoltaic-thermal) panel installation. What is the correct input approach under RdSAP 10?

A) Record the system as PV only — the thermal contribution is not recognised in RdSAP.
B) Record the system as solar thermal only — PV-T is not in the PCDB.
C) Record separately as a PV system and a solar thermal system using two distinct inputs.
D) Use the dedicated PV-T input pathway, recording electrical kWp and thermal aperture area separately within a single system entry.

**Correct answer: D**
*RdSAP 10 introduces a specific PV-T input pathway. Entering the system as two separate technologies (option C) is explicitly identified as an error in the conventions document.*

---

## Further Reading

- **BRE.** *SAP 10.2: The Government's Standard Assessment Procedure for Energy Rating of Dwellings (2022 edition).* Available from: https://www.bregroup.com/sap/standard-assessment-procedure-sap-2012/ — primary source for the full SAP methodology underpinning RdSAP 10.

- **BRE.** *RdSAP 10: Reduced Data Standard Assessment Procedure — Conventions and Specifications.* Available from the BRE SAP website — the definitive reference for all input conventions, default assumptions, and evidence requirements discussed in this course.

- **BSI.** *PAS 2035:2023 — Retrofitting dwellings for improved energy efficiency. Specification and guidance.* Available from: https://knowledge.bsigroup.com/ — essential reading for assessors whose EPCs inform retrofit programmes.

- **MHCLG.** *Domestic Energy Performance Certificate: Reform and Methodology Update — Consultation Response and Policy Summary.* Available from: https://www.gov.uk/government/consultations — sets out the policy rationale for the transition to SAP 10.2 / RdSAP 10 and the revised EPC framework.

---

*© Meridian CPD 2026. All rights reserved. Unauthorised reproduction prohibited.*
*This course material is licensed to individual subscribers only.*