#!/usr/bin/env python3
"""
Build Day 5 priority/recommendation tables for BQ5.

Inputs:
  reports/tables/theme_summary_overall.csv
  reports/tables/theme_summary_by_app.csv

Outputs:
  reports/tables/theme_priority_score.csv
  reports/tables/theme_priority_by_app.csv
  reports/tables/recommendation_matrix.csv
"""

from __future__ import annotations

from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
TABLES = ROOT / "reports" / "tables"
OVERALL_CSV = TABLES / "theme_summary_overall.csv"
BY_APP_CSV = TABLES / "theme_summary_by_app.csv"


def _minmax(series: pd.Series) -> pd.Series:
    s = pd.to_numeric(series, errors="coerce").fillna(0.0)
    lo = float(s.min())
    hi = float(s.max())
    if hi <= lo:
        return pd.Series(0.0, index=s.index)
    return (s - lo) / (hi - lo)


def _owner_from_category(category: str) -> str:
    mapping = {
        "Stability": "Engineering",
        "Performance": "Engineering",
        "Monetization": "Product + Economy",
        "Game Design": "Game Design",
        "Operations": "LiveOps",
        "Account": "Platform/Backend",
        "UX": "UX",
        "Positive": "Core Product",
    }
    return mapping.get(str(category), "Product")


def _action_from_theme(row: pd.Series) -> str:
    tid = str(row["theme_id"])
    polarity = str(row.get("polarity", ""))
    if polarity == "positive":
        return "Preserve and amplify this positive driver."

    action_map = {
        "crash_bug": "Prioritize crash triage and top-stack fixes in next release.",
        "loading_performance": "Optimize cold-start/loading path and reduce lag spikes.",
        "pay_to_win": "Rebalance economy pressure (moves, boosters, paywall pacing).",
        "purchase_issue": "Fix purchase failure/refund edge-cases and monitor payment errors.",
        "ads_volume": "Reduce ad frequency, especially in early progression and fail loops.",
        "ads_quality": "Block low-quality ad creatives and tighten ad network filters.",
        "difficulty_progression": "Tune progression curve and reduce hard-level clustering.",
        "algorithm_fairness": "Audit RNG fairness perception and expose clearer game feedback.",
        "update_issue": "Add pre-release regression checklist and staged rollout guardrails.",
        "account_login": "Stabilize login/sync flows and progress restoration paths.",
        "liveops_events": "Improve event QA and tournament stability before campaign launch.",
        "ui_navigation": "Simplify menu/findability and improve tutorial guidance.",
        "rewards_energy": "Adjust rewards/energy pacing to reduce frustration loops.",
    }
    return action_map.get(tid, "Define targeted fix plan with PM + engineering.")


def _bucket_from_score(score: float, q1: float, q2: float, q3: float, is_critical: int) -> str:
    if is_critical == 1 and score > 0:
        return "P0"
    if score >= q3:
        return "P0"
    if score >= q2:
        return "P1"
    if score >= q1:
        return "P2"
    return "P3"


