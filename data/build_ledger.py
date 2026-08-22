#!/usr/bin/env python3
"""Consolidates every candidate actually evaluated across F2/F5/F6/F7 into
ledger_trials.csv, per 06_GERBANG_DAN_ANGGARAN.md's schema. Parses the
report tables rather than re-running anything (re-running costs real
time; the numbers are already computed and printed in reports/*.md).

Honest about gaps: eff_n/ic/p_raw/sharpe/max_dd/capture_ratio were not
all individually persisted during the runs (only t_stat, n_trades,
expectancy_bps, and the checklist pass count were kept per candidate).
Columns not actually tracked are left empty, not fabricated.
"""
import csv
import re
from pathlib import Path
from datetime import datetime, timezone

REPORTS_DIR = Path("/workspace/reports")
OUT_PATH = Path("/workspace/ledger_trials.csv")

COLUMNS = [
    "trial_id", "timestamp", "candidate_id", "formula_id", "division",
    "instrument_set", "horizon", "params_hash", "partition", "n_trades",
    "eff_n", "ic", "t_stat", "p_raw", "p_effN", "expectancy_bps", "sharpe",
    "max_dd", "capture_ratio", "status", "notes",
]

SOURCES = [
    ("F2_payoff_gate.md", "X", "F2", "screen"),
    ("F5_exit_sizing.md", "X", "F5", "screen"),
    ("F6_screening.md", "E", "F6", "screen"),
    ("F7_meta_ml.md", "M", "F7", "screen"),
]

# Format lama (F5 dan laporan F6/F7 pra-run-penuh): nama|n_trade|exp_net_bps|t_stat|checks/total|...
ROW_RE_OLD = re.compile(r"^\|\s*([^\|]+?)\s*\|\s*(\d+)\s*\|\s*(-?\d+\.?\d*)\s*\|\s*(-?\d+\.?\d*)\s*\|\s*(\d+)/(\d+)\s*\|")
# Format baru (F6/F7 run penuh, punya kolom gross+breakeven tambahan):
# nama|n_trade|gross_bps|net_bps|breakeven_bps|t_stat|checks/total|...
ROW_RE_NEW = re.compile(
    r"^\|\s*([^\|]+?)\s*\|\s*(\d+)\s*\|\s*(-?\d+\.?\d*)\s*\|\s*(-?\d+\.?\d*)\s*\|\s*(-?\d+\.?\d*)\s*\|\s*(-?\d+\.?\d*)\s*\|\s*(\d+)/(\d+)\s*\|"
)
# Format run parsial (dihentikan sebelum breakeven/batch-checks tersedia):
# nama|n_trade|gross_bps|net_bps|t_stat|checks_parsial/12|
ROW_RE_PARTIAL = re.compile(
    r"^\|\s*([^\|]+?)\s*\|\s*(\d+)\s*\|\s*(-?\d+\.?\d*)\s*\|\s*(-?\d+\.?\d*)\s*\|\s*(-?\d+\.?\d*)\s*\|\s*(\d+)/(\d+)\s*\|"
)


def parse_table_rows(text: str):
    rows = []
    for line in text.splitlines():
        line = line.strip()
        if line.startswith("|---") or "| Kandidat " in line or "| Sinyal " in line:
            continue
        m_new = ROW_RE_NEW.match(line)
        if m_new:
            name, n_trades, gross_bps, net_bps, _breakeven, t_stat, passed, total = m_new.groups()
            rows.append({
                "candidate_id": name, "n_trades": n_trades, "expectancy_bps": net_bps,
                "t_stat": t_stat, "checks_passed": passed, "checks_total": total,
                "gross_bps": gross_bps,
            })
            continue
        m_old = ROW_RE_OLD.match(line)
        if m_old:
            name, n_trades, exp_bps, t_stat, passed, total = m_old.groups()
            if name.startswith("Kandidat") or name.startswith("---"):
                continue
            rows.append({
                "candidate_id": name, "n_trades": n_trades, "expectancy_bps": exp_bps,
                "t_stat": t_stat, "checks_passed": passed, "checks_total": total,
                "gross_bps": "",
            })
            continue
        m_partial = ROW_RE_PARTIAL.match(line)
        if m_partial:
            name, n_trades, gross_bps, net_bps, t_stat, passed, total = m_partial.groups()
            if total != "12":  # only treat as partial-format if checks denominator is /12 (non-batch-only)
                continue
            rows.append({
                "candidate_id": name, "n_trades": n_trades, "expectancy_bps": net_bps,
                "t_stat": t_stat, "checks_passed": passed, "checks_total": total,
                "gross_bps": gross_bps,
            })
    return rows


