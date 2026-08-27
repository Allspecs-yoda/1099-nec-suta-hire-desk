#!/usr/bin/env python3
"""1099-NEC + SUTA Hire Desk — offline W-2 vs contractor quote.

No network. No API keys. Reads ../data/*.csv next to this file.

Usage:
  python3 desk/quote.py --state TX --wages 65000 --suta-rate 0.027
  python3 desk/quote.py --state WA --wages 65000 --suta-rate 0.015 --compare
  python3 desk/quote.py --contractor --net-profit 80000
  python3 desk/quote.py --nec --paid 1995 --next 80
  python3 desk/quote.py --batch data/hire_worksheet.csv
  python3 desk/quote.py --list IA
  python3 desk/quote.py --roster data/contractor_roster.csv
  python3 desk/quote.py --futa-watch
  python3 desk/quote.py --state CA --wages 65000 --suta-rate 0.034 --futa-range
  python3 desk/quote.py --gaps
  python3 desk/quote.py --nec --paid 900 --next 0 --state MA
"""
from __future__ import annotations

import argparse
import csv
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data"


def load_csv(name: str) -> list[dict]:
    path = DATA / name
    with path.open(encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f))


def federal_map() -> dict[str, str]:
    return {r["item"]: r["value"] for r in load_csv("federal_payroll.csv")}


def fnum(v: str | float | int) -> float:
    return float(v)


def money(n: float) -> str:
    sign = "-" if n < 0 else ""
    n = abs(n)
    return f"{sign}${n:,.2f}"


def suta_rows(state: str) -> list[dict]:
    st = state.strip().upper()
    out = []
    for r in load_csv("suta_wage_bases.csv"):
        if r["abbrev"].upper() == st or r["jurisdiction"].upper() == st:
            out.append(r)
    return out


def pick_suta(state: str, kind: str | None) -> dict:
    rows = suta_rows(state)
    if not rows:
        raise SystemExit(f"unknown state {state!r} — try --list TX")
    if kind:
        for r in rows:
            if r["kind"] == kind:
                return r
        kinds = ", ".join(sorted({r["kind"] for r in rows}))
        raise SystemExit(f"no kind {kind!r} for {state}; have: {kinds}")
    for r in rows:
        if r["kind"] == "standard":
            return r
    return rows[0]


def ss_medicare_employer(wages: float, fed: dict) -> dict:
    ss_base = fnum(fed["social_security_wage_base_2026"])
    ss = min(wages, ss_base) * fnum(fed["oasdi_employer_rate"])
    med = wages * fnum(fed["medicare_employer_rate"])
    # Additional Medicare is employee-only; employer does not match the 0.9%.
    return {"ss": ss, "medicare": med, "ss_base": ss_base}


def futa_tax(wages: float, fed: dict, extra_rate: float) -> dict:
    base = fnum(fed["futa_wage_base"])
    net = fnum(fed["futa_net_rate_full_credit"]) + extra_rate
    if net < 0:
        net = 0.0
    tax = min(wages, base) * net
    return {"base": base, "rate": net, "tax": tax, "extra": extra_rate}


def suta_tax(wages: float, row: dict, rate: float) -> dict:
    base = fnum(row["wage_base_2026"])
    tax = min(wages, base) * rate
    return {
        "jurisdiction": row["jurisdiction"],
        "abbrev": row["abbrev"],
        "kind": row["kind"],
        "base": base,
        "base_2025": fnum(row["wage_base_2025"]),
        "delta": fnum(row["delta"]),
        "rate": rate,
        "tax": tax,
        "notes": row["notes"],
        "employee_sui": row["employee_sui_note"],
    }


