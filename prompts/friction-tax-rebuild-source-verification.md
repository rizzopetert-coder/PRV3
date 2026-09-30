# Friction Tax Rebuild: Source Verification (2026-09-30)

Status: findings recorded, no engine code changed. Section 1 is verbatim as relayed by Pete from Claude.ai (primary-source checked). Section 2 is a read-only data pull run by Claude Code on 2026-09-30 from the BLS file named below. Nothing here is a decision until Pete confirms.

Context: MOB Section 13b/14 FRICTION TAX REBUILD (opened 2026-09-28/29). This closes the three verification items listed there as "next" (Gallup 18% composition, Gallup Q12 quartile spread, BLS management share by industry).

## 1. Findings relayed from Claude.ai

### 1a. Gallup 18%

The source is the Gallup 2020 article "Increase Productivity at the Lowest Possible Cost" (gallup.com/workplace/321743, page is NOINDEX), which applies 18% of salary to "not engaged" employees (worked example: 10,000 x 67% x $50,000 x 18% = $60.3M). The SOGW 2026 methodology (gallup.com/workplace/349484) is a utility analysis of lost output that explicitly excludes turnover, safety, theft and healthcare costs.

Conclusions:
- No turnover double count.
- The population is broad not-engaged, not only actively disengaged.
- The 34% figure has no primary source found, excluded.
- P2 partial-year discount still applies.

### 1b. Gallup Q12 meta-analysis, 11th ed. (2024)

Top vs bottom quartile median differences:
- Productivity: 18% sales / 14% production.
- Turnover: 21% (>40% annual turnover orgs) / 51% (<=40%).
- Absenteeism: 78%.

These are unit-level within organizations (avg 18 employees), pooled across 53 industries, and compare top vs bottom quartile, not bottom vs typical.

Status: does not meet P4 as amended, pending Pete.

### 1c. BLS OEWS

National May 2025 SOC 11-0000 = 11,132,700 of 155,495,730 (7.16%), mean annual wage $145,260. Construction May 2023 = 7.83%, $122,190. 11-0000 excludes first-line supervisors. The rebuild proposal's decision-quality channel assumed a 20% manager share, flagged by Gemini on 2026-09-29 as uncited. It is not a live engine value (not found in engine/friction_tax.py or prompts/friction-tax-*.md, 2026-09-30). The published 11-0000 share is roughly a third of it. Open: whether to include first-line supervisors (Pete).

CORRECTION 2026-09-30: Claude.ai's relay described this as the engine's current value. Claude Code's search showed it is a proposal assumption only.

## 2. BLS OEWS industry pull (Claude Code, read-only)

Vintage used: **May 2025**, the newest available. `https://www.bls.gov/oes/special-requests/oesm25in4.zip` returned HTTP 200 (May 2024 `oesm24in4.zip` and May 2023 `oesm23in4.zip` also exist and were not used). File used: `nat3d_M2025_dl.xlsx` (national, 3-digit NAICS industries, ownership-blended, 38,789 rows). Note this is 3-digit NAICS only. The file has no 2-digit sector rows, so each sector below is built by summing its 3-digit industries.

Method:
- Total employment, 11-0000 employment, and first-line supervisor (FLS) employment are straight sums of the 3-digit rows. Percent is the sum over total employment.
- FLS = the sum of every detailed-level occupation whose title begins "First-Line Supervisors" (33-1011 through 53-1047, 19 detailed codes, broad-level rows excluded to avoid double counting). 53-1047 excludes aircraft cargo handling supervisors, so that small group is not in the FLS figure.
- 11-0000 mean wage is the 11-0000 employment-weighted mean of the 3-digit A_MEAN values. FLS mean wage is the same method, weighted by each detailed FLS occupation's employment within each 3-digit industry. Both are recomputed figures, not published BLS sector wages.
- Cross-check: the 3-digit sums give 155,495,830 total and 11,132,750 for 11-0000 (7.16%), within 100 and 50 of the published national 155,495,730 and 11,132,700. The difference is BLS rounding. FLS nationally sums to 7,681,710 (4.94%).
- No 3-digit row had a suppressed 11-0000 or total value.
- Sector 99 is the OEWS Government designation (federal, state, and local government excluding state and local schools and hospitals and the U.S. Postal Service). Postal Service (491000) sits inside sector 48-49 as published here. Sector 61 and 62 include the state and local government schools and hospitals that OEWS reports within them.
- Sector 11 covers only NAICS 113 and 115. OEWS does not cover crop or animal production.

