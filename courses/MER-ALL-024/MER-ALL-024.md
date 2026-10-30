# Heating Series, Part 3: Cost, Carbon, Grid and the Assessor's View
**Course ID:** MER-ALL-024 | **CPD Hours:** 2 | **Published:** October 2026
*© Meridian CPD 2026. All rights reserved.*

---

## Learning Objectives

By the end of this course you should be able to:
- Work out the cost of a kilowatt hour of heat from a heat pump and from a gas boiler at the current Ofgem price cap, find the break-even seasonal performance factor, and explain why the comparison has to be re-run after 31 March 2027.
- Explain why the price ratio inside an RdSAP 10 rating differs from the ratio in the EPC's running costs and on a household bill, and which set of prices each part of an EPC uses.
- Calculate carbon per kilowatt hour of heat from the emission factors in RdSAP 10 and in SAP 10.3, and say when EPCs are due to change.
- State the Boiler Upgrade Scheme grant levels, the main eligibility conditions and the latest published uptake figures, with their dates.
- Describe the government's timetable for smart, flexible electricity use, and how RdSAP 10 treats tariffs, meters and controls for a heat pump.
- Enter a heat pump in RdSAP 10 correctly: database record or Table 4a default, the MCS installation factor, and the conventions that apply. Know what to record on site and when to refer the householder on.

---

## Introduction

Part 1 of the Heating Series covered how heat pumps work and what two government field trials measured. Part 2 covered design, siting and installer standards. This final part covers the questions householders put to an assessor once a heat pump is on the table. What will it cost to run? Is it lower carbon? What grant is there? Will the grid cope? What will it do to the EPC?

Most of those answers contain a number, and most of the numbers change: the price cap every quarter, electricity VAT and the off-gas grant uplift on 31 March 2027, and the EPC itself in the second half of 2027. So this course teaches the method as well as the figures, and every calculation shows its inputs so you can re-run it.

The aim is not to argue for or against heat pumps. It is to let you give an accurate, dated answer, say where it stops, and record what you see. You do not design, commission or judge the performance of a heat pump; where a householder needs that, suggest professional advice.

### Where this course applies

This course is written for England and Wales:
- **The Boiler Upgrade Scheme** "is open to people in England and Wales" (gov.uk, *Apply for the Boiler Upgrade Scheme*).
- **RdSAP 10** and its conventions apply to EPCs across the UK. Convention 9.02 has a separate Scottish version; the England, Wales and Northern Ireland version is used here.
- **Ofgem's price cap** figures are Ofgem's averages for direct debit customers on a default tariff.
- **PAS 2035:2023** applies where a scheme or client requires it.

### How the sources were handled

Every figure, threshold and quotation comes from a document opened for this course. The RdSAP 10 specification (BRE, version 4.0, 7 June 2026), the RdSAP 10 conventions (v12.2, applicable from 6 August 2026), the SAP 10.3 specification (version 12-06-2026), BRE's list of prices used for SAP and RdSAP fuel costs (from July 2026) and PAS 2035:2023 were read and are quoted briefly by section, table or convention. Where a source could not be opened, the course says so. The gaps that matter:
- **The Product Characteristics Data File.** The specification places the EPC's running-cost prices in its Table 191. The file itself was not opened; the course uses BRE's published list.
- **SAP 10.2 Tables 4a and 4b.** Only section 9.2.7 of SAP 10.2 could be read, so no default heat pump or boiler efficiencies are given.
- **Measured grid carbon intensity** and **measured heat pump peak demand** were not opened.
- **BS 40101:2022** is a paid standard. The Wider view panel uses BSI's listing and PAS 2035:2023's references to it.

Numbers marked "Calculated" are Meridian's arithmetic, with inputs shown.

---

## Section 1: Running Costs from the Price Cap

**In short:** You can work out what a unit of heat costs by dividing the unit price of the fuel by how efficiently it turns into heat. At the October to December 2026 price cap, electricity costs 3.30 times as much as gas per kilowatt hour. A heat pump therefore needs a seasonal performance factor of about 3.30 times the boiler's efficiency to match gas per unit of heat. VAT on electricity returns after 31 March 2027, so re-run the sums then.

### The cap, as at October 2026

Ofgem's price cap for 1 October to 31 December 2026 sets these average rates for a direct debit customer (Ofgem, *Changes to energy price cap between 1 October and 31 December 2026*, 26 August 2026):

| | Unit rate | Standing charge |
|---|---|---|
| Electricity | 26.32p per kWh | 54.83p per day |
| Gas | 7.97p per kWh | 29.68p per day |

Ofgem says "The government has removed VAT from electricity bills from 1 October 2026 to 31 March 2027", while gas still carries 5% VAT, and that costs "cannot be compared directly to previous periods because of this change." The cap for 1 January to 31 March 2027 is due to be announced on 25 November 2026.

### The price ratio

> Calculated: 26.32 ÷ 7.97 = 3.30

At this cap a kilowatt hour of electricity costs 3.30 times as much as one of gas. A heat pump turns each kilowatt hour of electricity into several of heat; a boiler turns each kilowatt hour of gas into slightly less than one. The question is which effect is larger.

### Cost per kilowatt hour of heat

Divide the unit price by the efficiency: the seasonal performance factor (SPF) for a heat pump, the seasonal efficiency as a decimal for a boiler.

The heat pump figures are the field-trial results from Part 1, at the H4 boundary. The Electrification of Heat interim report gives a median air source SPFH4 of 2.80 (interquartile range 2.53 to 3.09, n = 291), against 2.44 in the earlier RHPP trial (Energy Systems Catapult, *Interim insights from heat pump performance data*, sections 1.1.1 and 5.1). Part 1 sets out their limits.

No opened source gives a typical gas boiler efficiency (the defaults are in SAP 10.2 Table 4b, which was not read). The boiler figures are illustrative inputs, not published values. Use the boiler's own record where you have it.

| System | Efficiency used | Sum | Pence per kWh of heat |
|---|---|---|---|
| Heat pump, RHPP median | SPF 2.44 | 26.32 ÷ 2.44 | 10.79 |
| Heat pump, EoH lower quartile | SPF 2.53 | 26.32 ÷ 2.53 | 10.40 |
| Heat pump, EoH median | SPF 2.80 | 26.32 ÷ 2.80 | 9.40 |
| Heat pump, EoH upper quartile | SPF 3.09 | 26.32 ÷ 3.09 | 8.52 |
| Gas boiler, illustrative | 80% | 7.97 ÷ 0.80 | 9.96 |
| Gas boiler, illustrative | 85% | 7.97 ÷ 0.85 | 9.38 |
| Gas boiler, illustrative | 90% | 7.97 ÷ 0.90 | 8.86 |