def income_tax(taxable: float, status: str) -> float:
    rows = [r for r in load_csv("federal_brackets_2026.csv") if r["status"] == status]
    if not rows:
        raise SystemExit(f"no brackets for {status}")
    tax = 0.0
    remaining = max(0.0, taxable)
    ordered = sorted(rows, key=lambda r: fnum(r["bracket_low"]))
    for r in ordered:
        low = fnum(r["bracket_low"])
        high = fnum(r["bracket_high"])
        rate = fnum(r["rate"])
        if remaining <= 0:
            break
        width = high - low
        slice_amt = min(remaining, width)
        if slice_amt > 0 and taxable > low:
            tax += slice_amt * rate
            remaining -= slice_amt
    return tax


def w2_loaded(state: str, wages: float, suta_rate: float, futa_extra: float, kind: str | None) -> dict:
    fed = federal_map()
    row = pick_suta(state, kind)
    fica = ss_medicare_employer(wages, fed)
    futa = futa_tax(wages, fed, futa_extra)
    suta = suta_tax(wages, row, suta_rate)
    employer = fica["ss"] + fica["medicare"] + futa["tax"] + suta["tax"]
    return {
        "mode": "w2",
        "wages": wages,
        "state": suta["abbrev"],
        "suta_kind": suta["kind"],
        "employer_ss": round(fica["ss"], 2),
        "employer_medicare": round(fica["medicare"], 2),
        "futa": round(futa["tax"], 2),
        "futa_rate": futa["rate"],
        "suta": round(suta["tax"], 2),
        "suta_base": suta["base"],
        "suta_base_2025": suta["base_2025"],
        "suta_delta": suta["delta"],
        "suta_rate": suta_rate,
        "suta_notes": suta["notes"],
        "employee_sui_note": suta["employee_sui"],
        "employer_burden": round(employer, 2),
        "fully_loaded": round(wages + employer, 2),
        "burden_pct": round(100.0 * employer / wages, 2) if wages else 0.0,
        "disclaimer": "FUTA uses 0.6% + optional --futa-add-rate. DOL finalizes credit reduction Nov 10.",
    }


def contractor_quote(net_profit: float, status: str, apply_qbi: bool) -> dict:
    fed = federal_map()
    se_base = net_profit * fnum(fed["se_net_multiplier"])
    ss_cap = fnum(fed["social_security_wage_base_2026"])
    ss = min(se_base, ss_cap) * fnum(fed["oasdi_self_employed_rate"])
    med = se_base * fnum(fed["medicare_self_employed_rate"])
    se_tax = ss + med
    se_deduction = se_tax / 2.0
    agi = net_profit - se_deduction
    std = fnum(fed["standard_deduction_single_2026"] if status == "single" else "standard_deduction_mfj_2026")
    qbi = 0.0
    if apply_qbi:
        # Simple 20% of QBI after 1/2 SE. Does not model taxable-income / wage / UBIA limits.
        qbi = max(0.0, (net_profit - se_deduction) * fnum(fed["qbi_rate"]))
    taxable = max(0.0, agi - std - qbi)
    itax = income_tax(taxable, status)
    total = se_tax + itax
    quarterly = total / 4.0
    return {
        "mode": "contractor_self",
        "net_profit": net_profit,
        "status": status,
        "se_base": round(se_base, 2),
        "ss_wage_base": ss_cap,
        "se_ss": round(ss, 2),
        "se_medicare": round(med, 2),
        "se_tax": round(se_tax, 2),
        "se_deduction": round(se_deduction, 2),
        "standard_deduction": std,
        "qbi_applied": apply_qbi,
        "qbi_deduction": round(qbi, 2),
        "taxable_income": round(taxable, 2),
        "federal_income_tax": round(itax, 2),
        "annual_estimated": round(total, 2),
        "quarterly_equal": round(quarterly, 2),
        "q4_due": "2027-01-18",
        "note": "Equal-installment estimate. Safe harbor is 100%/110% of 2025 tax. Not tax advice.",
    }