def build_theme_priority() -> pd.DataFrame:
    df = pd.read_csv(OVERALL_CSV, encoding="utf-8-sig")
    df["theme_share"] = pd.to_numeric(df["theme_share"], errors="coerce").fillna(0.0)
    df["rating_gap"] = pd.to_numeric(df["rating_gap"], errors="coerce").fillna(0.0)
    df["share_low_1_2"] = pd.to_numeric(df["share_low_1_2"], errors="coerce").fillna(0.0)
    df["n_reviews"] = pd.to_numeric(df["n_reviews"], errors="coerce").fillna(0).astype(int)

    critical_ids = {"crash_bug", "account_login", "purchase_issue"}
    df["is_critical"] = df["theme_id"].apply(lambda x: 1 if x in critical_ids else 0)

    # Keep positives visible in table, but their impact for fix-priority is zero.
    df["impact_effective"] = df.apply(
        lambda r: max(float(r["rating_gap"]), 0.0) if str(r.get("polarity", "")) == "negative" else 0.0,
        axis=1,
    )
    df["severity_effective"] = df.apply(
        lambda r: float(r["share_low_1_2"]) if str(r.get("polarity", "")) == "negative" else 0.0,
        axis=1,
    )
    df["frequency_effective"] = df.apply(
        lambda r: float(r["theme_share"]) if str(r.get("polarity", "")) == "negative" else 0.0,
        axis=1,
    )

    df["frequency_norm"] = _minmax(df["frequency_effective"])
    df["impact_norm"] = _minmax(df["impact_effective"])
    df["severity_norm"] = _minmax(df["severity_effective"])

    base = df["frequency_norm"] * df["impact_norm"] * df["severity_norm"]
    df["priority_score"] = base * (1.5 ** df["is_critical"])

    negatives = df[df["polarity"] == "negative"].copy()
    q1 = float(negatives["priority_score"].quantile(0.25))
    q2 = float(negatives["priority_score"].quantile(0.50))
    q3 = float(negatives["priority_score"].quantile(0.75))
    df["priority_bucket"] = df.apply(
        lambda r: (
            "P3"
            if str(r.get("polarity", "")) == "positive"
            else _bucket_from_score(float(r["priority_score"]), q1, q2, q3, int(r["is_critical"]))
        ),
        axis=1,
    )

    df["recommended_owner"] = df["category"].apply(_owner_from_category)
    df["recommended_action"] = df.apply(_action_from_theme, axis=1)
    df["priority_rank"] = (
        df[df["polarity"] == "negative"]["priority_score"].rank(method="min", ascending=False).reindex(df.index)
    )
    df["priority_rank"] = df["priority_rank"].fillna(0).astype(int)

    cols = [
        "theme_id",
        "theme_label",
        "category",
        "polarity",
        "n_reviews",
        "theme_share",
        "rating_gap",
        "share_low_1_2",
        "is_critical",
        "frequency_norm",
        "impact_norm",
        "severity_norm",
        "priority_score",
        "priority_rank",
        "priority_bucket",
        "recommended_owner",
        "recommended_action",
    ]
    out = df[cols].sort_values(
        by=["polarity", "priority_score", "n_reviews"], ascending=[True, False, False], kind="stable"
    )
    return out


def build_app_priority() -> pd.DataFrame:
    df = pd.read_csv(BY_APP_CSV, encoding="utf-8-sig")
    df["theme_share_in_app"] = pd.to_numeric(df["theme_share_in_app"], errors="coerce").fillna(0.0)
    df["rating_gap"] = pd.to_numeric(df["rating_gap"], errors="coerce").fillna(0.0)
    df["share_low_1_2"] = pd.to_numeric(df["share_low_1_2"], errors="coerce").fillna(0.0)
    df["n_reviews"] = pd.to_numeric(df["n_reviews"], errors="coerce").fillna(0).astype(int)

    critical_ids = {"crash_bug", "account_login", "purchase_issue"}
    df = df[df["polarity"] == "negative"].copy()
    df["is_critical"] = df["theme_id"].apply(lambda x: 1 if x in critical_ids else 0)

    freq = df["theme_share_in_app"]
    impact = df["rating_gap"].clip(lower=0.0)
    sev = df["share_low_1_2"]
    df["app_priority_score"] = freq * impact * sev * (1.5 ** df["is_critical"])

    q1 = float(df["app_priority_score"].quantile(0.25))
    q2 = float(df["app_priority_score"].quantile(0.50))
    q3 = float(df["app_priority_score"].quantile(0.75))
    df["priority_bucket"] = df.apply(
        lambda r: _bucket_from_score(float(r["app_priority_score"]), q1, q2, q3, int(r["is_critical"])),
        axis=1,
    )
    df["recommended_owner"] = df["category"].apply(_owner_from_category)
    df["recommended_action"] = df.apply(_action_from_theme, axis=1)
    df["within_app_rank"] = df.groupby("app_id")["app_priority_score"].rank(method="min", ascending=False).astype(int)

    cols = [
        "app_id",
        "app_name",
        "theme_id",
        "theme_label",
        "category",
        "n_reviews",
        "theme_share_in_app",
        "rating_gap",
        "share_low_1_2",
        "is_critical",
        "app_priority_score",
        "within_app_rank",
        "priority_bucket",
        "recommended_owner",
        "recommended_action",
    ]
    return df[cols].sort_values(by=["app_name", "within_app_rank"], kind="stable")