All figures are calculated. At this cap, a heat pump at the EoH median and a boiler at an assumed 85% cost almost the same per unit of heat: 9.40p against 9.38p.

### The break-even SPF

You can turn this round. The heat pump matches the boiler per unit of heat when:

> SPF = price ratio × boiler efficiency

| Boiler efficiency (illustrative) | Sum | Break-even SPF |
|---|---|---|
| 80% | 3.30 × 0.80 | 2.64 |
| 85% | 3.30 × 0.85 | 2.81 |
| 90% | 3.30 × 0.90 | 2.97 |

Above the break-even SPF the heat pump costs less per unit of heat; below it, more. That is why two neighbours can report different outcomes: the result depends on the SPF achieved, the boiler replaced and the prices at the time.

The Energy Saving Trust says that on standard tariffs "heat pumps can cost slightly more to run than new gas or oil boilers", but that "by switching to a heat pump time‑of‑use tariff, you can reduce running costs significantly" (EST, *Air source heat pumps*, updated 16 July 2026). Tariffs are covered in Section 5.

### Standing charges and a whole-year illustration

A household that removes its gas supply stops paying the gas standing charge; the electricity standing charge is paid either way.

> Calculated: 29.68p × 365 days = £108.33 a year

Take an assumed demand of 10,000 kWh of heat a year (an illustration, not a typical figure for any house type).

| | Fuel used | Unit cost | Annual fuel cost |
|---|---|---|---|
| Heat pump, SPF 2.80 | 10,000 ÷ 2.80 = 3,571 kWh | × 26.32p | £940 |
| Heat pump, SPF 2.44 | 10,000 ÷ 2.44 = 4,098 kWh | × 26.32p | £1,079 |
| Gas boiler, 85% (illustrative) | 10,000 ÷ 0.85 = 11,765 kWh | × 7.97p | £938 |
| Gas boiler, 90% (illustrative) | 10,000 ÷ 0.90 = 11,111 kWh | × 7.97p | £886 |

If the gas supply is removed, add the £108 standing charge to the gas rows when comparing: £1,046 and £994. All figures are calculated and rounded to the nearest pound.

### After 31 March 2027

As an illustration only, if 5% VAT were added back to the current electricity rate and nothing else changed:

> Calculated: 26.32 × 1.05 = 27.64p per kWh; price ratio 27.64 ÷ 7.97 = 3.47; break-even SPF at an illustrative 85% boiler, 3.47 × 0.85 = 2.95

In practice the cap is reset every quarter, so nothing else will stay the same. The point is that the break-even SPF moves with the price ratio. Date any figure you give, and do not repeat a winter 2026 comparison unchanged in spring 2027.

**Visual:** Worked-numbers chart. Horizontal bars, pence per kWh of heat at the October to December 2026 cap: heat pump at SPF 2.44, 2.53, 2.80 and 3.09 (10.79p, 10.40p, 9.40p, 8.52p) in lime; gas boiler at 80%, 85% and 90% (9.96p, 9.38p, 8.86p) in grey, "illustrative efficiency". Dashed line at the 85% boiler. Side panel: "Break-even SPF = 3.30 × 0.85 = 2.81." Footer: "Electricity VAT-free to 31 March 2027. Re-run after. Meridian arithmetic."

---

## Section 2: Three Sets of Prices: Bills, the Rating and the EPC Running Costs

**In short:** An EPC does not use today's tariffs. RdSAP 10 calculates the energy rating from the prices in its Table 32, which repeat the SAP 2012 prices, with electricity 3.79 times the price of gas. The running costs and savings shown on the EPC use a second set, BRE's fuel-cost prices from July 2026, where the ratio is 4.10. A household bill on the October 2026 cap uses a third set, at 3.30. Expect the three to point in different directions.

### What the specification says

Section 19.1 of the RdSAP 10 specification says the rating "is to be calculated using Table 32 prices (not Table 12)", and that these "are the same as in Table 12 of the SAP 2012 specification". The conventions repeat the point on their front page: "Use RdSAP v10 Table 32 when referring to Fuel prices."

Section 20 sets a second set for the certificate's costs: incremental savings and "total running costs" use the prices "in Table 191 of the Product Characteristics Data File". Because every rating must use the SAP 2012 prices, "software must maintain two sets of fuel prices" (section 20). BRE publishes the current cost prices as *Prices used by SAP/RdSAP for calculation of fuel costs*, from July 2026. The data file itself was not opened, so the figures below are taken from BRE's list. The householder's bill is a third set:

| | Used for | Electricity (standard) | Mains gas | Ratio |
|---|---|---|---|---|
| RdSAP 10 Table 32 | The energy efficiency rating (and its improvement steps) | 13.19p per kWh | 3.48p per kWh | 3.79 (calculated) |
| BRE fuel-cost prices, from July 2026 | Running costs and savings shown on the EPC | 26.00p per kWh; £192 a year standing charge | 6.34p per kWh; £113 a year standing charge | 4.10 (calculated) |
| Ofgem cap, Oct to Dec 2026 | The household's actual bill (default tariff) | 26.32p per kWh | 7.97p per kWh | 3.30 (calculated) |

> Calculated: 13.19 ÷ 3.48 = 3.79; 26.00 ÷ 6.34 = 4.10

The two electricity unit prices for running costs and the bill are close (26.00p and 26.32p). The gas prices are not (6.34p and 7.97p), which is most of the difference between the two ratios.

### Why the ratios matter

> Calculated, rating prices: heat pump at SPF 2.80, 13.19 ÷ 2.80 = 4.71p per kWh of heat; gas boiler at an illustrative 85%, 3.48 ÷ 0.85 = 4.09p; break-even SPF 3.79 × 0.85 = 3.22

> Calculated, EPC running-cost prices: heat pump at SPF 2.80, 26.00 ÷ 2.80 = 9.29p per kWh of heat; gas boiler at an illustrative 85%, 6.34 ÷ 0.85 = 7.46p; break-even SPF 4.10 × 0.85 = 3.49

At the cap the break-even SPF was 2.81. At the same illustrative boiler efficiency it is 3.22 inside the rating and 3.49 in the EPC's running costs. Both EPC price sets are less favourable to electric heating than the October 2026 cap. That is a property of the price sets, not a statement about any home, and it is one reason a household's bills and its EPC can move differently after a heat pump install. Another is that the EPC uses RdSAP's efficiency for the heat pump (Section 6), not a measured SPF.

