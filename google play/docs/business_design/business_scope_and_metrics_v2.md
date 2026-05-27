# 项目业务场景与指标体系设计 v2

> **对外 / 作品集 / mentor 材料**：优先使用三层结构主文档 [`business_scope_three_layer_design.md`](business_scope_three_layer_design.md)（Main + Appendix + Future Work）。本文件保留为 **v2 技术详版**（7 BQ、完整公式与指标表），与三层版并行维护。

## Google Play Review Analytics for Mobile Game User Satisfaction
### 面向休闲手游用户满意度优化的 Google Play 评论分析项目

> **版本**：v2.0  
> **相对 v1 的变更**：BQ6 改为版本对比（采集 `app_version`）；新增 §7 正交化 Health Score（含贝叶斯收缩 + Confidence guardrail）；新增 §9.8 主题方法论 + §9.9 开发者回复 / Helpfulness 信号；新增 §10 细化主题分类（4 大类 × 18 主题）；新增 §12 BQ ↔ Primary Metric 对应表；新增 §13 Limitations 集中段；§5 竞品池替换为 7 publisher × 2 = 14 App 平衡集；§9.6 因果语言全面修正。

---

## 1. 目标公司设定

本项目以一家模拟的中型 free-to-play 移动休闲游戏公司作为业务场景。该公司主要在 Google Play 平台发行和运营休闲益智类手游，产品类型覆盖 match-3、blast puzzle、merge game、story decoration 和 light simulation 等细分品类。

该公司依赖 Google Play 平台进行用户获取，并通过用户评分、评论质量、平台口碑和应用商店排名影响潜在用户的下载决策。因此，Google Play 用户评论不仅是产品反馈来源，也是衡量用户满意度、识别产品体验问题和分析竞品表现的重要外部数据。

在本项目中，目标公司被设定为一家希望提升用户满意度和平台评分健康度的移动游戏公司。由于缺少内部用户行为数据，例如留存率、转化率、付费率和 DAU，本项目主要使用 Google Play 公开评论数据作为外部 proxy signals，分析用户感知满意度、低分评论痛点、高分评论驱动因素和竞品体验差异。

---

## 2. 目标公司业务模式

目标公司采用典型的 **free-to-play mobile game business model**。用户可以免费下载游戏，并通过关卡推进、任务完成、剧情解锁、合成、装饰或社交互动持续参与游戏。公司主要通过内购、广告和 LiveOps 活动实现收入增长。

其核心业务模式可以概括为：

| 业务模块       | 说明                                          |
| ---------- | ------------------------------------------- |
| 用户获取       | 通过 Google Play 自然搜索、应用商店推荐、广告投放和平台排名获取新用户   |
| 免费下载       | 用户可以免费安装并开始游戏，降低进入门槛                        |
| 核心玩法       | 通过 match-3、blast、merge、装修、剧情或轻度经营玩法推动用户持续游玩 |
| 内购收入       | 用户购买金币、体力、道具、booster、礼包或关卡辅助资源              |
| 广告收入       | 通过激励视频广告、插屏广告或奖励广告实现变现                      |
| LiveOps 活动 | 通过限时活动、排行榜、团队任务和节日活动提高活跃度                   |
| 平台口碑       | Google Play 评分和评论影响新用户信任、下载转化和长期品牌形象        |

从增长逻辑来看，该类游戏通常遵循以下路径：

```text
Google Play 曝光
→ 下载转化
→ 新手体验
→ 关卡推进
→ 留存
→ 内购 / 广告变现
→ 用户评分和评论
→ 影响下一批用户下载决策
```

由于本项目无法直接获取客户内部的留存、转化和付费数据，因此 Google Play 评分和评论被用于衡量用户感知满意度与产品体验摩擦的外部 proxy 指标。

---

## 3. 项目业务背景

移动休闲游戏市场竞争激烈，同类产品之间的玩法、视觉设计、关卡机制、广告体验和商业化策略高度相似。对于一家中型游戏公司而言，用户在 Google Play 上留下的评论能够反映大量关键业务问题，例如：

1. 用户为什么给低分；
2. 哪些体验问题最影响满意度；
3. 哪些竞品 App 的用户评价更好；
4. 高分用户主要认可哪些产品体验；
5. 版本更新后用户反馈是否改善；
6. 哪些问题应该优先进入产品优化 backlog。

然而，Google Play 评论本身是非结构化文本。如果产品团队只是人工查看少量评论，很难系统性地识别用户痛点、长期趋势和竞品差异。因此，本项目希望通过数据分析方法，将大量 Google Play 评论转化为结构化指标、可视化看板和可执行的产品优化建议。

本项目的业务目标是：

> 通过分析 14 个同类休闲手游在 Google Play 上的用户评论，帮助目标公司理解用户满意度趋势、识别核心体验痛点、对比竞品表现，并为 UX 和 Product 团队提供数据驱动的优化建议。

### 3.1 数据来源与抓样性质（Data Honesty）

评论数据通过 `google-play-scraper` 公开接口获取，结果为 Google Play 默认排序（NEWEST / MOST_RELEVANT）的子集，**非随机样本，亦非全量**。所有满意度结论建立在该样本之上，不外推到 App 全部历史评论或全部用户群体。竞品间对比假设各 App 的抓样偏差结构相似（同一接口、同一时间窗）。详细限制汇总见 §13。

---

## 4. 核心业务问题

本项目围绕以下七个核心业务问题展开：

### BQ1：整体用户满意度健康情况如何？

通过 **App Satisfaction Health Score**（见 §7）综合 Level / Polarization / Momentum 三个正交维度，结合 Confidence guardrail，评估目标 App 与竞品 App 的整体用户满意度健康水平。

### BQ2：哪些竞品 App 表现最好？哪些风险最高？

通过 Health Score Rank、Low-Star Share Rank 和 Volume vs Rating Scatter，对 14 个竞品（默认全集）以及去重后的 **7-App 跨 publisher benchmark set**（见 §5）进行满意度排名，识别表现优秀的产品和存在明显用户不满风险的产品。

### BQ3：用户低分评论主要在抱怨什么？

对 1–2 星评论按 §10 主题体系进行多标签分类，识别用户主要不满来源（crash、ads、payment、performance、update issue、algorithm fairness、LiveOps issue 等）。配套的 secondary 维度还包括 **Low-Star Theme Dev Reply Rate**（开发者是否优先回复差评）和 **Helpfulness-Weighted Theme Share**（社区共鸣度加权）。

### BQ4：高分评论主要认可什么？

