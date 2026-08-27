# Sources

This pack is a **cited bench**, not tax advice and not a substitute for your state unemployment notice or a CPA.

## Federal payroll / SE

| Fact | Value used | Source |
| --- | --- | --- |
| Social Security wage base 2026 | $184,500 | [SSA contribution and benefit base](https://www.ssa.gov/oact/cola/cbb.html); SSA FAQ KA-02387 |
| Social Security wage base 2025 | $176,100 | SSA (prior year, for Δ) |
| OASDI rate | 6.2% employee + 6.2% employer (12.4% SE) | SSA / IRC 1401 |
| Medicare | 1.45% + 1.45% (2.9% SE); no wage cap | SSA |
| Additional Medicare | 0.9% employee-only above $200k / $250k MFJ | IRC 3101(b)(2) — **not** in employer burden |
| SE base | net profit × 0.9235 | IRC 1402(a)(12) |
| FUTA wage base | $7,000 | FUTA; EY Tax Alert 2026-0124 |
| FUTA net (full credit) | 0.6% | IRC 3301 / 3302 (6.0% − 5.4%) |
| FUTA credit-reduction final date | Nov 10 of the tax year | [DOL OUI FUTA credit reductions](https://oui.doleta.gov/unemploy/futa_credit.asp) (page updated 2026-08-25) |
| Standard deduction TY2026 | $16,100 single / $32,200 MFJ / $24,150 HoH | [IRS inflation adjustments TY2026](https://www.irs.gov/newsroom/irs-releases-tax-inflation-adjustments-for-tax-year-2026-including-amendments-from-the-one-big-beautiful-bill) |
| TY2026 brackets | 10% to $12,400 single / $24,800 MFJ; 12/22/24/32/35/37 as published | same IRS newsroom |
| QBI | simple 20% of QBI after ½ SE; **no** wage/UBIA/taxable-income limit model | IRC 199A |
| Estimated-tax $1,000 test | Topic 306 | IRS |
| Safe harbor | 100% prior-year tax, or 110% if 2025 AGI > $150,000 | Pub 505 |
| 2026 estimate due dates | Apr 15, Jun 15, Sep 15, **Jan 18 2027** (Jan 15 is Saturday) | Pub 505 / Form 1040-ES weekend rule |

## 1099-NEC

| Fact | Value used | Source |
| --- | --- | --- |
| Box 1a federal threshold TY2026 | **$2,000** (tax years beginning after 2025) | [IRS Instructions for Forms 1099-MISC and 1099-NEC (12/2026)](https://www.irs.gov/instructions/i1099mec) — What’s New |
| File + furnish | January 31 (paper or e-file) | same; IRC 6071(c) |
| 1099-MISC IRS due | Feb 28 paper / Mar 31 e-file | same |
| E-file if 10+ information returns | T.D. 9972 | same |
| Backup withholding | 24% | [IRS Backup withholding](https://www.irs.gov/businesses/small-businesses-self-employed/backup-withholding) |
| Penalties due in 2026 | $60 / $130 / $340 / $680 intentional | [IRS information return penalties](https://www.irs.gov/payments/information-return-penalties) |
| New boxes 1b/1c/1d | cash tips, TTOC, overtime | 12/2026 instructions |

**State 1099 thresholds may still be $600.** This desk flags the federal $2,000 line only.

## SUTA wage bases

Primary table: **EY Tax Alert 2026-0124**, “2026 state unemployment insurance taxable wage bases,” **as of 2026-01-05**.

Cross-check (not used when it conflicts with EY): Nextep 2026 SUTA rundown (posted 2025-11-17; NY still listed $13,000). This pack uses **EY’s New York 2026 = $17,600** and notes the conflict in `suta_wage_bases.csv`. Verify against NYS DOL before you accrue.

Michigan has two rows (good-standing $9,000 vs delinquent $9,500). Nebraska and Rhode Island have max-rate / negative-balance rows.

Employer **SUTA rates are not in this pack** — they are on your experience-rating notice. Pass `--suta-rate`.

## 2026 FUTA credit-reduction watch (not final)

| Fact | Value used | Source |
| --- | --- | --- |
| Final date | Nov 10 of the tax year | [DOL OUI FUTA credit reductions](https://oui.doleta.gov/unemploy/futa_credit.asp) (updated 2026-08-25) |
| Title XII borrowers Jan 1 2026 | **two** jurisdictions, $21.4B | [DOL Trust Fund Solvency Report 2026](https://oui.doleta.gov/unemploy/docs/trustFundSolvReport2026.pdf) (Feb 2026) |
| Named on the potential-2026 list | California, U.S. Virgin Islands | PayrollOrg 2026-04-07 citing DOL *Potential 2026 FUTA Credit Reductions* (2026-01-15) |
| CA potential | 1.5% base, or 5.3% with 3.8% BCR add-on (waiver possible) | same; Bloomberg Tax 2026-04-10 |
| VI potential | 4.8% base; no BCR add-on cited for 2026 | same |
| Extra $ / employee on $7,000 vs 0.6% | CA $105 / $371; VI $336 | arithmetic on FUTA wage base $7,000 |
| When the extra is due | Q4 Form 940 / Schedule A; January 31 following year | [IRS FUTA credit reduction](https://www.irs.gov/businesses/small-businesses-self-employed/futa-credit-reduction) |

The calculator **default extra rate is still 0**. `--futa-watch` and `--futa-range` print the potential benches. Do not treat commercial “seven states” lists as the 2026 watch.

## State 1099 / 1099-K gaps

| Fact | Value used | Source |
| --- | --- | --- |
| MA 1099-NEC | Follows IRS Pub 1220 amounts; **direct** MassTaxConnect file even if you use IRS CF/SF; NEC due Jan 31 | [Mass.gov Form 1099 Filing Requirements](https://www.mass.gov/info-details/massachusetts-form-1099-filing-requirements) (updated 2026-07-24) |
| MA 1099-K | **$600** gross, any transaction count (federal TPSO goods/services restored to $20,000 and 200) | same Mass.gov page |
| CA information returns | File with FTB if CA resident/part-year or CA-source; CF/SF forwards matching amounts | [FTB Guidance for reporting information returns](https://www.ftb.ca.gov/file/business/information-returns.html) (updated 2026-04-03) |
| CA 1099-K TPSO goods/services | $20,000 **and** >200 transactions (Notice 2024-85 phase-in superseded, retroactive to 2022) | same FTB page |
| CA 1099-K app-based drivers | **$600** still applies | same FTB page |
| OR 1099-NEC | Follows IRS guidelines; **iWire** required; due Jan 31 | [Oregon DOR iWire](https://www.oregon.gov/dor/programs/businesses/pages/iwire.aspx) |

This is **not** a 50-state 1099 matrix. Rows are only the official pages pulled this cycle.

## What this pack will not invent

- A **final** 2026 FUTA credit-reduction list. DOL says the year is not final until **November 10**. The watch CSV is potential only; extra rate starts at 0.
- Per-employee Additional Medicare on the employer side.
- State income-tax estimates (except the employee-SUI footnotes EY published for AK / NJ / PA).
- Worker classification. Cheaper ≠ 1099.
- Uncited state 1099 $600 floors. Only MA / CA / OR pages above.

Figures compiled 2026-08-26; FUTA-watch polish 2026-08-27. Re-pull SSA / IRS / your state DOL if you ship after a statutory change.
