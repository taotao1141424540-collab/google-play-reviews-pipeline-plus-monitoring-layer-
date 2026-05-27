# Google Play Review Analytics for Mobile Game User Satisfaction

## 面向休闲手游用户满意度优化的 Google Play 评论分析项目

---

# Part I. Main Design Document

## 主文档

---

## 1. Project Overview 项目概述

本项目以一家模拟的中型 **free-to-play 移动休闲游戏公司** 作为业务场景。该公司主要在 Google Play 平台发行和运营休闲益智类手游，产品类型覆盖 match-3、blast puzzle、story decoration、IP-themed puzzle 和 light casual puzzle 等细分品类。

该公司依赖 Google Play 平台进行用户获取，并通过用户评分、评论质量、平台口碑和应用商店排名影响潜在用户的下载决策。因此，Google Play 用户评论不仅是产品反馈来源，也是衡量用户感知满意度、识别产品体验问题和分析竞品表现的重要外部数据来源。

本项目的核心目标是：

> 通过分析 14 个同类休闲手游在 Google Play 上的公开用户评论，帮助目标公司理解用户满意度趋势、识别核心体验痛点、对比竞品表现，并为 UX 和 Product 团队提供数据驱动的优化建议。

由于本项目无法获取客户内部数据，例如留存率、转化率、付费率、DAU 或用户行为路径，因此项目不会直接声称对真实业务增长产生影响，而是使用 Google Play 评分和评论作为外部 proxy signals，评估用户感知满意度和产品体验摩擦。

---

## 2. Business Context 业务背景

移动休闲游戏市场竞争激烈，同类产品之间在玩法、视觉设计、关卡机制、广告体验、商业化策略和 LiveOps 活动上高度相似。对于一家中型游戏公司而言，Google Play 评论可以帮助产品团队回答以下问题：

1. 用户为什么给低分？
2. 哪些体验问题最影响满意度？
3. 哪些竞品 App 的用户评价更好？
4. 高分用户主要认可哪些产品体验？
5. 用户满意度是否在改善或恶化？
6. 哪些问题应该优先进入产品优化 backlog？

但是，Google Play 评论本身是非结构化文本。如果产品团队仅靠人工查看少量评论，很难系统性地识别长期趋势、核心痛点和竞品差异。因此，本项目通过数据分析方法，将大量用户评论转化为结构化指标、可视化 dashboard 和可执行的产品优化建议。

---

## 3. Business Model 目标公司业务模式

目标公司采用典型的 **free-to-play mobile game business model**。用户可以免费下载游戏，并通过关卡推进、任务完成、剧情解锁、装饰、收集或社交互动持续参与游戏。公司主要通过内购、广告和 LiveOps 活动实现收入增长。

| 业务模块       | 说明                                              |
| ---------- | ----------------------------------------------- |
| 用户获取       | 通过 Google Play 自然搜索、应用商店推荐、广告投放和平台排名获取新用户       |
| 免费下载       | 用户可以免费安装并开始游戏，降低进入门槛                            |
| 核心玩法       | 通过 match-3、blast、装修、剧情、IP 收集或轻度 puzzle 推动用户持续游玩 |
| 内购收入       | 用户购买金币、体力、道具、booster、礼包或关卡辅助资源                  |
| 广告收入       | 通过激励视频广告、插屏广告或奖励广告实现变现                          |
| LiveOps 活动 | 通过限时活动、排行榜、团队任务和节日活动提高活跃度                       |
| 平台口碑       | Google Play 评分和评论影响新用户信任、下载转化和长期品牌形象            |

该类产品的增长逻辑可以概括为：

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

本项目无法直接观察留存、转化和付费，因此重点分析最后一环：**用户评分和评论如何反映产品体验健康度。**

---

## 4. Data Scope and Data Honesty 数据范围与边界

评论数据通过 `google-play-scraper` 从 Google Play 公开页面获取。该数据具有以下特点：

1. 数据是公开评论子集，不是 App 全量历史评论；
2. 数据不是严格随机样本，可能受到 Google Play 排序方式影响；
3. 竞品间对比假设各 App 的抓样方式一致，因此偏差结构相对接近；
4. 所有满意度分析仅基于抓取到的评论样本；
5. 本项目不外推到 App 全部用户群体；
6. 本项目不使用内部业务数据，因此不直接分析真实留存、转化、付费或 DAU。

因此，本项目中的指标应被理解为：

> Review-based proxy signals for perceived user satisfaction and UX friction.

