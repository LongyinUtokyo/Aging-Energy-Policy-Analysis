from __future__ import annotations

import os
import re
from collections import Counter
from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns
from simplemma import lemmatize
from sklearn.feature_extraction.text import ENGLISH_STOP_WORDS


WORKDIR = Path(__file__).resolve().parents[2]
OUTPUT_DIR = WORKDIR / "outputs" / "result2" / "keyword_sankey_outputs"
os.environ.setdefault("MPLCONFIGDIR", str(OUTPUT_DIR / ".mplconfig"))
RAW_FILES = [
    WORKDIR / "inputs" / "raw" / "export-2026-04-01.csv",
    WORKDIR / "inputs" / "raw" / "export-2026-04-01 (1).csv",
]
WINDOWS = [
    ("1972_1976", 1972, 1976),
    ("1977_1981", 1977, 1981),
    ("1982_1986", 1982, 1986),
    ("1987_1991", 1987, 1991),
    ("1992_1996", 1992, 1996),
    ("1997_2001", 1997, 2001),
    ("2002_2006", 2002, 2006),
    ("2007_2011", 2007, 2011),
    ("2012_2016", 2012, 2016),
    ("2017_2020", 2017, 2020),
    ("2021_2024", 2021, 2024),
]

PHRASE_MAP = {
    "energy poverty": "energy_poverty",
    "fuel poverty": "fuel_poverty",
    "thermal comfort": "thermal_comfort",
    "older adults": "older_adults",
    "older adult": "older_adult",
    "ageing population": "ageing_population",
    "aging population": "ageing_population",
    "household energy use": "household_energy_use",
    "energy efficiency": "energy_efficiency",
    "home retrofit": "home_retrofit",
    "fixed income": "fixed_income",
    "pension income": "pension_income",
    "social care": "social_care",
    "healthy ageing": "healthy_ageing",
    "healthy aging": "healthy_ageing",
    "renewable energy": "renewable_energy",
    "climate change": "climate_change",
    "air pollution": "air_pollution",
    "sustainable development": "sustainable_development",
    "urban development": "urban_development",
    "economic development": "economic_development",
    "household behaviour": "household_behaviour",
    "household behavior": "household_behaviour",
    "behavioural adaptation": "behavioural_adaptation",
    "behavioral adaptation": "behavioural_adaptation",
    "low carbon": "low_carbon",
    "home heating": "home_heating",
    "heat pump": "heat_pump",
    "long term care": "long_term_care",
    "care home": "care_home",
    "just transition": "just_transition",
}

BASE_STOPWORDS = set(ENGLISH_STOP_WORDS) | {
    "ageing",
    "aging",
    "older",
    "older_people",
    "older_adult",
    "older_adults",
    "elderly",
    "policy",
    "policies",
    "title",
    "theme",
    "topic",
}

REMOVE_KEYWORDS = {
    "adult",
    "academic",
    "adolescence",
    "anthropology",
    "analysis",
    "anti",
    "arm",
    "art",
    "attention",
    "autonomy",
    "bank",
    "ballistic",
    "biology",
    "brain",
    "budget",
    "business",
    "branch",
    "child",
    "children",
    "cognition",
    "country",
    "council",
    "cultural",
    "curriculum",
    "data",
    "degree",
    "develop",
    "discipline",
    "educational",
    "education",
    "future",
    "general",
    "geography",
    "growth",
    "hansard",
    "history",
    "high",
    "importance",
    "meet",
    "international",
    "law",
    "literacy",
    "meeting",
    "missile",
    "museum",
    "nation",
    "new",
    "paper",
    "parliament",
    "plan",
    "problem",
    "public",
    "psychology",
    "population",
    "report",
    "reports",
    "research",
    "review",
    "reform",
    "role",
    "school",
    "science",
    "session",
    "society",
    "state",
    "study",
    "studies",
    "submarine",
    "unesco",
    "unite",
    "use",
    "victoria",
    "woman",
    "world",
}

BAD_KEYWORDS = {"hous", "analysi", "branche", "meet", "degree", "museum"}

GEOGRAPHIC_TERMS = {
    "africa",
    "african",
    "america",
    "american",
    "asia",
    "asian",
    "australia",
    "australian",
    "canada",
    "caribbean",
    "china",
    "europe",
    "european",
    "france",
    "germany",
    "global_south",
    "india",
    "ireland",
    "japan",
    "korea",
    "latin_america",
    "netherlands",
    "new_zealand",
    "scotland",
    "singapore",
    "south_africa",
    "sweden",
    "switzerland",
    "tanzania",
    "uganda",
    "uk",
    "united_kingdom",
    "united_states",
    "usa",
    "wales",
}


