#!/usr/bin/env python3
"""
Day 6 — render the bilingual User Satisfaction Insight Report into a PDF.

Reads the Markdown source at reports/每日复盘/User_Satisfaction_Insight_Report.md
and emits a styled, image-embedded PDF at the same folder.

Output:
  reports/每日复盘/User_Satisfaction_Insight_Report.pdf
"""

from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
MD_PATH = ROOT / "reports" / "每日复盘" / "User_Satisfaction_Insight_Report.md"
OUT_PDF = ROOT / "reports" / "每日复盘" / "User_Satisfaction_Insight_Report.pdf"
FIG_DIR = ROOT / "reports" / "每日复盘" / "figures"


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


def _inline(text: str) -> str:
    # Order matters: bold first (** does not conflict), then backtick code spans.
    # We deliberately do NOT convert `_x_` to italics because many field names
    # contain underscores (e.g. crash_bug) and there is no reliable lexer here.
    text = re.sub(r"\*\*(.+?)\*\*", r"<b>\1</b>", text)
    text = re.sub(r"`(.+?)`", r"<font face='Courier'>\1</font>", text)
    return text


def main() -> None:
    from reportlab.lib import colors
    from reportlab.lib.pagesizes import A4
    from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
    from reportlab.lib.units import cm
    from reportlab.platypus import Image, PageBreak, Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle

    if not MD_PATH.is_file():
        raise FileNotFoundError(MD_PATH)
    md = MD_PATH.read_text(encoding="utf-8").splitlines()

    zh = _zh_font()
    styles = getSampleStyleSheet()
    s_title = ParagraphStyle("t", parent=styles["Heading1"], fontName="Helvetica-Bold", fontSize=16, spaceAfter=10, alignment=0)
    s_h1 = ParagraphStyle("h1", parent=styles["Heading1"], fontName=zh, fontSize=14, spaceBefore=10, spaceAfter=6)
    s_h2 = ParagraphStyle("h2", parent=styles["Heading2"], fontName=zh, fontSize=12, spaceBefore=8, spaceAfter=5)
    s_h3 = ParagraphStyle("h3", parent=styles["Heading3"], fontName=zh, fontSize=10.5, spaceBefore=5, spaceAfter=4)
    s_body = ParagraphStyle("b", parent=styles["Normal"], fontName=zh, fontSize=9.4, leading=13, spaceAfter=4)
    s_bullet = ParagraphStyle("bl", parent=s_body, leftIndent=12, bulletIndent=4)
    s_quote = ParagraphStyle("q", parent=s_body, leftIndent=10, rightIndent=10, textColor="#1a3a6e", spaceAfter=6)
    s_sub = ParagraphStyle("si", parent=styles["Normal"], fontSize=7.5, textColor="#444444")

    story: list = []

    def flush_table(rows: list[list[str]]) -> None:
        if not rows:
            return
        col_widths = None
        ncols = max(len(r) for r in rows)
        # Pad short rows
        rows = [r + [""] * (ncols - len(r)) for r in rows]
        # Convert each cell to Paragraph for wrapping
        para_rows: list[list[Paragraph]] = []
        for i, r in enumerate(rows):
            style = ParagraphStyle("cell", parent=s_body, fontSize=8.2, leading=10, spaceAfter=0)
            if i == 0:
                style = ParagraphStyle("hdr", parent=style, fontName=zh, textColor="#ffffff")
            para_rows.append([Paragraph(_inline(c), style) for c in r])
        page_width = A4[0] - 2.6 * cm
        col_widths = [page_width / ncols] * ncols
        t = Table(para_rows, colWidths=col_widths, hAlign="LEFT", repeatRows=1)
        t.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#2c3e50")),
            ("GRID", (0, 0), (-1, -1), 0.3, colors.HexColor("#8aa0c4")),
            ("VALIGN", (0, 0), (-1, -1), "TOP"),
            ("LEFTPADDING", (0, 0), (-1, -1), 4),
            ("RIGHTPADDING", (0, 0), (-1, -1), 4),
            ("TOPPADDING", (0, 0), (-1, -1), 3),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
        ]))
        story.append(t)
        story.append(Spacer(1, 0.25 * cm))

    i = 0
    pending_table: list[list[str]] = []

    def flush_pending_table() -> None:
        nonlocal pending_table
        if pending_table:
            # First row is header; drop the separator row of dashes if present
            cleaned = [r for r in pending_table if not all(set(c.strip()) <= {"-", ":"} for c in r)]
            flush_table(cleaned)
            pending_table = []

    while i < len(md):
        line = md[i].rstrip("\n")
        stripped = line.strip()

        if stripped.startswith("|") and stripped.endswith("|"):
            cells = [c.strip() for c in stripped.strip("|").split("|")]
            pending_table.append(cells)
            i += 1
            continue
        else:
            flush_pending_table()

        if not stripped:
            i += 1
            continue

        # Headings
        if stripped.startswith("# "):
            story.append(Paragraph(_inline(stripped[2:]), s_title))
        elif stripped.startswith("## "):
            story.append(Paragraph(_inline(stripped[3:]), s_h1))
        elif stripped.startswith("### "):
            story.append(Paragraph(_inline(stripped[4:]), s_h2))
        elif stripped.startswith("#### "):
            story.append(Paragraph(_inline(stripped[5:]), s_h3))
        elif stripped.startswith("![") and "](" in stripped:
            m = re.match(r"!\[(.*?)\]\((.*?)\)", stripped)
            if m:
                _alt, rel = m.group(1), m.group(2)
                img_path = (MD_PATH.parent / rel).resolve()
                if img_path.exists():
                    max_w = A4[0] - 2.6 * cm
                    try:
                        img = Image(str(img_path))
                        ratio = img.imageHeight / img.imageWidth
                        img.drawWidth = max_w
                        img.drawHeight = max_w * ratio
                        story.append(Spacer(1, 0.15 * cm))
                        story.append(img)
                        story.append(Paragraph(f"<i>Figure: {rel.split('/')[-1]}</i>", s_sub))
                        story.append(Spacer(1, 0.2 * cm))
                    except Exception as e:
                        story.append(Paragraph(f"[image error: {e}]", s_body))
        elif stripped.startswith("> "):
            story.append(Paragraph(_inline(stripped[2:]), s_quote))
        elif re.match(r"^[\-\*] ", stripped):
            story.append(Paragraph("• " + _inline(stripped[2:]), s_bullet))
        elif re.match(r"^\d+\. ", stripped):
            story.append(Paragraph(_inline(stripped), s_bullet))
        elif stripped.startswith("---"):
            story.append(Spacer(1, 0.25 * cm))
        else:
            story.append(Paragraph(_inline(stripped), s_body))
        i += 1

    flush_pending_table()

    OUT_PDF.parent.mkdir(parents=True, exist_ok=True)
    SimpleDocTemplate(
        str(OUT_PDF),
        pagesize=A4,
        leftMargin=1.3 * cm, rightMargin=1.3 * cm,
        topMargin=1.4 * cm, bottomMargin=1.4 * cm,
        title="User Satisfaction Insight Report v1",
    ).build(story)
    print(f"Saved: {OUT_PDF}")


if __name__ == "__main__":
    main()