def nec_check(paid: float, nxt: float, state: str | None = None) -> dict:
    rules = {r["rule"]: r for r in load_csv("1099_rules.csv")}
    thresh = fnum(rules["nec_box1a_threshold_ty2026"]["value"])
    after = paid + nxt
    gaps = []
    if state:
        st = state.strip().upper()
        for r in load_csv("state_1099_gaps.csv"):
            if r["abbrev"].upper() == st:
                gaps.append(
                    {
                        "form": r["form"],
                        "threshold_usd": fnum(r["threshold_usd"]),
                        "federal_threshold_usd": fnum(r["federal_threshold_usd"]),
                        "gap_usd": fnum(r["gap_usd"]),
                        "direct_state_file": r["direct_state_file"],
                        "due": r["due"],
                        "notes": r["notes"],
                    }
                )
    return {
        "mode": "nec",
        "ytd_paid": paid,
        "next_invoice": nxt,
        "after": after,
        "federal_threshold_ty2026": thresh,
        "legacy_600": 600.0,
        "crosses_2000": paid < thresh <= after,
        "already_over": paid >= thresh,
        "still_under": after < thresh,
        "must_file_federal": after >= thresh,
        "due": rules["nec_irs_due"]["value"],
        "e_file_if_forms": rules["e_file_threshold"]["value"],
        "backup_withholding": rules["backup_withholding_rate"]["value"],
        "penalty_30d": rules["penalty_30_days_2026"]["value"],
        "penalty_aug1": rules["penalty_aug1_2026"]["value"],
        "penalty_after": rules["penalty_after_aug1_2026"]["value"],
        "state": state.upper() if state else None,
        "state_gaps": gaps,
        "note": "State 1099 / 1099-K floors can still be $600 even when federal NEC is $2,000. Log every payment. Not tax advice.",
    }


def futa_watch_rows() -> list[dict]:
    return load_csv("futa_credit_watch_2026.csv")


def pick_futa_watch(state: str) -> dict | None:
    st = state.strip().upper()
    for r in futa_watch_rows():
        if r["abbrev"].upper() == st and r["status"] == "potential":
            return r
    return None


def futa_scenarios(state: str, wages: float, suta_rate: float, kind: str | None) -> dict:
    watch = pick_futa_watch(state)
    if not watch:
        full = w2_loaded(state, wages, suta_rate, 0.0, kind)
        return {
            "mode": "futa_range",
            "on_watch": False,
            "state": state.upper(),
            "note": "Not on the cited 2026 potential FUTA-reduction list. Default extra rate = 0 until DOL finalizes Nov 10.",
            "full_credit": full,
        }
    base_extra = fnum(watch["potential_base_reduction"])
    bcr_extra = fnum(watch["potential_total_with_bcr"])
    none = w2_loaded(state, wages, suta_rate, 0.0, kind)
    base = w2_loaded(state, wages, suta_rate, base_extra, kind)
    bcr = w2_loaded(state, wages, suta_rate, bcr_extra, kind)
    return {
        "mode": "futa_range",
        "on_watch": True,
        "state": watch["abbrev"],
        "jurisdiction": watch["jurisdiction"],
        "final_date": watch["final_date"],
        "title_xii_jan1_2026": watch["title_xii_jan1_2026"],
        "bcr_waiver_possible": watch["bcr_waiver_possible"],
        "potential_base_reduction": base_extra,
        "potential_bcr_addon": fnum(watch["potential_bcr_addon"]),
        "potential_total_with_bcr": bcr_extra,
        "extra_per_ee_base_usd": fnum(watch["extra_per_ee_base_usd"]),
        "extra_per_ee_bcr_usd": fnum(watch["extra_per_ee_bcr_usd"]),
        "source": watch["source"],
        "notes": watch["notes"],
        "full_credit": none,
        "if_base": base,
        "if_bcr": bcr,
        "q4_note": "Credit-reduction extra is a Q4 Form 940 / Schedule A item (due Jan 31 following year). Not final until Nov 10.",
    }