中文：

> 基于公开评论数据构建的用户感知满意度和体验摩擦 proxy 指标。

这一部分必须保留，因为它能体现你对数据边界和业务解释边界的理解。

---

## 5. Competitor Pool Design 竞品池设计

为了避免单一发行商样本占比过高导致竞品分析结果被拖偏，本项目采用平衡竞品池设计：

> **7 家 publisher × 每家 2 款游戏 = 14 个 App**

这种设计可以减少 publisher-level sampling bias，同时保留同公司双产品对比和跨公司 benchmark 两种分析口径。

| 序号 | App                     | Publisher     | 子类型                          | 选择理由                       |
| -: | ----------------------- | ------------- | ---------------------------- | -------------------------- |
|  1 | Royal Match             | Dream Games   | Match-3                      | 当前 match-3 头部 benchmark    |
|  2 | Royal Kingdom           | Dream Games   | Match-3                      | 同公司新作，可观察系列化策略             |
|  3 | Candy Crush Saga        | King          | Match-3                      | 经典 match-3 标杆              |
|  4 | Candy Crush Soda Saga   | King          | Match-3                      | 同系列延展                      |
|  5 | Gardenscapes            | Playrix       | Match-3 + Decoration         | 三消 + 剧情 + 装修代表             |
|  6 | Homescapes              | Playrix       | Match-3 + Decoration         | 家装剧情类代表                    |
|  7 | Toon Blast              | Peak Games    | Blast Puzzle                 | 点击消除标杆                     |
|  8 | Toy Blast               | Peak Games    | Blast Puzzle                 | 同公司成熟 blast puzzle 产品      |
|  9 | Cookie Jam              | Jam City      | Match-3                      | 老牌 match-3，长尾运营典型          |
| 10 | Disney Emoji Blitz      | Jam City      | Match-3 + IP                 | IP 题材 puzzle，可观察品牌/IP 体验差异 |
| 11 | Lily's Garden           | Tactile Games | Match-3 + Story + Garden     | 剧情、园艺、三消结合                 |
| 12 | Penny & Flo             | Tactile Games | Match-3 + Story + Decoration | 同公司装修剧情类对照                 |
| 13 | Angry Birds Dream Blast | Rovio         | Blast + IP                   | Angry Birds IP + blast 玩法  |
| 14 | Angry Birds Friends     | Rovio         | Slingshot Puzzle + IP        | 弹射 puzzle + 社交竞赛           |

### 5.1 分析口径

本项目支持**三种**竞品分析口径：

| 分析口径                      | 用途                             |
| ------------------------- | ------------------------------ |
| App-level Benchmark       | 比较 14 个 App 的满意度健康度、低分风险、主题痛点  |
| Publisher-level Benchmark | 每家 publisher 两个产品，比较公司层面的体验模式  |
| Flagship 7-App Benchmark  | 每家 publisher 选一个旗舰 App，用于跨公司排名 |

这样可以同时回答：

1. 哪一款游戏用户满意度最高？
2. 哪家公司整体产品体验更稳定？
3. 同一 publisher 的新旧产品是否存在体验差异？
4. 不同子类型游戏的用户痛点是否不同？

---

## 6. Core Business Questions 核心业务问题

为了避免项目过度复杂，主文档保留 5 个核心业务问题。原先更高级的趋势斜率、版本窗口和 developer reply 分析放入 Appendix 或 Future Work。

### BQ1：整体用户满意度健康情况如何？

通过 App Satisfaction Health Score、Adjusted Average Rating、Positive Share 和 Low-Star Share，评估目标 App 和竞品 App 的整体用户满意度健康水平。

### BQ2：哪些 App / Publisher 表现最好？哪些风险最高？

通过 Health Score Rank、Low-Star Share Rank、Review Volume vs Rating Scatter，对 14 个竞品和 7 家 publisher 进行 benchmark，识别表现优秀的产品和存在明显用户不满风险的产品。

### BQ3：用户低分评论主要在抱怨什么？

对 1–2 星评论进行主题分类，识别用户主要不满来源，例如 crash、ads、pay-to-win、difficulty、performance、update issue、account issue 等。

### BQ4：高分评论主要认可什么？

对 4–5 星评论进行主题分析，识别正向体验驱动因素，例如 fun & addictive、visuals、story / decoration、social features、updates & new content 等。

### BQ5：产品团队应该优先优化哪些问题？

