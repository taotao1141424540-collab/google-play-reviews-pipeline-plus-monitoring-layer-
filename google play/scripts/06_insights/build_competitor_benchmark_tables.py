#!/usr/bin/env python3
"""
Competitor benchmark tables (BQ2): app-level, publisher-level, flagship subset,
volume vs rating scatter source, and draft Page 2 bullets.

Inputs:
  reports/tables/app_base_metrics.csv
  reports/tables/app_health_score.csv
  config/app_list.xlsx  (category + ordering reference)
  config/benchmark_flagship.json

Outputs:
  reports/tables/app_benchmark_bq2.csv
  reports/tables/publisher_benchmark.csv
  reports/tables/flagship_7_benchmark.csv
  reports/tables/volume_vs_rating_scatter.csv
  reports/page2_competitor_findings_draft.md
"""

from __future__ import annotations

import json
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
BASE_CSV = ROOT / "reports" / "tables" / "app_base_metrics.csv"
HEALTH_CSV = ROOT / "reports" / "tables" / "app_health_score.csv"
APP_LIST = ROOT / "config" / "app_list.xlsx"
FLAGSHIP_JSON = ROOT / "config" / "benchmark_flagship.json"
OUT_DIR = ROOT / "reports" / "tables"
PAGE2_MD = ROOT / "reports" / "page2_competitor_findings_draft.md"


def publisher_from_app_id(app_id: str) -> str:
    rules = [
        ("com.king.", "King"),
        ("com.playrix.", "Playrix"),
        ("com.dreamgames.", "Dream Games"),
        ("net.peakgames.", "Peak Games"),
        ("air.com.sgn.", "SGN (Jam City)"),
        ("com.disney.", "Disney"),
        ("dk.tactile.", "Tactile Games"),
        ("com.rovio.", "Rovio"),
    ]
    for prefix, name in rules:
        if app_id.startswith(prefix):
            return name
    return "Other"


