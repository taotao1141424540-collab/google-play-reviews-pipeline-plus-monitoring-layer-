# Power BI Dashboard Build Guide (4 Pages)

> Step-by-step instructions to rebuild the 4-page satisfaction dashboard from
> the Day 1-5 source tables. Designed for ~90 minutes in Power BI Desktop.

---

## 0. Load these CSVs into Power BI

Open Power BI Desktop → **Home → Get Data → Text/CSV** → import each of the
files below (UTF-8). Make sure to set the data types on numeric columns.

| File | Grain | Used on |
|---|---|---|
| `reports/tables/app_health_score.csv` | App | Page 1, Page 2 |
| `reports/tables/app_base_metrics.csv` | App | Page 1 |
| `reports/tables/app_benchmark_bq2.csv` | App | Page 2 |
| `reports/tables/publisher_benchmark.csv` | Publisher | Page 2 |
| `reports/tables/volume_vs_rating_scatter.csv` | App | Page 2 |
| `reports/tables/theme_summary_overall.csv` | Theme | Page 3 |
| `reports/tables/theme_summary_by_app.csv` | App × Theme | Page 3 |
| `reports/tables/low_star_theme_summary.csv` | Theme | Page 3 |
| `reports/tables/theme_priority_score.csv` | Theme | Page 4 |
| `reports/tables/theme_priority_by_app.csv` | App × Theme | Page 4 |
| `reports/tables/recommendation_matrix.csv` | Theme (P0/P1) | Page 4 |

---

## 1. Build the data model (Modeling view)

Create two small **dimension tables** so visuals share consistent slicers:

### 1.1 dim_App
- New Table (DAX):
  ```DAX
  dim_App =
  DISTINCT(
      SELECTCOLUMNS(
          app_health_score,
          "app_id",      app_health_score[app_id],
          "app_name",    app_health_score[app_name]
      )
  )
  ```
- Mark as dimension.

### 1.2 dim_Theme
- New Table (DAX):
  ```DAX
  dim_Theme =
  DISTINCT(
      SELECTCOLUMNS(
          theme_summary_overall,
          "theme_id",     theme_summary_overall[theme_id],
          "theme_label",  theme_summary_overall[theme_label],
          "category",     theme_summary_overall[category],
          "polarity",     theme_summary_overall[polarity]
      )
  )
  ```

### 1.3 Relationships (single-direction, 1:*)
- `dim_App[app_id]` → `app_health_score[app_id]`
- `dim_App[app_id]` → `app_base_metrics[app_id]`
- `dim_App[app_id]` → `app_benchmark_bq2[app_id]`
- `dim_App[app_id]` → `volume_vs_rating_scatter[app_id]`
- `dim_App[app_id]` → `theme_summary_by_app[app_id]`
- `dim_App[app_id]` → `theme_priority_by_app[app_id]`
- `dim_Theme[theme_id]` → `theme_summary_overall[theme_id]`
- `dim_Theme[theme_id]` → `theme_summary_by_app[theme_id]`
- `dim_Theme[theme_id]` → `low_star_theme_summary[theme_id]`
- `dim_Theme[theme_id]` → `theme_priority_score[theme_id]`
- `dim_Theme[theme_id]` → `theme_priority_by_app[theme_id]`
- `dim_Theme[theme_id]` → `recommendation_matrix[theme_id]`

> Tip: Power BI auto-detects most of these. Verify in **Model view**.

---

## 2. Recommended DAX measures (Modeling → New Measure)

