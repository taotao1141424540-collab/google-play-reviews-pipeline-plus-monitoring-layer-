#!/usr/bin/env python3
"""
Sample reviews for manual theme validation (design doc Appendix E.2).

Strategy:
  - Per theme (priority on those with >=20 hits), draw up to `--per-theme` rows.
  - Additionally include reviews with `n_themes_hit == 0` for recall checking.
  - Stratify across low-star (<=2), mid (3), high (>=4) to expose negation issues.

Output:
  reports/tables/theme_validation_sample.csv
    columns: app_name, score, content_clean, theme_tags, n_themes_hit,
             precision_correct (blank for human), missed_theme (blank),
             notes (blank)
"""

from __future__ import annotations

import argparse
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
REVIEWS_CSV = ROOT / "data" / "processed" / "reviews_with_themes.csv"
OUT_CSV = ROOT / "reports" / "tables" / "theme_validation_sample.csv"


def _theme_columns(df: pd.DataFrame) -> list[str]:
    return [c for c in df.columns if c.startswith("theme_") and c != "theme_tags"]


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--per-theme", type=int, default=15, help="rows to draw per theme (default 15)")
    parser.add_argument("--zero-tag-rows", type=int, default=30, help="rows with no theme hits (recall check)")
    parser.add_argument("--random-state", type=int, default=42)
    args = parser.parse_args()

    if not REVIEWS_CSV.is_file():
        raise FileNotFoundError(f"Missing {REVIEWS_CSV}. Run build_review_themes.py first.")

    df = pd.read_csv(REVIEWS_CSV, encoding="utf-8-sig")
    df["score"] = pd.to_numeric(df["score"], errors="coerce")
    keep_cols = ["app_name", "score", "content_clean", "theme_tags", "n_themes_hit"]
    keep_cols = [c for c in keep_cols if c in df.columns]

    parts: list[pd.DataFrame] = []
    chosen: set = set()
    theme_cols = _theme_columns(df)

    def _band(s: float) -> str:
        if pd.isna(s):
            return "unknown"
        if s <= 2:
            return "low"
        if s == 3:
            return "mid"
        return "high"

    df["_score_band"] = df["score"].apply(_band)

    for col in theme_cols:
        sub = df[df[col] == 1]
        if sub.empty:
            continue
        bands = sub.groupby("_score_band", observed=True)
        per_band = max(1, args.per_theme // 3)
        for _, g in bands:
            take = g.sample(min(per_band, len(g)), random_state=args.random_state)
            parts.append(take[keep_cols].assign(_source=f"theme={col}"))
            chosen.update(take.index.tolist())

    zero = df[(df["n_themes_hit"] == 0) & (~df.index.isin(chosen))]
    if len(zero):
        z = zero.sample(min(args.zero_tag_rows, len(zero)), random_state=args.random_state)
        parts.append(z[keep_cols].assign(_source="zero_tag"))

    out = pd.concat(parts, ignore_index=True).drop_duplicates(subset=["content_clean"], keep="first")
    out["precision_correct"] = ""
    out["missed_theme"] = ""
    out["notes"] = ""

    OUT_CSV.parent.mkdir(parents=True, exist_ok=True)
    out.to_csv(OUT_CSV, index=False, encoding="utf-8-sig")
    print(f"Saved: {OUT_CSV}")
    print(f"Rows: {len(out)} (theme-stratified + zero-tag)")
    print("Fill columns: precision_correct (Y/N), missed_theme, notes — then revise themes.yml.")


if __name__ == "__main__":
    main()