Two more features of Table 32:
- **The energy cost deflator** (0.42) is applied before the rating is calculated, so the rating does not move with general fuel price inflation, but individual ratings "are affected by relative changes in the price" of particular fuels (note (r)).
- **Standing charges.** For energy ratings the standard electricity standing charge "is omitted"; the off-peak standing charge is added where heating or hot water uses off-peak electricity, and the gas standing charge where gas is used for space or water heating (note (a)).

### The improvement threshold uses current prices

The EPC's measures list uses both price sets. A recommendation needs to raise the rating by at least one SAP point (0.5 for three small measures), and is dropped as "Cost saving too small" when the "Total energy cost reduction is less than £10 when recalculated using current fuel prices". The specification's own example is a measure that adds 0.51 points while "total energy cost increases", because of "differential price changes" since the SAP Table 12 prices were set (section 20).

You can tell a householder, accurately, that the rating uses reference prices set for SAP 2012, that the EPC's costs use BRE's current list, and that neither is their tariff. For their own running costs, the Section 1 method with their tariff and a designer's SPF estimate is closer to the question.

**Visual:** Twin-to-rule-out grid. Three columns: "Your bill (Ofgem cap, Oct to Dec 2026)", "EPC rating (RdSAP 10 Table 32, SAP 2012 prices)" and "EPC running costs (BRE prices from July 2026)". Rows: electricity price, gas price, ratio, break-even SPF at an illustrative 85% boiler, what it is used for. Cells: 26.32p / 7.97p / 3.30 / 2.81; 13.19p / 3.48p / 3.79 / 3.22; 26.00p / 6.34p / 4.10 / 3.49. Footer: "Three price sets. Do not compare across columns. Meridian arithmetic."

---

## Section 3: Carbon per Unit of Heat

**In short:** RdSAP 10 uses SAP 10.2's emission factors: 0.136 kg CO2e per kWh for electricity and 0.210 for mains gas. SAP 10.3, the current full SAP, has 0.086 and 0.214. Divide each by efficiency to get carbon per unit of heat. On RdSAP's factors a heat pump at SPF 2.80 comes to about 0.049 kg, against 0.247 kg for a boiler at an illustrative 85%. On SAP 10.3's factors the gap is wider.

### The factors in the EPC

Section 19.2 of the RdSAP 10 specification says both the CO2 factors and the primary energy factors "are the same as in Table 12 of SAP10.2 specification". They are replicated in Table 32:

| Fuel | Emission factor (kg CO2e per kWh) | Primary energy factor |
|---|---|---|
| Mains gas | 0.210 | 1.130 |
| Heating oil | 0.298 | 1.180 |
| Bulk LPG | 0.241 | 1.141 |
| Electricity, any tariff | 0.136 | 1.501 |

Three notes to Table 32 matter:
- The figures are "CO2 equivalent" values, including methane and nitrous oxide.
- For electricity, "The average figure given in this table is therefore not used directly": the worksheet uses monthly factors from SAP 10.2 Tables 12d and 12e (notes (s) and (t)), which were not opened.
- The electricity factors "are a 5-year projection for 2020-2025", not a measurement of any particular year.

### Worked numbers

Using the annual factors as an illustration (an EPC, using monthly factors, will differ):

| System | Sum | kg CO2e per kWh of heat |
|---|---|---|
| Heat pump, SPF 2.44 | 0.136 ÷ 2.44 | 0.056 |
| Heat pump, SPF 2.80 | 0.136 ÷ 2.80 | 0.049 |
| Gas boiler, illustrative 85% | 0.210 ÷ 0.85 | 0.247 |
| Gas boiler, illustrative 90% | 0.210 ÷ 0.90 | 0.233 |
| Oil boiler, illustrative 85% | 0.298 ÷ 0.85 | 0.351 |

> Calculated: at SPF 2.80 against gas at 85%, 0.049 ÷ 0.247 = 0.20, so about 80% less per unit of heat on these factors.

For the 10,000 kWh illustration in Section 1:

> Calculated: heat pump at SPF 2.80, 3,571 kWh × 0.136 = 486 kg CO2e; gas boiler at 85%, 11,765 kWh × 0.210 = 2,471 kg CO2e

The same break-even method works for carbon. The factor ratio is 0.136 ÷ 0.210 = 0.65, so on these annual factors a heat pump emits less than a gas boiler per unit of heat whenever its SPF is above 0.65 times the boiler's efficiency.

> Calculated: carbon break-even SPF against gas at an illustrative 85%, 0.65 × 0.85 = 0.55

That is well below the medians reported in both field trials in Part 1. On these factors, the cost break-even in Section 1 is the tighter of the two tests.

The EPC also reports primary energy:

> Calculated: heat pump at SPF 2.80, 3,571 × 1.501 = 5,360 kWh; gas boiler at 85%, 11,765 × 1.130 = 13,294 kWh

### SAP 10.3

The gov.uk SAP page (updated 8 June 2026) says "The current version of SAP is SAP 10.3", that SAP 10.3 is currently the sole methodology available, and that "The current version of RdSAP is RdSAP 10.0.1". The RdSAP 10 specification of 7 June 2026 still states "Heat pumps - Calculation according to SAP 10.2" and takes its emission factors from SAP 10.2 (Introduction; section 19.2). No opened source says when, or whether, RdSAP will move to SAP 10.3's factors.

The SAP 10.3 specification (version 12-06-2026) lists Table 12 among its changes from SAP 10.2 (Introduction). Its Table 12 gives:

| Fuel | SAP 10.2 / RdSAP 10 (kg CO2e per kWh; PE factor) | SAP 10.3 (kg CO2e per kWh; PE factor) |
|---|---|---|
| Mains gas | 0.210; 1.130 | 0.214; 1.12 |
| Heating oil | 0.298; 1.180 | 0.298; 1.136 |
| Electricity, any tariff | 0.136; 1.501 | 0.086; 1.969 |

In SAP 10.3 the annual electricity figure "is used directly in the SAP worksheet"; the monthly factors in its Table 12d "are for comparison purposes only" (notes (s) and (t)).

> Calculated, SAP 10.3 factors: heat pump at SPF 2.80, 0.086 ÷ 2.80 = 0.031 kg CO2e per kWh of heat (SPF 2.44: 0.035); gas boiler at an illustrative 85%, 0.214 ÷ 0.85 = 0.252 (90%: 0.238); 10,000 kWh illustration, 3,571 × 0.086 = 307 kg against 11,765 × 0.214 = 2,518 kg

> Calculated: factor ratio 0.086 ÷ 0.214 = 0.40; carbon break-even SPF against gas at 85%, 0.40 × 0.85 = 0.34; primary energy, 3,571 × 1.969 = 7,031 kWh against 11,765 × 1.12 = 13,177 kWh