对 4–5 星评论进行主题分析，识别正向体验驱动因素（fun & addictive、visuals、story / decoration、social、updates & new content 等）。同样使用 thumbs_up 加权得到社区共识级正向标签。

### BQ5：用户满意度是在改善还是恶化？

通过 **Weekly Avg Rating slope (8-week OLS)**、Weekly Low-Star Share 和 Weekly Volume，判断不同 App 的用户满意度趋势，并识别潜在恶化信号。

### BQ6：版本更新后，用户反馈是否变化？

采集 `reviewCreatedVersion` 字段后，按 `app_version_major` 分组对比相邻版本（vN-1 vs vN）的 Avg Rating、Low-Star Share、Top Theme 排名以及 **开发者回复速率 / SLA 在版本前后的变化**（dev reply / replied_at 的版本横切观察）。该分析为 **descriptive within-window comparison**，不声称版本本身是观察到差异的原因（详见 §9.6 因果免责声明）。

### BQ7：产品团队应该优先优化哪些问题？

基于 **Helpfulness-Weighted Frequency × Impact × Severity × ReplyAttention** 构建 Priority Score（见 §9.7），将用户评论转化为 P0 / P1 / P2 / P3 产品优化建议；其中 ReplyAttention 因子让 "高频差评但开发者尚未接住" 的主题获得优先级提升。

---

## 5. 竞品池设计

本项目选取 14 个 Google Play 上的休闲手游作为竞品池。选取标准包括：品类相近、评论量较高、玩法具有代表性、能够覆盖 match-3、blast、decoration、story 和 IP-themed puzzle 等核心细分方向；并通过 **每家 publisher 严格 2 个产品** 的设计，避免单一公司主导跨厂排名。

| 序号 | App                       | 公司           | 子类型                               | 选择理由                                  |
|---:|---------------------------|----------------|------------------------------------|-----------------------------------------|
|  1 | Royal Match               | Dream Games    | Match-3                            | 当前 match-3 头部 benchmark             |
|  2 | Royal Kingdom             | Dream Games    | Match-3                            | 同公司新作，可观察系列化策略           |
|  3 | Candy Crush Saga          | King           | Match-3                            | 经典 match-3 标杆                       |
|  4 | Candy Crush Soda Saga     | King           | Match-3                            | 同系列延展                              |
|  5 | Gardenscapes              | Playrix        | Match-3 + Decoration               | 三消 + 剧情 + 装修代表                  |
|  6 | Homescapes                | Playrix        | Match-3 + Decoration               | 家装剧情                                |
|  7 | Toon Blast                | Peak Games     | Blast Puzzle                       | 点击消除标杆                            |
|  8 | Toy Blast                 | Peak Games     | Blast Puzzle                       | 同公司对照                              |
|  9 | Cookie Jam                | Jam City       | Match-3                            | 老牌 match-3，长尾运营典型              |
| 10 | Disney Emoji Blitz        | Jam City       | Match-3 + IP                       | 同公司 + IP 题材，可观察 IP 体验差异     |
| 11 | Lily's Garden             | Tactile Games  | Match-3 + Story + Garden           | 女性向剧情 + 园艺                       |
| 12 | Penny & Flo               | Tactile Games  | Match-3 + Story + Decoration       | 同公司装修剧情                          |
| 13 | Angry Birds Dream Blast   | Rovio          | Bubble Blast + IP                  | 经典 IP + blast 玩法                    |
| 14 | Angry Birds Friends       | Rovio          | Slingshot Puzzle + IP              | 弹射类 puzzle + IP 友好对照             |

### 5.1 Publisher 平衡性

```text
Dream Games × 2  | King × 2     | Playrix × 2  | Peak Games × 2
Jam City × 2     | Tactile × 2  | Rovio × 2
```

7 家公司 × 2 个产品，**单家最高占比 14%**（2/14），任何一家公司都不会单方面拖偏跨 publisher 排名；同时保留同 publisher 双产品，方便做系列化策略对比。

### 5.2 双口径对比设计

- **同 publisher 系列对比（7 对）**：观察"系列化策略"对用户满意度的影响。
  Royal Match vs Royal Kingdom · Candy Crush Saga vs Soda · Gardenscapes vs Homescapes · Toon Blast vs Toy Blast · Cookie Jam vs Disney Emoji Blitz · Lily's Garden vs Penny & Flo · Angry Birds Dream Blast vs Friends。
- **跨 publisher 对比（去重 7-App benchmark set）**：用于 BQ1 / BQ2 / BQ7 的跨公司排名。每家取一个旗舰：
  Royal Match · Candy Crush Saga · Gardenscapes · Toon Blast · Cookie Jam · Lily's Garden · Angry Birds Dream Blast。

### 5.3 子类型分布（用于 §9.5 Category Benchmark）

| 子类型                          | App 数 | 代表                                                            |
|--------------------------------|------:|----------------------------------------------------------------|
| Pure Match-3                   |    4  | Royal Match, Candy Crush Saga, Candy Crush Soda, Cookie Jam   |
| Match-3 + Decoration / Story   |    4  | Gardenscapes, Homescapes, Lily's Garden, Penny & Flo          |
| Match-3 + IP                   |    1  | Disney Emoji Blitz                                             |
| Match-3 (新作)                  |    1  | Royal Kingdom                                                  |
| Blast Puzzle                   |    2  | Toon Blast, Toy Blast                                          |
| Blast + IP                     |    1  | Angry Birds Dream Blast                                        |
| Slingshot + IP                 |    1  | Angry Birds Friends                                            |

子类型扩展到 5 大类，使 Category Benchmark 维度真正具备可比内容。

---

## 6. 指标体系设计：North Star-inspired Review Satisfaction Framework

为了让项目更贴近 DA / BA / Product Analyst 场景，本项目采用 **North Star-inspired metric framework** 和 **Objective–Signal–Metric, OSM** 思维搭建指标体系。

由于本项目无法获取客户内部数据，例如留存率、转化率、付费率或 DAU，因此不直接定义客户公司的真实北极星指标，而是基于 Google Play 公开评论数据，设计一个外部可观测的满意度 proxy 指标：

> **App Satisfaction Health Score**
> App 用户满意度健康分

该指标用于回答：

> 从 Google Play 用户评论看，一个 App 的用户体验健康程度如何？

---

## 7. 北极星 Proxy 指标：App Satisfaction Health Score

### 7.1 设计原则：四维正交 + Confidence 修正系数

