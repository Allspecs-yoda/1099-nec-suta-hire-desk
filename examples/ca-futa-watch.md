# Worked: California FUTA watch (not final)

DOL’s FUTA credit-reduction page still says the **year is not final until November 10**.
DOL’s February 2026 Trust Fund Solvency Report: **two** jurisdictions had a Title XII
advance on January 1, 2026 ($21.4B) and “may be subject to additional FUTA credit reductions.”

PayrollOrg (2026-04-07), citing DOL *Potential 2026 Federal Unemployment Tax Act (FUTA)
Credit Reductions* (2026-01-15), names those two as **California** and the **U.S. Virgin Islands**:

| | CA potential | VI potential |
| --- | --- | --- |
| Base reduction | 1.5% | 4.8% |
| BCR add-on | 3.8% (waiver possible) | none cited |
| Total if BCR sticks | 5.3% | 4.8% |
| Extra $ / employee on $7,000 vs 0.6% | $105 / $371 | $336 |
| Fully loaded FUTA / employee | $147 / $413 | $378 |

```bash
python3 desk/quote.py --futa-watch
python3 desk/quote.py --state CA --wages 65000 --suta-rate 0.034 --futa-range
python3 desk/quote.py --state CA --wages 65000 --suta-rate 0.034 --futa-scenario base
python3 desk/quote.py --state VI --wages 65000 --suta-rate 0.02 --futa-scenario base
python3 desk/quote.py --gaps
python3 desk/quote.py --nec --paid 900 --next 0 --state MA
```

Default `--futa-add-rate` is still **0**. Do not accrue the extra until DOL posts the final
list after Nov 10. The extra, if it lands, is a **Q4** Form 940 / Schedule A item
(due January 31 of the following year) — IRS FUTA credit-reduction page.

Massachusetts 1099-K is a different trap: DOR still wants **$600** gross (updated 2026-07-24)
while federal TPSO goods/services is **$20,000 and 200 transactions**.