```DAX
Total Reviews = SUM(app_health_score[n_reviews])

Avg Adjusted Rating =
DIVIDE(
    SUMX(app_health_score, app_health_score[bayesian_adjusted_avg] * app_health_score[n_reviews]),
    SUM(app_health_score[n_reviews])
)

Avg Health Score = AVERAGE(app_health_score[health_score])

Low-Star Share (weighted) =
DIVIDE(
    SUMX(app_benchmark_bq2, app_benchmark_bq2[share_low_1_2] * app_benchmark_bq2[n_reviews]),
    SUM(app_benchmark_bq2[n_reviews])
)

Positive Share (weighted) =
DIVIDE(
    SUMX(app_benchmark_bq2, app_benchmark_bq2[share_high_4_5] * app_benchmark_bq2[n_reviews]),
    SUM(app_benchmark_bq2[n_reviews])
)

Critical Theme Share =
DIVIDE(
    CALCULATE(SUM(theme_summary_overall[n_reviews]),
              theme_summary_overall[theme_id] IN {"crash_bug","account_login","purchase_issue"}),
    SUM(theme_summary_overall[n_reviews])
)

P0 Theme Count =
CALCULATE(
    DISTINCTCOUNT(theme_priority_score[theme_id]),
    theme_priority_score[priority_bucket] = "P0"
)
```

---

## 3. Page 1 — Executive Overview (8 visuals)

Layout suggestion: **3 KPI cards top row · 2 KPI cards row 2 · 1 ranking · 1 ranking** (1280×720).

| # | Visual | Field bindings |
|---|---|---|
| 1 | **Card** — Total Reviews | `[Total Reviews]` measure |
| 2 | **Card** — Apps in pool | `DISTINCTCOUNT(dim_App[app_id])` |
| 3 | **Card** — Avg Adjusted Rating | `[Avg Adjusted Rating]` measure (format 2 decimals) |
| 4 | **Card** — Low-Star Share | `[Low-Star Share (weighted)]` (format %) |
| 5 | **Card** — Avg Health Score | `[Avg Health Score]` (format 3 decimals, 0-1 range) |
| 6 | **Horizontal bar** — Top 5 by Health Score | Axis: `dim_App[app_name]`; Values: `health_score`; Filter top N=5 desc; sort desc |
| 7 | **Horizontal bar** — Bottom 5 by Low-Star Share | Axis: `dim_App[app_name]`; Values: `app_benchmark_bq2[share_low_1_2]`; Filter top N=5 by value desc |
| 8 | **Card** — Critical Theme Share | `[Critical Theme Share]` measure |

> Reference look: `reports/每日复盘/figures/01_top_bottom_health.png`

---

## 4. Page 2 — Competitor Benchmarking (5 visuals + 2 slicers)

| # | Visual | Field bindings |
|---|---|---|
| 1 | **Slicer** — Publisher | `publisher_benchmark[publisher]` |
| 2 | **Slicer** — App | `dim_App[app_name]` |
| 3 | **Horizontal bar** — App Health Score Ranking (all 14 apps) | Axis: `dim_App[app_name]`; Values: `app_health_score[health_score]`; Sort desc |
| 4 | **Horizontal bar** — Low-Star Share Ranking | Axis: `dim_App[app_name]`; Values: `app_benchmark_bq2[share_low_1_2]`; Sort desc |
| 5 | **Horizontal bar** — Publisher Weighted Health | Axis: `publisher_benchmark[publisher]`; Values: `weighted_health_score`; Sort desc |
| 6 | **Scatter** — Volume vs Rating | X: `volume_vs_rating_scatter[n_reviews]`; Y: `volume_vs_rating_scatter[mean_score]`; Legend: `publisher`; Tooltip: `app_name`, `health_score` |
| 7 | **Table** — App benchmark table | `app_name`, `n_reviews`, `mean_score`, `share_low_1_2`, `share_high_4_5`, `health_score`, `health_score_rank` |

> Reference look: `figures/02_volume_vs_rating_scatter.png`, `03_publisher_weighted_health.png`

---

## 5. Page 3 — Pain Point & Positive Driver (6 visuals + 1 slicer)