On SAP 10.3's factors the heat pump's carbon advantage is larger and its primary energy advantage smaller than on RdSAP's. If a new-build SAP assessment and an EPC for similar homes show different carbon figures, the version difference is one possible reason. SAP 10.3's Table 12 also has its own fuel prices (electricity 16.49p, gas 3.64p); they are not the prices in an RdSAP rating.

**Visual:** Worked-numbers chart. Two panels side by side. Left: kg CO2e per kWh of heat, paired bars (RdSAP 10 / SAP 10.3) for heat pump SPF 2.44 (0.056 / 0.035), SPF 2.80 (0.049 / 0.031) and gas at 85% (0.247 / 0.252), plus oil at 85% (0.351, both). Right: the 10,000 kWh illustration, heat pump 486 kg / 307 kg against gas 2,471 kg / 2,518 kg. Footer: "Annual factors: RdSAP 10 Table 32 (SAP 10.2; worksheet uses monthly electricity factors) and SAP 10.3 Table 12. Boiler efficiencies illustrative. Meridian arithmetic."

---

## Section 4: The Boiler Upgrade Scheme

**In short:** The Boiler Upgrade Scheme, open in England and Wales, gives £7,500 towards an air source or ground source heat pump, £2,500 towards an air-to-air heat pump and £5,000 towards biomass in limited cases. An extra £1,500 applies until March 2027 where oil or LPG heating is replaced and there is no mains gas. There is no insulation condition, and an EPC is no longer required. Check current guidance before quoting.

### Grant levels

The gov.uk page *Apply for the Boiler Upgrade Scheme: what you can get* (metadata updated 19 October 2026) and Ofgem's *Installer Guidance V5.1* (2 July 2026, para 1.02) give:

| Technology | Grant |
|---|---|
| Air source (air-to-water) heat pump | £7,500 |
| Ground source heat pump, including water source and shared ground loops | £7,500 |
| Air-to-air heat pump (residential only) | £2,500 |
| Biomass boiler (limited circumstances) | £5,000 |
| Air source or ground source replacing oil or LPG, off the gas grid | £7,500 + £1,500 = £9,000, from 21 July 2026 to 31 March 2027 |

Capacity limits are 45 kWth for a single system, 70 kWth with additional heat pumps and 300 kWth for shared ground loops. "You cannot get a grant for a hybrid heat pump system" (gov.uk, what you can get). Part 1 covers system types.

### The off-gas uplift

Ofgem sets the conditions for the £9,000 rate (V5.1, paras 3.46 to 3.51). The property must not be fuelled by mains gas, and "capped or clamped supply meter points are still considered as being fuelled by mains gas"; it must have no current gas meter point record and must not be on a heat network or be a new build (3.47). The system replaced must be oil or LPG (3.48). Self-builds cannot get the uplift but may still get £7,500 (3.50). gov.uk says the extra £1,500 is available "Until March 2027"; the pages opened show no end date for the scheme itself.

### Eligibility

From gov.uk, *Check if you're eligible*:
- The applicant must "own the property you're applying for", including second homes, businesses and properties rented to tenants.
- Excluded: "most new build properties", "social housing", and a property already given government funding or support for a heat pump or biomass boiler.
- "You're still eligible if you've already had funding to make your property more energy efficient", insulation being an example.
- "Your installer must commission and install the heat pump within 120 days of applying for the grant."

Ofgem's guidance has a 120-day rule for the other order of events: "the application must be properly made within 120 days of the commissioning date" (V5.1, para 3.13). Vouchers last three months for air-to-water, air-to-air and biomass, and six months for ground source (para 1.06).

### Insulation and the EPC

Two conditions assessors will remember have gone:
- **Insulation.** Ofgem's summary of updates for version 3 of its installer guidance (undated; its web address places it in May 2024) says paragraph 3.18 was added to address "the removal of EPC insulation requirements on the scheme", and installers "should discuss the benefits of energy efficiency measures with property owners" (on para 5.6).
- **The EPC.** From 28 April 2026 a valid EPC is no longer needed to apply. If one exists, its number must still be given; a valid EPC is the most recent for the property and no more than ten years old. Without one, installers give other evidence, such as a recent utility bill and photographs of the existing system (V5.1, paras 3.40, 3.41 and 3.43).

So your EPC may form part of a BUS application, but it is no longer a condition of one. The technical conditions sit with the installer: an in-situ SCOP of at least 2.8 from the MCS calculator, checked against the MCS installation certificate, and an electrically driven compressor (paras 3.83 and 3.84). Part 1 explains why a calculated SCOP is not a measured SPF.

### Uptake, as published

| Measure | Figure | Source and date |
|---|---|---|
| Voucher applications received | 160,874 | Ofgem, *BUS monthly scheme update*, 23 May 2022 to 30 September 2026 (updated 13 October 2026) |
| Vouchers issued (excluding expired, revoked or withdrawn) | 106,185, worth £763,205,500 | same |
| Vouchers redeemed | 96,611, grants paid £687,450,500 | same |
| Year 5 budget remaining (1 April 2026 to 31 March 2027) | £143,585,000 | same; Ofgem calls it a dynamic figure |
| Grants paid to 31 July 2026 | 90,115, worth £635,377,500 | Ofgem, *BUS Quarterly Report Issue 17* (31 August 2026), Figure 2 |
| Grants paid in Wales to 31 July 2026 | 4,722 (5.2%) | same, Figure 6 |
| Year 5 budget | £400,000,000 | same, Figure 3 |

The quarterly report notes that part of the budget is set aside for future innovation activity, so it may not equal the money available for vouchers (Figure 3, footnote 13). The technology split is in Part 1.

> Calculated: 96,611 ÷ 106,185 = 91% of issued vouchers (as counted on 30 September 2026) had been redeemed.

Quote these counts with their dates.

**Visual:** Traffic light. A BUS fact check in three bands, each row with its source. Green (stated conditions): owner of the property; England or Wales; replacing fossil fuel heating; installer with MCS certification. Amber (check before quoting): "Oil or LPG, no mains gas (capped meter counts as gas): £9,000 to 31 March 2027"; the two 120-day rules; "EPC not required; if one exists, give its number". Red (outside the scheme as stated): hybrid with a boiler; most new builds; social housing; earlier government funding for a heat pump or biomass boiler. Footer: "Guidance as at 19 October 2026. The installer and Ofgem confirm eligibility."

---

## Section 5: The Grid, Tariffs and Smart Control

**In short:** The government aims for 10 to 12 GW of consumer-led flexibility by 2030, with businesses that control home heat pumps, chargers and batteries needing a licence from March 2028. NESO says greater flexibility could cut peak demand in half. In RdSAP 10, a heat pump on a dual meter takes the 10-hour tariff, and a smart meter does not change the calculation. Record the meter, tariff evidence and controls as you find them.