v1 旧设计将 Positive Share、Normalized Avg Rating 和 (1 − Low-Star Share) 同时加权，三者本质都是评分分布形状的不同切片，相关系数实测 ≥ 0.85，95% 权重在度量同一件事。v2 改为 **三个正交满意度维度 + 一个 Confidence 乘数 cap**，每个分量度量独立信息：

```text
Health Score
  = ( 0.40 × Level
    + 0.35 × Polarization
    + 0.25 × Momentum
    ) × Confidence
```

| 维度          | 测什么                | 公式                                                    | 范围  |
|---------------|----------------------|--------------------------------------------------------|-------|
| **Level**         | 平均满意度水平       | `BayesianAdjustedAvg / 5`（公式 7.2）                  | 0 ~ 1 |
| **Polarization**  | 极端不满风险         | `1 − LowStarShare`（LowStar = score ≤ 2）              | 0 ~ 1 |
| **Momentum**      | 近期趋势             | `clip( 0.5 + slope_last8w / scale, 0, 1 )`（公式 7.3） | 0 ~ 1 |
| **Confidence**    | 样本可信度（cap）   | `min(1, n_reviews / 200)`                              | 0 ~ 1 |

### 7.2 Bayesian Adjusted Average（IMDb Top 250 同款收缩公式）

```text
BayesianAdjustedAvg
  = ( n × app_avg + k × global_avg ) / ( n + k )

其中：
  n           = 该 App 评论数
  app_avg     = 该 App 原始均分
  global_avg  = 14 个 App 总体均分（先用一次性 EDA 计算后固定）
  k           = 平滑系数，建议 200（≈ 一个"足够大的样本量"）
```

**效果**：评论少的 App，均分自动被往全局均分拉。50 条样本 4.9 分的小 App 会被收缩到接近全局均值，而 5000 条样本 4.6 分的旗舰 App 几乎不变——直接解决"小样本均分偶然偏高"的失真问题。

### 7.3 Momentum slope

```text
slope_last8w
  = OLS slope of (week_index, weekly_avg_rating) over last 8 weeks

Momentum
  = clip( 0.5 + slope_last8w / scale, 0, 1 )
  scale = 0.05    # 一周变化 0.05 星即拉满或归零
```

| slope（每周变化）             | Momentum |
|-----------------------------|---------:|
| ≥ +0.05 星 / 周（强改善）   | ≈ 1.0    |
| ≈ 0（持平）                  | = 0.5    |
| ≤ −0.05 星 / 周（强恶化）   | ≈ 0.0    |

相比 v1 的 1 / 0.5 / 0 三档，OLS slope 分辨率更高且对单周噪声不敏感。

### 7.4 Confidence 作为乘数 cap

```text
Confidence = min(1, n_reviews / 200)

效果：
  n =  50 → Confidence = 0.25 → Health Score 最高只能到原值的 25%
  n = 100 → Confidence = 0.50
  n = 200 → Confidence = 1.00 → 不削减
```

含义：**样本不够，分数直接被压低**。这是 §9 Guardrail 的第一层柔性约束，避免小样本 App 凭运气挤入头部。

### 7.5 输出范围与解读阈值

| Health Score 区间 | 含义       | 行动                                  |
|-------------------|----------|--------------------------------------|
| **≥ 0.75**        | Healthy   | 维持，作为 benchmark                  |
| **0.55 – 0.75**   | Watch     | 关注 momentum 与 polarization         |
| **< 0.55**        | At Risk   | 进入 BQ7 优先级矩阵                    |
| **Confidence < 0.5** | Low Sample | 不参与 ranking，单独标注 "Insufficient Sample" |

### 7.6 权重选择依据 + Sensitivity Analysis

权重 0.40 / 0.35 / 0.25 为业务先验：满意度水平最重要（Level 0.40），其次是极端风险控制（Polarization 0.35，casual game 玩家流失对 1–2 星评论高度敏感），最后是变化趋势（Momentum 0.25）。

**Sensitivity check**：附录 A 提供 5 套候选权重（如 0.50/0.30/0.20、0.33/0.34/0.33、0.40/0.40/0.20、0.30/0.40/0.30、0.45/0.35/0.20）下的 14 App 排名 Spearman 相关矩阵；只要 5 套权重下排名相关 ≥ 0.85，即可认为结论对权重不敏感。

> 这是健康分公式的"可解释性背书"——面试中被问 "为什么是这个权重？" 时，一句 "我们做了 sensitivity analysis，5 套权重下排名 Spearman ≥ 0.85" 就能挡住绝大多数追问。

### 7.7 范围声明

该健康分不是客户公司内部真实业务 KPI，而是基于公开 Google Play 评论数据构建的外部满意度 proxy metric，主要用于竞品对比、用户满意度追踪和产品优化优先级判断。

---

## 8. OSM 指标框架

### Objective 1：提升用户感知满意度

| Objective         | Signal              | Metric                              |
|-------------------|---------------------|-------------------------------------|
| 提升用户感知满意度 | 用户给出更高评分     | Bayesian Adjusted Avg Rating         |
| 提升用户感知满意度 | 更多用户给 4–5 星    | Positive Share                       |
| 提升用户感知满意度 | 更少用户给 1–2 星    | Low-Star Share                       |
| 提升用户感知满意度 | 评分结构更健康       | Rating Distribution                  |
| 提升用户感知满意度 | 最近评分趋势改善     | Weekly Avg Rating Slope (8w OLS)     |

### Objective 2：降低关键用户痛点

| Objective       | Signal                          | Metric                              |
|----------------|--------------------------------|-------------------------------------|
| 降低关键用户痛点 | crash / bug 相关评论减少         | Crash & Bug Theme Share              |
| 降低关键用户痛点 | ads 相关负面评论减少             | Ads Volume / Ads Quality Share       |
| 降低关键用户痛点 | login / account 问题减少         | Account & Login Theme Share          |
| 降低关键用户痛点 | payment / purchase 问题减少      | Purchase Issue Theme Share           |
| 降低关键用户痛点 | 低分评论中的核心痛点下降          | Low-Star Theme Share                 |
| 降低关键用户痛点 | 严重主题的平均评分提升            | Theme Avg Rating                     |
| 降低关键用户痛点 | **社区共识级痛点优先**            | **Helpfulness-Weighted Theme Share** |
| 降低关键用户痛点 | **运营是否优先回复差评主题**       | **Low-Star Theme Dev Reply Rate**    |

### Objective 3：识别竞品优势和弱点