### 2a. By NAICS sector, May 2025

| NAICS | Sector | Total emp | 11-0000 emp | 11-0000 % | 11-0000 mean wage | FLS emp | FLS % | FLS mean wage | Mgmt+FLS % |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|
| 11 | Agriculture/Forestry support (113,115) | 413,350 | 11,980 | 2.90% | $111,284 | 21,550 | 5.21% | $62,499 | 8.11% |
| 21 | Mining | 570,220 | 47,520 | 8.33% | $178,353 | 47,990 | 8.42% | $97,930 | 16.75% |
| 22 | Utilities | 598,000 | 56,040 | 9.37% | $172,580 | 50,710 | 8.48% | $117,354 | 17.85% |
| 23 | Construction | 8,298,380 | 678,470 | 8.18% | $129,869 | 784,310 | 9.45% | $85,701 | 17.63% |
| 31-33 | Manufacturing | 12,654,340 | 878,270 | 6.94% | $157,483 | 716,360 | 5.66% | $78,412 | 12.60% |
| 42 | Wholesale Trade | 6,024,600 | 643,570 | 10.68% | $157,362 | 340,320 | 5.65% | $78,998 | 16.33% |
| 44-45 | Retail Trade | 15,503,420 | 640,820 | 4.13% | $105,452 | 1,395,180 | 9.00% | $55,348 | 13.13% |
| 48-49 | Transportation & Warehousing | 7,448,650 | 283,170 | 3.80% | $128,806 | 367,970 | 4.94% | $76,725 | 8.74% |
| 51 | Information | 2,879,630 | 382,330 | 13.28% | $194,606 | 81,480 | 2.83% | $81,770 | 16.11% |
| 52 | Finance & Insurance | 6,281,650 | 798,250 | 12.71% | $190,881 | 228,410 | 3.64% | $82,605 | 16.34% |
| 53 | Real Estate & Rental | 2,427,960 | 451,360 | 18.59% | $106,112 | 134,190 | 5.53% | $70,145 | 24.12% |
| 54 | Professional/Scientific/Technical (541) | 10,800,470 | 1,391,610 | 12.88% | $183,740 | 173,470 | 1.61% | $82,473 | 14.49% |
| 55 | Management of Companies (551) | 2,828,130 | 641,960 | 22.70% | $193,000 | 90,810 | 3.21% | $87,038 | 25.91% |
| 56 | Admin/Support/Waste (561,562) | 9,114,350 | 488,670 | 5.36% | $139,220 | 425,340 | 4.67% | $62,962 | 10.03% |
| 61 | Educational Services (611) | 13,852,050 | 868,650 | 6.27% | $123,680 | 191,210 | 1.38% | $65,822 | 7.65% |
| 62 | Health Care & Social Assistance | 24,031,390 | 1,095,710 | 4.56% | $123,934 | 385,520 | 1.60% | $64,691 | 6.16% |
| 71 | Arts/Entertainment/Recreation | 2,765,330 | 176,190 | 6.37% | $114,158 | 159,200 | 5.76% | $56,002 | 12.13% |
| 72 | Accommodation & Food Services | 14,276,590 | 512,770 | 3.59% | $80,566 | 1,192,450 | 8.35% | $46,771 | 11.94% |
| 81 | Other Services (811,812,813) | 4,484,430 | 389,720 | 8.69% | $118,456 | 236,000 | 5.26% | $62,168 | 13.95% |
| 99 | Government excl schools/hospitals/USPS | 10,242,890 | 695,690 | 6.79% | $133,430 | 659,240 | 6.44% | $89,445 | 13.23% |

