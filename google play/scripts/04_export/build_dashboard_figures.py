#!/usr/bin/env python3
"""
Day 6: render dashboard-quality PNG figures from Day 1-5 tables.

These PNGs serve double duty:
  1. Embedded in `User_Satisfaction_Insight_Report.pdf` so the narrative
     report ships with visuals out of the box.
  2. Reference mockups for the Power BI build (Pages 1-4).

Inputs:
  reports/tables/app_health_score.csv
  reports/tables/volume_vs_rating_scatter.csv
  reports/tables/publisher_benchmark.csv
  reports/tables/low_star_theme_summary.csv
  reports/tables/theme_summary_overall.csv
  reports/tables/theme_summary_by_app.csv
  reports/tables/theme_priority_score.csv

Outputs (PNG, 1600x900-ish, 200 dpi):
  reports/每日复盘/figures/01_top_bottom_health.png
  reports/每日复盘/figures/02_volume_vs_rating_scatter.png
  reports/每日复盘/figures/03_publisher_weighted_health.png
  reports/每日复盘/figures/04_low_star_theme_top10.png
  reports/每日复盘/figures/05_rating_gap_top10.png
  reports/每日复盘/figures/06_app_theme_heatmap.png
  reports/每日复盘/figures/07_impact_frequency_matrix.png
  reports/每日复盘/figures/08_priority_score_ranking.png
"""

from __future__ import annotations

import os
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
TABLES = ROOT / "reports" / "tables"
OUT_DIR = ROOT / "reports" / "每日复盘" / "figures"

os.environ.setdefault("MPLCONFIGDIR", str(ROOT / ".mplconfig"))
Path(os.environ["MPLCONFIGDIR"]).mkdir(parents=True, exist_ok=True)

plt.rcParams.update({
    "figure.dpi": 110,
    "savefig.dpi": 200,
    "axes.titlesize": 13,
    "axes.labelsize": 10,
    "axes.spines.top": False,
    "axes.spines.right": False,
    "font.size": 10,
})

NEG_COLOR = "#c0392b"
POS_COLOR = "#27ae60"
NEUTRAL = "#3a6fb0"
CRITICAL = "#8e44ad"


def _save(fig: plt.Figure, name: str) -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    fp = OUT_DIR / name
    fig.tight_layout()
    fig.savefig(fp, bbox_inches="tight")
    plt.close(fig)
    print(f"Saved: {fp}")


def fig01_top_bottom_health() -> None:
    df = pd.read_csv(TABLES / "app_health_score.csv", encoding="utf-8-sig").sort_values(
        "health_score", ascending=False
    )
    top5 = df.head(5)
    bot5 = df.tail(5).iloc[::-1]
    fig, axes = plt.subplots(1, 2, figsize=(11, 4.3))

    for ax, sub, title, color in (
        (axes[0], top5, "Top 5 by Health Score", POS_COLOR),
        (axes[1], bot5, "Bottom 5 by Health Score", NEG_COLOR),
    ):
        y = np.arange(len(sub))
        ax.barh(y, sub["health_score"].values, color=color, alpha=0.85)
        ax.set_yticks(y, labels=sub["app_name"].values)
        ax.invert_yaxis()
        ax.set_xlim(0, 1)
        ax.set_xlabel("Health Score (0-1)")
        ax.set_title(title)
        for yi, v in zip(y, sub["health_score"].values):
            ax.text(v + 0.012, yi, f"{v:.3f}", va="center", fontsize=9)

    fig.suptitle("App Satisfaction Health Score — winners vs at-risk", fontsize=12, y=1.02)
    _save(fig, "01_top_bottom_health.png")


def fig02_volume_vs_rating() -> None:
    df = pd.read_csv(TABLES / "volume_vs_rating_scatter.csv", encoding="utf-8-sig")
    fig, ax = plt.subplots(figsize=(9.8, 5.6))
    ax.scatter(df["n_reviews"], df["mean_score"], s=110, c=df["health_score"],
               cmap="RdYlGn", edgecolors="black", linewidths=0.6)
    for _, r in df.iterrows():
        ax.annotate(r["app_name"], (r["n_reviews"], r["mean_score"]),
                    xytext=(6, 4), textcoords="offset points", fontsize=8.5)
    ax.set_xlabel("Number of English reviews (sample size)")
    ax.set_ylabel("Mean star rating (1-5)")
    ax.set_title("Volume vs Rating — every app, colored by Health Score")
    ax.grid(True, alpha=0.3)
    sm = plt.cm.ScalarMappable(cmap="RdYlGn", norm=plt.Normalize(vmin=df["health_score"].min(),
                                                                 vmax=df["health_score"].max()))
    sm.set_array([])
    cb = fig.colorbar(sm, ax=ax, fraction=0.04, pad=0.02)
    cb.set_label("Health Score", fontsize=9)
    _save(fig, "02_volume_vs_rating_scatter.png")