基于 Frequency、Impact 和 Severity 构建 Priority Score，将用户评论转化为 P0 / P1 / P2 / P3 产品优化建议。

> **注（主线范围）**：满意度**趋势**（周期变化、斜率等）与**版本 / 事件窗口前后对比**不作为第一版主线的独立核心 BQ；实现思路与指标定义见 **Appendix C**（Momentum / Trend）与 **Appendix G**（Version / Event Window）。开发者回复类辅助信号见 **Appendix F**。第一版主线以横截面健康度、主题洞察与优先级为主。

---

## 7. North Star-inspired Metric Framework 指标体系设计

本项目采用 **North Star-inspired review satisfaction framework**。由于缺少内部留存、转化、付费和 DAU 数据，项目不定义客户公司的真实北极星指标，而是构建一个基于公开评论数据的外部满意度 proxy metric：

> **App Satisfaction Health Score**
> App 用户满意度健康分

该指标用于回答：

> 从 Google Play 用户评论看，一个 App 的用户体验健康程度如何？

---

## 8. App Satisfaction Health Score 简化版

主文档中使用简化表达，具体公式和稳健性检查放入 Appendix。

App Satisfaction Health Score 由三个核心维度和一个样本可信度修正组成：

| 维度           | 含义        | 代表指标                          |
| ------------ | --------- | ----------------------------- |
| Level        | 用户整体满意度水平 | Adjusted Average Rating       |
| Polarization | 极端不满风险    | 1 - Low-Star Share            |
| Momentum     | 近期趋势信号    | Rating Trend / Period Change  |
| Confidence   | 样本可信度     | Review Count-based Confidence |

书面表达建议：

> App Satisfaction Health Score is a review-based proxy metric designed to compare perceived user satisfaction across comparable mobile games. It combines adjusted rating level, low-star risk, and recent rating momentum, with a sample-size confidence adjustment to reduce the risk of over-ranking apps with limited review volume.

中文：

> App Satisfaction Health Score 是一个基于公开评论数据的用户满意度 proxy 指标，用于比较同类手游之间的感知满意度。该指标综合考虑调整后的评分水平、低分评论风险和近期评分趋势，并引入样本量可信度修正，避免评论量过少的 App 因偶然高分而被错误排到前列。

**详细计算公式、权重与 Confidence 修正、Momentum 的两种实现方式及稳健性检查，分别见 Appendix A、B、C、D。**

---

## 9. Objective–Signal–Metric Framework

### Objective 1：提升用户感知满意度

| Objective | Signal      | Metric                       |
| --------- | ----------- | ---------------------------- |
| 提升用户感知满意度 | 用户给出更高评分    | Adjusted Average Rating      |
| 提升用户感知满意度 | 更多用户给 4–5 星 | Positive Share               |
| 提升用户感知满意度 | 更少用户给 1–2 星 | Low-Star Share               |
| 提升用户感知满意度 | 评分结构更健康     | Rating Distribution          |
| 提升用户感知满意度 | 近期趋势改善      | Rating Trend / Period Change |

### Objective 2：降低关键体验痛点

| Objective | Signal                  | Metric                     |
| --------- | ----------------------- | -------------------------- |
| 降低关键体验痛点  | crash / bug 相关评论减少      | Crash & Bug Theme Share    |
| 降低关键体验痛点  | ads 相关负面评论减少            | Ads Theme Share            |
| 降低关键体验痛点  | payment / purchase 问题减少 | Purchase Issue Theme Share |
| 降低关键体验痛点  | 低分评论中核心痛点下降             | Low-Star Theme Share       |
| 降低关键体验痛点  | 严重主题的评分提升               | Theme Avg Rating           |

### Objective 3：识别竞品优势和弱点

| Objective | Signal                  | Metric                         |
| --------- | ----------------------- | ------------------------------ |
| 识别竞品优势    | 某些 App 高分率更高            | Positive Share by App          |
| 识别竞品优势    | 高分 App 正向主题更集中          | Positive Theme Share           |
| 识别竞品弱点    | 某些 App 低分率更高            | Low-Star Share by App          |
| 识别竞品弱点    | 某些 App 在广告、付费、性能上负面反馈更多 | App Theme Matrix               |
| 识别品类模式    | 不同子类型存在共同痛点             | Category-level Theme Benchmark |

### Objective 4：支持产品优化优先级