def compare(state: str, cash: float, suta_rate: float, futa_extra: float, kind: str | None, status: str) -> dict:
    w2 = w2_loaded(state, cash, suta_rate, futa_extra, kind)
    # Contractor billed the same cash. Employer burden = 0 in this model.
    # Worker-side SE+income shown so the buyer sees who actually pays FICA.
    worker = contractor_quote(cash, status, apply_qbi=True)
    return {
        "mode": "compare",
        "cash_to_worker": cash,
        "w2_employer_cost": w2["fully_loaded"],
        "w2_employer_burden": w2["employer_burden"],
        "contractor_employer_cost": cash,
        "employer_saves_vs_w2": round(w2["fully_loaded"] - cash, 2),
        "contractor_self_annual_tax": worker["annual_estimated"],
        "w2": w2,
        "contractor_self": worker,
        "misclass_flag": "W-2 vs 1099 is a facts-and-circumstances test (common-law). Cheaper is not a classification.",
    }


def print_w2(d: dict) -> None:
    print(f"W-2 hire  {d['state']}  wages {money(d['wages'])}  kind={d['suta_kind']}")
    print(f"  employer SS           {money(d['employer_ss'])}")
    print(f"  employer Medicare     {money(d['employer_medicare'])}")
    print(f"  FUTA @ {d['futa_rate']*100:.2f}%          {money(d['futa'])}")
    print(f"  SUTA base {money(d['suta_base'])} (2025 {money(d['suta_base_2025'])}, Δ {d['suta_delta']:+.0f})")
    print(f"  SUTA @ {d['suta_rate']*100:.2f}%          {money(d['suta'])}")
    if d["employee_sui_note"]:
        print(f"  employee SUI note     {d['employee_sui_note']}")
    print(f"  employer burden       {money(d['employer_burden'])}  ({d['burden_pct']:.2f}%)")
    print(f"  fully loaded          {money(d['fully_loaded'])}")
    print(f"  {d['disclaimer']}")


def print_contractor(d: dict) -> None:
    print(f"Contractor self-tax  net {money(d['net_profit'])}  {d['status']}")
    print(f"  SE base (×0.9235)     {money(d['se_base'])}  (SS cap {money(d['ss_wage_base'])})")
    print(f"  SE Social Security    {money(d['se_ss'])}")
    print(f"  SE Medicare           {money(d['se_medicare'])}")
    print(f"  SE tax                {money(d['se_tax'])}")
    print(f"  1/2 SE deduction      {money(d['se_deduction'])}")
    print(f"  standard deduction    {money(d['standard_deduction'])}")
    print(f"  QBI (simple 20%)      {money(d['qbi_deduction'])}" + ("" if d["qbi_applied"] else "  [off]"))
    print(f"  taxable income        {money(d['taxable_income'])}")
    print(f"  federal income tax    {money(d['federal_income_tax'])}")
    print(f"  annual estimate       {money(d['annual_estimated'])}")
    print(f"  equal quarterly       {money(d['quarterly_equal'])}   Q4 due {d['q4_due']}")
    print(f"  {d['note']}")


def print_nec(d: dict) -> None:
    flag = (
        "CROSSES $2,000 — file 1099-NEC"
        if d["crosses_2000"]
        else ("ALREADY OVER — file 1099-NEC" if d["already_over"] else "still under federal $2,000 (log it anyway)")
    )
    print(f"1099-NEC  YTD {money(d['ytd_paid'])} + next {money(d['next_invoice'])} = {money(d['after'])}")
    print(f"  federal TY2026 threshold {money(d['federal_threshold_ty2026'])}  (legacy $600 is dead for federal box 1a)")
    print(f"  {flag}")
    print(f"  IRS + payee due {d['due']}; e-file if you file {d['e_file_if_forms']}+ information returns")
    print(f"  backup withholding {float(d['backup_withholding'])*100:.0f}% if no TIN")
    print(f"  penalties 2026: {d['penalty_30d']} / {d['penalty_aug1']} / {d['penalty_after']} per return (30d / through Aug 1 / after)")
    if d.get("state_gaps"):
        print(f"  state {d['state']} information-return gaps:")
        for g in d["state_gaps"]:
            print(
                f"    {g['form']}: state ${g['threshold_usd']:.0f} vs federal ${g['federal_threshold_usd']:.0f} "
                f"(gap ${g['gap_usd']:.0f}) due {g['due']}"
            )
            print(f"      {g['notes']}")
            print(f"      file: {g['direct_state_file']}")
    print(f"  {d['note']}")