### Why peak matters

NESO's *Future Energy Scenarios: Pathways to Net Zero 2025* press release (July 2025) says "electricity demand could rise nearly threefold from 290 Terawatt-hour (TWh) today to between 705 and 797 TWh in 2050", and that "introducing greater demand flexibility could cut peak demand in half." It refers to "significant increases in heat pump installations" but gives no numbers. Published measurements of heat pump demand at peak times could not be opened, so no per-home figure is given.

### The government's flexibility programme

The Department for Energy Security and Net Zero's *Smart Secure Electricity Systems (SSES) Programme: Government response to the 2025 SSES Licensing consultation* (2026) sets out the plan:

| Date | Step | Source in the response |
|---|---|---|
| Autumn 2026 | Load control licensing regulations to be laid in Parliament | Section 1.3 |
| March 2027 | Licence applications open, "subject to Parliamentary scrutiny" | Section 1.3 |
| March 2028 | Requirement to hold a licence comes into force | Section 1.3 |
| 31 December 2027 | Phase 1 energy smart appliance regulations: minimum requirements for smart battery storage and EV charge points | Section 1.1 |
| 2030 | "10-12 GW" of consumer-led flexibility (the aim) | Section 1.1 |

Licensing covers "domestic-scale technologies such as EVSCPs, relevant heat technologies and home batteries" (section 2.2); the licence is held by the load controller, not the household. The response says the Phase 1 regulations will also mandate that electric heating appliances are "placed on the market with smart functionality", but gives no date for them (section 1.1). Do not quote 31 December 2027 for heat pumps.

The ministerial foreword says: "Homes with heat pumps could save more than £250 each year by adopting a smart tariff." The response bases this on departmental analysis of one supplier's heat pump time-of-use tariff against price cap rates, July 2023 to July 2024, assuming the heat pump does not run at peak times. Households avoiding 4pm to 7pm use "could save £200 annually" on a tariff that varies with market rates; no basis is given for that figure. Both are government estimates, not measurements for any home.

### How RdSAP 10 treats tariffs and meters

RdSAP 10's electricity tariffs are standard, 7-hour, 10-hour, 18-hour and 24-hour (Table 32); there is no separate heat pump or time-of-use tariff. Section 12 sets the rules:
- A single meter means the standard tariff.
- An unknown meter is treated as single, "except where" heating is intended for off-peak or "main heating is ground source or water source heat pump".
- On a dual meter, rule 3 says that where main heating is a "heat pump (211 to 224, 521 to 524, or database)", "it is 10-hour tariff", unless an earlier rule applies.

Table 32's 10-hour rating prices are 14.68p (high) and 7.50p (low), with a £23 extra standing charge. For the EPC's running costs, BRE's July 2026 list gives 28.26p and 19.28p, with £87 extra. The split between rates is in SAP 10.2 Table 12a, which was not opened.

Convention 9.13 says that if choosing a particular tariff, "additional information should be gathered such as recent electricity bill", and that smart meter evidence must be "a smart meter unit or a portable display" showing readings. The specification records a smart meter (items 1-17 and 1-18) but it "Does not affect the calculation; used for statistical reasons only" (Table 31).

### Controls, PV and batteries

- A smart thermostat can be entered alongside certain control types and "is always defined from PCDB" (section 10.3). A compensating controller is a yes/no entry, from the database if "Yes" (Table 31).
- Measure G1-3 (Table 33) recommends "Time and temperature zone control" where a heat pump with radiators or underfloor heating has less than that.
- For PV, convention 9.05: if the peak power cannot be found, "the declared net capacity (DNC) stated on the MCS certificate may be used instead", and PV counts only if the dwelling "has a PV generation meter serving it".
- For batteries, convention 9.05 asks for "photographic or written evidence" of the battery's make, model and usable capacity in kWh, and otherwise "a default of 5kWh per battery". Table 31 (item 11-4) also gives 5kWh; section 11.2 prints "5kW". The conventions take precedence over the specification.

**Visual:** Cutaway house map. A semi-detached house cut away at the rear. Callouts: (1) outdoor unit, "10-hour tariff if dual meter (section 12, rule 3)"; (2) smart meter and display, "recorded; no effect on the calculation"; (3) zoned thermostats, "measure G1-3"; (4) roof PV and generation meter, "convention 9.05"; (5) home battery, "make, model and kWh, or 5kWh default (convention 9.05)". Side timeline: autumn 2026 regulations laid; March 2027 licence applications; 31 December 2027 battery and charge point rules; March 2028 licence required; 2030 aim 10 to 12 GW.

---

## Section 6: Heat Pumps in RdSAP 10

**In short:** RdSAP 10 calculates heat pumps as SAP 10.2 does. Use the product database whenever you can identify the model; otherwise the software uses a Table 4a default. An MCS installation factor raises a Table 4a default only where an MCS certificate is provided. Record design flow temperature as unknown unless documents show a low temperature design and commissioning. Where a heat pump is part of the system, it is main system 1.

### Database first

Section 10.1 of the RdSAP 10 specification says that for boilers, micro-CHP and heat pumps "the database is to be used whenever possible", because there is "a significant difference" between database efficiency values and the Table 4a/4b defaults "in many cases". Data item 7-3 asks for the "Brand Name, model, and model qualifier (or/and index number) whenever possible", and if the product can be identified "its characteristics are obtained via the database" (Table 31).

If the heat pump is in the database but its plant size ratio is out of range, the software reports this and advises the assessor to select "the appropriate one from Table 4a in SAP10.2" (section 10.1).

Convention 4.07, dated 1 March 2022, covers the case where the model cannot be found: "If a boiler or a heat pump is not in the PCDB, use default." The convention does not name the default or mention MCS.

### The MCS installation factor

SAP 10.2 section 9.2.7 says "The preferred source of annual efficiency data for heat pumps is the PCDB." Where a Table 4a default is used, an installation factor from its table is applied to the efficiency, and these factors "apply only where an MCS certificate, or equivalent, has been produced by the installer" (SAP 10.2, section 9.2.7). Section 9.2.7 of SAP 10.3 prints the same factors and adds that the certificate is "made available to the assessor".

| Heat pump type (Table 4a rows) | Space heating | Water heating |
|---|---|---|
| Ground source, flow 35°C or below (211, 213) | × 1.39 | × 1.32 |
| Air source, flow 35°C or below (214) | × 1.47 | × 1.03 |
| Heat pump for water heating only (941) | – | × 1.03 |
| Ground source, other cases (221, 223) | × 1.53 | × 1.35 |
| Air source, other cases (224) | × 1.29 | × 1.12 |

