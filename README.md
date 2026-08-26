# 1099-NEC + SUTA Hire Desk

Offline 2026 desk that prices a W-2 hire against the same cash on a 1099, using the new **$2,000** federal NEC threshold, SSA’s **$184,500** wage base, and a 57-row SUTA wage-base table (50 states + DC + PR + VI + FUTA).

## Who it's for

Agency operators, tiny payroll shops, and freelancers who pay contractors **and** hire W-2s and need the 2026 line-moves in one folder — not a blog post.

## What's included

- `data/suta_wage_bases.csv` — 57 rows from EY Tax Alert 2026-0124 (Jan 5, 2026), including MI / NE / RI split kinds
- `data/federal_payroll.csv` — SSA $184,500, FUTA $7,000 / 0.6%, TY2026 standard deductions
- `data/federal_brackets_2026.csv` — IRS published TY2026 ordinary brackets
- `data/1099_rules.csv` — $2,000 NEC box 1a, Jan 31, 10-return e-file, 24% BWH, 2026 penalty tiers
- `data/estimated_tax_calendar.csv` — 2026 quarters; Q4 due **2027-01-18**
- `data/hire_worksheet.csv` / `data/contractor_roster.csv` — sample quotes and a live roster
- `desk/quote.py` — offline `--compare`, `--contractor`, `--nec`, `--batch`, `--roster`, `--list`
- `examples/` — TX vs WA, W-2 vs 1099, $2,000 cross, Iowa wage-base cut
- `data/SOURCES.md` — citations

## Quick start

```bash
python3 desk/quote.py --state TX --wages 65000 --suta-rate 0.027
python3 desk/quote.py --state WA --wages 65000 --suta-rate 0.015 --compare
python3 desk/quote.py --contractor --net-profit 80000
python3 desk/quote.py --nec --paid 1995 --next 80
python3 desk/quote.py --batch data/hire_worksheet.csv
python3 desk/quote.py --roster data/contractor_roster.csv
python3 desk/quote.py --list IA
```

Pass **your** SUTA rate (`--suta-rate 0.027`). FUTA extra credit-reduction defaults to 0 — DOL does not finalize 2026 until November 10; use `--futa-add-rate 0.003` if you already know it.

No API keys. Files work after Gamut credits are gone. Not tax advice.

## Price

$49 USD. Unlimited non-exclusive buyers; copies may be resold. Pay the Stripe link in this README (filled after checkout is created) then open a GitHub issue titled `CLAIM: 1099-NEC + SUTA Hire Desk` with the receipt last-4. If checkout is down, star + watch and open the same CLAIM issue.

## License

MIT for the desk code, CSVs, and docs. Cited IRS / SSA / EY / DOL figures remain their works. See LICENSE.

## Foundry

Shipped by Night Shift Foundry for Dakota (@Allspecs-yoda).
SKU: NSF-20260826-NEC-SUTA-HIRE | Decision: list | Cycle: 2026-08-26