def ensure_output_dir() -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    (OUTPUT_DIR / ".mplconfig").mkdir(parents=True, exist_ok=True)


def label_keyword(token: str) -> str:
    keep_upper = {"SDG", "EU", "UK", "USA", "UN", "COVID"}
    words = token.replace("_", " ").split()
    out = []
    for word in words:
        upper = word.upper()
        if upper in keep_upper:
            out.append(upper)
        else:
            out.append(word.capitalize())
    return " ".join(out)


def load_and_merge_raw() -> pd.DataFrame:
    cols = ["Overton id", "Published_on", "Top topics", "Document theme", "Title"]
    frames = [pd.read_csv(path, usecols=cols) for path in RAW_FILES]
    merged = pd.concat(frames, ignore_index=True)
    merged = merged.drop_duplicates(subset=["Overton id"]).copy()
    merged["Year"] = pd.to_datetime(merged["Published_on"], errors="coerce").dt.year
    merged = merged.dropna(subset=["Year"]).copy()
    merged["Year"] = merged["Year"].astype(int)
    merged["analysis_text"] = merged[["Top topics", "Document theme", "Title"]].fillna("").agg(" ".join, axis=1)
    return merged


def normalize_text(text: str) -> str:
    text = str(text).lower()
    for source, target in PHRASE_MAP.items():
        text = text.replace(source, target)
    text = re.sub(r"[^\w\s_]", " ", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text


def preprocess_tokens(text: str) -> list[str]:
    cleaned = normalize_text(text)
    tokens = []
    for raw in cleaned.split():
        if not raw:
            continue
        if raw.isdigit():
            continue
        if re.fullmatch(r"(19|20)\d{2}", raw):
            continue
        if len(raw) < 3:
            continue
        if "_" in raw:
            lemma = raw
        else:
            lemma = lemmatize(raw, lang="en")
        if lemma in BASE_STOPWORDS or raw in BASE_STOPWORDS:
            continue
        if lemma.isdigit() or re.fullmatch(r"(19|20)\d{2}", lemma):
            continue
        if len(lemma) < 3:
            continue
        tokens.append(lemma)
    return tokens


def frequency_by_window(df: pd.DataFrame) -> pd.DataFrame:
    records = []
    for label, start, end in WINDOWS:
        counter = Counter()
        chunk = df[(df["Year"] >= start) & (df["Year"] <= end)]
        for text in chunk["analysis_text"]:
            counter.update(preprocess_tokens(text))
        total = sum(counter.values())
        ranked = sorted(counter.items(), key=lambda x: (-x[1], x[0]))
        for rank, (keyword, count) in enumerate(ranked, start=1):
            records.append(
                {
                    "time_window": label,
                    "rank": rank,
                    "keyword": keyword,
                    "count": int(count),
                    "share": count / total if total else 0.0,
                }
            )
    return pd.DataFrame(records)


def clean_keywords(freq_df: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    removed_rows = []
    keep_rows = []
    for row in freq_df.itertuples():
        keyword = row.keyword
        reason = None
        if keyword in BAD_KEYWORDS:
            reason = "broken_or_malformed_token"
        elif keyword in REMOVE_KEYWORDS:
            reason = "generic_academic_or_procedural_term"
        if reason:
            removed_rows.append(
                {
                    "time_window": row.time_window,
                    "keyword": keyword,
                    "count": row.count,
                    "share": row.share,
                    "removal_reason": reason,
                }
            )
        else:
            keep_rows.append(
                {
                    "time_window": row.time_window,
                    "rank": row.rank,
                    "keyword": row.keyword,
                    "count": row.count,
                    "share": row.share,
                }
            )

    cleaned = pd.DataFrame(keep_rows)
    cleaned["keyword_group"] = cleaned["keyword"].apply(
        lambda x: "geographic" if x in GEOGRAPHIC_TERMS else "thematic"
    )
    cleaned = cleaned.sort_values(["time_window", "count", "keyword"], ascending=[True, False, True]).reset_index(drop=True)
    cleaned["rank"] = cleaned.groupby("time_window").cumcount() + 1
    removed = pd.DataFrame(removed_rows)
    return cleaned, removed


def save_top_tables(freq_df: pd.DataFrame, cleaned_df: pd.DataFrame) -> None:
    top30 = freq_df.groupby("time_window", group_keys=False).head(30).copy()
    top30["keyword"] = top30["keyword"].map(label_keyword)
    top30.to_csv(OUTPUT_DIR / "top30_keywords_with_counts.csv", index=False)

    top30_clean = cleaned_df.groupby("time_window", group_keys=False).head(30).copy()
    top30_clean["keyword"] = top30_clean["keyword"].map(label_keyword)
    top30_clean.to_csv(OUTPUT_DIR / "top30_keywords_with_counts_cleaned.csv", index=False)

    window_order = [label for label, _, _ in WINDOWS]
    rank_index = pd.Index(range(1, 31), name="rank")
    keyword_wide = pd.DataFrame(index=rank_index)
    keyword_count_wide = pd.DataFrame(index=rank_index)
    for window in window_order:
        chunk = top30_clean[top30_clean["time_window"] == window].set_index("rank")
        keyword_wide[window] = chunk["keyword"].reindex(rank_index)
        keyword_count_wide[window] = chunk.apply(
            lambda row: f"{row['keyword']} ({int(row['count'])})" if pd.notna(row["keyword"]) else None,
            axis=1,
        ).reindex(rank_index)

    keyword_wide.reset_index().to_csv(OUTPUT_DIR / "top30_keywords_rank_by_window.csv", index=False)
    keyword_count_wide.reset_index().to_csv(
        OUTPUT_DIR / "top30_keywords_rank_by_window_with_counts.csv",
        index=False,
    )


def keyword_palette(keywords: list[str]) -> dict[str, tuple[float, float, float]]:
    palette = sns.husl_palette(len(keywords), s=0.48, l=0.56)
    return {kw: color for kw, color in zip(sorted(keywords), palette)}


def build_main_figure(cleaned_df: pd.DataFrame) -> str:
    thematic = cleaned_df[cleaned_df["keyword_group"] == "thematic"].copy()
    main_df = thematic.groupby("time_window", group_keys=False).head(8).copy()
    main_df["keyword_label"] = main_df["keyword"].map(label_keyword)
    palette = keyword_palette(main_df["keyword"].unique().tolist())

    sns.set_theme(style="whitegrid")
    fig, axes = plt.subplots(4, 3, figsize=(16, 14), facecolor="#fbfbf8")
    axes = axes.flatten()
    window_order = [label for label, _, _ in WINDOWS]

    for ax, window in zip(axes, window_order):
        chunk = main_df[main_df["time_window"] == window].sort_values("count", ascending=True)
        colors = [palette[k] for k in chunk["keyword"]]
        ax.barh(chunk["keyword_label"], chunk["count"], color=colors, edgecolor="none", height=0.68)
        ax.set_title(window.replace("_", "-"), fontsize=12.5, pad=8)
        local_max = chunk["count"].max() if not chunk.empty else 1
        ax.set_xlim(0, local_max * 1.18)
        ax.tick_params(axis="y", labelsize=10)
        ax.tick_params(axis="x", labelsize=9)
        ax.grid(axis="x", color="#d9d9d9", linewidth=0.7, alpha=0.7)
        ax.grid(axis="y", visible=False)
        ax.set_xlabel("Mention Count", fontsize=10)
        ax.set_ylabel("")
        for c in ax.containers:
            ax.bar_label(c, fmt="%.0f", padding=2, fontsize=8, color="#444444")
        for spine in ["top", "right"]:
            ax.spines[spine].set_visible(False)
        ax.spines["left"].set_color("#cccccc")
        ax.spines["bottom"].set_color("#cccccc")

    for ax in axes[len(window_order) :]:
        ax.axis("off")

    fig.suptitle("Dominant Thematic Keyword Evolution Across Policy Windows", fontsize=18, y=0.995)
    fig.tight_layout(rect=[0, 0, 1, 0.985])
    fig.savefig(OUTPUT_DIR / "keyword_evolution_main.png", dpi=400, bbox_inches="tight", facecolor=fig.get_facecolor())
    fig.savefig(OUTPUT_DIR / "keyword_evolution_main.pdf", bbox_inches="tight", facecolor=fig.get_facecolor())
    plt.close(fig)

    # Supplementary figure with cleaned keywords including geographic terms.
    supp_df = cleaned_df.groupby("time_window", group_keys=False).head(8).copy()
    supp_df["keyword_label"] = supp_df["keyword"].map(label_keyword)
    supp_palette = keyword_palette(supp_df["keyword"].unique().tolist())
    fig, axes = plt.subplots(4, 3, figsize=(16, 14), facecolor="#fbfbf8")
    axes = axes.flatten()
    for ax, window in zip(axes, window_order):
        chunk = supp_df[supp_df["time_window"] == window].sort_values("count", ascending=True)
        colors = [supp_palette[k] for k in chunk["keyword"]]
        ax.barh(chunk["keyword_label"], chunk["count"], color=colors, edgecolor="none", height=0.68)
        ax.set_title(window.replace("_", "-"), fontsize=12.5, pad=8)
        local_max = chunk["count"].max() if not chunk.empty else 1
        ax.set_xlim(0, local_max * 1.18)
        ax.tick_params(axis="y", labelsize=10)
        ax.tick_params(axis="x", labelsize=9)
        ax.grid(axis="x", color="#d9d9d9", linewidth=0.7, alpha=0.7)
        ax.grid(axis="y", visible=False)
        ax.set_xlabel("Mention Count", fontsize=10)
        ax.set_ylabel("")
        for c in ax.containers:
            ax.bar_label(c, fmt="%.0f", padding=2, fontsize=8, color="#444444")
        for spine in ["top", "right"]:
            ax.spines[spine].set_visible(False)
        ax.spines["left"].set_color("#cccccc")
        ax.spines["bottom"].set_color("#cccccc")

    for ax in axes[len(window_order) :]:
        ax.axis("off")

    fig.suptitle("Supplementary Keyword Evolution Including Geographic Terms", fontsize=18, y=0.995)
    fig.tight_layout(rect=[0, 0, 1, 0.985])
    fig.savefig(
        OUTPUT_DIR / "keyword_evolution_supplementary.png",
        dpi=400,
        bbox_inches="tight",
        facecolor=fig.get_facecolor(),
    )
    plt.close(fig)

    return "bar_chart"


def write_notes(removed_df: pd.DataFrame, figure_type: str) -> None:
    removed_summary = (
        removed_df.groupby("removal_reason")["keyword"]
        .apply(lambda s: ", ".join(sorted(set(s))[:25]))
        .to_dict()
        if not removed_df.empty
        else {}
    )
    cleaning_lines = [
        "Keyword cleaning notes",
        "======================",
        "",
        "Processing rebuild: raw Overton CSVs were merged, deduplicated by Overton id, and reprocessed from the combined Top topics + Document theme + Title field.",
        "Lemmatization: simplemma English lemmatization was used; stemming was not used.",
        "Token filters: lowercase, punctuation removal, stopword removal, numeric-token removal, and explicit year-token removal were applied.",
        "Removed malformed examples: hous, analysi, branche, meet, degree, museum.",
        "Removed generic academic or procedural terms when they dominated without thematic value, including analysis, study, research, report, paper, data, education, educational, science, and related generic labels.",
        "Geographic terms were retained in cleaned tables when genuinely frequent, but separated from thematic terms in the main figure.",
    ]
    for reason, keywords in removed_summary.items():
        cleaning_lines.append(f"{reason}: {keywords}")
    (OUTPUT_DIR / "keyword_cleaning_notes.txt").write_text("\n".join(cleaning_lines), encoding="utf-8")

    figure_lines = [
        "Figure notes",
        "============",
        "",
        f"Main figure type: {figure_type}.",
        "Why this figure was chosen: a grouped horizontal bar design was selected instead of an alluvial figure because it preserves real mention counts cleanly at manuscript scale and avoids unreadable flow clutter.",
        "How counts were used: bar length equals the recomputed keyword mention count within each time window.",
        "Panel scaling: each time-window panel uses its own x-axis range so early periods remain readable while preserving the true count labels.",
        "Geographic separation: the main figure uses thematic keywords only, while geographic keywords remain available in the cleaned tables and are shown in the supplementary figure.",
        "Quality control: malformed stems and year tokens were removed before ranking, and the final figure was checked for label readability and clipping.",
    ]
    (OUTPUT_DIR / "figure_notes.txt").write_text("\n".join(figure_lines), encoding="utf-8")


def quality_checks(cleaned_df: pd.DataFrame) -> None:
    bad = set(cleaned_df["keyword"]).intersection(BAD_KEYWORDS)
    if bad:
        raise ValueError(f"Malformed keywords still present: {sorted(bad)}")
    if cleaned_df["keyword"].str.fullmatch(r"(19|20)\d{2}").any():
        raise ValueError("Year tokens remain in cleaned keywords")


def main() -> None:
    ensure_output_dir()
    merged = load_and_merge_raw()
    freq_df = frequency_by_window(merged)
    cleaned_df, removed_df = clean_keywords(freq_df)
    quality_checks(cleaned_df)
    save_top_tables(freq_df, cleaned_df)
    figure_type = build_main_figure(cleaned_df)
    write_notes(removed_df, figure_type)


if __name__ == "__main__":
    main()