| Objective | Signal             | Metric               |
| --------- | ------------------ | -------------------- |
| 支持产品优化优先级 | 高频问题应优先处理          | Theme Frequency      |
| 支持产品优化优先级 | 对评分伤害大的问题应优先处理     | Theme Rating Gap     |
| 支持产品优化优先级 | 低分占比高的问题应优先处理      | Theme Low-Star Share |
| 支持产品优化优先级 | 阻断型问题优先级更高         | Critical Theme Flag  |
| 支持产品优化优先级 | 综合评分形成 backlog 优先级 | Priority Score       |

---

## 10. Metric Dictionary 指标体系

### 10.1 数据范围指标

| 指标                   | 公式                              | 用途        | Dashboard 展示 |
| -------------------- | ------------------------------- | --------- | ------------ |
| Total Reviews        | COUNT(review_id)                | 衡量数据规模    | KPI Card     |
| App Count            | COUNTD(app_id)                  | 衡量竞品覆盖数量  | KPI Card     |
| Date Range           | MIN(date) 到 MAX(date)           | 展示分析周期    | Text / Card  |
| Reviews per App      | COUNT(review_id) by app         | 判断样本是否均衡  | Bar Chart    |
| English Review Share | English reviews / total reviews | 判断文本分析可用性 | KPI / Donut  |

### 10.2 满意度指标

| 指标                      | 公式                               | 用途        | Dashboard 展示   |
| ----------------------- | -------------------------------- | --------- | -------------- |
| Average Rating          | AVG(score)                       | 原始平均评分    | KPI / Bar      |
| Adjusted Average Rating | 小样本修正后的平均评分                      | 降低小样本评分失真 | KPI / Bar      |
| Positive Share          | COUNT(score ≥ 4) / total reviews | 满意用户占比    | KPI / Bar      |
| Low-Star Share          | COUNT(score ≤ 2) / total reviews | 不满风险      | KPI / Bar      |
| Rating Distribution     | COUNT by score / total reviews   | 评分结构      | Stacked Bar    |
| Health Score            | 综合满意度 proxy                      | App 健康度排名 | Ranking / Card |
| Confidence              | 基于评论数的样本可信度                      | 标注低样本 App | KPI / Flag     |

### 10.3 主题分析指标

| 指标                   | 公式                                                 | 用途       | Dashboard 展示  |
| -------------------- | -------------------------------------------------- | -------- | ------------- |
| Theme Count          | COUNT(review_id) by theme                          | 痛点规模     | Bar           |
| Theme Share          | Theme count / total reviews                        | 痛点占比     | Bar / Treemap |
| Theme Avg Rating     | AVG(score) by theme                                | 主题满意度水平  | Table         |
| Theme Low-Star Share | Low-star reviews in theme / theme reviews          | 主题负面程度   | Table         |
| Low-Star Theme Share | Low-star reviews in theme / total low-star reviews | 低分主要原因   | Bar           |
| Rating Gap           | Overall Avg Rating - Theme Avg Rating              | 主题对评分的伤害 | Matrix        |
| Theme Coverage Rate  | reviews with at least one theme / total reviews    | 方法论质量检查  | KPI           |

### 10.4 竞品对比指标

| 指标                      | 公式                           | 用途          | Dashboard 展示     |
| ----------------------- | ---------------------------- | ----------- | ---------------- |
| App Health Score Rank   | Rank by Health Score         | 综合健康度排名     | Ranking Table    |
| App Low-Star Risk Rank  | Rank by Low-Star Share       | 高风险 App 排名  | Ranking Table    |
| App Positive Share Rank | Rank by Positive Share       | 正向体验表现      | Bar              |
| App Theme Matrix        | App × Theme Share            | 对比痛点结构      | Heatmap / Matrix |
| Publisher Benchmark     | 聚合到 publisher 层面             | 比较公司级体验模式   | Bar / Table      |
| Review Volume vs Rating | X = review count, Y = rating | 找高声量高风险 App | Scatter Plot     |

### 10.5 优先级指标

主文档建议使用简化版：

```text
Priority Score = Frequency × Impact × Severity
```

| 维度        | 定义                                    | 业务含义   |
| --------- | ------------------------------------- | ------ |
| Frequency | 某主题出现频率                               | 问题影响范围 |
| Impact    | Overall Avg Rating - Theme Avg Rating | 对评分的伤害 |
| Severity  | Theme Low-Star Share                  | 负面严重程度 |

