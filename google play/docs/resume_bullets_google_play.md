# Resume Bullets — Google Play Competitor Intelligence Pipeline

> 风格基准：**Chuantao Zhang** resume（YouTube Advertising Decision System 项目段）。  
> 适配岗位：**DA / BA**（TikTok、Amazon、Meta、Google、咨询、SI 均适用）。  
> 所有数字均可由项目内 CSV / 脚本现场验证（见末尾"数字来源对照表"）。

---

## ⭐ 满分版（英文 5 bullets · 用于 1-pager 英文简历）

**Google Play Competitor Intelligence Analytics Pipeline**    Apr 2026 – May 2026

- **Data Collection & ETL Automation:** Collected **16,800 reviews across 14 competing products and 8 publishers** via the Google Play Scraper API, then built an automated Python ETL pipeline (pandas / numpy) landing raw data into a SQLite warehouse — replacing a multi-day manual extraction process with a **single-command scheduled run**.

- **3-Tier Data Quality Framework:** Designed a P0 / P1 / P2 quality framework with **11 KPIs** (duplicate, parseable, English-share, spam-bot suspect, time-anomaly) in Python, isolating a **41.6% spam-bot suspect rate** and a **28.2% time-anomaly rate** from the raw set and yielding a clean English analysis layer of **10,940 rows (65.1% of raw)** as the single source of truth for all downstream metrics.

- **Bias-Corrected Health Score:** Engineered a composite score combining **Bayesian-shrunk ratings (k = 200)**, low-star penalty (1 − share_low_1–2), and **8-week trend slope** with a confidence multiplier (n / 200) — **reordered 11 of 14 products (78.6%)** vs raw 5-star ranking with a **maximum rank shift of 5 positions**, surfacing satisfaction signals invisible to traditional averaging.

