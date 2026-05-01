

# Future Homes Standard 2025: What Energy Assessors Need to Know
**Course ID:** MER-ALL-007 | **CPD Hours:** 1 | **Published:** May 2026
*© Meridian CPD 2026. All rights reserved.*

---

## Learning Objectives

- Identify the key regulatory changes introduced by the Future Homes Standard (FHS) and explain how they supersede the 2021 interim uplift to Part L of the Building Regulations in England.
- Describe the role of the Home Energy Model (HEM) as the replacement for SAP and understand the timeline for its adoption in new-build and existing-dwelling assessments.
- Evaluate the practical impact of tightened fabric performance standards, the effective prohibition of fossil-fuel heating in new homes, and revised ventilation and overheating requirements on energy assessment workflows.
- Apply knowledge of transitional provisions to correctly determine which calculation methodology and compliance standard applies to a given dwelling based on its building control timeline.
- Recognise the competency, software, and registration changes that accreditation bodies (Elmhurst, Quidos, Stroma, etc.) are implementing in response to FHS and plan accordingly for continued practice.

---

## Introduction

The Future Homes Standard is not a future event. Following the MHCLG consultation response published in March 2026, implementation is confirmed and the regulatory machinery is now in motion. For every working assessor in England — whether you lodge EPCs, file on-construction SAP calculations, or advise on retrofit — FHS changes the tools you use, the benchmarks you assess against, and the competencies you need to demonstrate.

At its core, the FHS sets a new performance target for dwellings: new homes are expected to produce approximately 75–80% fewer CO₂ emissions than one built to 2013 Part L standards. The mechanism for achieving this is twofold. First, fabric efficiency standards are being materially tightened, with lower U-values for walls, floors, roofs, and glazing, alongside stricter airtightness requirements. Second, fossil-fuel combustion heating in new homes is effectively ended; low-carbon heating systems — overwhelmingly heat pumps — become the default compliance pathway.

Critically for assessors, the Standard also retires SAP 10 for new-build assessments and replaces it with the Home Energy Model (HEM). HEM is a fundamentally different calculation engine: it uses a monthly-to-sub-hourly hybrid approach, incorporates updated climate datasets, and introduces new metrics. If you currently produce SAP calculations, your software, your data-entry conventions, and your understanding of what constitutes a "pass" are all changing.

For existing-dwelling EPC assessors, the transition is staged but still significant. RdSAP is being replaced by a reduced-data input version of HEM (commonly referred to as RdHEM or HEM for existing dwellings), which will alter how you record and process survey data and how the resulting energy ratings are generated. The timeline for this transition is staggered, but the direction is unambiguous.

This course cuts through the consultation language and the trade-press summaries. It sets out what has actually been confirmed, what the transitional arrangements look like, where the key uncertainties remain, and — most importantly — what you need to do in the next twelve months to stay current, compliant, and competent. No padding. No speculation. Just the regulatory substance and the workflow implications.

---

## Section 1: The Regulatory Framework — What FHS Actually Changes in Part L

The Future Homes Standard operates primarily through amendments to Approved Document L (Conservation of Fuel and Power) for dwellings in England, supported by a revised Approved Document O (Overheating) and consequential changes to Approved Document F (Ventilation). Understanding the hierarchy matters: FHS is not a standalone regulation — it is a set of performance targets and prescriptive backstop values delivered through existing Building Regulations mechanisms.

**New performance targets**

The headline metric shifts. Under SAP 10, compliance was assessed against the Target Emission Rate (TER) and Target Fabric Energy Efficiency (TFEE). Under HEM, the primary compliance metric becomes the Target Primary Energy Rate (TPER) alongside a space heating demand metric. The dwelling must also meet or beat a concurrent carbon emission target expressed in kgCO₂/m²/year. Assessors need to understand that compliance is now dual-track: you must satisfy both the energy and emissions targets simultaneously.

The notional building specification — the hypothetical "just-compliant" dwelling against which the actual design is compared — has been comprehensively updated. It now assumes a heat pump as the primary heating system, triple or high-performance double glazing, and significantly improved fabric U-values. This means a gas-boiler design cannot realistically meet the target, even with exceptional fabric, because the carbon intensity differential is too large.

**Fabric backstop values**

The FHS introduces tightened limiting fabric parameters (backstop values) that apply regardless of trade-offs elsewhere:

- **External walls**: The backstop U-value is set at a level consistent with full-fill or enhanced insulation strategies (assessors should verify the precise figure in the published Approved Document L, as values were refined between consultation and final publication).
- **Roofs, floors, and glazing**: All backstop values are lowered relative to the 2021 interim standard. For glazing, compliance with energy-related performance specifications should be cross-referenced with [L38] BS 6262-2 — Glazing for Buildings: Energy, light and sound, which provides the framework for evaluating thermal, solar, and optical properties of glazing units.
- **Airtightness**: The notional building assumes a design air permeability significantly below the 2021 interim level. While the backstop remains a maximum allowable figure, the practical implication is that achieving overall compliance without good airtightness is extremely difficult.

**Overheating and ventilation**

FHS does not exist in isolation. The tightened fabric and airtightness requirements amplify overheating risk, which is why Approved Document O and its simplified overheating assessment carry greater weight. Assessors working on new-build compliance will need to ensure that their modelling accounts for both the energy and overheating pathways — they are no longer optional extras but integral to sign-off.

The key message: Part L post-FHS is not an incremental uplift. It is a structural shift in what "compliant" looks like, and the notional building specification makes fossil-fuel heating a de facto impossibility for new homes.

---

## Section 2: The Home Energy Model — SAP's Replacement and What It Means for You

The retirement of SAP is the single most significant operational change for energy assessors. Whether you work on new-build or existing dwellings, your calculation methodology is being replaced. Understanding how and when is essential.

**What HEM is**

The Home Energy Model is an open-source, physics-based dwelling energy model developed under MHCLG's direction and hosted publicly (the source code is available on GitHub). Unlike SAP, which was a largely closed-specification monthly steady-state calculation, HEM uses a hybrid approach: it can operate at sub-hourly timesteps for certain calculations (particularly heating system responsiveness and thermal mass effects) while retaining monthly aggregation where appropriate.

Key technical differences from SAP include:

- **Updated climate data**: HEM uses more recent weather datasets and allows for regional variation at greater granularity. This means identical dwellings in different locations may show more divergent performance than under SAP.
- **Revised heating system modelling**: Heat pump performance is modelled with greater fidelity, including sensitivity to flow temperature, weather compensation, and system sizing. This matters because heat pumps are now the notional-building default — getting the modelling wrong has direct compliance consequences.
- **New metrics**: HEM outputs include primary energy, carbon emissions, and a space heating demand figure. The familiar A–G banding for EPCs is retained, but the underlying scores are generated differently. A dwelling that scored, say, a B under SAP 10 may score differently under HEM for the same physical specification.
- **Transparency**: The open-source nature of HEM means the calculation logic is auditable. This is a philosophical shift — assessors and software developers can inspect and query the methodology directly.

**Transition timeline**

For new-build assessments, HEM becomes the mandated calculation methodology aligned with the FHS implementation date. All design-stage and as-built SAP submissions for dwellings that fall under the new regulations must use HEM-compliant software.

For existing dwellings, the transition from RdSAP to HEM's reduced-data pathway is on a separate, later timeline. MHCLG has confirmed the direction of travel, and the development of reduced-data input conventions for HEM is underway. Assessors currently lodging EPCs using RdSAP should monitor announcements from their accreditation schemes closely, as the switchover date and any parallel-running period will be confirmed through scheme-level guidance.

**Software implications**

Every approved SAP/RdSAP software provider — Elmhurst's Design SAP, Stroma's FSAP, JPA Designer, and others — must release HEM-compliant versions. Beta and early-release versions are already in testing. Assessors should confirm with their software vendor the expected release date and whether any additional licensing or training is required. Do not assume your current software will auto-update to HEM; in many cases it will be a new product or a major version change requiring manual migration.

---

## Section 3: Impact on EPC Assessments, New-Build Compliance, and Retrofit Benchmarking

FHS doesn't just affect those producing on-construction calculations. Its consequences ripple across every domain of energy assessment.

**New-build compliance workflows**

If you produce design-stage or as-built energy calculations for new dwellings, your workflow changes substantially. The compliance checklist now includes:

- A dual-target check (primary energy rate and carbon emission rate) against the HEM-generated notional building.
- A fabric performance audit against tightened backstop U-values — every element must be individually verified, not just the aggregate.
- A mandatory space heating demand assessment.
- A cross-check against Approved Document O for overheating (the simplified method or dynamic thermal modelling, depending on the project).

Builder and developer clients will need educating. Many smaller housebuilders are still designing around gas-boiler specifications. Your role as the assessor producing the compliance calculation is to flag non-compliance early — at design stage, not at completion. The cost of redesigning a heating strategy post-construction is an order of magnitude higher.

**EPC production for existing dwellings**