### 2b. Engine industry keys beside a proposed NAICS mapping

LOCKED by Pete 2026-09-30, with the decision 12 privately owned rows (611 and 622) for Nonprofit & Education and Healthcare & Life Sciences. The engine industries are the 11 values in `INTAKE_FIELDS["industry"]` (`engine/data/intake.py`), which equal `INDUSTRIES` in `engine/friction_tax.py` exactly, in the same order. `PAYROLL_BASELINE_GRID` is keyed `(headcount, industry)` over those 11 industries and 6 headcount buckets, 66 cells.

The proposed mapping below follows the component logic already in each `_INDUSTRY_WAGE_DATA` entry (May 2023) so the two vintages stay comparable. It is a starting point for Pete, not a recommendation to adopt.

| Engine industry | NAICS components (proposed) | Total emp | 11-0000 % | 11-0000 mean wage | FLS % | FLS mean wage | Mgmt+FLS % |
|---|---|---:|---:|---:|---:|---:|---:|
| Professional Services | sector 54 (541 only 3-digit) | 10,800,470 | 12.88% | $183,740 | 1.61% | $82,473 | 14.49% |
| Healthcare & Life Sciences | sectors 62 | 24,031,390 | 4.56% | $123,934 | 1.60% | $64,691 | 6.16% |
| Financial Services | sectors 52 | 6,281,650 | 12.71% | $190,881 | 3.64% | $82,605 | 16.34% |
| Technology | sectors 51 | 2,879,630 | 13.28% | $194,606 | 2.83% | $81,770 | 16.11% |
| Manufacturing | sectors 31-33 | 12,654,340 | 6.94% | $157,483 | 5.66% | $78,412 | 12.60% |
| Retail & Hospitality | sectors 44-45, 72 | 29,780,010 | 3.87% | $94,390 | 8.69% | $51,395 | 12.56% |
| Nonprofit & Education | sectors 61, 81 | 15,281,450 | 7.16% | $125,663 | 1.53% | $64,928 | 8.69% |
| Government & Public Sector | sectors 99 | 10,242,890 | 6.79% | $133,430 | 6.44% | $89,445 | 13.23% |
| Construction | sectors 23 | 8,298,380 | 8.18% | $129,869 | 9.45% | $85,701 | 17.63% |
| Transportation & Warehousing | sectors 48-49 | 7,448,650 | 3.80% | $128,806 | 4.94% | $76,725 | 8.74% |
| Other | sectors 11, 21, 22, 42, 53, 55, 56, 71, 81 less 813 | 27,796,970 | 9.65% | $147,973 | 5.26% | $71,045 | 14.91% |

Proposed component detail:
- Professional Services: NAICS 541 only.
- Healthcare & Life Sciences: sector 62 (621, 622, 623, 624). Note this includes Social Assistance (624), so it is broader than the label.
- Financial Services: sector 52.
- Technology: sector 51 (Information). The existing engine note already flags this as broader than ideal for the label (includes telecom, broadcasting, publishing).
- Manufacturing: sectors 31-33.
- Retail & Hospitality: sector 44-45 plus NAICS 721 (Accommodation) and 722 (Food Services and Drinking Places).
- Nonprofit & Education: NAICS 611 (Educational Services) plus 813 (Religious, Grantmaking, Civic, Professional, and Similar Organizations).
- Government & Public Sector: OEWS government designation (999000).
- Construction: sector 23.
- Transportation & Warehousing: sectors 48-49 (includes Postal Service 491).
- Other: sectors 11, 21, 22, 42, 53, 55, 56, 71, and 81 less 813.