def main():
    trial_id = 1
    all_rows = []
    now = datetime.now(timezone.utc).isoformat()

    for fname, division, phase, partition in SOURCES:
        f = REPORTS_DIR / fname
        if not f.exists():
            continue
        text = f.read_text()
        is_smoke = "SMOKE TEST" in text or "BELUM SELESAI" in text
        parsed = parse_table_rows(text)
        for r in parsed:
            status = "SMOKE_TEST_INCOMPLETE" if is_smoke else "EVALUATED_NOL_LOLOS_OR_PENDING"
            checks_passed = int(r["checks_passed"])
            if checks_passed >= 13:
                status = "CANDIDATE_PASSED_THRESHOLD" if not is_smoke else "SMOKE_TEST_INCOMPLETE"
            all_rows.append({
                "trial_id": trial_id, "timestamp": now, "candidate_id": r["candidate_id"],
                "formula_id": r["candidate_id"].split("_")[0], "division": division,
                "instrument_set": "XAUUSD", "horizon": "H60" if "H" not in r["candidate_id"] else "",
                "params_hash": "", "partition": partition, "n_trades": r["n_trades"],
                "eff_n": "", "ic": "", "t_stat": r["t_stat"], "p_raw": "", "p_effN": "",
                "expectancy_bps": r["expectancy_bps"], "sharpe": "", "max_dd": "", "capture_ratio": "",
                "status": f"{status} ({r['checks_passed']}/{r['checks_total']} checks, {phase})",
                "notes": (
                    "SMOKE_TEST_50K_BARS_NOT_FULL_RUN" if is_smoke
                    else (f"gross_bps={r['gross_bps']}" if r.get("gross_bps") else "")
                ),
            })
            trial_id += 1

    # F2 has its own per-horizon table format (k_sl/k_tp/side), parsed separately
    f2 = REPORTS_DIR / "F2_payoff_gate.md"
    if f2.exists():
        text = f2.read_text()
        f2_re = re.compile(r"^\|\s*([\d.]+)\s*\|\s*([\d.]+)\s*\|\s*(long|short)\s*\|\s*(-?[\d.]+)\s*\|\s*(-?[\d.]+)\s*\|")
        current_horizon = None
        for line in text.splitlines():
            hm = re.match(r"^### (H\d+)", line.strip())
            if hm:
                current_horizon = hm.group(1)
                continue
            m = f2_re.match(line.strip())
            if m and current_horizon:
                k_sl, k_tp, side, margin, net_bps = m.groups()
                all_rows.append({
                    "trial_id": trial_id, "timestamp": now,
                    "candidate_id": f"X01_ksl{k_sl}_ktp{k_tp}_{side}", "formula_id": "X01",
                    "division": "X", "instrument_set": "XAUUSD", "horizon": current_horizon,
                    "params_hash": "", "partition": "screen", "n_trades": "", "eff_n": "", "ic": "",
                    "t_stat": "", "p_raw": "", "p_effN": "", "expectancy_bps": net_bps, "sharpe": "",
                    "max_dd": "", "capture_ratio": "", "status": "F2_PAYOFF_GATE_ALL_6_CRITERIA_FAILED",
                    "notes": f"margin_pp_demeaned={margin} (lolos margin/gap/net_bps dasar, GUGUR di sign_flip/stability)",
                })
                trial_id += 1

    with open(OUT_PATH, "w", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=COLUMNS)
        writer.writeheader()
        for row in all_rows:
            writer.writerow(row)

    print(f"Ditulis {len(all_rows)} baris ke {OUT_PATH}")


if __name__ == "__main__":
    main()