| Objective    | Signal                       | Metric                              |
|-------------|------------------------------|-------------------------------------|
| 识别竞品优势 | 某些 App 高分率明显更高        | Positive Share by App                |
| 识别竞品优势 | 高分 App 的正向主题更集中      | Positive Theme Share                 |
| 识别竞品弱点 | 某些 App 低分率明显更高        | Low-Star Share by App                |
| 识别竞品弱点 | 某些 App 在广告 / 付费 / 性能上负面反馈更多 | App Theme Matrix                     |
| 识别竞品模式 | 同类 App 是否存在共同痛点      | Category-level Theme Benchmark       |
| 识别竞品运营 | 哪些公司差评回复覆盖更高        | Low-Star Dev Reply Rate by App       |

### Objective 4：支持产品优化优先级

| Objective       | Signal                        | Metric                              |
|----------------|------------------------------|-------------------------------------|
| 支持产品优化优先级 | 高频问题应优先处理            | Theme Frequency / Helpfulness-Weighted |
| 支持产品优化优先级 | 对评分伤害大的问题应优先处理   | Theme Rating Gap (Impact)            |
| 支持产品优化优先级 | 低分评论占比高的问题应优先处理 | Low-Star Theme Share (Severity)      |
| 支持产品优化优先级 | 阻断型问题应优先处理          | Critical Theme Flag                  |
| 支持产品优化优先级 | **运营盲区主题应优先处理**     | **ReplyAttention Factor**            |
| 支持产品优化优先级 | 综合评分形成 backlog 优先级    | Priority Score                       |

---

## 9. 完整指标体系

### 9.1 数据范围指标

| 指标                  | 公式                              | 用途              | Dashboard 展示  |
|----------------------|-----------------------------------|-----------------|----------------|
| Total Reviews         | COUNT(review_id)                   | 衡量数据规模      | KPI Card        |
| App Count             | COUNTD(app_id)                     | 衡量覆盖竞品数量   | KPI Card        |
| Date Range            | MIN(date) 到 MAX(date)             | 展示分析周期      | Text / Card     |
| Reviews per App       | COUNT(review_id) by app            | 判断样本是否均衡   | Bar Chart       |
| English Review Share  | English reviews / total reviews    | 判断文本分析可用性 | KPI / Donut     |
| **Version Coverage**  | non_null(app_version) / total      | **判断 BQ6 可行性** | KPI / Card      |

### 9.2 满意度指标

| 指标                          | 公式                                 | 用途                  | Dashboard 展示    |
|------------------------------|--------------------------------------|---------------------|------------------|
| Average Rating                | AVG(score)                           | 原始平均评分          | KPI / Bar         |
| **Bayesian Adjusted Avg**     | (n·app_avg + 200·global_avg)/(n+200) | **小样本收缩后平均**   | KPI / Bar         |
| Median Rating                 | MEDIAN(score)                        | 衡量稳健评分水平      | Table             |
| Positive Share                | COUNT(score ≥ 4) / total reviews     | 衡量满意用户占比      | KPI / Bar         |
| Low-Star Share                | COUNT(score ≤ 2) / total reviews     | 衡量不满风险          | KPI / Bar         |
| 1-Star Share                  | COUNT(score = 1) / total reviews     | 衡量强烈不满风险      | Bar               |
| Rating Distribution           | COUNT by score / total reviews       | 展示评分结构          | Stacked Bar       |
| **Health Score**              | §7 综合公式                          | App 满意度健康水平    | Ranking / Card    |
| **Confidence**                | min(1, n / 200)                      | 样本可信度 cap       | KPI               |

### 9.3 趋势指标

| 指标                       | 公式                                              | 用途             | Dashboard 展示       |
|---------------------------|---------------------------------------------------|----------------|--------------------|
| Weekly Avg Rating          | AVG(score) by week                                 | 观察满意度趋势    | Line Chart          |
| Weekly Low-Star Share      | Low-star share by week                             | 观察负面反馈趋势  | Line Chart          |
| Weekly Positive Share      | Positive share by week                             | 观察正向反馈趋势  | Line Chart          |
| Weekly Review Volume       | COUNT(review_id) by week                           | 衡量用户反馈热度  | Column Chart        |
| **Weekly Avg Rating Slope**| OLS slope over last 8 weeks                        | **趋势量化（BQ5 主指标）** | KPI / Sparkline      |
| Rating Change              | Current period avg − previous period avg           | 判断评分改善或恶化| KPI / Table         |
| Low-Star Change            | Current low-star share − previous low-star share   | 判断负面风险变化  | KPI / Table         |
| Review Spike               | Current volume vs baseline volume                  | 识别版本或事件风险| Line + annotation   |

### 9.4 主题分类指标

| 指标                              | 公式                                                       | 用途                | Dashboard 展示  |
|----------------------------------|------------------------------------------------------------|-------------------|---------------|
| Theme Count                       | COUNT(review_id) where is_theme_X = 1                       | 痛点规模            | Bar             |
| Theme Share                       | Theme count / total reviews                                  | 痛点占比            | Treemap / Bar   |
| **Helpfulness-Weighted Share**    | Σ log(1+thumbs_up) · is_theme / Σ log(1+thumbs_up)          | **社区共识加权占比**  | Bar             |
| Theme Avg Rating                  | AVG(score) where is_theme_X = 1                              | 主题满意度水平       | Table           |
| Theme Low-Star Share              | Low-star reviews in theme / theme reviews                    | 主题负面程度        | Bar / Table     |
| Low-Star Theme Share              | Low-star reviews in theme / total low-star reviews           | 低分主要原因         | Bar             |
| Rating Gap (Impact)               | Overall avg rating − theme avg rating                        | 主题对评分的伤害      | Matrix          |
| Critical Complaint Share          | Critical theme reviews / total reviews                       | 关键问题风险         | KPI             |
| **Low-Star Theme Dev Reply Rate** | dev_reply count in (theme ∩ low-star) / theme low-star count | **运营是否覆盖该痛点** | Bar             |
| Theme Coverage Rate               | reviews with ≥ 1 theme hit / total reviews                   | 方法论质量（Guardrail）| KPI             |

### 9.5 竞品对比指标

| 指标                       | 公式                            | 用途                                   | Dashboard 展示    |
|---------------------------|---------------------------------|--------------------------------------|------------------|
| App Health Score Rank      | Rank by Health Score             | 综合健康度排名                          | Ranking Table     |
| App Rating Rank            | Rank by Bayesian Adjusted Avg    | 评分水平排名                           | Ranking Table     |
| App Low-Star Risk Rank     | Rank by low-star share           | 高风险 App                              | Ranking Table     |
| App Positive Share Rank    | Rank by positive share           | 体验优势 App                            | Bar               |
| App Theme Matrix           | App × Theme Count / Share         | 痛点结构对比                            | Heatmap / Matrix  |
| Category Benchmark         | 按子类型聚合（§5.3）              | match-3 / blast / IP 等子类对比         | Bar               |
| Review Volume vs Rating    | X = reviews, Y = rating          | 高声量 + 高 / 低风险 App                  | Scatter Plot      |
| **Low-Star Reply Rate Rank** | Rank by Low-Star Dev Reply Rate | 哪家运营覆盖差评最好                     | Bar               |

