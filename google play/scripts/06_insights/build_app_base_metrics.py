#!/usr/bin/env python3
"""
App-level base metrics from the English analysis set (canonical KPI table).

Input:
  data/processed/clean_en_only.csv

Output:
  reports/tables/app_base_metrics.csv

Cross-check (same input + same app grain):
  reports/eda_section_a/A2_mean_score_by_app.csv  -> mean, count
  reports/eda_section_a/A2_rating_counts_by_app.csv -> star counts / shares
"""

from __future__ import annotations

from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
CLEAN_EN_CSV = ROOT / "data" / "processed" / "clean_en_only.csv"
OUT_CSV = ROOT / "reports" / "tables" / "app_base_metrics.csv"


def main() -> None:
    if not CLEAN_EN_CSV.is_file():
        raise FileNotFoundError(f"Missing {CLEAN_EN_CSV}. Run scripts/02_clean/clean_and_eda.py first.")

    df = pd.read_csv(CLEAN_EN_CSV, encoding="utf-8-sig")
    if df.empty:
        raise ValueError("clean_en_only.csv is empty.")

    df = df.copy()
    df["score"] = pd.to_numeric(df["score"], errors="coerce")
    scored = df[df["score"].notna()].copy()
    if scored.empty:
        raise ValueError("No rows with parseable score.")

    # Star counts 1..5 per app (same basis as EDA A2).
    counts = (
        scored.groupby(["app_id", "app_name", "score"], observed=True)
        .size()
        .unstack(fill_value=0)
        .reindex(columns=range(1, 6), fill_value=0)
    )
    n = counts.sum(axis=1).astype("int64")
    shares = counts.div(n.replace(0, pd.NA), axis=0)

    base = scored.groupby(["app_id", "app_name"], observed=True).agg(
        mean_score=("score", "mean"),
        median_score=("score", "median"),
        std_score=("score", "std"),
    )

    out = base.join(
        pd.DataFrame(
            {
                "n_reviews": n,
                "share_1": shares[1],
                "share_2": shares[2],
                "share_3": shares[3],
                "share_4": shares[4],
                "share_5": shares[5],
            }
        )
    )

    out["share_high_4_5"] = out["share_4"] + out["share_5"]
    out["share_low_1_2"] = out["share_1"] + out["share_2"]

    gb = scored.groupby(["app_id", "app_name"], observed=True)
    # Quality / reply rates (same grain as EDA; flags come from 02_clean).
    if "has_dev_reply" in scored.columns:
        out["share_has_dev_reply"] = gb["has_dev_reply"].mean()
    if "is_noise" in scored.columns:
        out["share_is_noise"] = gb["is_noise"].mean()
    if "is_spam_bot_suspect" in scored.columns:
        out["share_is_spam_bot_suspect"] = gb["is_spam_bot_suspect"].mean()
    if "is_time_anomaly" in scored.columns:
        out["share_is_time_anomaly"] = gb["is_time_anomaly"].mean()
    if "is_inconsistent_rating" in scored.columns:
        out["share_is_inconsistent_rating"] = gb["is_inconsistent_rating"].mean()

    out = out.reset_index()

    # Round for readability (keep enough precision for reconciliation).
    for col in out.columns:
        if col.startswith("share_") or col in ("mean_score", "median_score", "std_score"):
            out[col] = pd.to_numeric(out[col], errors="coerce").round(6)

    out = out.sort_values(["app_name", "app_id"], kind="stable").reset_index(drop=True)

    OUT_CSV.parent.mkdir(parents=True, exist_ok=True)
    out.to_csv(OUT_CSV, index=False, encoding="utf-8-sig")

    print(f"Saved: {OUT_CSV}")
    print(f"Rows (apps): {len(out)}")


if __name__ == "__main__":
    main()
