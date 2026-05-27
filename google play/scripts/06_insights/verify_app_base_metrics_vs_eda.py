#!/usr/bin/env python3
"""
Verify reports/tables/app_base_metrics.csv against EDA Section A exports.

Checks:
  - A2_mean_score_by_app: mean_score vs mean, n_reviews vs count
  - A2_rating_counts_by_app: share_1..5 vs counts-derived shares

Exit code 0 if all checks pass, 1 otherwise.
Prints PASS/FAIL only (no report file).
"""

from __future__ import annotations

import sys
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
BASE_CSV = ROOT / "reports" / "tables" / "app_base_metrics.csv"
A2_MEAN = ROOT / "reports" / "eda_section_a" / "A2_mean_score_by_app.csv"
A2_COUNTS = ROOT / "reports" / "eda_section_a" / "A2_rating_counts_by_app.csv"
MEAN_TOL = 1e-5
SHARE_TOL = 1e-5


def main() -> int:
    missing = [p for p in (BASE_CSV, A2_MEAN, A2_COUNTS) if not p.is_file()]
    if missing:
        print("Missing files:", *[str(p) for p in missing], sep="\n  ")
        return 1

    base = pd.read_csv(BASE_CSV, encoding="utf-8-sig")
    a2_mean = pd.read_csv(A2_MEAN, encoding="utf-8-sig")
    a2_counts = pd.read_csv(A2_COUNTS, encoding="utf-8-sig")

    issues: list[str] = []

    if len(base) != len(a2_mean):
        issues.append(f"app count mismatch: base={len(base)} vs A2_mean={len(a2_mean)}")
    if len(base) != len(a2_counts):
        issues.append(f"app count mismatch: base={len(base)} vs A2_counts={len(a2_counts)}")

    m = base.merge(a2_mean, on="app_id", how="outer", suffixes=("", "_eda_mean"), indicator=True)
    if not m["_merge"].eq("both").all():
        only_left = m.loc[m["_merge"] == "left_only", "app_id"].tolist()
        only_right = m.loc[m["_merge"] == "right_only", "app_id"].tolist()
        if only_left:
            issues.append(f"app_ids only in app_base_metrics: {only_left}")
        if only_right:
            issues.append(f"app_ids only in A2_mean: {only_right}")
    m = m[m["_merge"] == "both"].drop(columns=["_merge"])

    m["delta_mean"] = (m["mean_score"] - m["mean"]).abs()
    m["delta_count"] = (m["n_reviews"] - m["count"]).abs()
    mean_fail = m["delta_mean"] > MEAN_TOL
    count_fail = m["delta_count"] > 0

    if mean_fail.any():
        issues.append(
            "mean mismatch (> tol): "
            + m.loc[mean_fail, ["app_name", "mean_score", "mean", "delta_mean"]].to_string(index=False)
        )
    if count_fail.any():
        issues.append(
            "count mismatch: "
            + m.loc[count_fail, ["app_name", "n_reviews", "count"]].to_string(index=False)
        )

    # Shares from A2 counts
    star_cols = ["1", "2", "3", "4", "5"]
    if not all(c in a2_counts.columns for c in star_cols):
        issues.append(f"A2_rating_counts missing columns {star_cols}; got {list(a2_counts.columns)}")
        _print_summary(issues)
        return 1

    cnt = a2_counts.copy()
    row_tot = cnt[star_cols].sum(axis=1)
    for k in range(1, 6):
        cnt[f"eda_share_{k}"] = cnt[str(k)] / row_tot.replace(0, pd.NA)

    mc = base.merge(cnt[["app_id"] + [f"eda_share_{k}" for k in range(1, 6)]], on="app_id", how="outer", indicator=True)
    if not mc["_merge"].eq("both").all():
        issues.append("app_id alignment failed when merging rating counts")
    mc = mc[mc["_merge"] == "both"].drop(columns=["_merge"])

    for k in range(1, 6):
        d = (mc[f"share_{k}"] - mc[f"eda_share_{k}"]).abs()
        bad = d > SHARE_TOL
        if bad.any():
            issues.append(
                f"share_{k} mismatch (> {SHARE_TOL}):\n"
                + mc.loc[bad, ["app_name", f"share_{k}", f"eda_share_{k}"]].assign(delta=d).to_string(index=False)
            )

    _print_summary(issues)
    return 1 if issues else 0


def _print_summary(issues: list[str]) -> None:
    if issues:
        print("VERIFICATION FAILED")
        for line in issues:
            print(line)
    else:
        print("VERIFICATION OK — app_base_metrics matches EDA A2 (mean, count, shares).")


if __name__ == "__main__":
    sys.exit(main())
