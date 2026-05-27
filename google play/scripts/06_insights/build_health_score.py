#!/usr/bin/env python3
"""
Compute App Satisfaction Health Score (design doc Appendix A–C).

Reads:
  reports/tables/app_base_metrics.csv  (must run build_app_base_metrics.py first)
  data/processed/clean_en_only.csv    (timestamps for momentum)

Formula:
  Health = (wL*Level + wP*Polarization + wM*Momentum) * Confidence
  Level = BayesianAdjustedAvg / 5
  Polarization = 1 - share_low_1_2
  Confidence = min(1, n_reviews / confidence_reference_n)
  BayesianAdjustedAvg = (n*mean + k*global_mean) / (n + k)

Momentum:
  Prefer linear slope of weekly mean rating over the latest N calendar weeks (min weeks gate);
  else fallback: mean(score | date >= median) - mean(score | date < median).

Outputs:
  reports/tables/app_health_score.csv
"""

from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
CONFIG_JSON = ROOT / "config" / "metrics.json"
BASE_CSV = ROOT / "reports" / "tables" / "app_base_metrics.csv"
CLEAN_EN_CSV = ROOT / "data" / "processed" / "clean_en_only.csv"
OUT_CSV = ROOT / "reports" / "tables" / "app_health_score.csv"


def _load_config() -> dict:
    if not CONFIG_JSON.is_file():
        raise FileNotFoundError(f"Missing {CONFIG_JSON}")
    return json.loads(CONFIG_JSON.read_text(encoding="utf-8"))


def _min_max_01(s: pd.Series) -> pd.Series:
    s = pd.to_numeric(s, errors="coerce")
    lo = s.min(skipna=True)
    hi = s.max(skipna=True)
    if pd.isna(lo) or pd.isna(hi) or hi - lo < 1e-12:
        return pd.Series(0.5, index=s.index)
    return (s - lo) / (hi - lo)


def _momentum_raw_per_app(df: pd.DataFrame, cfg: dict) -> pd.Series:
    """Return raw momentum signal per app_id (unnormalized)."""
    window_weeks = int(cfg["momentum"]["calendar_weeks_window"])
    min_weeks = int(cfg["momentum"]["min_distinct_weeks_for_slope"])

    sub = df[["app_id", "score", "at_parsed"]].copy()
    sub["at_parsed"] = pd.to_datetime(sub["at_parsed"], errors="coerce")
    sub = sub[sub["at_parsed"].notna() & sub["score"].notna()]
    sub["score"] = pd.to_numeric(sub["score"], errors="coerce")
    sub = sub[sub["score"].notna()]

    raw: dict[object, float] = {}
    for aid, g in sub.groupby("app_id", observed=True):
        latest = g["at_parsed"].max()
        if pd.isna(latest):
            raw[aid] = np.nan
            continue
        cut = latest - pd.Timedelta(weeks=window_weeks)
        recent = g[g["at_parsed"] >= cut].copy()
        recent["week_period"] = recent["at_parsed"].dt.to_period("W-MON")
        wk_mean = recent.groupby("week_period", observed=True)["score"].mean().sort_index()
        if len(wk_mean) >= min_weeks:
            x = np.arange(len(wk_mean), dtype=float)
            y = wk_mean.to_numpy(dtype=float)
            slope = float(np.polyfit(x, y, 1)[0])
            raw[aid] = slope
            continue
        # Fallback: median split on full app history in English set
        med = g["at_parsed"].median()
        early = g.loc[g["at_parsed"] < med, "score"]
        late = g.loc[g["at_parsed"] >= med, "score"]
        if len(early) == 0 or len(late) == 0:
            raw[aid] = np.nan
        else:
            raw[aid] = float(late.mean() - early.mean())

    return pd.Series(raw, dtype=float)


def main() -> None:
    cfg = _load_config()
    k = float(cfg["bayesian_k"])
    ref_n = float(cfg["confidence_reference_n"])
    w = cfg["weights"]
    wL, wP, wM = float(w["level"]), float(w["polarization"]), float(w["momentum"])

    if not BASE_CSV.is_file():
        raise FileNotFoundError(f"Missing {BASE_CSV}. Run build_app_base_metrics.py first.")
    if not CLEAN_EN_CSV.is_file():
        raise FileNotFoundError(f"Missing {CLEAN_EN_CSV}.")

    base = pd.read_csv(BASE_CSV, encoding="utf-8-sig")
    scored = pd.read_csv(CLEAN_EN_CSV, encoding="utf-8-sig")

    # Global mean for Bayesian shrinkage (weighted by n).
    total_n = base["n_reviews"].sum()
    global_mean = float((base["mean_score"] * base["n_reviews"]).sum() / total_n) if total_n else 3.0

    n = base["n_reviews"].astype(float)
    app_avg = base["mean_score"].astype(float)
    bayesian_avg = (n * app_avg + k * global_mean) / (n + k)
    level = bayesian_avg / 5.0

    low_star_share = base["share_low_1_2"].astype(float)
    polarization = 1.0 - low_star_share

    confidence = np.minimum(1.0, n / ref_n)

    mom_series = _momentum_raw_per_app(scored, cfg)
    mom_raw = base["app_id"].map(mom_series)
    momentum_01 = _min_max_01(mom_raw)
    momentum_01 = momentum_01.fillna(0.5)

    combo_pre = wL * level + wP * polarization + wM * momentum_01
    health = combo_pre * confidence

    out = pd.DataFrame(
        {
            "app_id": base["app_id"],
            "app_name": base["app_name"],
            "n_reviews": base["n_reviews"].astype(int),
            "global_mean_for_bayesian": global_mean,
            "bayesian_k": k,
            "bayesian_adjusted_avg": bayesian_avg,
            "component_level": level,
            "component_polarization": polarization,
            "component_momentum_raw": mom_raw,
            "component_momentum_01": momentum_01,
            "component_confidence": confidence,
            "health_score_pre_confidence": combo_pre,
            "health_score": health,
        }
    )
    out = out.sort_values("health_score", ascending=False, kind="stable").reset_index(drop=True)
    out.insert(2, "health_score_rank", range(1, len(out) + 1))

    OUT_CSV.parent.mkdir(parents=True, exist_ok=True)
    out.to_csv(OUT_CSV, index=False, encoding="utf-8-sig")
    print(f"Saved: {OUT_CSV}")
    print(f"global_mean (weighted): {global_mean:.6f}")


if __name__ == "__main__":
    main()
