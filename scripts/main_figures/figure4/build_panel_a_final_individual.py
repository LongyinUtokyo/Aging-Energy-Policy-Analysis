from pathlib import Path
import math
import shutil

import matplotlib.pyplot as plt
import pandas as pd
from PIL import Image, ImageDraw, ImageFont


BASE = Path("/Users/longlab/Desktop/Aging Energy/working_project/07_figures_working/figure3_updated_panels/panel_a")
OUT = BASE / "final_individual"
WC_OUT = BASE / "wordclouds_clean"
OUT.mkdir(parents=True, exist_ok=True)
WC_OUT.mkdir(parents=True, exist_ok=True)

KEYWORDS = pd.read_csv(BASE / "panel_a_top6_clean_keywords_no_overlap.csv")
COUNTRIES = pd.read_csv(BASE / "panel_a_top3_country_contributions_no_overlap.csv")

FONT_BOLD = Path("/System/Library/Fonts/Supplemental/Arial Bold.ttf")

PERIODS = ["2012-2016", "2017-2020", "2021-2024"]
PERIOD_SOURCE = {"2012-2016": "2012–2016", "2017-2020": "2017–2020", "2021-2024": "2021–2024"}

KEYWORD_COLORS = {
    "health": "#00A087",
    "economic": "#E64B35",
    "social": "#3C5488",
    "climate": "#4DBBD5",
    "child": "#8E6BBE",
    "air pollution": "#F0A202",
    "sustainable": "#8491B4",
    "covid": "#DC0000",
}


DISPLAY_LABELS = {"air pollution": "air pollution"}


def text_bbox(draw, text, font, xy):
    box = draw.textbbox(xy, text, font=font, anchor="mm")
    return box


def overlaps(box, boxes, pad=6):
    l1, t1, r1, b1 = box
    l1 -= pad
    t1 -= pad
    r1 += pad
    b1 += pad
    for l2, t2, r2, b2 in boxes:
        if not (r1 < l2 or r2 < l1 or b1 < t2 or b2 < t1):
            return True
    return False


def spiral_points(cx, cy, max_radius=260, step=6):
    yield cx, cy
    theta = 0.0
    radius = 8.0
    while radius < max_radius:
        yield cx + math.cos(theta) * radius, cy + math.sin(theta) * radius
        theta += 0.32
        radius += step / (2 * math.pi)


def build_compact_wordcloud(period_label):
    period = PERIOD_SOURCE[period_label]
    df = KEYWORDS[KEYWORDS["period"] == period].sort_values("mention_count", ascending=False).reset_index(drop=True)

    canvas_w, canvas_h = 900, 900
    img = Image.new("RGB", (canvas_w, canvas_h), "white")
    draw = ImageDraw.Draw(img)

    values = df["mention_count"].astype(float)
    vmin, vmax = values.min(), values.max()
    denom = max(math.log(vmax + 1) - math.log(vmin + 1), 1e-6)

    layout = [
        (0.50, 0.13, 840, 142),
        (0.50, 0.29, 840, 142),
        (0.50, 0.45, 840, 136),
        (0.50, 0.61, 840, 130),
        (0.50, 0.76, 840, 116),
        (0.50, 0.90, 840, 104),
    ]

    for i, row in df.iterrows():
        word = row["keyword"]
        scaled = (math.log(row["mention_count"] + 1) - math.log(vmin + 1)) / denom
        x_frac, y_frac, max_width, max_size = layout[i]
        start_size = int(max_size * (0.82 + 0.18 * scaled))
        font = ImageFont.truetype(str(FONT_BOLD), size=start_size)
        while start_size > 42 and text_bbox(draw, word, font, (canvas_w * x_frac, canvas_h * y_frac))[2] - text_bbox(draw, word, font, (canvas_w * x_frac, canvas_h * y_frac))[0] > max_width:
            start_size -= 3
            font = ImageFont.truetype(str(FONT_BOLD), size=start_size)
        draw.text(
            (canvas_w * x_frac, canvas_h * y_frac),
            word,
            font=font,
            fill=KEYWORD_COLORS.get(word, "#333333"),
            anchor="mm",
        )

    out_name = f"figure3_panel_a_wordcloud_{period_label.replace('-', '_')}.png"
    img.save(WC_OUT / out_name, quality=95)
    img.save(OUT / out_name, quality=95)