The RdSAP data item is "For heat pumps, MCS installation (yes/no)", with the comment "Yes only if documentary evidence available" (Table 31, item 7-4). The factor applies to a Table 4a efficiency, not to a database value. So where the model is not in the database, the MCS certificate changes the efficiency the software uses, and "yes" can be entered only on the document.

### Emitters and flow temperature

Item 7-4 also covers:
- **Emitter type** for heat pumps to water: radiators, underfloor or fan coil units ("Fan coil units only for heat pumps").
- **Design flow temperature**: unknown, over 45°C, 45°C or below and over 35°C, or 35°C or below; "Unknown unless documentary evidence is available giving the design flow temperature". The middle band is "not available for heat pumps from SAP Tables".

Convention 4.01b says the design flow temperature for condensing boilers and heat pumps "should be recorded as unknown" unless there is documentary evidence that the system was "designed and commissioned as a low temperature one". Part 2 covers the design documents.

For a heat pump serving both radiators and underfloor heating, convention 4.01a says "enter radiators when they are serving 50% or more of the total floor area". The conventions state that where a convention conflicts with the published specification, "the Convention takes precedence" (front page).

### Main system 1, hot water and other conventions

| Convention | What it says for heat pumps (v12.2) |
|---|---|
| 4.09a (added 1 January 2024) | Single systems with multiple outputs are entered as two main systems. "Any system that has a heat pumps, this must be main system 1" (sic). |
| 6.04 | A separate boiler or heat pump for hot water only: main system 1 provides 100% of space heating; main system 2 provides hot water with 0% of the heat. |
| 4.05b (added 13 July 2026) | Heat as a service, where the provider owns or operates the generator, is treated as community heating. "Specific documentary evidence must be provided". "Where the service is powered by electricity, use community heat pump." |
| 9.04 | Cooling systems: "Do not include reversible heat pumps." |
| 9.02 | Documentary evidence must relate to the property. "Evidence of intent to install does not on its own qualify". |

For hot water, Table 29 adds that a supplementary immersion heater is assumed "if generic heat pump supplying space and water heating (from Table 4a in SAP10.2)", but is "Not applicable if heat pump from database", because supplementary heating is already included in the database record's water heating efficiency.

### Heat pumps in the recommendations

Table 33 has two heat pump measures: Z1 (air or ground source heat pump with radiators) and Z2 (with underfloor heating). Both apply to a "House or bungalow (not flat or maisonette)"; for flats and maisonettes "heat pump is not recommended". They apply where the heating is not already a heat pump or community heating, and need the dwelling to be "fairly insulated, e.g. measures A to Q2 are NOT triggered". The heat pump is recommended when the rating with it is "equal or better than" with the heating measure the software would otherwise recommend. Air and ground source heat pumps are "not alternative measures anymore" (Introduction).

So an RdSAP heat pump recommendation follows the rating's own rules: house type, fabric measures and rating prices. It is not a design assessment or a BUS eligibility check.

**Visual:** Section detail with the critical point highlighted. A flow strip: "Model identified? (item 7-3)" → yes: "PCDB record, own efficiency"; no, or plant size ratio out of range: "Table 4a default (4.07; 10.1)" → "MCS certificate seen? (7-4)" → yes: "× installation factor, e.g. air source other cases × 1.29 space, × 1.12 water (SAP 10.2, 9.2.7)"; no: "default only". The MCS certificate box in lime: "Yes only on documentary evidence". Beneath: "Flow temperature unknown without documents (4.01b). Heat pump = main system 1 (4.09a)."

---

## Section 7: EPC Reform, What You Record, and When to Refer

**In short:** The government has moved the launch of EPC reform to the second half of 2027, and the Home Energy Model will in time replace SAP for ratings. Until then, RdSAP 10 applies. On site, record the heat pump's identity, documents, emitters, controls, meter and hot water as found. Under PAS 2035:2023, the coordinator evaluates every project. Refer performance, cost and grant questions to the right person.

### EPC reform: where it stands

The gov.uk consultation page *Reforms to the Energy Performance of Buildings regime* was updated on 9 March 2026 to say the government has "decided to move the launch of the reforms to the second half of 2027". The same page records a partial government response confirming four new headline metrics for new-style domestic EPCs. The metrics are not set out here; Meridian's Home Energy Model series will cover them.

The gov.uk SAP page says "The Home Energy Model will replace the SAP for the energy rating of dwellings", that its launch was delayed so that it is "as robust as possible", and that the Home Energy Model consultation on EPCs ran from 21 January to 18 March 2026.

| Date | Point | Source |
|---|---|---|
| 21 January to 18 March 2026 | Home Energy Model: EPCs consultation | gov.uk SAP page |
| 9 March 2026 | Launch of EPC reforms moved to the second half of 2027 | gov.uk EPC reform consultation page |
| 8 June 2026 | SAP 10.3 the current SAP; RdSAP 10.0.1 the current RdSAP (still on SAP 10.2 for heat pumps) | gov.uk SAP page; RdSAP 10 specification |
| July 2026 | BRE fuel-cost prices for EPC running costs | BRE price list |
| 31 March 2027 | Electricity VAT cut ends; off-gas BUS uplift ends | Ofgem cap page; BUS V5.1 |
| Second half of 2027 | New-style EPCs | gov.uk EPC reform consultation page |

### What you record on site

| Item | What to record | RdSAP reference |
|---|---|---|
| Identity | Brand, model, qualifier or index number from the data plate or documents; photograph the plate | Table 31, 7-3; section 10.1 |
| Installation evidence | MCS certificate: seen or not seen, with date and installer | Table 31, 7-4; SAP 10.2, 9.2.7 |
| Design flow temperature | Value only from a design or commissioning document; otherwise unknown | Convention 4.01b; Table 31, 7-4 |
| Emitters | Radiators, underfloor or fan coils; share of floor area if mixed | Convention 4.01a |
| System role | Heat pump as main system 1; any boiler, hot-water-only unit or heat-as-a-service arrangement | Conventions 4.09a, 6.04, 4.05b |
| Hot water | Cylinder, immersion, whether the heat pump heats water | Table 29; convention 6.04 |
| Controls | Programmer, thermostats, zones, smart thermostat, compensation | Section 10.3; Table 31 |
| Meter and tariff | Single or dual meter; smart meter present; tariff evidence such as a recent bill | Section 12; convention 9.13 |
| PV and battery | kWp or DNC, generation meter; battery number, make, model and usable kWh | Convention 9.05; Table 31, 11-4 |
| Gas supply | Present, capped, clamped or removed | (relevant to BUS uplift, para 3.47) |