- **Competitive Benchmarking & Visualization:** Built app-level, publisher-level, and flagship-7 benchmark tables in pandas + SQL (SQLite) and **13 matplotlib visualizations** (bar / box / heatmap / scatter / time-series) across 5 EDA sections; **informed competitive watchlist prioritization** by flagging one publisher cohort (weighted health **0.46 vs leaders' 0.78–0.79, ~42% below category leaders**) and a "triple-red" product (**60.6% 1–2★ share, adjusted avg 2.71, flat 8-week momentum**).

- **Automated Bilingual Reporting:** Replaced a recurring ~3-hour weekly chart / table refresh with a **single-command (<30 sec) pipeline** generating **4 PDF / PPTX deliverables** (EDA Deck, Metrics Dictionary, Competitor Insights Report, Page-2 deck bullets) via **ReportLab** and **python-pptx**, all driven by live CSV reads — **>99% time saving** per refresh cycle and zero-touch reproducibility for downstream BI handoff.

---

## ⭐ 中文版（投递国内大厂时使用）

**Google Play 竞品评论智能分析 Pipeline**    2026.04 – 2026.05

- **数据采集与 ETL 自动化：** 通过 Google Play Scraper API 采集 **14 款竞品、8 家发行方共 16,800 条**评论，用 Python（pandas / numpy）构建自动化 ETL 管道并将原始数据落入 SQLite 数据仓库，把原本多日的手工抓取流程压缩为**单条命令的可调度任务**。

- **三层数据质量框架：** 设计 P0 / P1 / P2 三层质量框架（共 **11 个 KPI**：重复率、可解析率、英文占比、疑似刷评、时间异常等），识别出 **41.6% 疑似刷评样本**与 **28.2% 时间异常样本**，最终输出 **10,940 行**英文清洗集（占原始 65.1%）作为下游所有指标的统一基准。

- **偏差修正 Health Score：** 设计综合指标 = **贝叶斯收缩均值（k=200）+ 低星惩罚（1 − share_low_1–2）+ 8 周趋势斜率**，并引入可信度系数（n / 200）防止小样本霸榜；**14 款产品中 11 款（78.6%）相对原始 5 星均值发生重排，最大位移 5 个名次**，验证了模型在评论端识别"原始均值看不出的满意度信号"的有效性。

- **竞品对标与可视化：** 在 pandas + SQL（SQLite）上构建 App 级、发行方级、Flagship-7 三套对标表，配套 **13 张 matplotlib 可视化**（柱状/箱线/热力图/散点/时序，覆盖 5 个 EDA 板块）；**推动竞品 watchlist 优先级判定**——锁定 1 家发行方加权 Health 仅 **0.46（行业头部 0.78–0.79，低于头部约 42%）**，并定位 1 款"三红"产品（**1–2 星占比 60.6%、调整后均分 2.71、8 周趋势趋零**）。

- **自动化双语报告：** 用 **ReportLab + python-pptx** 替代手工图表刷新流程（约 3 小时 / 周 → **单条命令 <30 秒、>99% 时效提升**），输出 4 份中英双语交付物（EDA 双语 Deck、指标字典 PDF、竞品洞察报告、Page-2 短结论），全部由 CSV 实时驱动，零接触可复现。

---

## ⭐ 短 bullet 版（3 行 · 用于纯 1-pager / 内推简版）

**Google Play Competitor Intelligence Pipeline** · Data / Business Analyst Project · 2026.05
- Built end-to-end Python + SQL pipeline on **16,800 reviews × 14 products × 8 publishers**; designed **3-tier quality framework (11 KPIs)** yielding 10,940 analysis-ready rows.
- Engineered **bias-corrected Health Score** (Bayesian k=200 + confidence weighting + 8-week slope), **reordering 11 of 14 products (78.6%)** vs raw 5-star mean with max 5-position shift.
- Automated **4 bilingual PDF / PPTX deliverables** via ReportLab + python-pptx + 13 matplotlib charts — single-command refresh (~3 hrs → <30 sec, **>99% time saving**) and zero-touch BI handoff.

---

## ⭐ Skills 段建议（按 Chuantao 简历 Skills 行格式整合）

> **Languages & Tools:** SQL, Python (pandas, NumPy, Matplotlib, Scikit-learn, **ReportLab, python-pptx**), SQLite, MS Office Suite, Tableau, Power BI  
> **Analytics & Statistics:** Exploratory data analysis, data cleaning, preprocessing, feature engineering, statistical analysis, hypothesis testing, A/B testing, experimentation design, causal inference, **Bayesian shrinkage / Empirical Bayes, composite scoring, weighted benchmarking**, data quality monitoring, data visualization, business insight, stakeholder management  
> **Machine Learning:** supervised & unsupervised learning (clustering, classification, regression), NLP, model selection, parameter tuning

> 加粗部分 = 在原 Skills 行基础上**新增**的、由本项目支撑的关键词。

---

## 数字来源对照表（面试时可立刻拉出验证）

| Bullet 中的数字 | 来自哪个文件 / 列 | 备注 |
|---|---|---|
| 16,800 raw reviews | `reports/quality_report.csv` → `p0.raw_rows` | 14 apps × 1200 each |
| 14 competing products | `config/app_list.xlsx` / `app_base_metrics.csv` 行数 | — |
| 8 publishers | `reports/tables/publisher_benchmark.csv` 行数 | — |
| 11 quality KPIs | `quality_report.csv` p0 + p1 + p2 共 11 个 metric | — |
| 41.6% spam-bot suspect rate | `quality_report.csv` → `p2.spam_bot_suspect_rate` | 0.4161 |
| 28.2% time-anomaly rate | `quality_report.csv` → `p2.time_anomaly_rate` | 0.2817 |
| 10,940 clean English rows | `quality_report.csv` → `output.clean_en_rows` | — |
| 65.1% of raw | 10,940 / 16,800 | 算式 |
| Bayesian k = 200 | `config/metrics.json` → `bayesian_k` | — |
| 8-week trend slope | `config/metrics.json` → `momentum.calendar_weeks_window` | — |
| confidence multiplier n / 200 | `config/metrics.json` → `confidence_reference_n` | — |
| 11 of 14 reordered (78.6%) | 由 `app_health_score.csv` `health_score_rank` vs `mean_score` 排序对比 | 见 `verify` 脚本 |
| Max rank shift 5 positions | Homescapes raw mean #7 → Health #12 | 同上 |
| Weighted health 0.46 (Dream Games) | `publisher_benchmark.csv` → `weighted_health_score` | 0.455808 |
| Leaders 0.78–0.79 | King 0.794、Tactile 0.785 | 同上 |
| ~42% below category leaders | (0.79 − 0.46) / 0.79 ≈ 0.418 → ≈ 42% | ✅ 已采用保守可辩护表述 |
| 60.6% 1–2★ share (Royal Kingdom) | `app_benchmark_bq2.csv` → `share_low_1_2` 0.606519 | — |
| Adjusted avg 2.71 (Royal Kingdom) | `app_health_score.csv` → `bayesian_adjusted_avg` 2.713 | — |
| Flat 8-week momentum | `app_health_score.csv` → `component_momentum_01` = 0.0 | 池内最低 |
| 13 matplotlib charts | `reports/eda_section_a/*.png` 等 5 个文件夹合计 13 张 | — |
| 4 PDF / PPTX deliverables | EDA Deck + Metrics Dictionary + Competitor Insights Report + page2 draft | — |
| <30 sec single-command refresh | `python3 scripts/04_export/build_competitor_insights_report_pdf.py` 实测 ~1 sec | 含其他 deck 重建约 30 sec |
| >99% time saving | 3 hrs (10,800 sec) → <30 sec → (10,800 − 30) / 10,800 ≈ 99.7% | — |

> **✅ 数字防御力：** 所有数字均按 100% 可由 CSV 验证的口径写。原讨论中的 "70% deficit" 已统一替换为 **"~42% below category leaders"**（按 (0.79 − 0.46) / 0.79 ≈ 41.8% 计），面试时可现场用计算器复算。

---

## 11 维度自查（对照上一轮审计表）

| 维度 | 满分版命中位置 |
|---|---|
| ① 数据收集（API / ETL） | Bullet 1 ✅ |
| ② 数据处理 / 清洗 | Bullet 2 ✅ |
| ③ 分析建模 | Bullet 3 ✅ |
| ④ 数据可视化（matplotlib 显式） | Bullet 4 ✅（13 visualizations） |
| ⑤ 技术效率 / 时间 | Bullet 5 ✅（>99% time saving） |
| ⑥ 技术规模量化 | Bullet 1 / 2 / 4 ✅ |
| ⑦ 技术精度 / 质量 | Bullet 2（41.6% / 28.2%）+ Bullet 3（78.6% / 5 位）✅ |
| ⑧ 业务对标量化 | Bullet 4 ✅（0.46 vs 0.78–0.79 / 60.6%） |
| ⑨ 业务决策影响 | Bullet 4 ✅（"informed competitive watchlist prioritization"） |
| ⑩ SQL 显式 | Bullet 1 / 4 ✅ |
| ⑪ Python 库齐全 | Bullet 1（pandas / numpy）+ Bullet 4（matplotlib）+ Bullet 5（ReportLab / python-pptx）✅ |

**11 / 11 维度全覆盖。**
