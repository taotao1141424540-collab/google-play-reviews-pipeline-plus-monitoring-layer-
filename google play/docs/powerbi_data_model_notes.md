# Power BI Data Model Notes (Day 5)

## Core tables
- `reports/tables/app_health_score.csv` (app grain)
- `reports/tables/app_benchmark_bq2.csv` (app grain)
- `reports/tables/theme_summary_overall.csv` (theme grain)
- `reports/tables/theme_summary_by_app.csv` (app x theme grain)
- `reports/tables/theme_priority_score.csv` (theme grain)
- `reports/tables/theme_priority_by_app.csv` (app x theme grain)
- `reports/tables/recommendation_matrix.csv` (theme recommendation grain)

## Suggested relationships
1. App dimension (`app_id`) -> app-grain tables (1:*).
2. Theme dimension (`theme_id`) -> theme-grain tables (1:*).
3. App x Theme tables are bridge/fact tables for heatmap and priority drill-down.

## Page mapping
- Page 3: `theme_summary_overall.csv` + `theme_summary_by_app.csv`
- Page 4: `theme_priority_score.csv` + `theme_priority_by_app.csv` + `recommendation_matrix.csv`

## Notes
- Keep `theme_label` from one canonical theme dimension to avoid duplicated text columns in visuals.
- Prefer `priority_bucket` as a slicer for recommendation views.
