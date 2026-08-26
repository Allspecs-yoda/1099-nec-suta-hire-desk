# Worked: $120k engineer, Texas — W-2 vs same cash 1099

```bash
python3 desk/quote.py --state TX --wages 120000 --suta-rate 0.027 --compare
```

Employer:

- W-2 loaded ≈ wages + employer SS + Medicare + FUTA + SUTA
- 1099 cash = $120,000 (this model: no employer FICA/FUTA/SUTA)

Worker-side (1099, single, simple 20% QBI, TY2026 std $16,100, SS cap $184,500):

- SE tax on $120,000 × 0.9235
- plus federal income tax after ½ SE + standard deduction + simple QBI
- divide by 4 → equal estimated payment (Q4 due **2027-01-18**)

The printout’s “employer saves vs W-2” line is **not** a classification opinion. IRS common-law control still applies. Cheaper is not a 1099.
