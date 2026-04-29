from pathlib import Path
import random
import colorsys

import pandas as pd
from wordcloud import WordCloud
from PIL import Image


BASE = Path("/Users/longlab/Desktop/Aging Energy/working_project/07_figures_working/figure3_updated_panels/panel_a")
DATA = BASE / "wordcloud_full_keyword_data" / "panel_a_all_clean_keywords_by_period.csv"
OUT = BASE / "wordclouds_clean"
OUT_FINAL = BASE / "final_individual"
OUT.mkdir(parents=True, exist_ok=True)
OUT_FINAL.mkdir(parents=True, exist_ok=True)

FONT = "/System/Library/Fonts/Supplemental/Arial Bold.ttf"

CATEGORY_COLORS = {
    "welfare and care": ["#3C5488", "#4E6E9E", "#5A78A8"],
    "health and vulnerability": ["#009E73", "#1B9E77", "#00A087"],
    "housing and thermal comfort": ["#B8860B", "#C49A00", "#D4A017"],
    "energy transition and efficiency": ["#0072B2", "#1F78B4", "#4DBBD5"],
    "household behaviour and adoption": ["#7B3294", "#8E6BBE", "#6A51A3"],
    "affordability and income constraints": ["#D81B60", "#E64B35", "#C51B7D"],
}

PERIODS = ["2012–2016", "2017–2020", "2021–2024"]
SLUG = {"2012–2016": "2012_2016", "2017–2020": "2017_2020", "2021–2024": "2021_2024"}


def soften_hex(hex_color, amount):
    hex_color = hex_color.lstrip("#")
    r = int(hex_color[0:2], 16)
    g = int(hex_color[2:4], 16)
    b = int(hex_color[4:6], 16)
    r = int(r + (255 - r) * amount)
    g = int(g + (255 - g) * amount)
    b = int(b + (255 - b) * amount)
    return f"#{r:02x}{g:02x}{b:02x}"


def recolor_factory(color_lookup, frequency_lookup):
    def color_func(word, font_size, position, orientation, random_state=None, **kwargs):
        colors = color_lookup.get(word.lower(), ["#2F4858"])
        rng = random.Random(hash(word) % 100000)
        base = rng.choice(colors)
        rank_weight = frequency_lookup.get(word.lower(), 0)
        # Small words become lighter so the eye lands on the largest terms first.
        lighten = 0.08 + (1 - rank_weight) * 0.52
        return soften_hex(base, lighten)

    return color_func


def build(period, df):
    sub = df[df["period"] == period].copy()
    sub = sub[sub["mention_count"] > 0].sort_values("mention_count", ascending=False)

    # Emphasize the head of the distribution while retaining the full keyword pool.
    max_count = sub["mention_count"].max()
    frequencies = {
        row["keyword"]: int((row["mention_count"] / max_count) ** 1.35 * 10000)
        for _, row in sub.iterrows()
    }
    color_lookup = {
        row["keyword"].lower(): CATEGORY_COLORS.get(row["category"], ["#2F4858"])
        for _, row in sub.iterrows()
    }
    min_f = min(frequencies.values())
    max_f = max(frequencies.values())
    denom = max(max_f - min_f, 1)
    frequency_lookup = {
        word.lower(): (freq - min_f) / denom
        for word, freq in frequencies.items()
    }

    wc = WordCloud(
        width=1500,
        height=760,
        background_color="white",
        mode="RGB",
        max_words=65,
        min_font_size=8,
        max_font_size=220,
        relative_scaling=0.72,
        prefer_horizontal=0.88,
        collocations=False,
        normalize_plurals=False,
        margin=2,
        random_state=51,
        font_path=FONT,
        repeat=False,
    ).generate_from_frequencies(frequencies)

    wc = wc.recolor(color_func=recolor_factory(color_lookup, frequency_lookup), random_state=51)
    img = wc.to_image()

    # Crop outside whitespace and paste back to a compact horizontal canvas.
    bbox = Image.eval(img.convert("L"), lambda x: 255 - x).getbbox()
    if bbox:
        cropped = img.crop(bbox)
        margin = 24
        canvas = Image.new("RGB", (cropped.width + margin * 2, cropped.height + margin * 2), "white")
        canvas.paste(cropped, (margin, margin))
        canvas.thumbnail((1500, 760), Image.Resampling.LANCZOS)
        final = Image.new("RGB", (1500, 760), "white")
        final.paste(canvas, ((1500 - canvas.width) // 2, (760 - canvas.height) // 2))
    else:
        final = img

    name = f"figure3_panel_a_wordcloud_{SLUG[period]}.png"
    final.save(OUT / name, quality=95)
    final.save(OUT_FINAL / name, quality=95)
    print(OUT / name)


def main():
    df = pd.read_csv(DATA)
    for period in PERIODS:
        build(period, df)


if __name__ == "__main__":
    main()