Although the immediate FHS requirements target new build, the ripple effect on existing-dwelling EPCs is significant for two reasons. First, when HEM's reduced-data methodology replaces RdSAP, existing dwellings will be reassessed under a different engine. Energy ratings may shift — some properties will score better, some worse — purely due to methodological change. Second, as new-build standards rise, the relative performance gap between new and existing stock widens, which has implications for retrofit advice, EPC recommendation reports, and any future regulatory minimum standards for existing homes (e.g., Minimum Energy Efficiency Standards for the private rented sector).

Assessors should prepare clients — particularly landlords and portfolio holders — for the possibility that EPC ratings produced under the new methodology may differ from current certificates, even where no physical change has been made to the property.

**Retrofit benchmarking**

PAS 2035 retrofit projects and whole-house retrofit assessments increasingly reference EPC data as a baseline. The shift to HEM changes that baseline. Retrofit Coordinators and Assessors working within TrustMark-registered schemes should understand that:

- Pre-retrofit assessments produced under RdSAP and post-retrofit assessments produced under HEM are not directly comparable without conversion factors or caveats.
- The dwelling fabric metrics used in HEM may alter the cost-benefit hierarchy of retrofit measures. For example, changes in how thermal bridging or party wall heat loss is modelled could shift the relative value of different insulation interventions.
- Any government-funded retrofit programmes referencing EPC bands will need to clarify which methodology applies. Assessors should document clearly which engine was used for each assessment.

The overarching point is this: FHS is a new-build standard, but its methodological and benchmarking consequences extend across the entire assessment landscape. No assessor is unaffected.

---

## Section 4: Competency, Accreditation, and Preparing Your Practice

Knowing the technical content is necessary but not sufficient. You also need to navigate the accreditation, CPD, and business-practice changes that FHS triggers.

**Accreditation scheme responses**

Elmhurst, Quidos, Stroma, and other approved accreditation schemes are each implementing FHS-related updates to their assessor requirements. While the specifics vary by scheme, common themes include:

- **Mandatory FHS training modules**: Most schemes are requiring assessors to complete FHS/HEM-specific training before they can lodge calculations under the new methodology. Check your scheme's published timeline — in many cases, a deadline is already set.
- **Software certification**: Only software formally approved against the HEM specification will be accepted for lodgement. Schemes will publish approved software lists; using non-approved tools will result in rejected lodgements.
- **Audit and quality thresholds**: Expect increased audit scrutiny during the transition period. Schemes are aware that early HEM submissions carry higher error risk and will be sampling accordingly.

**What you should do now**

1. **Confirm your scheme's FHS requirements**: Log in to your accreditation scheme portal and review any published FHS/HEM transition guidance. Identify deadlines for training completion and software migration.
2. **Engage with HEM early**: The Home Energy Model source code and documentation are publicly available. Familiarise yourself with the input conventions and output metrics. You do not need to read the code line-by-line, but understanding the model's structure — what it calculates, how it differs from SAP — is non-negotiable professional knowledge.
3. **Audit your client base**: If you serve housebuilders, identify any projects currently at pre-planning or early design stage that will fall under FHS. Initiate conversations about heating system strategy and fabric specification now, before designs are locked.
4. **Plan for dual-running**: During the transition period, you may need to operate under both SAP/RdSAP and HEM, depending on transitional provisions and project timelines. Ensure you have access to both toolsets and understand which methodology applies to which project based on the building control initial notice or full plans application date.
5. **Budget for software and training costs**: New software licences, training course fees, and the time cost of familiarisation are real overheads. Factor them into your business planning for the next financial year.

The assessors who thrive through this transition will be those who treat it as a technical upgrade to their professional toolkit — not as an administrative inconvenience to be deferred until the last possible moment.

---

## Key Takeaways

- The Future Homes Standard delivers an approximate 75–80% carbon reduction for new homes relative to 2013 Part L, effectively mandating low-carbon heating and substantially tighter fabric standards.
- SAP is being replaced by the Home Energy Model (HEM) for new-build compliance calculations, with a separate later transition for existing-dwelling EPCs (replacing RdSAP).
- Compliance is now assessed against dual targets — primary energy rate and carbon emission rate — alongside fabric backstop values and a space heating demand metric.
- Fossil-fuel heating in new homes is effectively prohibited; the notional building specification assumes a heat pump, making gas-boiler compliance practically unachievable.
- Existing-dwelling EPC ratings may change under HEM's reduced-data methodology even where no physical alterations have been made — communicate this proactively to landlord and portfolio clients.
- Accreditation schemes are imposing mandatory HEM training, software certification requirements, and heightened audit procedures during the transition; confirm your scheme's specific deadlines immediately.
- Transitional provisions are date-sensitive, typically triggered by the building control application date — ensure you correctly identify which methodology and standard applies to each project.

