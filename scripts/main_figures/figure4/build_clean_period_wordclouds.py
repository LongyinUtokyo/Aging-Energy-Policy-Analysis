from pathlib import Path
import math

import pandas as pd
from PIL import Image, ImageDraw, ImageFont


BASE = Path("/Users/longlab/Desktop/Aging Energy/working_project/07_figures_working/figure3_updated_panels/panel_a")
OUT = BASE / "wordclouds_clean"
OUT.mkdir(parents=True, exist_ok=True)

DATA = pd.read_csv(BASE / "panel_a_top6_clean_keywords_no_overlap.csv")

FONT_BOLD = Path("/System/Library/Fonts/Supplemental/Arial Bold.ttf")
FONT_REG = Path("/System/Library/Fonts/Supplemental/Arial.ttf")

COLORS = {
    "health": "#6CB6B1",
    "economic": "#D81B60",
    "social": "#4E79A7",
    "climate": "#2A9D8F",
    "child": "#5B84B1",
    "air pollution": "#43AA8B",
    "sustainable": "#C9A227",
    "covid": "#E15759",
}

PERIODS = ["2012–2016", "2017–2020", "2021–2024"]
SLUG = {"2012–2016": "2012_2016", "2017–2020": "2017_2020", "2021–2024": "2021_2024"}


def text_size(draw, text, font):
    box = draw.textbbox((0, 0), text, font=font)
    return box[2] - box[0], box[3] - box[1]


def fit_font(draw, text, target_width, start_size, min_size=26):
    size = start_size
    while size >= min_size:
        font = ImageFont.truetype(str(FONT_BOLD), size=size)
        w, h = text_size(draw, text, font)
        if w <= target_width:
            return font
        size -= 2
    return ImageFont.truetype(str(FONT_BOLD), size=min_size)


def draw_centered(draw, xy, text, font, fill, anchor="mm"):
    draw.text(xy, text, font=font, fill=fill, anchor=anchor)


def build_wordcloud(period):
    df = DATA[DATA["period"] == period].sort_values("mention_count", ascending=False).reset_index(drop=True)
    width, height = 760, 360
    img = Image.new("RGB", (width, height), "white")
    draw = ImageDraw.Draw(img)

    frame = "#F3F6F7"
    for x in range(18, width - 18, 64):
        draw.line((x, 16, x, height - 16), fill=frame, width=1)
    for y in range(16, height - 16, 54):
        draw.line((18, y, width - 18, y), fill=frame, width=1)

    values = df["mention_count"].astype(float)
    vmin, vmax = values.min(), values.max()
    spread = max(math.log(vmax + 1) - math.log(vmin + 1), 1e-6)

    size_map = {}
    for _, row in df.iterrows():
        scaled = (math.log(row["mention_count"] + 1) - math.log(vmin + 1)) / spread
        size_map[row["keyword"]] = int(42 + scaled * 46)

    positions = [
        (width * 0.50, height * 0.50, 500),
        (width * 0.31, height * 0.31, 350),
        (width * 0.68, height * 0.32, 350),
        (width * 0.29, height * 0.68, 330),
        (width * 0.70, height * 0.66, 350),
        (width * 0.50, height * 0.80, 430),
    ]

    for i, row in df.iterrows():
        word = row["keyword"]
        x, y, max_w = positions[i]
        font = fit_font(draw, word, max_w, size_map[word])
        color = COLORS.get(word, "#333333")
        draw_centered(draw, (x, y), word, font, color)

    img.save(OUT / f"figure3_panel_a_wordcloud_{SLUG[period]}.png", quality=95)


for period in PERIODS:
    build_wordcloud(period)

print(OUT)