| Priority | 判断标准              | 示例                                      |
| -------- | ----------------- | --------------------------------------- |
| P0       | 高频 + 评分伤害大 + 阻断使用 | crash、login、payment                     |
| P1       | 高频 + 明显影响体验       | ads、performance、update issue            |
| P2       | 中频 + 可优化体验        | UI、onboarding、difficulty                |
| P3       | 低频或偏偏好类           | visual preference、minor feature request |

Developer reply coverage 和 thumbs_up 加权可以作为辅助信号，但不进入主公式。

---

## 11. Theme Taxonomy 主题分类体系

本项目采用 rule-based multi-label theme tagging，将每条评论映射到一个或多个产品/体验主题。第一版使用关键词规则，而不是复杂 NLP 模型，原因是规则更透明、可重复、容易解释，也更适合 DA/BA 项目展示。

### 11.1 Negative Themes

| 一级类别         | 二级主题                     | 关键词示例                                          | 业务含义    |
| ------------ | ------------------------ | ---------------------------------------------- | ------- |
| Stability    | Crash & Bug              | crash, bug, glitch, freeze, black screen       | 崩溃 / 闪退 |
| Performance  | Loading & Performance    | slow, lag, loading, stuck                      | 加载与性能   |
| Monetization | Ads Volume               | too many ads, forced ads, pop-up ads            | 广告频率过高  |
| Monetization | Ads Quality              | inappropriate ads, scam ads, misleading ads    | 广告质量问题  |
| Monetization | Pay-to-win / Greedy      | pay to win, money grab, greedy, expensive      | 付费公平感   |
| Monetization | Purchase Issue           | refund, charge, payment failed, didn't receive | 交易问题    |
| Game Design  | Difficulty & Progression | too hard, impossible level, stuck, lives       | 难度与卡点   |
| Game Design  | Algorithm Fairness       | rigged, scripted, manipulated, set up to fail  | 算法公平感   |
| Game Design  | Rewards & Energy         | not enough rewards, energy, coins, boosters    | 激励与资源机制 |
| Operations   | Update Issue             | after update, latest update, new version broke | 版本回归    |
| Operations   | LiveOps & Events         | event bug, tournament glitch, team event       | 活动质量    |
| Account      | Account & Login          | login, account, lost progress, sync failed     | 账号与进度   |
| UX           | UI / Navigation          | confusing menu, tutorial unclear, hard to find | 界面与引导   |

### 11.2 Positive Themes

| 一级类别     | 二级主题                  | 关键词示例                                       | 业务含义   |
| -------- | --------------------- | ------------------------------------------- | ------ |
| Positive | Fun & Addictive       | fun, addictive, love it, relaxing           | 核心玩法乐趣 |
| Positive | Visual & Graphics     | beautiful, cute, graphics, design           | 视觉体验   |
| Positive | Story & Decoration    | story, decorate, garden, mansion, room      | 剧情与装饰  |
| Positive | Social & Team         | team, friends, leaderboard, compete         | 社交体验   |
| Positive | Updates & New Content | new levels, fresh content, frequent updates | 正向更新体验 |

### 11.3 主题打标方法

1. 对评论文本进行 lowercase、去标点、去噪声处理；
2. 使用 `config/themes.yml` 保存每个主题的关键词和排除词；
3. 每条评论可以命中多个主题；
4. 输出 `reviews_with_themes.csv`；
5. 抽样检查误判和漏判；
6. 根据检查结果更新关键词字典。

---

## 12. Dashboard Design Dashboard 设计

Power BI dashboard 设计为 4 页，第一版不建议做太多页面。

### Page 1：Executive Overview

目的：让业务方快速了解整体用户满意度健康情况。

核心组件：

* Total Reviews
* App Count
* Average / Adjusted Rating
* Positive Share
* Low-Star Share
* App Satisfaction Health Score
* Top 5 Apps by Health Score
* Bottom 5 Apps by Low-Star Risk
* Confidence / Sample Size Flag

### Page 2：Competitor Benchmarking

目的：比较 14 个竞品和 7 家 publisher 的满意度表现。

核心组件：

* App Health Score Ranking
* App Low-Star Share Ranking
* Publisher-level Average Rating
* Review Volume vs Rating Scatter
* Category Filter：match-3 / blast / IP / decoration
* App / Publisher / Category Slicers

### Page 3：Pain Point and Positive Driver Analysis

目的：识别低分评论痛点和高分评论驱动因素。

核心组件：

* Low-Star Theme Ranking
* Positive Theme Ranking
* Theme Avg Rating
* Rating Gap by Theme
* App × Theme Heatmap
* Critical Complaint Share