def build_keyword_bar(period_label):
    period = PERIOD_SOURCE[period_label]
    df = KEYWORDS[KEYWORDS["period"] == period].sort_values("rank_in_period")

    plt.rcParams.update(
        {
            "font.family": "Arial",
            "axes.titlesize": 26,
            "axes.labelsize": 18,
            "xtick.labelsize": 15,
            "ytick.labelsize": 20,
        }
    )

    fig, ax = plt.subplots(figsize=(7.8, 6.8), dpi=240)
    colors = [KEYWORD_COLORS.get(k, "#666666") for k in df["keyword"]]
    x = range(len(df))
    ax.bar(x, df["mention_count"], color=colors, edgecolor="white", linewidth=0.8)
    ax.set_ylim(0, 9000)
    ax.set_xlabel("")
    ax.set_ylabel("")
    ax.set_title(period_label, fontweight="bold", pad=8)
    ax.spines[["top", "right"]].set_visible(False)
    ax.grid(False)
    ax.set_xticks(list(x))
    ax.set_xticklabels([DISPLAY_LABELS.get(k, k) for k in df["keyword"]], rotation=90, ha="center", va="top")
    ax.tick_params(axis="x", labelsize=22, pad=8)
    ax.tick_params(axis="y", labelsize=15)
    for i, row in enumerate(df.itertuples(index=False)):
        ax.text(i, row.mention_count + 140, f"{int(row.mention_count)}", va="bottom", ha="center", fontsize=14)
    fig.subplots_adjust(bottom=0.32, top=0.88, left=0.14, right=0.98)
    fig.savefig(OUT / f"figure3_panel_a_top_keywords_{period_label.replace('-', '_')}.png", bbox_inches="tight", facecolor="white")
    plt.close(fig)


def build_country_bars(period_label):
    period = PERIOD_SOURCE[period_label]
    top3_keywords = (
        KEYWORDS[KEYWORDS["period"] == period]
        .sort_values("rank_in_period")
        .head(3)["keyword"]
        .tolist()
    )
    for keyword in top3_keywords:
        sub = COUNTRIES[(COUNTRIES["period"] == period) & (COUNTRIES["keyword"] == keyword)].sort_values("mention_count", ascending=True)
        color = KEYWORD_COLORS.get(keyword, "#666666")
        fig, ax = plt.subplots(figsize=(5.2, 3.6), dpi=240)
        ax.barh(sub["Source country"], sub["mention_count"], color=color, edgecolor="white", linewidth=0.8)
        ax.set_title(keyword, loc="left", fontsize=22, fontweight="bold", pad=4)
        ax.set_xlabel("")
        ax.set_ylabel("")
        ax.spines[["top", "right"]].set_visible(False)
        ax.grid(False)
        ax.tick_params(axis="x", labelsize=13)
        ax.tick_params(axis="y", labelsize=18)
        xmax = sub["mention_count"].max() * 1.18
        ax.set_xlim(0, xmax)
        for i, val in enumerate(sub["mention_count"]):
            ax.text(val + xmax * 0.025, i, f"{int(val)}", ha="left", va="center", fontsize=13)
        fig.tight_layout()
        safe_kw = keyword.replace(" ", "_")
        fig.savefig(OUT / f"figure3_panel_a_country_top3_{period_label.replace('-', '_')}_{safe_kw}.png", bbox_inches="tight", facecolor="white")
        plt.close(fig)


def clean_old_outputs():
    for p in OUT.glob("*.png"):
        p.unlink()
    for p in WC_OUT.glob("*.png"):
        p.unlink()


clean_old_outputs()
for period_label in PERIODS:
    build_keyword_bar(period_label)
    build_compact_wordcloud(period_label)
    build_country_bars(period_label)

print(f"Saved final individual panel A figures to {OUT}")