Observations for the decision (not conclusions):
- Every mapped-industry 11-0000 share is well under the proposal's 20% assumption. The only sector above it is Management of Companies (22.70%), and the next highest is Real Estate (18.59%). Both sit inside 'Other'. The highest mapped industries are Technology (13.28%), Professional Services (12.88%), and Financial Services (12.71%). The lowest are Retail & Hospitality (3.87%), Transportation & Warehousing (3.80%), and Healthcare (4.56%).
- Adding FLS moves the share materially in frontline-heavy industries. Construction goes from 8.18% to 17.63% and Retail & Hospitality from 3.87% to 12.56%, while Healthcare (6.16%) and Professional Services (14.49%) barely move. The FLS decision matters most for Construction, Retail & Hospitality, Manufacturing, and Government.
- OEWS counts establishments of all sizes, so the manager share at the small end of the PRV3 client range is untested (the Demographic Applicability Filter has not been run against it).
- Sectors 61, 62 and 99 blend in public ownership. Sector 61 includes state and local government schools by BLS definition, and Educational Services is 91% of the Nonprofit & Education row's employment (13.85M of 15.28M). The public/private split was not computed from this file.
- "Other" includes sector 55 (22.70%, headquarters establishments), which raises its average.

## 3. Repo search: "43%" and "81%" near turnover, absenteeism, or Gallup

Searched `web/content`, `web/lib`, `engine`, and `prompts` for 43 or 81 followed by %, "percent", or "pct" (including decimals), then filtered for turnover, absenteeism, Gallup, engagement, and disengagement.

**Hits: none.** The unfiltered pattern (43% or 81% anywhere in those four directories) also returned zero hits. As a method check, the same search for 42% returned 2 hits, so the pattern works. No edits were made.

## Open decisions (Pete)

Resolved 2026-09-30, see Decisions (Pete, 2026-09-30) below.

1. **18% population.** Gallup's 18% applies to the broad not-engaged population, not only actively disengaged. Decide whether the rebuild prices the broad population (as the source does) or restricts to a narrower one.
2. **P4 bound.** The Gallup Q12 quartile differences (1b) do not meet P4 as amended (top vs bottom quartile, unit-level, cross-industry, not bottom vs typical). Decide whether any of them may serve as a within-industry bound, or whether no above-typical adjustment is made for these channels.
3. **Supervisor inclusion.** 11-0000 excludes first-line supervisors. Decide whether the manager population is 11-0000 alone (national 7.16%) or 11-0000 plus first-line supervisors (national 12.10%, see 2a). Also open and dependent on this: confirm or revise the proposed NAICS mapping in 2b, and whether 3-digit aggregation (used here) is acceptable for sector wages.

## 4. McKinsey decision-time source (Claude.ai, primary-source checked 2026-09-30)

Source: McKinsey, "Decision making in the age of urgency," April 2019 (survey fielded Feb 13-23, 2018), n=1,259 from McKinsey's Online Executive Panel, 91 countries. One-third C-level, 35% senior managers, the rest middle managers in the exhibits. No first-line supervisors identified. 62% at companies under $1B revenue. Self-reported.

Inputs for the rebuild:
- 37% of working time on decisions (mean).
- 58% of that time used ineffectively (mean).
- Do NOT use the 61% figure. It is the share of respondents saying most of their time is ineffective, a different measure.

The 20% manager share originates in McKinsey's own "thought experiment" sidebar footnote: an average Fortune 500 company of 56,400 employees, 20% managers, 220 eight-hour days, priced at the 2017 BLS median for management occupations ($102,590). It is an illustrative assumption, not data. McKinsey itself used BLS 11-0000 for pay, so replacing the 20% with the BLS 11-0000 share by industry is internally consistent.

Stated limits, not adjusted:
- The sample is senior-skewed and larger than PRV3's clients.
- Decision time rises with seniority, while inefficiency is higher for middle managers (68%) than C-level (57%). The net effect for an SMB manager mix is unknown.

## 5. Relayed inputs verified (Claude.ai, primary-source checked 2026-09-30)