def print_futa_watch() -> None:
    print("2026 FUTA credit-reduction WATCH (not final — DOL Nov 10)")
    print(f"{'abbr':<4} {'status':<12} {'base':>7} {'BCR':>7} {'total':>7}  extra$/ee base/BCR")
    for r in futa_watch_rows():
        print(
            f"{r['abbrev']:<4} {r['status']:<12} {fnum(r['potential_base_reduction'])*100:6.1f}% "
            f"{fnum(r['potential_bcr_addon'])*100:6.1f}% {fnum(r['potential_total_with_bcr'])*100:6.1f}%  "
            f"{money(fnum(r['extra_per_ee_base_usd']))}/{money(fnum(r['extra_per_ee_bcr_usd']))}"
        )
        print(f"     {r['notes'][:110]}")
    print("Default calculator extra rate is still 0. Pass --futa-scenario base|bcr or --futa-range.")


def print_futa_range(d: dict) -> None:
    if not d["on_watch"]:
        print(f"{d['state']} — {d['note']}")
        print_w2(d["full_credit"])
        return
    print(f"{d['jurisdiction']} ({d['state']}) FUTA watch  wages {money(d['full_credit']['wages'])}")
    print(f"  potential base {d['potential_base_reduction']*100:.1f}%  BCR add-on {d['potential_bcr_addon']*100:.1f}%  total-with-BCR {d['potential_total_with_bcr']*100:.1f}%")
    print(f"  BCR waiver possible: {d['bcr_waiver_possible']}  final: {d['final_date']}")
    print(f"  extra $/employee vs 0.6%: base {money(d['extra_per_ee_base_usd'])}  with BCR {money(d['extra_per_ee_bcr_usd'])}")
    print()
    print("  — if full 5.4% credit (default, not final) —")
    print_w2(d["full_credit"])
    print()
    print("  — if base reduction lands —")
    print_w2(d["if_base"])
    print()
    print("  — if BCR add-on also lands —")
    print_w2(d["if_bcr"])
    print()
    print(f"  {d['q4_note']}")
    print(f"  {d['notes']}")


def cmd_gaps(state: str | None) -> None:
    rows = load_csv("state_1099_gaps.csv")
    if state:
        st = state.strip().upper()
        rows = [r for r in rows if r["abbrev"].upper() == st]
        if not rows:
            raise SystemExit(f"no cited 1099 gap rows for {state}")
    print(f"{'abbr':<4} {'form':<32} {'state$':>8} {'fed$':>8} {'gap$':>8}  due")
    for r in rows:
        print(
            f"{r['abbrev']:<4} {r['form']:<32} {int(fnum(r['threshold_usd'])):8d} "
            f"{int(fnum(r['federal_threshold_usd'])):8d} {int(fnum(r['gap_usd'])):8d}  {r['due']}"
        )
        print(f"     {r['notes']}")
        print(f"     {r['direct_state_file']}")


