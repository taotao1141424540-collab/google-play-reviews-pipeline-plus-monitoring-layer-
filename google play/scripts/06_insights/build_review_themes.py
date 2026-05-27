#!/usr/bin/env python3
"""
Rule-based multi-label theme tagging on clean_en_only (design doc §11).

Inputs:
  data/processed/clean_en_only.csv
  config/themes.yml

Output:
  data/processed/reviews_with_themes.csv
"""

from __future__ import annotations

from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
CLEAN_EN_CSV = ROOT / "data" / "processed" / "clean_en_only.csv"
THEMES_YML = ROOT / "config" / "themes.yml"
OUT_CSV = ROOT / "data" / "processed" / "reviews_with_themes.csv"


def _load_themes() -> list[dict]:
    if not THEMES_YML.is_file():
        raise FileNotFoundError(f"Missing {THEMES_YML}")
    try:
        import yaml
    except ImportError as e:
        raise ImportError("PyYAML required: pip install pyyaml") from e
    cfg = yaml.safe_load(THEMES_YML.read_text(encoding="utf-8"))
    themes = cfg.get("themes", [])
    if not themes:
        raise ValueError("themes.yml has no themes")
    return themes


def _text_for_match(row: pd.Series) -> str:
    if "content_clean" in row.index and pd.notna(row["content_clean"]) and str(row["content_clean"]).strip():
        return str(row["content_clean"]).lower()
    return str(row.get("content", "")).lower().strip()


def _matches_theme(text: str, theme: dict) -> bool:
    keywords = [str(k).lower() for k in theme.get("keywords", []) if k]
    exclude = [str(k).lower() for k in theme.get("exclude", []) if k]
    if not keywords:
        return False
    if any(ex in text for ex in exclude):
        return False
    return any(kw in text for kw in keywords)


def main() -> None:
    if not CLEAN_EN_CSV.is_file():
        raise FileNotFoundError(f"Missing {CLEAN_EN_CSV}. Run scripts/02_clean/clean_and_eda.py first.")

    themes = _load_themes()
    df = pd.read_csv(CLEAN_EN_CSV, encoding="utf-8-sig")
    texts = df.apply(_text_for_match, axis=1)

    theme_ids = [t["id"] for t in themes]
    hit_cols: dict[str, list[int]] = {tid: [] for tid in theme_ids}
    tag_lists: list[str] = []

    for text in texts:
        hits = [t["id"] for t in themes if _matches_theme(text, t)]
        tag_lists.append(";".join(hits))
        for tid in theme_ids:
            hit_cols[tid].append(1 if tid in hits else 0)

    out = df.copy()
    out["theme_tags"] = tag_lists
    out["n_themes_hit"] = out["theme_tags"].apply(lambda s: len(s.split(";")) if s else 0)
    for tid in theme_ids:
        out[f"theme_{tid}"] = hit_cols[tid]

    OUT_CSV.parent.mkdir(parents=True, exist_ok=True)
    out.to_csv(OUT_CSV, index=False, encoding="utf-8-sig")

    n = len(out)
    tagged = int((out["n_themes_hit"] > 0).sum())
    print(f"Saved: {OUT_CSV}")
    print(f"Rows: {n}; with >=1 theme: {tagged} ({tagged / n:.1%})")
    print(f"Themes configured: {len(theme_ids)}")


if __name__ == "__main__":
    main()
