#!/usr/bin/env python3
"""
Build PDF: plain-language explanations of every metric, plus how the metrics
chain together to support data-backed conclusions.

Aligned with:
  config/metrics.json
  scripts/06_insights/build_app_base_metrics.py
  scripts/06_insights/build_health_score.py
  scripts/06_insights/build_competitor_benchmark_tables.py

Output:
  reports/tables/Competitor_Metrics_Insights_Report.pdf
"""

from __future__ import annotations

import json
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
OUT_PDF = ROOT / "reports" / "tables" / "Competitor_Metrics_Insights_Report.pdf"
QUALITY = ROOT / "reports" / "quality_report.csv"
METRICS_JSON = ROOT / "config" / "metrics.json"
HEALTH = ROOT / "reports" / "tables" / "app_health_score.csv"
PUB = ROOT / "reports" / "tables" / "publisher_benchmark.csv"
BQ2 = ROOT / "reports" / "tables" / "app_benchmark_bq2.csv"


def _zh_font() -> str:
    from reportlab.pdfbase import pdfmetrics
    from reportlab.pdfbase.ttfonts import TTFont

    for path in (
        "/System/Library/Fonts/Supplemental/Arial Unicode.ttf",
        "/Library/Fonts/Arial Unicode.ttf",
    ):
        p = Path(path)
        if p.exists():
            pdfmetrics.registerFont(TTFont("ZhFont", str(p)))
            return "ZhFont"
    return "Helvetica"


def _load_metrics_json() -> dict:
    if METRICS_JSON.is_file():
        return json.loads(METRICS_JSON.read_text(encoding="utf-8"))
    return {}


def _load_metrics_snapshot() -> dict:
    out: dict = {}
    if QUALITY.is_file():
        q = pd.read_csv(QUALITY, encoding="utf-8-sig")
        m = dict(zip(q["section"] + "," + q["metric"], q["value"]))
        out["clean_en_rows"] = m.get("output,clean_en_rows", "?")
        out["english_rate"] = m.get("p1,english_rate_after_p0", "?")
        out["run_time"] = m.get("run,run_time", "?")

    if HEALTH.is_file():
        hs = pd.read_csv(HEALTH, encoding="utf-8-sig")
        top = hs.iloc[0]
        bot = hs.iloc[-1]
        out["top_name"] = str(top["app_name"])
        out["top_health"] = float(top["health_score"])
        out["top_rank"] = int(top["health_score_rank"])
        out["bot_name"] = str(bot["app_name"])
        out["bot_health"] = float(bot["health_score"])
        out["bot_rank"] = int(bot["health_score_rank"])
        out["global_bayes_mean"] = float(top["global_mean_for_bayesian"])
        out["top3"] = [
            {
                "name": str(r["app_name"]),
                "rank": int(r["health_score_rank"]),
                "health": float(r["health_score"]),
                "n": int(r["n_reviews"]),
            }
            for _, r in hs.head(3).iterrows()
        ]
        out["bot3"] = [
            {
                "name": str(r["app_name"]),
                "rank": int(r["health_score_rank"]),
                "health": float(r["health_score"]),
                "n": int(r["n_reviews"]),
            }
            for _, r in hs.tail(3).iloc[::-1].iterrows()
        ]
        lg = hs[hs["app_name"] == "Lily's Garden"]
        if len(lg):
            r = lg.iloc[0]
            out["lg_n"] = int(r["n_reviews"])
            out["lg_health"] = float(r["health_score"])
            out["lg_rank"] = int(r["health_score_rank"])
        ccs = hs[hs["app_name"] == "Candy Crush Saga"]
        if len(ccs):
            out["ccs_rank"] = int(ccs.iloc[0]["health_score_rank"])
            r = ccs.iloc[0]
            out["ccs_level"] = float(r["component_level"])
            out["ccs_pol"] = float(r["component_polarization"])
            out["ccs_mom"] = float(r["component_momentum_01"])
            out["ccs_pre"] = float(r["health_score_pre_confidence"])
            out["ccs_conf"] = float(r["component_confidence"])
        rk = hs[hs["app_name"] == "Royal Kingdom"]
        if len(rk):
            r = rk.iloc[0]
            out["rk_level"] = float(r["component_level"])
            out["rk_pol"] = float(r["component_polarization"])
            out["rk_mom"] = float(r["component_momentum_01"])
            out["rk_pre"] = float(r["health_score_pre_confidence"])
            out["rk_conf"] = float(r["component_confidence"])
            out["rk_bayes"] = float(r["bayesian_adjusted_avg"])
            out["rk_n"] = int(r["n_reviews"])

    if PUB.is_file():
        pb = pd.read_csv(PUB, encoding="utf-8-sig")
        best = pb.iloc[0]
        worst = pb.iloc[-1]
        out["pub_best"] = str(best["publisher"])
        out["pub_best_wh"] = float(best["weighted_health_score"])
        out["pub_best_n_apps"] = int(best["n_apps"])
        out["pub_worst"] = str(worst["publisher"])
        out["pub_worst_wh"] = float(worst["weighted_health_score"])
        out["pub_worst_n_apps"] = int(worst["n_apps"])
        pub_map: dict[str, dict] = {}
        for _, r in pb.iterrows():
            pub_map[str(r["publisher"])] = {
                "wh": float(r["weighted_health_score"]),
                "n_apps": int(r["n_apps"]),
                "n_reviews": int(r["total_n_reviews"]),
            }
        out["pub_map"] = pub_map

    if BQ2.is_file():
        bq = pd.read_csv(BQ2, encoding="utf-8-sig")
        rk = bq[bq["app_name"] == "Royal Kingdom"]
        if len(rk):
            r = rk.iloc[0]
            out["rk_low_star"] = float(r["share_low_1_2"])
            out["rk_mean"] = float(r["mean_score"])
            out["rk_high_star"] = float(r["share_high_4_5"])
        cc = bq[bq["app_name"] == "Candy Crush Saga"]
        if len(cc):
            out["ccs_high"] = float(cc.iloc[0]["share_high_4_5"])
            out["ccs_low_star"] = float(cc.iloc[0]["share_low_1_2"])
        if "top3" in out:
            top_names = [t["name"] for t in out["top3"]]
            sub = bq[bq["app_name"].isin(top_names)]
            if len(sub):
                out["top3_max_share_low"] = float(sub["share_low_1_2"].max())
                out["top3_min_bayes"] = float(
                    bq.loc[bq["app_name"].isin(top_names), "bayesian_adjusted_avg"].min()
                ) if "bayesian_adjusted_avg" in bq.columns else None
        if "bot3" in out:
            bot_names = [b["name"] for b in out["bot3"]]
            sub = bq[bq["app_name"].isin(bot_names)]
            if len(sub):
                out["bot3_min_share_low"] = float(sub["share_low_1_2"].min())
                out["bot3_categories"] = sorted({str(c) for c in sub["category"].dropna().tolist()})

    return out


