#!/usr/bin/env python3
"""
Theme-level summary tables for BQ3/BQ4 (design doc §10.3).

Inputs:
  data/processed/reviews_with_themes.csv
  config/themes.yml

Outputs:
  reports/tables/theme_summary_overall.csv
  reports/tables/theme_summary_by_app.csv
  reports/tables/low_star_theme_summary.csv
"""

from __future__ import annotations

from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
REVIEWS_CSV = ROOT / "data" / "processed" / "reviews_with_themes.csv"
THEMES_YML = ROOT / "config" / "themes.yml"
OUT_DIR = ROOT / "reports" / "tables"


def _load_theme_meta() -> pd.DataFrame:
    import yaml

    cfg = yaml.safe_load(THEMES_YML.read_text(encoding="utf-8"))
    rows = []
    for t in cfg.get("themes", []):
        rows.append(
            {
                "theme_id": t["id"],
                "theme_label": t.get("label", t["id"]),
                "category": t.get("category", ""),
                "polarity": t.get("polarity", ""),
            }
        )
    return pd.DataFrame(rows)


def _theme_columns(df: pd.DataFrame) -> list[str]:
    return [c for c in df.columns if c.startswith("theme_") and c != "theme_tags"]


def main() -> None:
    if not REVIEWS_CSV.is_file():
        raise FileNotFoundError(f"Missing {REVIEWS_CSV}. Run build_review_themes.py first.")

    df = pd.read_csv(REVIEWS_CSV, encoding="utf-8-sig")
    df["score"] = pd.to_numeric(df["score"], errors="coerce")
    theme_cols = _theme_columns(df)
    meta = _load_theme_meta()
    n_total = len(df)
    global_mean = float(df["score"].mean(skipna=True))

    overall_rows = []
    for col in theme_cols:
        tid = col.replace("theme_", "", 1)
        mask = df[col].astype(int) == 1
        sub = df.loc[mask]
        n = int(mask.sum())
        if n == 0:
            continue
        low = sub["score"].le(2)
        overall_rows.append(
            {
                "theme_id": tid,
                "n_reviews": n,
                "theme_share": round(n / n_total, 6),
                "mean_score": round(float(sub["score"].mean()), 6),
                "rating_gap": round(global_mean - float(sub["score"].mean()), 6),
                "share_low_1_2": round(float(low.mean()), 6),
                "low_star_theme_share": round(
                    float(low.sum()) / max(int(df["score"].le(2).sum()), 1), 6
                ),
            }
        )

    overall = pd.DataFrame(overall_rows).merge(meta, on="theme_id", how="left")
    overall = overall.sort_values("n_reviews", ascending=False, kind="stable")

    by_app_rows = []
    for (app_id, app_name), g in df.groupby(["app_id", "app_name"], observed=True):
        app_mean = float(g["score"].mean(skipna=True))
        app_n = len(g)
        for col in theme_cols:
            tid = col.replace("theme_", "", 1)
            mask = g[col].astype(int) == 1
            n = int(mask.sum())
            if n == 0:
                continue
            sub = g.loc[mask]
            by_app_rows.append(
                {
                    "app_id": app_id,
                    "app_name": app_name,
                    "theme_id": tid,
                    "n_reviews": n,
                    "theme_share_in_app": round(n / app_n, 6),
                    "mean_score": round(float(sub["score"].mean()), 6),
                    "rating_gap": round(app_mean - float(sub["score"].mean()), 6),
                    "share_low_1_2": round(float(sub["score"].le(2).mean()), 6),
                }
            )

    by_app = pd.DataFrame(by_app_rows).merge(meta, on="theme_id", how="left")

    low_star = df[df["score"].le(2)].copy()
    n_low = len(low_star)
    low_rows = []
    for col in theme_cols:
        tid = col.replace("theme_", "", 1)
        n = int((low_star[col].astype(int) == 1).sum())
        if n == 0:
            continue
        low_rows.append(
            {
                "theme_id": tid,
                "n_low_star_reviews": n,
                "low_star_theme_share": round(n / n_low, 6) if n_low else 0.0,
            }
        )
    low_summary = pd.DataFrame(low_rows).merge(meta, on="theme_id", how="left")
    low_summary = low_summary.sort_values("low_star_theme_share", ascending=False, kind="stable")

    coverage = float((df["n_themes_hit"] > 0).mean()) if "n_themes_hit" in df.columns else float("nan")

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    overall.to_csv(OUT_DIR / "theme_summary_overall.csv", index=False, encoding="utf-8-sig")
    by_app.to_csv(OUT_DIR / "theme_summary_by_app.csv", index=False, encoding="utf-8-sig")
    low_summary.to_csv(OUT_DIR / "low_star_theme_summary.csv", index=False, encoding="utf-8-sig")

    print(f"Saved: {OUT_DIR / 'theme_summary_overall.csv'} ({len(overall)} themes with hits)")
    print(f"Saved: {OUT_DIR / 'theme_summary_by_app.csv'} ({len(by_app)} rows)")
    print(f"Saved: {OUT_DIR / 'low_star_theme_summary.csv'}")
    print(f"Theme coverage rate (>=1 tag): {coverage:.1%}")


if __name__ == "__main__":
    main()