### Page 4：Product Recommendation

目的：将分析结果转化为产品优化优先级。

核心组件：

* Impact × Frequency Matrix
* Priority Score Ranking
* P0 / P1 / P2 / P3 Recommendation Table
* Suggested UX / Product Actions
* Limitations and Next Steps

---

## 13. Key Limitations 主要限制

本项目的主要限制包括：

1. **Sampling Bias**：Google Play 评论数据不是全量，也不是随机样本；
2. **Public Data Only**：项目不包含内部留存、转化、付费或 DAU 数据；
3. **Proxy Metrics**：所有满意度指标都是 review-based proxy，不代表真实业务 KPI；
4. **Theme Tagging Error**：关键词分类可能存在误判、漏判和反讽识别不足；
5. **No Causal Claim**：趋势和差异只能作为方向性信号，不能证明产品动作导致评分变化；
6. **Publisher and Category Differences**：不同子类型游戏的用户预期可能不同，因此跨品类对比需要谨慎解释。

---

## 14. Final Deliverables 最终交付

| 层级  | 交付物                                                                           |
| --- | ----------------------------------------------------------------------------- |
| 数据层 | cleaned review dataset, review-level table, app summary table                 |
| 分析层 | metric dictionary, theme taxonomy, app benchmark tables, theme summary tables |
| 看板层 | 4-page Power BI dashboard                                                     |
| 业务层 | user satisfaction insight report, product recommendation matrix               |
| 求职层 | resume bullets, portfolio README, interview story, dashboard screenshots      |

---

# Part II. Appendix / Methodology Notes

## 方法论附录

这一部分保留高级方法，但不作为主线。作品集中可以放在主文档之后，面试时只有在被追问时才讲。

---

## Appendix A. Health Score Formula

App Satisfaction Health Score can be calculated as:

```text
Health Score
= (0.40 × Level + 0.35 × Polarization + 0.25 × Momentum) × Confidence
```

| Component    | Definition             | Formula                       |
| ------------ | ---------------------- | ----------------------------- |
| Level        | Adjusted rating level  | Bayesian Adjusted Average / 5 |
| Polarization | Low-star risk control  | 1 - Low-Star Share            |
| Momentum     | Recent rating trend    | rating trend score            |
| Confidence   | Sample-size confidence | min(1, n_reviews / 200)       |

---

## Appendix B. Bayesian Adjusted Average

为降低小样本评分偶然偏高的问题，Adjusted Average Rating 可以采用贝叶斯收缩思想：

```text
BayesianAdjustedAvg
= (n × app_avg + k × global_avg) / (n + k)
```

其中：

| 参数         | 含义                  |
| ---------- | ------------------- |
| n          | 该 App 的评论数          |
| app_avg    | 该 App 原始平均评分        |
| global_avg | 全部 14 个 App 的整体平均评分 |
| k          | 平滑参数，可先设为 200       |

该方法的作用是：评论量较少的 App 会被适度拉回整体均值，避免小样本 App 因偶然高分被错误排到前列。

---

## Appendix C. Momentum / Trend Measurement

如果每周样本量足够，可以使用 8-week rating slope 衡量满意度趋势：

```text
Momentum = rating trend over the latest 8 weeks
```

如果每周样本量不足，则使用更简单的替代指标：

```text
Rating Change = Current Period Avg Rating - Previous Period Avg Rating
Low-Star Change = Current Period Low-Star Share - Previous Period Low-Star Share
```

这样可以避免为了追求复杂方法而牺牲可解释性和稳定性。

---

## Appendix D. Robustness Check / Sensitivity Analysis

Health Score 的权重可以作为稳健性检查进行测试。项目落地后，可以尝试不同权重组合，并观察 App 排名是否发生大幅变化。

示例权重组合：

| Scenario       | Level | Polarization | Momentum |
| -------------- | ----: | -----------: | -------: |
| Base Case      |  0.40 |         0.35 |     0.25 |
| Rating-heavy   |  0.50 |         0.30 |     0.20 |
| Risk-heavy     |  0.30 |         0.45 |     0.25 |
| Balanced       |  0.33 |         0.34 |     0.33 |
| Momentum-light |  0.45 |         0.35 |     0.20 |

建议写法：

> As a robustness check, alternative Health Score weights can be tested to examine whether app rankings remain stable.

不要在数据未跑出前承诺 Spearman 相关一定达到某个值。