---

## Self-Assessment Questions

**Q1.** What is the primary calculation methodology replacing SAP for new-build energy assessments under the Future Homes Standard?

A) RdSAP 10.2
B) PHPP (Passive House Planning Package)
C) The Home Energy Model (HEM)
D) SBEM (Simplified Building Energy Model)

**Correct answer: C**
*The Home Energy Model (HEM) is the MHCLG-mandated replacement for SAP for dwelling energy assessments. SBEM applies to non-domestic buildings, and PHPP is a voluntary Passivhaus tool.*

---

**Q2.** Under the FHS, new-build compliance requires the dwelling to satisfy which of the following?

A) Target Emission Rate only
B) Both a primary energy rate target and a carbon emission rate target, alongside fabric backstop values
C) A single fabric energy efficiency target with no emissions requirement
D) An air permeability target only

**Correct answer: B**
*FHS introduces dual-target compliance: primary energy and carbon emissions must both be met, alongside mandatory fabric backstop values and a space heating demand metric.*

---

**Q3.** Why is it practically impossible for a new home with a gas boiler to comply with the Future Homes Standard?

A) Gas boilers are explicitly banned by primary legislation
B) The notional building assumes a heat pump, creating a carbon emission differential that gas combustion cannot overcome even with excellent fabric
C) Gas boilers cannot be connected to new gas mains under the Gas Act
D) Gas boilers are incompatible with HEM software

**Correct answer: B**
*The FHS does not impose an outright statutory ban on gas boilers; however, the notional building specification assumes a heat pump, and the resultant carbon target is too stringent for combustion heating to meet in practice.*

---

**Q4.** Which transitional factor typically determines whether a new dwelling must comply with the FHS or the previous Part L standard?

A) The date the dwelling is physically occupied
B) The date of the building control initial notice or full plans application
C) The date the EPC is lodged
D) The date the developer purchased the land

**Correct answer: B**
*Transitional provisions under Building Regulations are typically triggered by the date of the building control application (initial notice or deposit of full plans), not by construction completion or EPC lodgement.*

---

**Q5.** How might the transition from RdSAP to HEM's reduced-data methodology affect existing-dwelling EPC ratings?

A) All ratings will automatically improve by one band
B) Ratings will remain identical because the physical dwelling has not changed
C) Ratings may change — either improving or worsening — due to differences in the underlying calculation methodology
D) Only dwellings with heat pumps will see any change

**Correct answer: C**
*A change in calculation methodology can alter the modelled energy performance of a dwelling even where its physical characteristics are unchanged. Assessors should prepare clients for potential rating shifts in either direction.*

---

## Further Reading

1. **MHCLG — The Future Homes Standard: 2025 Consultation Response and Government Response to the Future Homes Standard Consultation** (March 2026). Primary regulatory source. Available at: https://www.gov.uk/government/consultations/the-future-homes-standard-changes-to-part-l-and-part-f-of-the-building-regulations-for-new-dwellings

2. **HM Government — Approved Document L, Volume 1: Dwellings (2025 edition)**. The amended statutory guidance implementing FHS fabric and system performance requirements. Available via the Building Regulations Approved Documents page at: https://www.gov.uk/government/collections/approved-documents

3. **The Home Energy Model — Technical Documentation and Source Code**. MHCLG's open-source calculation engine. Available at: https://github.com/communitiesuk/epb-home-energy-model

4. **[L38] BS 6262-2 — Glazing for Buildings: Energy, light and sound**. British Standard providing the framework for evaluating glazing thermal, solar, and optical performance. Essential reference for assessing compliance of glazing elements against tightened FHS backstop U-values and solar factor requirements. Available via BSI: https://www.bsigroup.com

5. **HM Government — Approved Document O: Overheating (2025 edition)**. Revised statutory guidance on overheating risk assessment for new dwellings, directly linked to FHS fabric and airtightness standards. Available at: https://www.gov.uk/government/collections/approved-documents

6. **BRE — Home Energy Model: Assessor Guidance and Conventions**. Supplementary guidance for practitioners on HEM data input conventions and compliance reporting. Check BRE's publications page for the latest version: https://www.bregroup.com

---

*© Meridian CPD 2026. All rights reserved. Unauthorised reproduction prohibited.*
*This course material is licensed to individual subscribers only.*