Under PAS 2035:2023, the retrofit assessment records much of this too. For a distressed replacement of a heating appliance, the whole-dwelling assessment "shall be completed as soon as possible during or after the retrofit process" (clause 7.2.1), and the Retrofit Coordinator "shall be involved as soon as possible" (6.1.5). Heat pumps, air and ground source, both appear as measures in the measures interaction matrix (Annex D, Figure D.1).

Keep the record factual and attributed: "MCS certificate not seen; Table 4a default, no installation factor" rather than "not MCS"; "Householder reports higher bills than expected" rather than any statement about why.

### When to refer on

| Question | Who to suggest |
|---|---|
| "Is it working properly?" or a measured performance concern | The installer first; then the installer's consumer code or MCS (Parts 1 and 2 set out the route) |
| "What will it cost me to run?" | A designer or installer for an SPF estimate for their home; their supplier for tariffs. You can show the Section 1 method. |
| "Am I eligible for the grant?" | An installer holding MCS certification for the technology, against Ofgem's current guidance |
| "Can I put it there?" | The installer and the local planning authority (Part 2, Section 5) |
| Electrical supply capacity | The installer, who notifies the network operator (Part 2) |
| A PAS 2035 project where outcomes differ from those intended | The Retrofit Coordinator; clause 13.3.1 sets when further monitoring and evaluation applies |
| A safety concern | A competent professional, promptly |

Do not predict a household's bill, say whether their heat pump is performing, or say whether they will get a grant. Do not enter "MCS installation: yes" or a low design flow temperature without the document, or quote a price comparison without its date.

> **Wider view: evaluating performance after handover, and BS 40101**
>
> BS 40101:2022, *Building performance evaluation of occupied and operational buildings*, was published by BSI on 31 January 2022 and is listed as current. BSI's listing says it covers evaluation "at any point during the operational stage", offers a "tailored and graduated approach", and applies "across all building types and uses", with data from documentation review, testing and measurement, monitoring, occupant feedback and observation (BSI Knowledge listing). The standard itself is paid for and was not opened. The Chartered Institute of Architectural Technologists reported in January 2025 that a BSI user survey "is expected to inform a more formal refresh of the standard in due course" (CIAT, 29 January 2025).
>
> PAS 2035:2023 links BS 40101 to domestic retrofit. Clause 13 says the Retrofit Coordinator "shall evaluate every retrofit project" (13.1), and that basic evaluation, a questionnaire to the client and occupants, "shall be completed and reported within three months after handover" (13.4.3). Further monitoring and evaluation applies where, for example, outcomes are "significantly different" from those intended or unintended consequences are suspected (13.3.1). It is designed "in accordance with BS 40101 for Preliminary Evaluation, Light BPE, or Standard BPE" (13.5.1). Where further evaluation is carried out, the Retrofit Evaluator must be independent of the assessor, coordinator, designer and installer (A.5.1). A note to clause 7.3.2 adds that, where further monitoring and evaluation is carried out, comparing post-retrofit energy use and occupant survey results with those from the assessment is "beneficial".
>
> What the opened sources do not say is how BS 40101 should be applied to a heat pump specifically, for example whether a measured SPF is one of its performance parameters. That would need the standard itself.
>
> **What it means for your work:** your pre-retrofit record is the baseline any later evaluation is measured against. Record the heating system, controls, meter, tariff evidence and the householder's own account of costs and comfort carefully and with dates. If a heat pump project's outcomes look different from what was intended, that is a matter for the coordinator's evaluation under clause 13, not for an assessor's judgement on site.

**Visual:** Referral route. Start: "Assessor records what is there, with documents and dates". Branches: "Running cost → show the method; designer or installer for an SPF estimate"; "Grant → installer, against Ofgem guidance"; "Performance concern → installer first → consumer code or MCS"; "PAS 2035 outcomes differ → Retrofit Coordinator → basic evaluation within three months (13.4.3) → BS 40101 levels if triggered (13.5.1)". Red side box: "Safety concern: competent professional promptly". Caption: "Record, date, refer."

---

## Key Takeaways

- Cost per kWh of heat = unit price ÷ efficiency. At the 1 October to 31 December 2026 cap (electricity 26.32p, gas 7.97p), the price ratio is 3.30 and a heat pump breaks even with a boiler when SPF = 3.30 × boiler efficiency (2.81 at an illustrative 85%).
- Electricity is VAT-free only from 1 October 2026 to 31 March 2027. Date every comparison and re-run it after that.
- The RdSAP 10 rating uses the SAP 2012 prices in Table 32 (electricity 13.19p, gas 3.48p, ratio 3.79). EPC running costs use BRE's fuel-cost prices from July 2026 (electricity 26.00p, gas 6.34p, ratio 4.10). Neither is the household's tariff.
- RdSAP 10 uses SAP 10.2 emission factors: electricity 0.136, mains gas 0.210 kg CO2e per kWh, with monthly electricity factors in the worksheet. SAP 10.3, now the current SAP, uses 0.086 and 0.214; RdSAP 10.0.1 still calculates heat pumps per SAP 10.2.
- BUS: £7,500 air or ground source, £2,500 air-to-air, £5,000 biomass in limited cases; £9,000 for oil or LPG replacement off the gas grid until 31 March 2027. No insulation condition; no EPC required since 28 April 2026.
- Load control licensing is required from March 2028; the government aims for 10 to 12 GW of flexibility by 2030. RdSAP gives a heat pump on a dual meter the 10-hour tariff, and a smart meter does not affect the calculation.
- Use the PCDB whenever the model can be identified. The MCS installation factor applies to a Table 4a default only, and "MCS installation: yes" needs documentary evidence. A heat pump is main system 1 (4.09a); design flow temperature is unknown without documents (4.01b).
- The government has moved the launch of new-style EPCs to the second half of 2027 (gov.uk, 9 March 2026). Under PAS 2035:2023, the coordinator evaluates every project, with further evaluation to BS 40101 levels where triggered.

---

## Self-Assessment Questions

**Q1.** At the Ofgem cap for 1 October to 31 December 2026, electricity is 26.32p per kWh and gas 7.97p per kWh. Assuming a gas boiler seasonal efficiency of 90%, what seasonal performance factor would a heat pump need to match the boiler's cost per kWh of heat?

A) 2.44
B) 2.97
C) 3.30
D) 3.79

**Correct answer: B.** The price ratio is 26.32 ÷ 7.97 = 3.30, and break-even SPF = price ratio × boiler efficiency = 3.30 × 0.90 = 2.97. 3.30 is the ratio itself, and 3.79 is the ratio in RdSAP 10's Table 32 rating prices (Sections 1 and 2).

---

**Q2.** Which prices does RdSAP 10 use to calculate the energy efficiency rating on an EPC?