---

## Appendix E. Theme Tagging Methodology

第一版采用 rule-based multi-label keyword matching。

### E.1 选择原因

| 方法                          | 优点                          | 局限            |
| --------------------------- | --------------------------- | ------------- |
| Rule-based keyword matching | 可解释、可重复、低成本、适合 dashboard 展示 | 召回有限，可能漏掉同义表达 |
| Zero-shot LLM               | 召回较强，能处理复杂表达                | 成本高、黑盒、不完全可复现 |
| Topic modeling              | 可用于探索新主题                    | 不一定能直接映射业务问题  |

第一版选择 rule-based 方法，因为它更符合 DA/BA 项目对可解释性的要求。

### E.2 Validation Sample

建议不要写「两人交叉标注 + Cohen's κ」，除非你真的有第二个标注人。

替代写法：

> A validation sample of 200 reviews will be manually reviewed to identify false positives, false negatives, missing keywords, and common misclassification cases.

中文：

> 项目将人工抽查 200 条评论样本，识别主题分类中的误判、漏判、关键词缺口和常见失败案例。

### E.3 Quality Checks

| 检查项                     | 用途             |
| ----------------------- | -------------- |
| Theme Coverage Rate     | 看有多少评论至少命中一个主题 |
| Other / Unmatched Share | 看未分类评论是否过多     |
| Multi-label Rate        | 看每条评论平均命中几个主题  |
| False Positive Review   | 检查误判           |
| False Negative Review   | 检查漏判           |

---

## Appendix F. Optional Developer Reply Signal

Developer reply 可以作为运营响应信号，但不进入主线 Health Score 和 Priority Score。

可选指标包括：

| 指标                      | 定义                                          | 用途       |
| ----------------------- | ------------------------------------------- | -------- |
| Dev Reply Rate          | replied reviews / total reviews             | 整体运营响应   |
| Low-Star Dev Reply Rate | replied low-star reviews / low-star reviews | 是否优先处理差评 |
| Reply SLA Median Days   | median(reply date - review date)            | 回复时效     |
| Reply SLA P90 Days      | p90(reply date - review date)               | 长尾响应能力   |

建议定位：

> Developer reply metrics are used as optional operational response signals, not as core user satisfaction metrics.

中文：

> 开发者回复指标作为运营响应辅助信号，不作为核心用户满意度指标。

---

## Appendix G. Optional Version / Event Window Analysis

如果 `reviewCreatedVersion` 字段覆盖率足够，可以做版本窗口分析。

最低条件：

| 条件                    | 建议阈值  |
| --------------------- | ----- |
| Version Coverage Rate | ≥ 50% |
| Reviews per version   | ≥ 50  |
| Theme Coverage        | ≥ 60% |

可分析指标：

| 指标                         | 说明          |
| -------------------------- | ----------- |
| Per-version Avg Rating     | 每个主要版本的平均评分 |
| Per-version Low-Star Share | 每个主要版本的低分率  |
| Window Δ Avg Rating        | 相邻版本平均评分差异  |
| Window Δ Low-Star Share    | 相邻版本低分率差异   |
| Theme Rank Shift           | 更新前后主题排名变化  |

必须保留免责声明：

> This analysis is descriptive and does not claim that the version update caused the observed rating or theme changes.

中文：

> 该分析仅为描述性观察，不声称版本更新导致评分或主题变化。

---

# Part III. Future Work / Phase 2 Roadmap

## 后续扩展方向

这一部分放暂时不做、但未来可以拓展的内容。这样不会让主文档显得太满，也能体现项目有延展性。

---

## 1. LLM-assisted Theme Tagging

第一版使用关键词规则进行主题分类。未来可以引入 LLM 辅助：

1. 对未命中主题的评论进行二次分类；
2. 发现新的用户痛点主题；
3. 生成更细粒度的 complaint taxonomy；
4. 对 sarcasm、隐含抱怨和复杂表达进行识别。

建议表述：

> Future work could use LLM-assisted classification to improve theme recall for unmatched reviews, while keeping rule-based tags as the explainable baseline.

---

## 2. App Store Data Expansion

本项目只分析 Google Play 评论。未来可以扩展到 Apple App Store：

1. 对比 Android 与 iOS 用户反馈差异；
2. 判断同一 App 在不同平台的评分差异；
3. 扩大样本来源；
4. 支持更全面的 mobile app VOC analysis。

---

## 3. Internal Product Metrics Integration & Recurring VOC