def cmd_list(state: str | None) -> None:
    rows = load_csv("suta_wage_bases.csv")
    if state:
        rows = suta_rows(state)
        if not rows:
            raise SystemExit(f"unknown {state}")
    print(f"{'abbr':<4} {'kind':<16} {'2025':>10} {'2026':>10} {'Δ':>8}  notes")
    for r in rows:
        print(
            f"{r['abbrev']:<4} {r['kind']:<16} {int(fnum(r['wage_base_2025'])):10,d} "
            f"{int(fnum(r['wage_base_2026'])):10,d} {int(fnum(r['delta'])):8,d}  {r['notes'][:60]}"
        )


def cmd_batch(path: Path, suta_rate_override: float | None, json_out: bool) -> None:
    with path.open(encoding="utf-8", newline="") as f:
        rows = list(csv.DictReader(f))
    out = []
    for r in rows:
        wages = fnum(r["annual_wages"])
        kind_pay = r["kind"]
        rate = fnum(r["suta_rate"]) if suta_rate_override is None else suta_rate_override
        if kind_pay == "contractor":
            item = {
                "scenario_id": r["scenario_id"],
                "role": r["role"],
                "state": r["state"],
                "kind": "contractor",
                "cash": wages,
                "employer_cost": wages,
                "employer_burden": 0.0,
            }
        else:
            q = w2_loaded(r["state"], wages, rate, 0.0, None)
            item = {
                "scenario_id": r["scenario_id"],
                "role": r["role"],
                "state": r["state"],
                "kind": "w2",
                "cash": wages,
                "employer_cost": q["fully_loaded"],
                "employer_burden": q["employer_burden"],
                "suta": q["suta"],
                "suta_base": q["suta_base"],
                "futa": q["futa"],
            }
        out.append(item)
        if not json_out:
            print(
                f"{item['scenario_id']:<14} {item['kind']:<10} {item['state']:<3} "
                f"cash {money(item['cash']):>12}  employer {money(item['employer_cost']):>12}  "
                f"burden {money(item['employer_burden']):>10}"
            )
    if json_out:
        print(json.dumps(out, indent=2))


def cmd_roster(path: Path, json_out: bool) -> None:
    with path.open(encoding="utf-8", newline="") as f:
        rows = list(csv.DictReader(f))
    out = []
    for r in rows:
        paid = fnum(r["ytd_paid"])
        chk = nec_check(paid, 0.0)
        item = {
            "contractor_id": r["contractor_id"],
            "name": r["name"],
            "tin_on_file": r["tin_on_file"],
            "ytd_paid": paid,
            "must_file": chk["must_file_federal"],
            "backup": r["backup_withholding"] == "yes" or r["tin_on_file"] == "no",
            "state": r["state"],
            "notes": r["notes"],
        }
        out.append(item)
        if not json_out:
            flag = "FILE" if item["must_file"] else "under"
            bwh = " BWH-24%" if item["backup"] else ""
            print(
                f"{item['contractor_id']:<6} {item['name']:<16} {money(paid):>10}  {flag:<5}{bwh}  {item['notes']}"
            )
    if json_out:
        print(json.dumps(out, indent=2))


