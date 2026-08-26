# Worked: $65k support lead, Texas vs Washington

Same cash wages. Different SUTA wage bases. Demo SUTA rates: TX 2.7%, WA 1.5% — **replace with your notice**.

```bash
python3 desk/quote.py --state TX --wages 65000 --suta-rate 0.027
python3 desk/quote.py --state WA --wages 65000 --suta-rate 0.015
```

Expected shape (employer side, 2026 federal):

| | Texas | Washington |
| --- | --- | --- |
| SS 6.2% on $65k | $4,030 | $4,030 |
| Medicare 1.45% | $942.50 | $942.50 |
| FUTA 0.6% × $7,000 | $42 | $42 |
| SUTA wage base | $9,000 | **$78,200** |
| SUTA at demo rate | 2.7% × $9,000 = **$243** | 1.5% × $65,000 = **$975** |
| Employer burden | ~$5,258 | ~$5,990 |

Washington’s “cheap” 1.5% rate still costs more than Texas’s 2.7% because the 2026 WA wage base is $78,200 (EY 2026-0124) vs TX $9,000.

CA on the same wages (base $7,000) is even smaller SUTA — that is why a CA vs WA compare is in `data/hire_worksheet.csv`.