### 9.6 事件窗 / 版本对比指标（替换原 v1 §9.6）

> **方法选择**：v2 主走 **(A) 版本号路径**——`01_collect/collect_reviews.py` 采集 `reviewCreatedVersion`，存为 `reviews.app_version`，`02_clean` 派生 `app_version_major`（前 1–2 段，如 `"3.5.0.156"` → `"3.5"`）。v2 不主推 spike-window fallback；其作为 Limitations 兜底（详见 §13）。

| 指标                              | 公式                                                          | 用途                  | Guardrail                        |
|----------------------------------|---------------------------------------------------------------|---------------------|---------------------------------|
| Per-version Avg Rating            | AVG(score) by app × app_version_major                          | 单版本满意度水平       | n_reviews ≥ 50                   |
| Per-version Low-Star Share        | low_star / version_total                                        | 单版本不满风险          | n_reviews ≥ 50                   |
| **Window Δ Avg Rating**           | avg(vN) − avg(vN-1)                                             | 相邻版本评分描述性差异 | 两版本均 n ≥ 50                   |
| **Window Δ Low-Star Share**       | low_star_share(vN) − low_star_share(vN-1)                       | 相邻版本不满变化       | 两版本均 n ≥ 50                   |
| **Window Δ Top Theme Rank Shift** | rank-difference of top 5 themes between vN-1 and vN              | 主题结构变化           | Theme Coverage ≥ 60%             |
| Post-version Volume               | review count in vN                                              | 版本反馈热度            | —                                |
| **Δ Dev Reply Rate**              | dev_reply_rate(vN) − dev_reply_rate(vN-1)                       | 版本前后运营响应变化     | n_reviews ≥ 50                   |
| **Δ Reply SLA Days**              | median_reply_days(vN) − median_reply_days(vN-1)                 | 版本前后回复时效变化     | reply count ≥ 30                 |
| Version Coverage Rate             | non_null(app_version) / total_reviews                            | **决定 BQ6 能否出结论**  | ≥ 50% 才输出 BQ6 主指标           |

#### Causal Disclaimer（必备）

> All deltas in this table are **descriptive observations within fixed time windows** and **do not isolate version effects** from concurrent factors (LiveOps events, seasonality, marketing, sampling-window changes). Use as **directional signals** only. To establish causality, run a controlled experiment (A/B test or pre-registered RDD around the version release date).

#### 命名规范修正

| 旧命名（v1，因果语气）        | 新命名（v2，描述性语气）            |
|------------------------------|------------------------------------|
| Pre-update Avg Rating         | Pre-event window Avg Rating         |
| Post-update Avg Rating        | Post-event window Avg Rating        |
| Rating Delta                  | Window Δ Avg Rating                 |
| Pre/Post Low-Star Delta       | Window Δ Low-Star Share             |
| New Complaint Theme           | Theme rank shift in post window     |
| Post-update Review Spike      | Post-window volume spike            |

### 9.7 优先级指标

| 指标                          | 公式                                                                  | 用途                | Dashboard 展示    |
|------------------------------|----------------------------------------------------------------------|-------------------|-----------------|
| Frequency                     | Helpfulness-Weighted Theme Share                                      | 出现频率（社区共识加权） | Matrix            |
| Impact                        | Overall Avg Rating − Theme Avg Rating                                 | 评分伤害             | Matrix            |
| Severity                      | Theme Low-Star Share                                                  | 负面严重程度          | Table             |
| **ReplyAttention Factor**     | 1.2 if Low-Star Theme 且该主题 Dev Reply Rate < 20%, else 1.0         | **运营盲区加权**      | Tag               |
| **Priority Score (v2)**       | Frequency × Impact × Severity × ReplyAttention                         | 综合优先级            | Scatter / Table   |
| Priority Level                | P0 / P1 / P2 / P3                                                      | backlog 分类         | Table             |

#### 优先级判定规则（与 v1 一致，仍是面试讲述抓手）

| Priority | 判断标准                  | 示例                                      |
|---------|--------------------------|-----------------------------------------|
| P0       | 高频 + 评分伤害大 + 阻断使用 | crash, login, payment, algorithm fairness |
| P1       | 高频 + 明显影响体验         | ads volume, performance, update issue, LiveOps |
| P2       | 中频 + 可优化体验           | UI / navigation, onboarding, difficulty   |
| P3       | 低频或偏偏好类             | visual preference, minor feature request  |

### 9.8 主题方法论（v1 = Rule-based Multi-label Keyword Matching）

#### 9.8.1 选型决定

| 方案                          | 准确度 | 召回 | 可解释         | 成本 | 本项目选用   |
|-------------------------------|------|-----|--------------|------|-----------|
| (a) 关键词匹配                 | 中    | 中   | ★★★ 高        | $0    | ✅ v1      |
| (b) zero-shot LLM             | 高    | 高   | ★ 低（黑盒）  | $$    | v2 兜底     |
| (c) topic modeling (LDA / BERTopic) | 中 | 中 | ★★ 中        | $     | 探索性辅助  |

**v1 选 (a) 的理由**：  
(1) 一条评论 = 一个理由——关键词命中即解释，PM 可直接回溯触发词；  
(2) 完全可重复（同一份数据 → 同一份 theme 结果）；  
(3) 零依赖、零 API 成本；  
(4) 短评论（< 30 字）在 casual game 评论中占 60%+，LLM 在短文本上反而不稳。

#### 9.8.2 流程

```text
clean_en_only.csv
   │
   ▼
[1] 文本规范化：lowercase + strip 标点 + 替换 emoji → text_norm
   │
   ▼
[2] 加载主题词典 config/themes.yml（含正向 keywords + exclude_keywords）
   │
   ▼
[3] 多标签匹配：每条评论对每个主题独立判断
       命中规则：text_norm 至少出现 1 个 keyword 且未命中 exclude_keyword
   │
   ▼
[4] 输出宽表 reviews_with_themes.csv
       schema：review_id, app_id, score, ...,
              is_theme_crash, is_theme_ads, ..., is_theme_other
              theme_count = Σ is_theme_*
   │
   ▼
[5] 评估集：抽样 200 条人工标注 → 算每个主题的 P / R / F1
        + Coverage = sum(theme_count > 0) / total
        + Multi-label rate = mean(theme_count when > 0)
```