- US engagement: Gallup Global Indicator: Employee Engagement (gallup.com/394373), "As of May 2026, 31% of U.S. employees are engaged and 17% are actively disengaged." Not-engaged share for the engagement channel = 69%, consistent with the SOGW cost method covering both not engaged and actively disengaged. The spec draft's statement that the 2020 article's 67% "equals 100 minus the engaged share" does not reconcile for any year and is not the basis for 69%.
- 42% preventable: Gallup, "42% of Employee Turnover Is Preventable but Often Ignored," Tatel and Wigert, July 2024 (gallup.com/workplace/646538). Self-reported by voluntary leavers ("at least from the employee perspective"). Gallup's 2019 figure was 52%. Same article gives role-tiered replacement costs: about 200% of salary for leaders and managers, 80% technical, 40% frontline.
- Work Institute 33.3%: 2017 Retention Report, derived from a conservative $5,506 turnover cost on an $8/hour ($16,640) employee. The current Work Institute method is 33.3% of base salary, about 11% direct and 22% indirect. Limit: derived from a low-wage basis and applied to all salaries.

## Decisions (Pete, 2026-09-30)

1. The Gallup 18% applies to the broad not-engaged population, as Gallup does.
2. P4: no above-typical adjustment. The Q12 quartile differences don't qualify (top vs bottom units, not bottom vs typical).
3. Manager population = SOC 11-0000 only. Confirmed by the McKinsey sample check (Section 4).
4. Option A: identified states select which channels appear (per-state criteria > 0). Severity does not move the dollar figure.
5. Decision time is dropped from the dollar total. It stays as a written receipt citing McKinsey 2019 (37%, 58%), with no dollar figure.
6. Point estimate, not a range.
7. P2 partial-year factor f = 0.5, labelled an assumption (exits spread evenly across the year).

    CORRECTION 2026-09-30: withdrawn. The engagement channel prices position-years of payroll (P = N x W). A leaver's remaining year is filled by the replacement, who draws that payroll and is engaged or not like anyone else, so no partial-year discount applies. The only overlap is the vacancy gap between leaver and replacement, partly covered by Work Institute's ~22% indirect cost. Disclosed as a limit, not adjusted (Pete, 2026-09-30). This also withdraws the P2 amendment from the 2026-09-29 Gemini outcome.
8. Payroll wages refreshed to OEWS May 2025.
9. JOLTS mapping: "Other" = total private. Nonprofit & Education = private educational services plus other services, weighted by employment. Use BLS-published annual quits rates by industry if they exist, otherwise the monthly rate x 12 per the Table 22 footnote.
10. Use actual headcount when intake gives an integer. Bucket mean only for legacy string labels.

    CORRECTION 2026-09-30: "Bucket mean only for legacy string labels" assumed legacy strings still arrive. String tolerance in resolve_headcount_bucket was deliberately removed 2026-08-29. Corrected rule: use the actual integer headcount. Bucket-mean fallback only if a live path supplies no integer. Do not reintroduce string tolerance.
11. ORG_TYPE_SCALARS retired.
12. Wage W uses privately owned OEWS rows where the engine industry is private (Nonprofit & Education, Healthcare & Life Sciences, and any other mapped industry with a published privately owned row). Government stays all-ownership.
13. Engine headcount guard: N must be int or float, not bool, finite, and at least 2. N = 1 returns null (a solo principal has no workforce the sources measure).
14. inaction_cost_*: two lines (typical-loss point estimate, legal tail-risk range), not a sum.
15. Headcount ceiling: keep the 1,000 intake cap and state it on the output.

    Narrowed by decision 17: at the cap, dollars are withheld and only percent of payroll is shown.
16. OEWS industry mapping (Section 2b) locked as committed, with decision 12 rows.
17. At the 1,000 intake ceiling, the output shows percent of payroll only, with no dollar figure (Gemini round 2 failure mode 2: dollars would understate for larger organizations).