def fig03_publisher_weighted_health() -> None:
    df = pd.read_csv(TABLES / "publisher_benchmark.csv", encoding="utf-8-sig").sort_values(
        "weighted_health_score", ascending=True
    )
    fig, ax = plt.subplots(figsize=(9.5, 4.6))
    colors = [POS_COLOR if v >= 0.75 else NEUTRAL if v >= 0.6 else NEG_COLOR for v in df["weighted_health_score"]]
    y = np.arange(len(df))
    ax.barh(y, df["weighted_health_score"], color=colors, alpha=0.9)
    ax.set_yticks(y, labels=df["publisher"].values)
    ax.set_xlim(0, 1)
    ax.set_xlabel("Weighted Health Score (review-volume weighted)")
    ax.set_title("Publisher Benchmark — weighted Health Score")
    for yi, (v, n) in zip(y, zip(df["weighted_health_score"], df["n_apps"])):
        ax.text(v + 0.012, yi, f"{v:.3f}  ({int(n)} app)", va="center", fontsize=8.5)
    _save(fig, "03_publisher_weighted_health.png")


def fig04_low_star_theme_top10() -> None:
    df = pd.read_csv(TABLES / "low_star_theme_summary.csv", encoding="utf-8-sig").head(10).iloc[::-1]
    fig, ax = plt.subplots(figsize=(9.5, 5.2))
    colors = [POS_COLOR if p == "positive" else NEG_COLOR for p in df["polarity"]]
    y = np.arange(len(df))
    ax.barh(y, df["low_star_theme_share"] * 100, color=colors, alpha=0.88)
    ax.set_yticks(y, labels=df["theme_label"].values)
    ax.set_xlabel("Share of low-star (1-2★) reviews mentioning this theme (%)")
    ax.set_title("Low-Star Pain Points — what 1-2★ reviewers talk about")
    for yi, v in zip(y, df["low_star_theme_share"] * 100):
        ax.text(v + 0.15, yi, f"{v:.1f}%", va="center", fontsize=8.5)
    handles = [plt.Rectangle((0, 0), 1, 1, color=POS_COLOR, alpha=0.88),
               plt.Rectangle((0, 0), 1, 1, color=NEG_COLOR, alpha=0.88)]
    ax.legend(handles, ["positive theme (likely sarcasm in 1-2★)", "negative theme"], loc="lower right", fontsize=8)
    _save(fig, "04_low_star_theme_top10.png")


def fig05_rating_gap_top10() -> None:
    df = pd.read_csv(TABLES / "theme_summary_overall.csv", encoding="utf-8-sig")
    neg = df[df["polarity"] == "negative"].sort_values("rating_gap", ascending=False).head(10).iloc[::-1]
    fig, ax = plt.subplots(figsize=(9.5, 5.4))
    y = np.arange(len(neg))
    ax.barh(y, neg["rating_gap"], color=NEG_COLOR, alpha=0.85)
    ax.set_yticks(y, labels=neg["theme_label"].values)
    ax.set_xlabel("Rating Gap = global mean − theme mean (★)")
    ax.set_title("Rating Gap — themes that pull average score down the most")
    for yi, (v, n) in zip(y, zip(neg["rating_gap"], neg["n_reviews"])):
        ax.text(v + 0.04, yi, f"{v:+.2f}★  (n={int(n)})", va="center", fontsize=8.5)
    ax.axvline(1.0, color="grey", linestyle=":", linewidth=0.9)
    _save(fig, "05_rating_gap_top10.png")