def main() -> None:
    p = argparse.ArgumentParser(description="1099-NEC + SUTA Hire Desk")
    p.add_argument("--state", help="USPS or name (TX, Washington)")
    p.add_argument("--wages", type=float, help="annual cash wages / contractor cash")
    p.add_argument("--suta-rate", type=float, default=None, help="your employer SUTA rate as decimal (0.027)")
    p.add_argument("--suta-kind", default=None, help="standard | delinquent | max_rate | negative_balance | good_standing")
    p.add_argument("--futa-add-rate", type=float, default=0.0, help="extra FUTA credit-reduction rate (e.g. 0.003). Default 0.")
    p.add_argument("--futa-watch", action="store_true", help="print 2026 potential FUTA credit-reduction watch (not final)")
    p.add_argument("--futa-range", action="store_true", help="print full-credit / base / BCR FUTA scenarios for --state")
    p.add_argument(
        "--futa-scenario",
        choices=["full", "base", "bcr"],
        default=None,
        help="apply the cited watch rate for --state (full=0, base, or total-with-BCR). Still not final.",
    )
    p.add_argument("--gaps", nargs="?", const="ALL", help="print cited state 1099 / 1099-K gaps (optional state)")
    p.add_argument("--compare", action="store_true", help="W-2 employer cost vs same cash as 1099")
    p.add_argument("--contractor", action="store_true", help="self-employed estimated tax on --net-profit")
    p.add_argument("--net-profit", type=float, help="Schedule C net profit")
    p.add_argument("--status", default="single", choices=["single", "mfj"])
    p.add_argument("--no-qbi", action="store_true")
    p.add_argument("--nec", action="store_true")
    p.add_argument("--paid", type=float, default=0.0)
    p.add_argument("--next", dest="next_invoice", type=float, default=0.0)
    p.add_argument("--list", nargs="?", const="ALL", help="print SUTA wage bases (optional state)")
    p.add_argument("--batch", help="CSV of hire scenarios")
    p.add_argument("--roster", help="CSV of contractors")
    p.add_argument("--json", action="store_true")
    args = p.parse_args()

    if args.list:
        cmd_list(None if args.list == "ALL" else args.list)
        return
    if args.futa_watch:
        print_futa_watch()
        return
    if args.gaps:
        cmd_gaps(None if args.gaps == "ALL" else args.gaps)
        return
    if args.batch:
        cmd_batch(Path(args.batch), args.suta_rate, args.json)
        return
    if args.roster:
        cmd_roster(Path(args.roster), args.json)
        return
    if args.nec:
        d = nec_check(args.paid, args.next_invoice, args.state)
        print(json.dumps(d, indent=2) if args.json else "")
        if not args.json:
            print_nec(d)
        return
    if args.contractor:
        if args.net_profit is None:
            raise SystemExit("--contractor needs --net-profit")
        d = contractor_quote(args.net_profit, args.status, not args.no_qbi)
        if args.json:
            print(json.dumps(d, indent=2))
        else:
            print_contractor(d)
        return
    if args.futa_range:
        if args.wages is None or args.state is None:
            raise SystemExit("--futa-range needs --state and --wages")
        rate = 0.027 if args.suta_rate is None else args.suta_rate
        d = futa_scenarios(args.state, args.wages, rate, args.suta_kind)
        if args.json:
            print(json.dumps(d, indent=2))
        else:
            print_futa_range(d)
        return
    if args.wages is None or args.state is None:
        p.print_help()
        print("\nNeed --state and --wages (or --contractor / --nec / --list / --batch / --roster / --futa-watch / --gaps).", file=sys.stderr)
        raise SystemExit(2)
    rate = 0.027 if args.suta_rate is None else args.suta_rate
    extra = args.futa_add_rate
    if args.futa_scenario:
        watch = pick_futa_watch(args.state)
        if not watch:
            raise SystemExit(f"{args.state} is not on the cited 2026 FUTA watch; extra stays 0")
        if args.futa_scenario == "full":
            extra = 0.0
        elif args.futa_scenario == "base":
            extra = fnum(watch["potential_base_reduction"])
        else:
            extra = fnum(watch["potential_total_with_bcr"])
    if args.compare:
        d = compare(args.state, args.wages, rate, extra, args.suta_kind, args.status)
        if args.json:
            print(json.dumps(d, indent=2))
            return
        print_w2(d["w2"])
        print()
        print_contractor(d["contractor_self"])
        print()
        print(f"Employer cash: W-2 {money(d['w2_employer_cost'])} vs 1099 {money(d['contractor_employer_cost'])}")
        print(f"Employer saves vs W-2: {money(d['employer_saves_vs_w2'])}  — {d['misclass_flag']}")
        return
    d = w2_loaded(args.state, args.wages, rate, extra, args.suta_kind)
    if args.json:
        print(json.dumps(d, indent=2))
    else:
        print_w2(d)


if __name__ == "__main__":
    main()