#### 9.8.3 关键词字典格式（`config/themes.yml`）

```yaml
crash_bug:
  description: 崩溃 / 闪退 / 卡死
  keywords:
    - crash
    - crashes
    - crashed
    - crashing
    - bug
    - glitch
    - freeze
    - froze
    - stuck on loading
    - won't open
    - keeps closing
    - black screen

ads_volume:
  description: 广告频率过高
  keywords:
    - too many ads
    - so many ads
    - forced ads
    - unskippable
    - pop[- ]?up ads
    - ad spam
  exclude_keywords:
    - no ads
    - ad[- ]free
    - love the ads
```

> **关键设计点**：  
> · **正向关键词 + 排除词** 同时存在，避免 "love the ads" / "no ads" 被误判为投诉。  
> · 用列表而不是裸正则，业务同事可直接读、直接改。  
> · 每个主题带 description，写进 dashboard tooltip 即可让 PM 看懂。

#### 9.8.4 评估方案（差异化加分项）

`docs/themes/theme_eval_v1.md` 输出：

- **评估集**：random sample 200 条 `clean_en_only`，2 人交叉标注，报告 Cohen's κ。
- **每主题三列**：Precision = TP / (TP + FP)、Recall = TP / (TP + FN)、F1。
- **整体指标**：
  - Overall Coverage：≥ 60% 目标
  - Unmatched ('other') 比例：≤ 40% 目标
  - Avg theme / comment：1.5 ~ 2.5（多标签合理范围）
- **失败案例分析**：
  - 漏召回 top 10：补充 keywords
  - 误判 top 10：增加 exclude_keywords

#### 9.8.5 升级路径（roadmap，v1 不做）

- **v2**：对 `is_theme_other = 1` 的评论用 zero-shot LLM 兜底打标。
- **v3**：基于评估集 fine-tune 一个 distilbert 多标签分类器，替换关键词。

### 9.9 开发者回复 / Helpfulness 信号（横切多个 BQ）

数据层已采集 `has_dev_reply` / `replied_at` / `thumbs_up_count` 三个字段。本节不单独立 BQ，而是把这些信号**横切**进 BQ3 / BQ4 / BQ6 / BQ7：

| 信号                              | 定义                                                          | 出现于 BQ        | 角色                              |
|----------------------------------|--------------------------------------------------------------|-----------------|----------------------------------|
| Dev Reply Rate (overall)          | sum(has_dev_reply) / total_reviews                            | BQ2 / BQ6       | 整体回复覆盖（竞品 / 版本前后对比） |
| Low-Star Dev Reply Rate           | dev_reply count in (score ≤ 2) / count(score ≤ 2)             | BQ3 / BQ7       | 运营是否优先处理差评              |
| High-Star Dev Reply Rate          | dev_reply count in (score ≥ 4) / count(score ≥ 4)             | BQ4             | 是否同时维护好评关系              |
| Reply SLA Median Days             | median(replied_at_parsed − at_parsed) where has_dev_reply = 1 | BQ2 / BQ6       | 响应时效中位数                    |
| Reply SLA P90 Days                | p90 of same                                                  | BQ2             | 长尾响应能力                      |
| **Helpfulness Weight**            | log(1 + thumbs_up_count)                                      | BQ3 / BQ4 / BQ7 | 社区共识权重（用于 Frequency）     |
| **Helpfulness-Weighted Theme Share** | Σ weight · is_theme / Σ weight                              | BQ3 / BQ4       | 高赞痛点 / 驱动因素权重提升         |
| **ReplyAttention Factor**         | 1.2 if Low-Star Theme 且该主题 Dev Reply Rate < 20%, else 1.0 | BQ7             | 运营盲区主题优先级提升             |

**BQ6 的版本对比中**，`Δ Dev Reply Rate` 和 `Δ Reply SLA Days` 用于回答："版本更新后，运营响应行为是否同步变化？"——这正是把 dev_reply 信号挂到 BQ6 的方式。

#### 解读阈值（Casual game 行业经验）

| Low-Star Dev Reply Rate | 解读                                |
|-------------------------|------------------------------------|
| ≥ 50%                   | 运营投入高，customer support 团队成熟 |
| 20% – 50%               | 中等投入，可能仅回复关键词触发           |
| < 20%                   | 运营覆盖明显不足                     |

| Reply SLA Median        | 解读                          |
|-------------------------|-------------------------------|
| ≤ 2 天                   | 高响应（Playrix 系基准）         |
| 3 – 7 天                 | 中等                          |
| > 7 天                   | 滞后                          |

---

## 10. 主题分类体系（细化版）

针对 casual puzzle / match-3 / merge 游戏，本项目设计 **4 大类 × 18 个二级主题** 的多标签分类体系，并补全 v1 遗漏的 4 个 casual game 高频独立主题。

### 10.1 Negative Themes（13 个）

| 一级           | 二级主题                       | 关键词示例                                                                | 业务含义                                |
|---------------|-------------------------------|-----------------------------------------------------------------------|---------------------------------------|
| **Stability** | Crash & Bug                    | crash, bug, glitch, freeze, won't open, black screen, keeps closing  | 崩溃 / 闪退                             |
| Stability     | Loading & Performance          | slow, lag, loading forever, stuck loading, takes long                 | 加载与性能                              |
| **Monetization** | Ads Volume                  | too many ads, forced ads, unskippable, pop-up ads, ad spam            | 广告频率                                |
| Monetization  | **Ads Quality** ⭐ 新增          | inappropriate ads, scam ads, misleading ads, broken ad video         | 广告质量与合规（拆分自 v1 单一 Ads 主题） |
| Monetization  | Pay-to-win / Greedy            | pay to win, p2w, money grab, greedy, expensive, predatory             | 付费公平感                              |
| Monetization  | Purchase Issue                 | refund, didn't receive, charge twice, unauthorized, payment failed   | 交易问题                                |
| **Game Design** | Difficulty & Progression     | too hard, impossible level, level stuck, lives, energy wait           | 难度与卡点                              |
| Game Design   | **Algorithm Fairness** ⭐ 新增   | rigged, cheating, scripted, impossible board, set up to fail, manipulated | **算法公平感（casual 高频独立痛点）**    |
| Game Design   | Rewards & Energy               | not enough rewards, stingy, energy too slow, lives wait               | 资源激励                                |
| **Operations** | Update Issue                  | after update, new version broke, since update, latest update worse    | 版本回归                                |
| Operations    | **LiveOps & Events** ⭐ 新增      | event broken, team event bug, tournament glitch, event too short      | 活动质量（Playrix / Peak / Dream 高频）  |
| Operations    | Account & Login                | login, account, lost progress, password, can't log in, sync failed    | 账号与进度                              |
| **UX**        | UI / Navigation                | confusing menu, hard to find, button too small, tutorial unclear      | 界面与引导                              |