def fig06_app_theme_heatmap() -> None:
    df = pd.read_csv(TABLES / "theme_summary_by_app.csv", encoding="utf-8-sig")
    df = df[df["polarity"] == "negative"].copy()
    pivot = df.pivot_table(index="app_name", columns="theme_label",
                            values="share_low_1_2", aggfunc="max", fill_value=0)
    pivot = pivot.loc[:, sorted(pivot.columns, key=lambda c: pivot[c].mean(), reverse=True)]
    pivot = pivot.loc[sorted(pivot.index, key=lambda r: pivot.loc[r].mean(), reverse=True)]

    fig, ax = plt.subplots(figsize=(11.5, 6.5))
    im = ax.imshow(pivot.values, cmap="Reds", vmin=0, vmax=1, aspect="auto")
    ax.set_xticks(np.arange(len(pivot.columns)), labels=pivot.columns, rotation=35, ha="right", fontsize=8.5)
    ax.set_yticks(np.arange(len(pivot.index)), labels=pivot.index, fontsize=9)
    for i in range(pivot.shape[0]):
        for j in range(pivot.shape[1]):
            v = pivot.values[i, j]
            if v >= 0.5:
                ax.text(j, i, f"{int(v*100)}", ha="center", va="center",
                        fontsize=7.5, color="white" if v >= 0.7 else "black")
    cb = fig.colorbar(im, ax=ax, fraction=0.025, pad=0.02)
    cb.set_label("share_low_1_2 (1-2★ proportion within that App × theme)", fontsize=8.5)
    ax.set_title("App × Negative Theme Heatmap — concentration of low-star pain")
    _save(fig, "06_app_theme_heatmap.png")


def fig07_impact_frequency_matrix() -> None:
    df = pd.read_csv(TABLES / "theme_priority_score.csv", encoding="utf-8-sig")
    neg = df[df["polarity"] == "negative"].copy()
    fig, ax = plt.subplots(figsize=(9.5, 6))
    bucket_color = {"P0": NEG_COLOR, "P1": "#e67e22", "P2": "#3a6fb0", "P3": "#95a5a6"}
    for bucket, sub in neg.groupby("priority_bucket"):
        ax.scatter(sub["theme_share"] * 100, sub["rating_gap"],
                   s=200 + sub["share_low_1_2"] * 700,
                   color=bucket_color.get(bucket, NEUTRAL), alpha=0.78,
                   edgecolors="black", linewidths=0.7, label=bucket)
    for _, r in neg.iterrows():
        ax.annotate(r["theme_label"], (r["theme_share"] * 100, r["rating_gap"]),
                    xytext=(6, 5), textcoords="offset points", fontsize=8.5)
    ax.set_xlabel("Frequency = theme_share (%) — how often the theme appears")
    ax.set_ylabel("Impact = rating_gap (★) — how much it pulls score down")
    ax.set_title("Impact × Frequency Matrix — bubble size = Severity (share_low_1_2)")
    ax.axhline(1.0, color="grey", linestyle=":", linewidth=0.9)
    ax.legend(title="Priority Bucket", fontsize=9, loc="lower right")
    ax.grid(True, alpha=0.3)
    _save(fig, "07_impact_frequency_matrix.png")


def fig08_priority_score_ranking() -> None:
    df = pd.read_csv(TABLES / "theme_priority_score.csv", encoding="utf-8-sig")
    neg = df[df["polarity"] == "negative"].sort_values("priority_score", ascending=True)
    fig, ax = plt.subplots(figsize=(9.5, 5.6))
    bucket_color = {"P0": NEG_COLOR, "P1": "#e67e22", "P2": "#3a6fb0", "P3": "#95a5a6"}
    colors = [bucket_color.get(b, NEUTRAL) for b in neg["priority_bucket"]]
    y = np.arange(len(neg))
    ax.barh(y, neg["priority_score"], color=colors, alpha=0.9)
    labels = [f"{lbl}{' *' if int(c)==1 else ''}" for lbl, c in zip(neg["theme_label"], neg["is_critical"])]
    ax.set_yticks(y, labels=labels)
    ax.set_xlabel("Priority Score (normalized freq × impact × severity, critical × 1.5)")
    ax.set_title("Priority Score Ranking — what to fix first  ( * = critical theme )")
    for yi, (v, b) in zip(y, zip(neg["priority_score"], neg["priority_bucket"])):
        ax.text(v + 0.004, yi, f"{v:.3f}  [{b}]", va="center", fontsize=8.5)
    handles = [plt.Rectangle((0, 0), 1, 1, color=c, alpha=0.9) for c in bucket_color.values()]
    ax.legend(handles, list(bucket_color.keys()), title="Bucket", loc="lower right", fontsize=8.5)
    _save(fig, "08_priority_score_ranking.png")


def main() -> None:
    fig01_top_bottom_health()
    fig02_volume_vs_rating()
    fig03_publisher_weighted_health()
    fig04_low_star_theme_top10()
    fig05_rating_gap_top10()
    fig06_app_theme_heatmap()
    fig07_impact_frequency_matrix()
    fig08_priority_score_ranking()


if __name__ == "__main__":
    main()
