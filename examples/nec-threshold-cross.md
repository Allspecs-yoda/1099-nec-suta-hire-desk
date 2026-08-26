# Worked: the $2,000 NEC line (TY2026)

Federal box 1a moved from $600 to **$2,000** for tax years beginning after 2025
([IRS 1099-MISC/NEC instructions, 12/2026](https://www.irs.gov/instructions/i1099mec)).

```bash
python3 desk/quote.py --nec --paid 1995 --next 80
python3 desk/quote.py --roster data/contractor_roster.csv
```

- C-03 Jordan Lee at $1,995 + an $80 invoice **crosses** $2,000 → file 1099-NEC by January 31.
- C-06 Priya Shah at $600 is **under** the new federal line (legacy muscle memory).
- C-04 Alex Kim has no TIN → 24% backup withholding even if you also file.
- State 1099 copies may still use $600 — log every payment.

Penalties for returns **due in 2026**: $60 / $130 / $340 per return (30 days / through Aug 1 / after), $680 intentional disregard
([IRS information return penalties](https://www.irs.gov/payments/information-return-penalties)).