如果能够获得客户内部数据，可以将 review-based proxy metrics 与真实业务指标结合：

| 内部指标                 | 可回答的问题         |
| -------------------- | -------------- |
| Retention Rate       | 评论满意度是否与留存相关   |
| Conversion Rate      | 平台评分是否影响下载转化   |
| DAU / MAU            | 用户活跃是否与版本反馈相关  |
| In-app Purchase Rate | 付费体验评论是否关联收入   |
| Ad Engagement        | 广告抱怨是否影响广告变现策略 |

在具备稳定内部指标与数据管道的前提下，未来还可以将评论抓取、指标表刷新与看板更新衔接为**定期 VOC 复盘**：例如每周抓取最新评论、自动刷新 metric tables、更新 Power BI、输出 top risk themes，并形成 recurring VOC review workflow。

这样项目可以从外部评论分析升级为完整 Product Analytics 项目。

---

## 4. Causal Analysis / A/B Testing

当前项目只能做描述性分析，不能证明因果关系。未来如果有实验条件，可以设计：

1. A/B testing；
2. feature rollout analysis；
3. regression discontinuity around release date；
4. difference-in-differences；
5. controlled before-after experiment。

适合验证的问题包括：

1. 减少广告频率是否提升评分？
2. 优化登录流程是否减少低分评论？
3. 调整关卡难度是否改善满意度？
4. 新手引导改版是否提高正向评论？

---

## 5. Advanced Developer Response Analysis

如果开发者回复数据稳定，可以进一步研究：

1. 哪些 publisher 更积极回复差评；
2. 回复是否集中在特定主题；
3. 回复时效是否与后续评分趋势相关；
4. 客服/运营响应是否能帮助缓解低分风险。

但这部分建议保持为 Phase 2，不要放入第一版主线。

---

## 6. Advanced Theme Model

未来可以在人工校验样本基础上进一步升级分类方法：

1. zero-shot classification；
2. supervised multi-label classification；
3. embedding clustering；
4. BERTopic / topic modeling；
5. hybrid keyword + LLM approach。

建议不要在第一版写得太偏 ML，以免项目偏离 DA/BA 定位。

---

# Part IV. 从原 v2 到重构版的迁移表

| 原 v2 内容                | 新位置                    | 处理方式                                               |
| ---------------------- | ---------------------- | -------------------------------------------------- |
| 目标公司设定                 | 主文档                    | 保留                                                 |
| 业务模式                   | 主文档                    | 保留                                                 |
| Data Honesty           | 主文档                    | 保留并提前                                              |
| 14 App 竞品池             | 主文档                    | 保留                                                 |
| 7 个 BQ                 | 主文档压缩为 5 个核心 BQ        | 趋势见 Appendix C；版本 / 事件窗见 Appendix G                     |
| OSM 框架                 | 主文档                    | 保留                                                 |
| Health Score 复杂公式      | Appendix               | 主文档只讲 Level / Polarization / Momentum / Confidence |
| Bayesian Adjusted Avg  | Appendix               | 保留公式                                               |
| OLS slope scale        | Appendix               | 主文档只写 rating trend                                 |
| Sensitivity Analysis   | Appendix               | 改成 optional robustness check                       |
| Theme taxonomy         | 主文档                    | 保留                                                 |
| 主题评估 P/R/F1            | Appendix               | 简化成人工抽样检查                                          |
| Cohen's κ              | 删除                     | 除非真的有第二标注人                                         |
| Developer Reply / SLA  | Appendix / Future Work | 降级为 optional                                       |
| ReplyAttention Factor  | 删除主公式                  | 改成辅助标签                                             |
| Version-to-version BQ6 | Appendix / Future Work | 仅在 coverage 足够时做                                   |
| DistilBERT fine-tune   | Future Work            | 不放主线                                               |
| Dashboard 5 页          | 主文档压缩为 4 页             | 更适合第一版落地                                           |
| Limitations            | 主文档                    | 保留                                                 |

---

> **主文档负责「清晰、可落地、能展示」；Appendix 负责「方法论严谨」；Future Work 负责「高级扩展」。**

后续真正落地的时候，你只需要按这个顺序做：

1. 先完成主文档对应的 4 页 Power BI dashboard；
2. 跑出 14 个 App 的核心指标；
3. 做主题分类和低分痛点分析；
4. 输出 P0 / P1 / P2 recommendation；
5. 最后再决定 Appendix 里哪些高级方法真正补上。