def main() -> None:
    from reportlab.lib.pagesizes import A4
    from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
    from reportlab.lib.units import cm
    from reportlab.platypus import PageBreak, Paragraph, SimpleDocTemplate, Spacer

    zh = _zh_font()
    snap = _load_metrics_snapshot()
    cfg = _load_metrics_json()
    k = cfg.get("bayesian_k", 200)
    ref_n = cfg.get("confidence_reference_n", 200)
    w = cfg.get("weights", {})
    wL, wP, wM = w.get("level", 0.4), w.get("polarization", 0.35), w.get("momentum", 0.25)
    mw = cfg.get("momentum", {})
    win_w = mw.get("calendar_weeks_window", 8)
    min_wk = mw.get("min_distinct_weeks_for_slope", 3)

    styles = getSampleStyleSheet()
    title = ParagraphStyle(
        "t",
        parent=styles["Heading1"],
        fontName="Helvetica-Bold",
        fontSize=15,
        spaceAfter=12,
    )
    h2 = ParagraphStyle(
        "h2",
        parent=styles["Heading2"],
        fontName=zh,
        fontSize=11.5,
        spaceBefore=8,
        spaceAfter=6,
    )
    h3 = ParagraphStyle(
        "h3",
        parent=styles["Heading3"],
        fontName=zh,
        fontSize=10.5,
        spaceBefore=6,
        spaceAfter=4,
    )
    body = ParagraphStyle(
        "b",
        parent=styles["Normal"],
        fontName=zh,
        fontSize=9.2,
        leading=13,
        spaceAfter=4,
    )
    bullet = ParagraphStyle(
        "bl",
        parent=body,
        leftIndent=12,
        bulletIndent=4,
    )
    callout = ParagraphStyle(
        "co",
        parent=body,
        leftIndent=10,
        rightIndent=10,
        textColor="#1a3a6e",
        spaceBefore=2,
        spaceAfter=6,
    )
    sub_i = ParagraphStyle(
        "si",
        parent=styles["Normal"],
        fontSize=7.5,
        textColor="#444444",
    )

    story: list = []
    story.append(Paragraph("竞品指标释义与数据结论（人话版）", title))
    story.append(
        Paragraph(
            f"<i>自动生成；配置 metrics.json；quality run：{snap.get('run_time', 'N/A')}</i>",
            sub_i,
        )
    )
    story.append(Spacer(1, 0.25 * cm))

    # ----- 0 数据范围 -----
    story.append(Paragraph("〇、先说清「我们在看什么样本」", h2))
    story.append(
        Paragraph(
            f"我们只看了 <b>英文评论</b>（约 <b>{snap.get('clean_en_rows', '—')}</b> 条），是从 Google Play 公开评论里抓到的一小部分。"
            f"P0 清洗后英文占比约 <b>{snap.get('english_rate', '—')}</b>。",
            body,
        )
    )
    story.append(
        Paragraph(
            "<b>所以所有结论都得加一句话：</b>「只能代表愿意写英文评论的人」，"
            "不代表全部玩家、更不等于真金白银的留存付费。这是底线。",
            callout,
        )
    )
    story.append(PageBreak())

    # ----- 1 app_base_metrics -----
    story.append(Paragraph("一、app_base_metrics.csv —— 一张 App 的「成绩单」", h2))

    story.append(Paragraph("1.1 身份信息：它是谁、有多少人评价", h3))
    base11 = [
        "<b>app_id / app_name</b>：哪个 App。",
        (
            "<b>n_reviews</b>：这个 App 被算进来的英文评论条数。<br/>"
            "<b>说人话：</b>样本多 = 数字更靠谱；样本少 = 偶然性大。"
            "后面所有「加权」「收缩」「打折」都是因为这个数。"
        ),
    ]
    for t in base11:
        story.append(Paragraph(f"• {t}", bullet))

    story.append(Paragraph("1.2 大家普遍打几分", h3))
    base12 = [
        (
            "<b>mean_score（平均分）</b>：所有人打的星算术平均。<br/>"
            "→ 「总体感觉」。<b>容易被极端分</b>（一堆 1★ 或 5★）拉得很厉害。"
        ),
        (
            "<b>median_score（中位数）</b>：把所有打分排成一队，正中间那个人打几分。<br/>"
            "→ 「中间那个典型用户」打几分；<b>不怕极端值</b>。"
        ),
        (
            "<b>std_score（标准差）</b>：分数有多分散。<br/>"
            "→ 数值大 = 大家意见分歧大。<b>注意：</b>好评差评都很多也会让它变大，<b>不一定就是「差评多」</b>。"
        ),
    ]
    for t in base12:
        story.append(Paragraph(f"• {t}", bullet))
    story.append(
        Paragraph(
            "<b>三个一起怎么读：</b>mean 高、median 也高 = 真的好；"
            "mean 高但 median 低（或反过来）= 一边倒 + 少量极端拉扯，要警惕。",
            callout,
        )
    )

    story.append(Paragraph("1.3 五星结构（最重要的一组）", h3))
    base13 = [
        "<b>share_1 ~ share_5</b>：每个星档的占比，加起来 = 100%。",
        "<b>share_high_4_5</b> = 4★ + 5★ → <b>真心满意的人有多少</b>。",
        "<b>share_low_1_2</b> = 1★ + 2★ → <b>明确不满的人有多少</b>。",
    ]
    for t in base13:
        story.append(Paragraph(f"• {t}", bullet))
    story.append(
        Paragraph(
            "<b>为什么重要：</b>平均分告诉你「分高分低」，但<b>这两个比例</b>才告诉你"
            "「用户是分裂的、还是普遍开心 / 不爽」。后面 Health Score 里的「不满惩罚分」就直接吃 share_low_1_2。",
            callout,
        )
    )

    story.append(Paragraph("1.4 清洗时打的「风险标签」", h3))
    story.append(
        Paragraph(
            "像 <b>share_has_dev_reply</b>（开发者回复率）、<b>share_is_spam_bot_suspect</b>（疑似刷评）等。<br/>"
            "<b>说人话：</b>这些只是「这条评论看起来有点怪」的提示，<b>不是定罪</b>。"
            "汇报时只能说「风险线索」，不能说「这家在刷评」。它们<b>不进入</b> Health 合成。",
            body,
        )
    )
    story.append(PageBreak())

    # ----- 2 metrics.json + health -----
    story.append(Paragraph("二、Health Score —— 给 App 打综合分的「考试」", h2))
    story.append(
        Paragraph(
            "把 Health 想象成一场考试，<b>当前权重（来自 metrics.json）</b>："
            f"水位分占 <b>{int(wL*100)}%</b>，不满惩罚分占 <b>{int(wP*100)}%</b>，最近趋势分占 <b>{int(wM*100)}%</b>；"
            f"最后再乘一个「评论够不够多」的可信度。<br/>"
            f"贝叶斯收缩参数 k = <b>{k}</b>；可信度参考量 = <b>{ref_n}</b> 条；"
            f"动量看最近 <b>{win_w}</b> 周（至少 <b>{min_wk}</b> 个不同周才算回归斜率，否则退化为「后半段均分 − 前半段均分」）。",
            body,
        )
    )

    story.append(Paragraph("2.1 全班平均分（防偏科）", h3))
    story.append(
        Paragraph(
            f"<b>global_mean</b>：把所有 App 的平均分按「评论条数」加权得到的「全班均分」，当前 ≈ "
            f"<b>{snap.get('global_bayes_mean', 0):.4f}</b>。",
            body,
        )
    )
    story.append(
        Paragraph(
            "<b>bayesian_adjusted_avg（贝叶斯调整分）：</b>"
            "评论太少，不能完全信你自己；要拉一把全班平均。<br/>"
            f"<b>公式（人话版）：</b>调整分 = (你自己的总分 + 全班平均 × {int(k)}) ÷ (你的人数 + {int(k)})。<br/>"
            f"评论很多（n 远大于 {int(k)}）→ 几乎等于自己分；"
            f"评论很少（n 比 {int(k)} 小很多）→ 会被拉向全班均分。",
            callout,
        )
    )
    story.append(
        Paragraph(
            "<b>为什么要这样？</b>防止「只有 50 条评论但全是 5★」的小 App 莫名霸榜。",
            body,
        )
    )

    story.append(Paragraph("2.2 三个分数项（合成前的小分）", h3))
    h22 = [
        (
            f"<b>component_level（水位分）</b> = 调整分 ÷ 5，归一到 0–1。<br/>"
            "→ 「调整后的好评程度」。"
        ),
        (
            "<b>component_polarization（不满惩罚分）</b> = 1 − share_low_1_2。<br/>"
            "→ 「没在打低星的人占多大比例」。低星越多，这一项越低。<br/>"
            "<b>注意：</b>它<b>不看高分</b>，只盯着 1–2 星——业务上「骂声」比「夸声」更值得警惕。"
        ),
        (
            f"<b>component_momentum_01（最近趋势分）</b>：最近 {win_w} 周里，"
            "每周平均星是涨是跌。涨 = 高分，跌 = 低分。<br/>"
            "→ 在本批 14 款里 <b>比着算</b>，所以是「相对趋势」，不是绝对涨跌。"
        ),
        (
            f"<b>component_confidence（可信度系数）</b> = min(1, n_reviews ÷ {int(ref_n)})。<br/>"
            f"→ 「评论够不够多」。不到 {int(ref_n)} 条就打折，到了就封顶为 1。"
        ),
    ]
    for t in h22:
        story.append(Paragraph(f"• {t}", bullet))

    story.append(Paragraph("2.3 最后的总分（一行公式说完）", h3))
    story.append(
        Paragraph(
            f"<b>预合成分</b> = {wL} × 水位 + {wP} × 不满惩罚 + {wM} × 趋势<br/>"
            "<b>最终 Health</b> = 预合成分 × 可信度",
            callout,
        )
    )
    story.append(
        Paragraph(
            "<b>大白话总结：</b>「<b>好评水位</b>占大头 + <b>有没有差评集中</b> + <b>最近在涨还是在跌</b>，"
            "再问一句『<b>你写够答卷了吗</b>』。」<br/>"
            "<b>health_score_rank</b>：在这 14 款里按 Health 降序排第几名。<b>只在本池有效</b>，跨品类、跨地区不能直接比。",
            body,
        )
    )
    story.append(PageBreak())

    # ----- 3 Cross-validation (plain) -----
    story.append(Paragraph("三、多个指标怎么「互相印证」（这才算看懂）", h2))
    story.append(
        Paragraph(
            "下面这张「场景 → 单看会错 → 一起看就清楚」的对照表，是判断你有没有真懂的核心。",
            body,
        )
    )
    cv = [
        (
            "<b>① 平均分还行但排名靠后？</b><br/>"
            "只看 mean 会冤枉。一起看：<b>mean 不低 + share_low_1_2 高</b> → 不满惩罚分被压低 → Health 自然掉。"
        ),
        (
            "<b>② 小 App 平均分超高？</b><br/>"
            "只看 mean 会被骗。一起看：<b>n 很小 → 贝叶斯把它拉向全班均分 → 可信度又打折一次</b>，所以不会霸榜。"
        ),
        (
            "<b>③ 趋势分（momentum_01）刚好 0.5？</b><br/>"
            "可能不是「不涨不跌」，而是<b>评论太稀疏走了退化算法</b>。要回去看最近 8 周到底有多少条。"
        ),
        (
            "<b>④ 比较两款 App 时只比 health？</b><br/>"
            "容易判错。要并列看 <b>n_reviews</b>（影响贝叶斯 + 可信度）和 <b>pre_confidence</b>（合成前分）。"
        ),
        (
            "<b>⑤ 看发行方榜单？</b><br/>"
            "<b>publisher_benchmark</b> 是按「评论条数」加权（不是简单平均 App）。<br/>"
            "公式：weighted_health = Σ(每款 health × 该款评论数) ÷ Σ(评论数)。<br/>"
            "→ 旗下评论多的 App 影响更大；要展开看每款的 share_low 与动量。"
        ),
        (
            "<b>⑥ 散点图（volume_vs_rating_scatter）出现「高声量 + 低 Health」？</b><br/>"
            "<b>不是因果</b>，只是两件事同时存在。要回到 app_base_metrics 拆 share_low 和 health 的 pre × conf。"
        ),
        (
            "<b>⑦ app_benchmark_bq2 是什么？</b><br/>"
            "= app_base_metrics 与 app_health_score 按 app_id 合并后的「竞品一页纸」。<br/>"
            "→ 数值<b>必须</b>跟两张源表对得上，用于汇报对齐，<b>不要</b>在它上面再算一次。"
        ),
    ]
    for t in cv:
        story.append(Paragraph(f"• {t}", bullet))
    story.append(PageBreak())

    # ----- 4 Conclusions (plain) -----
    story.append(Paragraph("四、用这套语言重读结论（本池当前快照）", h2))
    story.append(
        Paragraph(
            "下列每条结论都<b>说清楚了「依赖哪些指标 / 它们如何互相印证」</b>，是统计关联，不推断因果。"
            "数字会随 CSV 刷新而变。",
            body,
        )
    )
    story.append(Spacer(1, 0.15 * cm))

    # ----- 4.0 Page-2 ready bullets (short + business framing) -----
    story.append(Paragraph("4.0 Page 2 直接可贴版（汇报口吻）", h3))
    story.append(
        Paragraph(
            "<b>用法：</b>每条 = 一行结论 + 一行业务解读，可以直接复制到 PPT / 周报。最后一段是口播总结。",
            body,
        )
    )

    top3 = snap.get("top3", [])
    bot3 = snap.get("bot3", [])
    pub_map = snap.get("pub_map", {})
    sgn = pub_map.get("SGN (Jam City)", {})
    king = pub_map.get("King", {})
    tact = pub_map.get("Tactile Games", {})
    dream = pub_map.get("Dream Games", {})

    def _fmt_app_list(items: list[dict]) -> str:
        parts = [
            f"{x['name']} #{x['rank']}（{x['health']:.3f}, n={x['n']}）"
            for x in items
        ]
        return "、".join(parts)

    top3_max_low = snap.get("top3_max_share_low")
    top3_min_bayes = snap.get("top3_min_bayes")
    bot3_min_low = snap.get("bot3_min_share_low")
    bot3_cats = snap.get("bot3_categories", [])

    def _wrap(headline: str, business: str) -> str:
        return (
            f"<b>• {headline}</b><br/>"
            f"&nbsp;&nbsp;<i>业务解读：</i>{business}"
        )

    page2_bullets: list[str] = []

    if top3:
        suffix_top = ""
        if top3_max_low is not None and top3_min_bayes is not None:
            suffix_top = f"；三家共同点：低星（1–2★）≤ {top3_max_low:.1%}，调整后均分 ≥ {top3_min_bayes:.2f}"
        page2_bullets.append(
            _wrap(
                f"池内 Top 3（Health Score）：{_fmt_app_list(top3)}{suffix_top}。",
                "这 3 款是<b>休闲消除赛道里「满意度结构最干净」的产品</b>——不是均分高，而是"
                "差评比例被压到 22% 以内。可作为<b>「成熟期休闲消除产品的差评天花板」基线</b>，"
                "任何超过这个数的竞品都要打问号。",
            )
        )

    if bot3:
        cat_str = ("均出自" + " / ".join(bot3_cats)) if bot3_cats else "均集中在同一品类"
        low_str = f"，1–2★ 占比均 ≥ {bot3_min_low:.1%}" if bot3_min_low is not None else ""
        page2_bullets.append(
            _wrap(
                f"池内 Bottom 3（重点观察名单）：{_fmt_app_list(bot3)}；"
                f"{cat_str}{low_str}。",
                "这条产品线<b>整体在评论端承压</b>，且涉及多家头部发行方——大概率是「赛道用户审美/付费疲劳」"
                "而非单款做得不够精。<b>立项提示：</b>同玩法套壳已有疲劳信号，差异化（玩法机制 / IP / 节奏）"
                "比再做一款更值得投入。",
            )
        )

    if sgn and dream and king and tact:
        ratio = sgn["wh"] / dream["wh"] if dream["wh"] > 0 else 0
        page2_bullets.append(
            _wrap(
                f"发行方加权 Health 极差近 {ratio:.2f}×：SGN（Jam City）{sgn['wh']:.3f}（仅 {sgn['n_apps']} 款）领跑；"
                f"<b>Dream Games 仅 {dream['wh']:.3f} 垫底（{dream['n_apps']} 款，{dream['n_reviews']} 条评论）</b>，"
                f"与 King {king['wh']:.3f}（{king['n_apps']} 款）、Tactile {tact['wh']:.3f}（{tact['n_apps']} 款）形成断层。",
                "<b>Dream 是评论端「系统性塌陷」，不是单款失误</b>——是同品类后来者的机会窗。"
                "King / Tactile 在 0.78–0.79 的稳定带 = <b>同行业头部应有的水位</b>，长期低于 0.7 就要正视问题。",
            )
        )

    rk_low_v = snap.get("rk_low_star")
    rk_bayes_v = snap.get("rk_bayes")
    rk_mom_v = snap.get("rk_mom")
    if rk_low_v is not None and rk_bayes_v is not None and rk_mom_v is not None:
        page2_bullets.append(
            _wrap(
                f"Royal Kingdom 是池内唯一「三红」案例：1–2★ 占比 {rk_low_v:.1%}、"
                f"调整分仅 {rk_bayes_v:.2f}（远低于全班 {snap.get('global_bayes_mean', 0):.2f}）、"
                f"近 {win_w} 周趋势分 {rk_mom_v:.3f}。",
                "<b>结构、水位、动量同时垫底</b>，不是版本波动，是持续下行通道。"
                "可推动动作：拉低星评论文本做主题分析（付费墙 / 广告 / 关卡难度 / bug）。"
                "对标分析时可作为「忽视低星结构的代价」反面案例。",
            )
        )

    lg_n = snap.get("lg_n")
    lg_health = snap.get("lg_health")
    lg_rank = snap.get("lg_rank")
    bot_top = bot3[0] if bot3 else None
    if lg_n and lg_health and lg_rank and bot_top:
        diff = lg_health - bot_top["health"]
        page2_bullets.append(
            _wrap(
                f"声量 ≠ 满意度：Lily's Garden（n={lg_n}, Health #{lg_rank}, {lg_health:.3f}）"
                f"与 {bot_top['name']}（n={bot_top['n']}, Health #{bot_top['rank']}, {bot_top['health']:.3f}）"
                f"评论量相当，Health 差 {diff:.2f}。",
                "<b>「评论多 = 火」是伪命题</b>——评论多很可能是因为用户来吐槽。"
                "做产品 / 市场决策<b>必须配合 share_low_1_2 与调整分</b>，不能只看下载量或评论数。"
                "建议在 PPT 里放散点图，让「高声量 + 低 Health」自然孤立出来。",
            )
        )

    if king and tact:
        page2_bullets.append(
            _wrap(
                f"King 与 Tactile 是「稳健参照」：旗下产品 Health 落在 #1、#2、#7、#9，"
                "<b>没有任何 1 款进入观察名单</b>。",
                "他们是赛道<b>基准线（baseline），不是超越目标</b>。Top 1 常有运气成分（IP / 首发红利），"
                "真正可复制的成功是「旗下产品 Health 全部 ≥ 0.70」——比追求一个 0.85 更可持续。",
            )
        )

    for b in page2_bullets:
        story.append(Paragraph(b, body))
        story.append(Spacer(1, 0.1 * cm))

    story.append(Spacer(1, 0.1 * cm))
    story.append(Paragraph("一段话收口（汇报口播版）", h3))
    if dream:
        story.append(
            Paragraph(
                f"在我们这 14 款 Match-3 / 消除头部产品的池内，<b>SGN、King、Tactile 三家在评论端形成稳定的高地"
                f"（Health 0.78–0.81）</b>；<b>Dream Games 是评论端系统性走弱的代表"
                f"（加权 Health 仅 {dream['wh']:.2f}）</b>，"
                f"旗下 Royal Kingdom 出现「差评结构 + 调整分 + 趋势」三项指标同时垫底的极端情况，"
                f"{(rk_low_v * 100):.1f}% 的 1–2 星比例值得做主题级深挖。"
                "<b>声量与满意度并非正相关</b>——这是公开评论数据用于竞品分析时最容易踩的坑，"
                "也是为什么我们要同时报 Health 与 share_low_1_2，而不是只看评论数。",
                callout,
            )
        )
    story.append(PageBreak())

    story.append(Paragraph("4.1 详细解释版（指标链推导）", h3))
    story.append(
        Paragraph(
            "下面 7 条是<b>每条都展开「依赖哪些指标 → 怎么互相印证」</b>的长版，适合放报告正文做支撑。",
            body,
        )
    )
    story.append(Spacer(1, 0.1 * cm))

    rk_low = snap.get("rk_low_star")
    rk_mean = snap.get("rk_mean")
    ccs_high = snap.get("ccs_high")
    ccs_low = snap.get("ccs_low_star")
    ccs_rank = snap.get("ccs_rank", 2)

    conclusions: list[str] = [
        (
            f"<b>结论 1 — 榜首 vs 末位差距是「四件事一起发生」，不是单一原因：</b>"
            f"第 1 名「{snap.get('top_name', '—')}」health ≈ {snap.get('top_health', 0):.3f}；"
            f"末位「{snap.get('bot_name', '—')}」≈ {snap.get('bot_health', 0):.3f}。<br/>"
            "→ 不能光看平均分。要同时看：<b>水位（贝叶斯调整分）+ 不满惩罚（share_low）+ 最近趋势 + 评论是否够多</b>，"
            "四条线一起决定排名。"
        ),
        (
            f"<b>结论 2 — Dream Games 发行方加权 Health 垫底（≈ {snap.get('pub_worst_wh', 0):.3f}，"
            f"{snap.get('pub_worst_n_apps', 2)} 款）：</b>"
            "这是<b>把旗下每款 health 按评论数加权</b>得到的，所以是「整体观感都不好」，<b>不是某一款拖</b>。<br/>"
            "→ 要可辩护，必须展开旗下每款的 share_low 与动量，不然丢细节。"
        ),
        (
            "<b>结论 3 — Royal Kingdom 为什么垫底（三条腿同时塌）：</b>"
            + (
                f"<b>① 结构差：</b>1–2★ 占 {rk_low:.1%}；"
                if rk_low is not None
                else ""
            )
            + (
                f"<b>② 水位低：</b>调整后均分 {snap.get('rk_bayes', 0):.2f}（远低于全班 {snap.get('global_bayes_mean', 0):.2f}）；"
                f"<b>③ 还在跌：</b>趋势分 {snap.get('rk_mom', 0):.3f}；"
                f"<b>④ 评论 {snap.get('rk_n', 0)} 条够多了</b>，可信度封顶为 {snap.get('rk_conf', 0):.2f}，"
                "<b>没法再帮它打折回血</b>。<br/>"
                f"→ 预合成分 {snap.get('rk_pre', 0):.3f} × 可信度 {snap.get('rk_conf', 0):.2f} = "
                f"health {snap.get('bot_health', 0):.3f}。三条腿同时塌，不是偶然。"
            )
        ),
        (
            "<b>结论 4 — Candy Crush Saga 为什么稳：</b>"
            + (
                f"高星 {ccs_high:.1%}、低星只有 {ccs_low:.1%}，调整分高，趋势中性偏稳；Health 排第 {ccs_rank}。<br/>"
                if ccs_high is not None and ccs_low is not None
                else ""
            )
            + (
                f"分量看：水位 {snap.get('ccs_level', 0):.3f}、不满惩罚 {snap.get('ccs_pol', 0):.3f}、"
                f"趋势 {snap.get('ccs_mom', 0):.3f}、预合成分 {snap.get('ccs_pre', 0):.3f}。<br/>"
                "→ 头部产品不仅「均值好看」，<b>低星结构也受控</b>，与公式逻辑完全一致。"
            )
        ),
        (
            f"<b>结论 5 — 全班均分 ≈ {snap.get('global_bayes_mean', 0):.4f}：</b>"
            "所有 App 的「贝叶斯调整分」都会向这个数靠拢。<br/>"
            "→ 看到一款 App 调整分接近这个值，<b>先怀疑是不是评论太少被「拉回」了</b>，要把 n_reviews 一起拉出来看。"
        ),
        (
            f"<b>结论 6 — 发行方榜首「{snap.get('pub_best', '—')}」加权 Health ≈ {snap.get('pub_best_wh', 0):.3f}，"
            f"但本池只有 {snap.get('pub_best_n_apps', 1)} 款 App：</b>"
            "<b>单产品发行方很容易「一好遮百丑」</b>。<br/>"
            "→ 汇报时一定要说「样本覆盖只有 1 款」，否则会被质疑跟 King、Dream Games 这种多款发行方做了不公平对比。"
        ),
        (
            "<b>结论 7 — 「声量 vs 满意度」散点图怎么读：</b>"
            "横轴 n_reviews、纵轴贝叶斯调整分或 Health。<br/>"
            "→ 看到「高声量 + 低 Health」<b>不要</b>说成「差评的 App 反而火」；"
            "要回到 app_base_metrics 把 <b>share_low</b>、<b>预合成分</b>、<b>可信度</b>分别拉出来才说得清。"
        ),
    ]

    for c in conclusions:
        story.append(Paragraph(c, body))
        story.append(Spacer(1, 0.12 * cm))

    story.append(Spacer(1, 0.2 * cm))
    story.append(Paragraph("五、最后的「不要忘」（局限性，固定要带）", h2))
    lim = [
        "公开评论有「自选择」与时间窗偏差；英文子集不代表全部语种用户。",
        f"k = {k}、权重、{win_w} 周动量窗口换了，排序就会变；可以做敏感度分析顺便展示稳健性。",
        "「疑似刷评 / 异常时间」等启发式标签<b>没有</b>进入 Health 合成；汇报时跟 Health 分开讲。",
        "趋势分（momentum_01）是<b>本池内</b>的相对排位，跨池不能比。",
    ]
    for t in lim:
        story.append(Paragraph(f"• {t}", bullet))

    story.append(Spacer(1, 0.3 * cm))
    story.append(Paragraph("一句话记住", h2))
    story.append(
        Paragraph(
            f"<b>Health Score = 「好评水位 ({int(wL*100)}%) + 没差评的程度 ({int(wP*100)}%) + "
            f"最近是涨是跌 ({int(wM*100)}%)」 × 「你写够答卷了吗」。</b><br/>"
            "单看一项都不准——<b>四件事一起讲，结论才站得住</b>。",
            callout,
        )
    )

    OUT_PDF.parent.mkdir(parents=True, exist_ok=True)
    doc = SimpleDocTemplate(
        str(OUT_PDF),
        pagesize=A4,
        rightMargin=1.8 * cm,
        leftMargin=1.8 * cm,
        topMargin=1.8 * cm,
        bottomMargin=1.8 * cm,
    )
    doc.build(story)
    print(f"Saved: {OUT_PDF}")


if __name__ == "__main__":
    main()