A) The current Ofgem price cap
B) The householder's own tariff, taken from a recent bill
C) Table 32 of the RdSAP 10 specification, which repeats the SAP 2012 Table 12 prices
D) The prices in Table 191 of the Product Characteristics Data File

**Correct answer: C.** Section 19.1 says the rating "is to be calculated using Table 32 prices", which "are the same as in Table 12 of the SAP 2012 specification". Table 191 prices are used for the running costs and savings shown on the EPC, not the rating (Section 2).

---

**Q3.** A householder's air source heat pump is not in the PCDB. You are shown an MCS certificate for the installation, and no design documents. How should it be treated in RdSAP 10?

A) Use the Table 4a default, record MCS installation as yes so the installation factor applies, and record design flow temperature as unknown
B) Use the Table 4a default with no installation factor, because the factor applies only to database records
C) Enter a design flow temperature of 35°C or below, because MCS installations are low temperature
D) Enter the heat pump as main system 2 if a boiler is also present

**Correct answer: A.** Convention 4.07 says to use the default; SAP 10.2 section 9.2.7 applies the installation factor to a Table 4a efficiency only where an MCS certificate has been produced, and item 7-4 allows "yes" only with documentary evidence. Convention 4.01b keeps the design flow temperature unknown without design and commissioning evidence, and convention 4.09a makes the heat pump main system 1 (Section 6).

---

**Q4.** A household in a home heated by oil, with a capped mains gas meter point, asks about the Boiler Upgrade Scheme in November 2026. Which statement matches Ofgem's guidance?

A) They qualify for £9,000 because the gas supply is capped
B) The capped meter point counts as being fuelled by mains gas, so the £1,500 off-gas uplift would not apply under para 3.47
C) They must first have loft and cavity insulation installed
D) They must provide a valid EPC before applying

**Correct answer: B.** Para 3.47 says "capped or clamped supply meter points are still considered as being fuelled by mains gas". There is no insulation condition, and since 28 April 2026 an EPC is no longer required (Section 4). Eligibility is decided by Ofgem, so the householder should confirm with an installer.

---

**Q5.** Under PAS 2035:2023, when must basic evaluation of a completed domestic retrofit project be completed and reported?

A) Before the retrofit design is agreed
B) Within three months after handover
C) Twelve months after handover, using BS 40101 Standard BPE
D) Only where the client asks for it

**Correct answer: B.** Clause 13.4.3 says basic evaluation "shall be completed and reported within three months after handover". Further monitoring and evaluation to BS 40101 levels applies only where triggered under clause 13.3.1 (Section 7, Wider view).

---

## Further Reading

Sources used for this course:
- **RdSAP10 Specification.** BRE, version 4.0, 7 June 2026. Introduction; sections 10.1, 10.3, 10.5.1, 11.1, 11.2, 12, 19.1, 19.2 and 20; Tables 29, 31 (items 1-17, 1-18, 7-3, 7-4, 11-4), 32 (with notes) and 33 (measures G1-3, Z1, Z2).
- **Conventions (v12.2) for RdSAP 10.** BRE for MHCLG, applicable from 6 August 2026. Front page; conventions 4.01a, 4.01b, 4.05b, 4.07, 4.09a, 6.04, 9.02, 9.04, 9.05 and 9.13.
- **The Government's Standard Assessment Procedure for Energy Rating of Dwellings, SAP 10.2** (11-04-2023). BRE for BEIS. Section 9.2.7 only.
- **SAP 10.3: The Government's Standard Assessment Procedure for Energy Rating of Dwellings**, version 12-06-2026. BRE for DESNZ. Introduction; section 9.2.7; Table 12 with notes (s) and (t).
- **Prices used by SAP/RdSAP for calculation of fuel costs, from July 2026.** BRE.
- **Standard Assessment Procedure.** gov.uk guidance page (updated 8 June 2026).
- **Reforms to the Energy Performance of Buildings regime.** gov.uk consultation page (update of 9 March 2026).
- **Changes to energy price cap between 1 October and 31 December 2026.** Ofgem, 26 August 2026.
- **Electrification of Heat Demonstration Project: Interim insights from heat pump performance data.** Energy Systems Catapult for DESNZ, 2023. Sections 1.1.1 and 5.1.
- **Air source heat pumps.** Energy Saving Trust (updated 16 July 2026).
- **Apply for the Boiler Upgrade Scheme**, including *What you can get* and *Check if you're eligible*. gov.uk (metadata updated 19 October 2026).
- **Boiler Upgrade Scheme: Installer Guidance V5.1.** Ofgem, 2 July 2026. Paras 1.02, 1.06, 3.13, 3.40, 3.41, 3.43, 3.46 to 3.51, 3.83 and 3.84.
- **Summary of updates in the BUS installer guidance, Version 3.** Ofgem (undated).
- **BUS monthly scheme update.** Ofgem (updated 13 October 2026).
- **Boiler Upgrade Scheme Quarterly Report Issue 17.** Ofgem, 31 August 2026. Figures 2, 3 and 6.
- **Smart Secure Electricity Systems (SSES) Programme: Government response to the 2025 SSES Licensing consultation.** DESNZ, 2026. Ministerial foreword; sections 1.1, 1.3 and 2.2.
- **Future Energy Scenarios: Pathways to Net Zero 2025.** NESO press release (14 July 2025).
- **PAS 2035:2023 Retrofitting dwellings for improved energy efficiency. Specification and guidance.** BSI. Clauses 6.1.5, 7.2.1, 7.3.2 (Notes 13 and 14), 13.1 to 13.5, A.4, A.5.1; Annex D, Figure D.1.
- **BS 40101:2022.** BSI Knowledge product listing (read 29 October 2026).
- **Call for evidence: BS 40101 Building performance evaluation of occupied and operational buildings.** CIAT news, 29 January 2025.

Not opened for this course: the Product Characteristics Data File, including Table 191; SAP 10.2 Tables 4a, 4b, 12a, 12d and 12e; BRE's paper S10TP-15 on SAP emission and primary energy factors (permission request not answered); the partial government response on EPC reform itself; published measurements of heat pump demand at peak times, including the RHPP load profile paper (permission request not answered); measured annual grid carbon intensity figures (permission request not answered); BS 40101:2022 itself (paid standard); SAP 10.2 sections other than 9.2.7.

Related Meridian courses: Parts 1 and 2 of the Heating Series (MER-ALL-022 and MER-ALL-023); MER-RA-001 (PAS 2035:2023 Overview for Retrofit Assessors).

---

*© Meridian CPD 2026. All rights reserved. Unauthorised reproduction prohibited.*
*This course material is licensed to individual subscribers only.*