### 10.2 Positive Themes（5 个）

| 一级       | 二级主题                          | 关键词示例                                                          | 业务含义                                 |
|-----------|----------------------------------|-----------------------------------------------------------------|----------------------------------------|
| **Positive** | Fun & Addictive                | fun, addictive, love it, can't stop, enjoyable, relaxing, satisfying | 核心玩法乐趣                              |
| Positive  | Visual & Graphics                 | beautiful, cute, graphics, art, design, colorful, gorgeous       | 视觉体验                                  |
| Positive  | Story & Decoration                | story, decorate, garden, mansion, room, customization, characters| 剧情装饰（与付费转化关联强）                |
| Positive  | Social & Team                     | team, friends, leaderboard, PvP, compete, helpful community      | 社交体验                                  |
| Positive  | **Updates & New Content** ⭐ 新增  | new levels, fresh content, frequent updates, love the new        | **正向更新（与 Update Issue 形成镜像对照）** |

### 10.3 v2 新增 4 个主题的设计动机

1. **Algorithm Fairness（算法公平感）**——casual / match-3 玩家**最高频独立痛点之一**，"the game is rigged" 在 1–2 星评论里仅次于 ads 类抱怨。  
   与 Pay-to-win 的差异：P2W 是**商业化抱怨**，Algorithm Fairness 是**对随机机制的信任崩塌**——两个主题对应到不同的产品决策（数值平衡 vs 客观随机性）。

2. **LiveOps & Events（活动质量）**——Playrix / Peak / Dream Games 系统重运营驱动，活动 bug / 队伍活动崩溃是高频差评源；与"普通 bug"分开后，能让 LiveOps 团队直接看到自己负责的指标。

3. **Ads Quality vs Ads Volume（拆开）**——Volume 由 Marketing / Monetization 决定（广告频次策略），Quality 由 Ad Network / 平台审核决定（广告内容合规）。合并会让 BQ7 recommendation 模糊到无法 actionable。

4. **Updates & New Content（正向更新）**——与 Update Issue 形成镜像对照，可在 BQ4 / BQ6 直接对比"新版本是好评驱动还是差评驱动"。

### 10.4 v1 已合并 / 移除项

- **Customer Support** —— 在 casual game 评论里出现频率 < 1%，合并进 §9.9 Dev Reply 信号，不单独立 theme。
- v1 旧主题中过宽的 `Story / Decoration` 与 `Positive Visuals` 在 v2 仍并列保留；说明 Story / Decoration 比纯 Visual 更预测付费转化（PM-relevant）。

### 10.5 主题分布的预期校验（写进 `theme_eval_v1.md`）

```text
预期 coverage（基于 casual game review benchmark）：
  · Top 5 themes 覆盖率应 ≥ 80%
    （多半是：Crash & Bug、Ads Volume、Difficulty & Progression、
              Fun & Addictive、Pay-to-win）
  · 'Other'（未命中任何主题）≤ 30%
  · 平均每条评论命中 1.5 ~ 2.5 个主题

若 coverage 显著偏离 → 关键词字典需要回校。
```

---

## 11. Dashboard 设计框架

基于上述业务问题和指标体系，Power BI dashboard 可以设计为 5 个页面。

### Page 1：Executive Overview

**目的**：展示整体用户满意度健康情况。  
**核心内容**：Total Reviews · App Count · Bayesian Adjusted Avg Rating · Positive Share · Low-Star Share · **App Satisfaction Health Score** · Top 5 Apps by Health Score · Bottom 5 Apps by Low-Star Risk · 全局 Confidence 警示。

### Page 2：Competitor Benchmarking

**目的**：比较 14 个竞品的满意度表现（同时支持去重 7-App 跨 publisher 视图）。  
**核心内容**：App Health Score Ranking · App Low-Star Share Ranking · App Bayesian Avg Rating Ranking · Review Volume vs Rating Scatter · Category Filter（match-3 / blast / IP / decoration）· **Low-Star Dev Reply Rate Ranking**。

### Page 3：Pain Point Drivers

**目的**：识别用户低分评论背后的核心原因。  
**核心内容**：Low-Star Theme Ranking · **Helpfulness-Weighted Theme Ranking**（社区共识版）· Theme Avg Rating · Rating Gap by Theme · App × Theme Heatmap · Critical Complaint Share · **Low-Star Theme Dev Reply Rate**（运营覆盖图）。

### Page 4：Trend & Event Signals

**目的**：观察用户满意度变化趋势和版本 / 事件风险信号。  
**核心内容**：Weekly Avg Rating Trend (with 8-week OLS slope) · Weekly Low-Star Share Trend · Review Volume Spike with annotations · **Version-to-Version Comparison Table**（含 Δ Avg, Δ Low-Star, Δ Dev Reply Rate, Δ Reply SLA）· Causal Disclaimer Banner · App Selector。

### Page 5：Product Recommendation

**目的**：将数据分析转化为产品优化建议。  
**核心内容**：Impact × Frequency Matrix · Priority Score Ranking · P0 / P1 / P2 / P3 Recommendation Table · Suggested UX / Product Actions · ReplyAttention Tag（标识"运营盲区"主题）· Limitations and Next Steps。

---

## 12. BQ ↔ Primary Metric 对应表

每个业务问题只挂一个 Primary Metric，其他作为 Secondary 或 Guardrail。这是面试中"用一个数字回答这个问题"的抓手。