def build_recommendation_matrix(theme_priority: pd.DataFrame, app_priority: pd.DataFrame) -> pd.DataFrame:
    top_theme = (
        theme_priority[theme_priority["polarity"] == "negative"]
        .sort_values(by=["priority_bucket", "priority_score"], ascending=[True, False], kind="stable")
        .copy()
    )
    top_theme = top_theme[top_theme["priority_bucket"].isin(["P0", "P1"])].copy()

    app_p0p1 = app_priority[app_priority["priority_bucket"].isin(["P0", "P1"])].copy()
    app_agg = (
        app_p0p1.groupby(["theme_id", "theme_label"], as_index=False)
        .agg(
            affected_apps=("app_name", "nunique"),
            top_apps=("app_name", lambda s: ", ".join(sorted(set(s))[:4])),
        )
        .copy()
    )

    out = top_theme.merge(app_agg, on=["theme_id", "theme_label"], how="left")
    out["affected_apps"] = out["affected_apps"].fillna(0).astype(int)
    out["top_apps"] = out["top_apps"].fillna("")
    out["next_30d_goal"] = out.apply(
        lambda r: (
            "Reduce low-star share in this theme by 10-15% through targeted fixes and release QA."
            if r["priority_bucket"] == "P0"
            else "Run scoped optimization experiment and monitor rating gap trend."
        ),
        axis=1,
    )

    cols = [
        "priority_bucket",
        "priority_rank",
        "theme_id",
        "theme_label",
        "category",
        "is_critical",
        "n_reviews",
        "theme_share",
        "rating_gap",
        "share_low_1_2",
        "priority_score",
        "affected_apps",
        "top_apps",
        "recommended_owner",
        "recommended_action",
        "next_30d_goal",
    ]
    return out[cols].sort_values(by=["priority_bucket", "priority_score"], ascending=[True, False], kind="stable")


def main() -> None:
    if not OVERALL_CSV.is_file():
        raise FileNotFoundError(f"Missing {OVERALL_CSV}. Run build_theme_summary_tables.py first.")
    if not BY_APP_CSV.is_file():
        raise FileNotFoundError(f"Missing {BY_APP_CSV}. Run build_theme_summary_tables.py first.")

    theme_priority = build_theme_priority()
    app_priority = build_app_priority()
    recommendation = build_recommendation_matrix(theme_priority, app_priority)

    TABLES.mkdir(parents=True, exist_ok=True)
    out_theme = TABLES / "theme_priority_score.csv"
    out_app = TABLES / "theme_priority_by_app.csv"
    out_rec = TABLES / "recommendation_matrix.csv"

    theme_priority.to_csv(out_theme, index=False, encoding="utf-8-sig")
    app_priority.to_csv(out_app, index=False, encoding="utf-8-sig")
    recommendation.to_csv(out_rec, index=False, encoding="utf-8-sig")

    neg = theme_priority[theme_priority["polarity"] == "negative"]
    p_counts = neg["priority_bucket"].value_counts().to_dict()
    print(f"Saved: {out_theme} ({len(theme_priority)} rows; negative={len(neg)})")
    print(f"Saved: {out_app} ({len(app_priority)} rows)")
    print(f"Saved: {out_rec} ({len(recommendation)} rows)")
    print(f"Negative theme priority distribution: {p_counts}")


if __name__ == "__main__":
    main()