def main() -> None:
    if not BASE_CSV.is_file() or not HEALTH_CSV.is_file():
        raise FileNotFoundError("Run build_app_base_metrics.py and build_health_score.py first.")

    base = pd.read_csv(BASE_CSV, encoding="utf-8-sig")
    hs = pd.read_csv(HEALTH_CSV, encoding="utf-8-sig")

    hs_cols = [
        "app_id",
        "health_score_rank",
        "bayesian_adjusted_avg",
        "health_score",
        "component_confidence",
    ]
    hs_sub = hs[[c for c in hs_cols if c in hs.columns]].copy()

    bq2 = base.merge(hs_sub, on="app_id", how="left", suffixes=("", "_hs"))
    if "app_name_hs" in bq2.columns:
        bq2 = bq2.drop(columns=[c for c in bq2.columns if c.endswith("_hs") and c != "app_id"])

    bq2["publisher"] = bq2["app_id"].map(publisher_from_app_id)

    if APP_LIST.is_file():
        meta = pd.read_excel(APP_LIST)
        if "category" in meta.columns:
            bq2 = bq2.merge(
                meta[["app_id", "category"]],
                on="app_id",
                how="left",
            )

    order_cols = [
        "app_id",
        "app_name",
        "publisher",
        "category",
        "n_reviews",
        "mean_score",
        "median_score",
        "share_high_4_5",
        "share_low_1_2",
        "bayesian_adjusted_avg",
        "health_score_rank",
        "health_score",
        "component_confidence",
    ]
    order_cols = [c for c in order_cols if c in bq2.columns]
    bq2_out = bq2[order_cols].sort_values(["publisher", "app_name"], kind="stable").reset_index(drop=True)

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    bq2_out.to_csv(OUT_DIR / "app_benchmark_bq2.csv", index=False, encoding="utf-8-sig")

    # Publisher-level
    rows = []
    for pub_name, sub in bq2.groupby("publisher", observed=True):
        tw = sub["n_reviews"].sum()
        wmean = float((sub["mean_score"] * sub["n_reviews"]).sum() / tw) if tw else float("nan")
        wbay = float((sub["bayesian_adjusted_avg"] * sub["n_reviews"]).sum() / tw) if tw else float("nan")
        whealth = float((sub["health_score"] * sub["n_reviews"]).sum() / tw) if tw else float("nan")
        rows.append(
            {
                "publisher": pub_name,
                "n_apps": int(sub["app_id"].nunique()),
                "total_n_reviews": int(tw),
                "weighted_mean_score": round(wmean, 6),
                "weighted_bayesian_adjusted_avg": round(wbay, 6),
                "weighted_health_score": round(whealth, 6),
            }
        )
    publisher_df = pd.DataFrame(rows).sort_values("weighted_health_score", ascending=False, kind="stable").reset_index(
        drop=True
    )
    publisher_df.insert(1, "publisher_health_rank", range(1, len(publisher_df) + 1))
    publisher_df.to_csv(OUT_DIR / "publisher_benchmark.csv", index=False, encoding="utf-8-sig")

    # Flagship 7
    if not FLAGSHIP_JSON.is_file():
        raise FileNotFoundError(f"Missing {FLAGSHIP_JSON}")
    cfg = json.loads(FLAGSHIP_JSON.read_text(encoding="utf-8"))
    flagship_ids = cfg.get("app_ids", [])
    flagship = bq2_out[bq2_out["app_id"].isin(flagship_ids)].copy()
    missing = set(flagship_ids) - set(flagship["app_id"].tolist())
    if missing:
        raise ValueError(f"Flagship app_ids not found in benchmark table: {missing}")
    flagship = flagship.set_index("app_id").loc[flagship_ids].reset_index()
    flagship.to_csv(OUT_DIR / "flagship_7_benchmark.csv", index=False, encoding="utf-8-sig")

    # Scatter
    scatter = bq2[
        [
            "app_id",
            "app_name",
            "publisher",
            "n_reviews",
            "mean_score",
            "bayesian_adjusted_avg",
            "health_score",
            "health_score_rank",
        ]
    ].copy()
    scatter = scatter.sort_values("n_reviews", ascending=False, kind="stable").reset_index(drop=True)
    scatter.to_csv(OUT_DIR / "volume_vs_rating_scatter.csv", index=False, encoding="utf-8-sig")

    # Draft Page 2 bullets (markdown)
    top_pub = publisher_df.iloc[0]

    lines = [
        "# Page 2 — Competitor findings (draft, data-driven)",
        "",
        f"_Generated from current `reports/tables/*.csv`. Selection rationale for flagship 7: {cfg.get('selection_rationale', '')}_",
        "",
        "## Bullets (edit wording for deck)",
        "",
    ]
    top_parts = [
        f"{r['app_name']} #{int(r['health_score_rank'])} ({float(r['health_score']):.3f}, n={int(r['n_reviews'])})"
        for _, r in hs.head(3).iterrows()
    ]
    bot_parts = [
        f"{r['app_name']} #{int(r['health_score_rank'])} ({float(r['health_score']):.3f}, n={int(r['n_reviews'])})"
        for _, r in hs.tail(3).iloc[::-1].iterrows()
    ]
    lines.append("- **Top 3 (Health Score in this 14-app pool)**: " + "; ".join(top_parts) + ".")
    lines.append("- **Watchlist (bottom 3 Health Score)**: " + "; ".join(bot_parts) + ".")
    lines.append(
        f"- **By publisher (weighted health in this pool)**: `{top_pub['publisher']}` leads "
        f"(weighted_health_score={float(top_pub['weighted_health_score']):.3f}, "
        f"{int(top_pub['n_apps'])} apps, {int(top_pub['total_n_reviews'])} reviews)."
    )
    lines.append(
        "- **Volume vs rating**: use `volume_vs_rating_scatter.csv` — high volume with weaker `bayesian_adjusted_avg` "
        "signals sustained visibility despite satisfaction pressure (descriptive only)."
    )
    lines.append("")
    lines.append("## Limitations")
    lines.append("- Public review sample; no revenue/retention; rankings valid only within this 14-app pool.")
    PAGE2_MD.parent.mkdir(parents=True, exist_ok=True)
    PAGE2_MD.write_text("\n".join(lines), encoding="utf-8")

    print(f"Saved: {OUT_DIR / 'app_benchmark_bq2.csv'}")
    print(f"Saved: {OUT_DIR / 'publisher_benchmark.csv'}")
    print(f"Saved: {OUT_DIR / 'flagship_7_benchmark.csv'}")
    print(f"Saved: {OUT_DIR / 'volume_vs_rating_scatter.csv'}")
    print(f"Saved: {PAGE2_MD}")


if __name__ == "__main__":
    main()