| BQ  | 业务问题             | **Primary Metric**                                              | Secondary Metric                                                                | Guardrail                                                | Owner                            |
|-----|--------------------|----------------------------------------------------------------|--------------------------------------------------------------------------------|---------------------------------------------------------|----------------------------------|
| BQ1 | 整体满意度健康       | **App Satisfaction Health Score**                                | Bayesian Adjusted Avg, Positive Share                                            | Confidence ≥ 0.5                                         | Product Lead                       |
| BQ2 | 竞品对比             | **Health Score Rank（去重 7-App set）**                          | Low-Star Share Rank, Volume vs Rating, Low-Star Reply Rate Rank                  | Sample Size Flag                                          | Competitive Intel / PM             |
| BQ3 | 低分痛点             | **Low-Star Theme Share**                                          | Theme Avg Rating, Theme Rating Gap, **Helpfulness-Weighted Share**, **Low-Star Theme Dev Reply Rate** | Theme Coverage ≥ 60%, English Share ≥ 70%             | UX Lead                           |
| BQ4 | 高分驱动             | **Positive Theme Share**                                          | Theme Avg Rating among 4–5★, **Helpfulness-Weighted Positive Share**             | Theme Coverage                                           | Marketing / Brand                 |
| BQ5 | 趋势                | **Weekly Avg Rating Slope (8-week OLS)**                           | Weekly Low-Star Share, Weekly Volume                                              | Weekly n ≥ 30                                            | LiveOps / PM                      |
| BQ6 | 版本对比             | **Window Δ Avg Rating（adjacent app_version_major）**             | Window Δ Low-Star Share, **Δ Dev Reply Rate**, **Δ Reply SLA Days**, Top Theme Rank Shift | Version Coverage ≥ 50%, n_per_version ≥ 50               | Release Manager                   |
| BQ7 | 优先级               | **Priority Score = Helpfulness-Weighted Frequency × Impact × Severity × ReplyAttention** | Priority Level (P0–P3)                                                            | Theme Coverage, Sample Size                              | PM + UX Lead                      |

---

## 13. Limitations & Honesty

集中陈列本项目所有方法论与数据边界，避免散落在各章造成 reader 混乱。

### 13.1 抓样偏差（Sampling Bias）

`google-play-scraper` 调用 Google Play 公开 web endpoint，按平台默认排序（NEWEST / MOST_RELEVANT）拉取分页结果。所以本项目数据：

1. **不是全量评论**——单 App 历史可能有数百万条，本项目能拉到的是几千到几万条；
2. **不是随机样本**——按"最新"或"最相关"排序本身有偏差；
3. **可能含 Google 反作弊已过滤的版本**——某些垃圾评论 Google 已删除，无法获取。

竞品间对比假设各 App 抓样偏差结构相似（同一接口 / 同一时间窗）。所有满意度结论**不外推**到 App 全部历史评论或全部用户群体。

### 13.2 主题方法论误差（Theme Methodology Error）

v1 主题打标为 **rule-based keyword matching**：

- **召回限制**：未在词典中收录的同义表达将被漏掉（goes into `is_theme_other`）。
- **精确度限制**：尽管使用 `exclude_keywords`，仍可能存在反讽 / 双关误判（"love how it crashes every 5 mins"）。
- **缓解措施**：§9.8.4 评估集 + Coverage Guardrail（Theme Coverage < 60% 时 BQ3 / BQ4 / BQ7 标警告）。
- **升级路径**：v2 用 zero-shot LLM 兜底未命中评论；v3 基于评估集 fine-tune 多标签分类器。

### 13.3 样本量差异（Sample Size Variance）

竞品池中各 App 抓到的评论数差异可能 1–2 个数量级（旗舰 vs 长尾产品）。

- **柔性约束**：Health Score Level 维度采用 Bayesian Adjusted Avg（k = 200）做收缩。
- **刚性约束**：Confidence = min(1, n / 200) 作为 Health Score 乘数 cap；Confidence < 0.5（n < 100）的 App 在 dashboard ranking 表中灰掉，单独放在 "Low-Confidence Apps" 区块。
- 主题分析与版本对比也分别有最低样本量 Guardrail（详见 §9.4 / §9.6）。

### 13.4 版本号字段覆盖（Version Coverage）

`google-play-scraper` 返回的 `reviewCreatedVersion` 字段并非每条评论都有，覆盖率因 App 与抓样时间不同。BQ6 输出前必须先看 `Version Coverage Rate`：

- ≥ 50% → 输出 BQ6 完整结论；
- < 50% → BQ6 标 "Insufficient Version Coverage"，仅输出方向性观察；
- **退路（备用）**：当版本号无法支撑分析时，可改用 review volume spike date 作为 event window 进行方向性观察（与版本对比同样语义，仅 event 锚点不同）。该兜底不写入主指标，仅在异常场景下使用。

### 13.5 因果性（Causality）

- BQ5 的 trend slope、BQ6 的 version delta、BQ7 的 ReplyAttention 都是 **descriptive** 信号，**不能**用来声称"版本 / 运营动作导致评分变化"。
- 同期 LiveOps 活动、季节性、营销推送、平台算法变化、抓样窗口偏差都可能贡献观察到的 delta。
- **如需因果**：须配合 A/B 实验或 RDD（详见 v2_AB 设计文档）。

### 13.6 内部数据缺失

本项目不接触客户内部数据：留存率、转化率、付费率、DAU / MAU、活动参与率均无法验证。所有满意度指标仅来自外部公开评论，是 **proxy signal**，不能替代客户公司真实业务 KPI。

---

## 14. 项目最终定位

本项目最终可以被定位为一个面向 DA / BA / Product Analyst 的用户评论分析项目，而不仅仅是一个数据采集或 EDA 项目。具体表现：

- **数据层**：完成 Google Play 评论采集（含 `app_version` 用于 BQ6）、三层清洗（P0 / P1 / P2）、SQLite 仓库与核验报告；
- **分析层**：7 个核心 BQ + OSM 框架 + 正交化 Health Score + 主题分类 + 优先级矩阵；
- **业务交付**：5 页 Power BI dashboard、双语 EDA 结论 deck、产品 backlog 优先级表（Page 5 衍生 `recommendations.md`）；
- **方法论严谨度**：每个 Primary Metric 配 Guardrail；主题方法论附评估集；BQ6 配因果免责声明；§13 集中 Limitations。

> 项目的差异化优势：**敢于把限制写进文档**（§13）、**Health Score 用贝叶斯收缩 + sensitivity analysis** 而不是凭直觉拍权重、**主题方法论附 P/R/F1 评估集**——这三点把项目从"作品集合格"拉到"BA 标准成品"。

---

## 附录 A：Health Score Sensitivity Analysis（占位）

完成数据跑数后，在此填入：

- 5 套候选权重对应的 14 App ranking
- 5 套排名两两 Spearman 相关矩阵
- 结论：相关均 ≥ 0.85 ⇒ Health Score 排名对权重不敏感

## 附录 B：Bayesian k 与 Confidence threshold 选择（占位）

- 不同 k（100 / 200 / 500）对小样本 App 排名的影响
- Confidence 阈值（0.3 / 0.5 / 0.7）的 dashboard 灰名单效果对比