| # | Visual | Field bindings |
|---|---|---|
| 1 | **Slicer** — Polarity | `dim_Theme[polarity]` |
| 2 | **Horizontal bar** — Low-Star Theme Top 10 | Axis: `dim_Theme[theme_label]`; Values: `low_star_theme_summary[low_star_theme_share]`; Sort desc; top N=10 |
| 3 | **Horizontal bar** — Positive Theme Top 5 | Axis: `dim_Theme[theme_label]`; Values: `theme_summary_overall[n_reviews]`; Filter `polarity = positive`; Sort desc; top N=5 |
| 4 | **Horizontal bar** — Rating Gap Top 10 (negative only) | Axis: `dim_Theme[theme_label]`; Values: `theme_summary_overall[rating_gap]`; Filter `polarity = negative`; Sort desc; top N=10 |
| 5 | **Matrix** — Theme Avg Rating | Rows: `dim_Theme[theme_label]`; Values: `theme_summary_overall[mean_score]`, `share_low_1_2`, `rating_gap`. Conditional formatting on `mean_score` (red→green). |
| 6 | **Matrix / Heatmap** — App × Theme | Rows: `dim_App[app_name]`; Columns: `dim_Theme[theme_label]`; Values: `theme_summary_by_app[share_low_1_2]`. Conditional formatting (Reds) |
| 7 | **Card** — Critical Complaint Share | `[Critical Theme Share]` measure |

> Reference look: `figures/04_low_star_theme_top10.png`, `05_rating_gap_top10.png`, `06_app_theme_heatmap.png`

---

## 6. Page 4 — Product Recommendation (5 visuals + 1 slicer)

| # | Visual | Field bindings |
|---|---|---|
| 1 | **Slicer** — Priority Bucket | `theme_priority_score[priority_bucket]` |
| 2 | **Scatter** — Impact × Frequency Matrix | X: `theme_priority_score[theme_share]`; Y: `theme_priority_score[rating_gap]`; Size: `share_low_1_2`; Legend: `priority_bucket`; Filter: `polarity = negative` |
| 3 | **Horizontal bar** — Priority Score Ranking | Axis: `dim_Theme[theme_label]`; Values: `theme_priority_score[priority_score]`; Filter: `polarity = negative`; Sort desc |
| 4 | **Card** — P0 Theme Count | `[P0 Theme Count]` measure |
| 5 | **Table** — Recommendation Matrix (the centerpiece) | `priority_bucket`, `theme_label`, `is_critical`, `n_reviews`, `theme_share`, `rating_gap`, `share_low_1_2`, `priority_score`, `affected_apps`, `top_apps`, `recommended_owner`, `recommended_action`, `next_30d_goal`. Filter to P0+P1. |
| 6 | **Text box** — Limitations & Next Steps | Hand-typed; copy from `User_Satisfaction_Insight_Report.md` §7. |

> Reference look: `figures/07_impact_frequency_matrix.png`, `08_priority_score_ranking.png`

---

## 7. Cross-page filtering & polish

- Enable **"Sync Slicers"** for `Publisher` and `App` across all 4 pages.
- Page titles bilingual: `Executive Overview / 总览`, etc.
- Footer (every page, small text): *"Data source: Google Play public reviews (English subset, 10,940 rows). Review-based proxy signals; not a full-population estimate."*
- Theme: **File → Options → Themes → built-in "Executive"** or import `themes/dashboard_theme.json` if you have one.

---

## 8. Export

1. **File → Export → Export to PDF** → save as
   `reports/每日复盘/Mobile_Game_Satisfaction_Dashboard.pdf`.
2. Take 4 screenshots (one per page) into
   `reports/每日复盘/figures/dashboard_page{1..4}.png`.
3. Re-run `python3 scripts/04_export/build_insight_report_pdf.py` so the
   insight report picks up the new screenshots (it will fall back to the
   matplotlib PNGs if the screenshots are not present).

---

## 9. Common Power BI gotchas

- **`share_*` columns**: format as percent in Modeling view, not %-multiplied. The CSV values are already 0-1.
- **Scatter "axis" vs "details"**: in Power BI scatter the field that uniquely identifies each dot must go to the **"Values"** well as `app_name`, not just axis.
- **Top N filter**: applied on visual filters pane, type = Top N, value = numeric column being sorted.
- **Heatmap colors**: use Conditional Formatting → Background Color → Color Scale (red gradient).
