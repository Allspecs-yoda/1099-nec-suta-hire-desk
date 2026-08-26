# Worked: Iowa’s 2026 SUTA wage-base cut

EY 2026-0124: Iowa **$39,500 → $20,400** after SF 607 (signed June 5, 2025).

```bash
python3 desk/quote.py --list IA
python3 desk/quote.py --state IA --wages 48000 --suta-rate 0.02
```

On a $48k ops hire at a demo 2.0% rate:

- 2025-style base $39,500 → SUTA $790
- 2026 base $20,400 → SUTA **$408**

Same person in New York (EY 2026 wage base **$17,600**, up $4,800 from 2025) at 2.5%:

```bash
python3 desk/quote.py --state NY --wages 48000 --suta-rate 0.025
```

Nextep’s Nov 2025 rundown still listed NY 2026 as $13,000. This pack follows EY (Jan 5, 2026) and tells you to verify NYS DOL before you accrue.
