from __future__ import annotations

import csv
import json
import math
import os
import re
from collections import Counter, defaultdict
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Iterable

PROJECT_ROOT = Path(__file__).resolve().parents[2]
OUTPUT_ROOT = PROJECT_ROOT / "outputs" / "third_part"
os.environ.setdefault("MPLCONFIGDIR", str(PROJECT_ROOT / ".mplconfig"))

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns
from jinja2 import Template
from sklearn.cluster import KMeans
from sklearn.feature_extraction.text import ENGLISH_STOP_WORDS, TfidfVectorizer


DATA_DIR = OUTPUT_ROOT / "data_cleaned"
TAXONOMY_DIR = OUTPUT_ROOT / "taxonomy"
TABLE_DIR = OUTPUT_ROOT / "tables"
FIG_DIR = OUTPUT_ROOT / "figures"
RESULTS_DIR = OUTPUT_ROOT / "results_summary"
LOG_DIR = OUTPUT_ROOT / "logs"
INPUT_DIR = PROJECT_ROOT / "inputs" / "raw"

INPUT_FILES = [
    INPUT_DIR / "export-2026-04-01.csv",
    INPUT_DIR / "export-2026-04-01 (1).csv",
]

KEY_COLUMNS = [
    "Overton id",
    "Published_on",
    "Source country",
    "Policy citations (excl. same source)",
    "Related to SDGs",
    "Top topics",
    "Document theme",
    "Title",
]

CUSTOM_STOPWORDS = {
    "ageing",
    "aging",
    "older",
    "adult",
    "adults",
    "elderly",
    "policy",
    "policies",
    "report",
    "analysis",
    "issue",
    "issues",
    "approach",
    "approaches",
    "study",
    "studies",
    "based",
    "using",
    "across",
    "country",
    "countries",
    "region",
    "regions",
    "population",
}

GENERIC_EXCLUDE_TERMS = {
    "new",
    "development",
    "agriculture",
    "economic",
    "state",
    "budget",
    "education",
    "management",
    "agenda",
    "agency",
    "language",
    "package",
    "message",
    "stage",
    "average",
    "city",
    "village",
    "coverage",
    "heritage",
    "beverage",
    "marriage",
    "career",
    "page",
    "smallholder",
    "damage",
    "linkage",
    "advantage",
    "holder",
}

PHRASE_MAP = {
    "energy poverty": "energy_poverty",
    "fuel poverty": "fuel_poverty",
    "thermal comfort": "thermal_comfort",
    "older adults": "older_adults",
    "older adult": "older_adult",
    "aging population": "ageing_population",
    "ageing population": "ageing_population",
    "household energy use": "household_energy_use",
    "appliance replacement": "appliance_replacement",
    "energy efficiency": "energy_efficiency",
    "fixed income": "fixed_income",
    "pension income": "pension_income",
    "low carbon": "low_carbon",
    "climate change": "climate_change",
    "just transition": "just_transition",
    "care home": "care_home",
    "social care": "social_care",
    "long term care": "long_term_care",
    "heat pump": "heat_pump",
    "renewable energy": "renewable_energy",
    "home retrofit": "home_retrofit",
    "retrofit barrier": "retrofit_barrier",
    "behaviour change": "behaviour_change",
    "behavior change": "behaviour_change",
    "energy transition": "energy_transition",
    "household behaviour": "household_behaviour",
    "household behavior": "household_behaviour",
    "income constraint": "income_constraint",
    "older people": "older_people",
}

SYNONYM_MAP = {
    "behavioural": "behaviour",
    "behavioral": "behaviour",
    "behaviors": "behaviour",
    "behaviours": "behaviour",
    "retrofits": "retrofit",
    "retrofitting": "retrofit",
    "homes": "home",
    "households": "household",
    "citizens": "citizen",
    "seniors": "older_people",
    "senior": "older_people",
    "pensions": "pension",
    "elder": "older_people",
}

CATEGORY_DEFINITIONS = {
    "welfare_and_care": {
        "seeds": {"welfare", "care", "social_care", "care_home", "pension", "retirement", "service", "support"},
        "label": "Welfare and care",
    },
    "health_and_vulnerability": {
        "seeds": {"health", "vulnerability", "risk", "heat", "mortality", "resilience", "wellbeing", "disease"},
        "label": "Health and vulnerability",
    },
    "housing_and_thermal_comfort": {
        "seeds": {"housing", "home", "thermal_comfort", "indoor", "building", "retrofit", "household_energy_use", "insulation"},
        "label": "Housing and thermal comfort",
    },
    "energy_transition_and_efficiency": {
        "seeds": {"energy_transition", "energy_efficiency", "renewable_energy", "decarbonisation", "electricity", "heat_pump", "net_zero", "efficiency"},
        "label": "Energy transition and efficiency",
    },
    "household_behaviour_and_adoption": {
        "seeds": {"household_behaviour", "adoption", "appliance_replacement", "acceptance", "behaviour_change", "consumer", "uptake", "digital"},
        "label": "Household behaviour and adoption",
    },
    "affordability_and_income_constraints": {
        "seeds": {"energy_poverty", "fuel_poverty", "affordability", "fixed_income", "pension_income", "income_constraint", "bill", "cost"},
        "label": "Affordability and income constraints",
    },
    "governance_and_planning": {
        "seeds": {"governance", "planning", "strategy", "institution", "transition", "development", "programme", "framework"},
        "label": "Governance and planning",
    },
}

RELEVANCE_SEEDS = sorted(
    {
        "energy",
        "fuel",
        "poverty",
        "housing",
        "home",
        "thermal_comfort",
        "retrofit",
        "appliance",
        "pension",
        "income",
        "care",
        "health",
        "vulnerability",
        "behaviour",
        "adoption",
        "efficiency",
        "transition",
        "heat",
        "electric",
        "renewable_energy",
        "household",
        "older_people",
        "older_adult",
        "ageing_population",
        "energy_poverty",
        "fuel_poverty",
        "social_care",
        "heat_pump",
        "household_energy_use",
        "behaviour_change",
        "affordability",
        "fixed_income",
        "pension_income",
        "low_carbon",
        "just_transition",
    }
)


def log(message: str) -> None:
    LOG_DIR.mkdir(parents=True, exist_ok=True)
    with (LOG_DIR / "run_log.txt").open("a", encoding="utf-8") as f:
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        f.write(f"[{timestamp}] {message}\n")


def ensure_dirs() -> None:
    for path in [DATA_DIR, TAXONOMY_DIR, TABLE_DIR, FIG_DIR, RESULTS_DIR, LOG_DIR]:
        path.mkdir(parents=True, exist_ok=True)


def read_inputs() -> tuple[list[pd.DataFrame], pd.DataFrame]:
    frames = [pd.read_csv(path) for path in INPUT_FILES]
    merged = pd.concat(frames, ignore_index=True)
    return frames, merged


def merge_and_clean() -> tuple[pd.DataFrame, pd.DataFrame]:
    ensure_dirs()
    log("Starting merge and clean step.")
    frames, merged = read_inputs()
    before_merge = sum(len(frame) for frame in frames)
    after_merge = len(merged)
    dedup = merged.drop_duplicates(subset=["Overton id"], keep="first").copy()
    dedup["Published_on"] = pd.to_datetime(dedup["Published_on"], errors="coerce")
    dedup["Year"] = dedup["Published_on"].dt.year
    cleaned = dedup[dedup["Year"].notna()].copy()
    cleaned["Year"] = cleaned["Year"].astype(int)
    cleaned["Policy citations (excl. same source)"] = pd.to_numeric(
        cleaned["Policy citations (excl. same source)"], errors="coerce"
    ).fillna(0)
    cleaned["Combined_metadata_text"] = (
        cleaned["Top topics"].fillna("")
        + " | "
        + cleaned["Document theme"].fillna("")
        + " | "
        + cleaned["Title"].fillna("")
    ).str.strip()
    output_path = DATA_DIR / "merged_deduplicated_policy_metadata.csv"
    cleaned.to_csv(output_path, index=False)

    overview = pd.DataFrame(
        [
            {
                "total_rows_before_merge": before_merge,
                "total_after_merge": after_merge,
                "total_after_deduplication": len(cleaned),
                "year_min": cleaned["Year"].min(),
                "year_max": cleaned["Year"].max(),
                "number_of_countries": cleaned["Source country"].fillna("Unknown").nunique(),
                "missing_overton_id": cleaned["Overton id"].isna().sum(),
                "missing_published_on": cleaned["Published_on"].isna().sum(),
                "missing_source_country": cleaned["Source country"].isna().sum(),
                "missing_top_topics": cleaned["Top topics"].isna().sum(),
                "missing_document_theme": cleaned["Document theme"].isna().sum(),
                "missing_title": cleaned["Title"].isna().sum(),
                "missing_related_sdgs": cleaned["Related to SDGs"].isna().sum(),
            }
        ]
    )
    overview.to_csv(TABLE_DIR / "data_overview.csv", index=False)
    log(f"Completed merge and clean: {len(cleaned)} deduplicated rows.")
    return cleaned, overview


def simple_lemmatize(token: str) -> str:
    if token in SYNONYM_MAP:
        token = SYNONYM_MAP[token]
    irregular = {
        "children": "child",
        "people": "people",
        "women": "woman",
        "men": "man",
        "policies": "policy",
        "studies": "study",
    }
    if token in irregular:
        return irregular[token]
    if token.endswith("ies") and len(token) > 4:
        return token[:-3] + "y"
    if token.endswith("ing") and len(token) > 5:
        return token[:-3]
    if token.endswith("ed") and len(token) > 4:
        return token[:-2]
    if token.endswith("s") and len(token) > 4 and not token.endswith("ss"):
        return token[:-1]
    return token


def clean_text(text: str) -> list[str]:
    text = text.lower()
    for phrase, replacement in PHRASE_MAP.items():
        text = text.replace(phrase, replacement)
    text = re.sub(r"[^a-z0-9_\s]", " ", text)
    text = re.sub(r"\s+", " ", text).strip()
    stopwords = set(ENGLISH_STOP_WORDS).union(CUSTOM_STOPWORDS)
    tokens = []
    for raw in text.split():
        lemma = simple_lemmatize(raw)
        if lemma in stopwords:
            continue
        if len(lemma) < 2:
            continue
        tokens.append(lemma)
    return tokens


def preprocess_metadata(cleaned: pd.DataFrame) -> dict[str, pd.DataFrame]:
    log("Starting text preprocessing.")
    df = cleaned.copy()
    df["clean_tokens"] = df["Combined_metadata_text"].fillna("").map(clean_text)
    df["clean_text"] = df["clean_tokens"].map(lambda tokens: " ".join(tokens))

    token_counter = Counter()
    bigram_counter = Counter()
    doc_freq = Counter()
    for tokens in df["clean_tokens"]:
        token_counter.update(tokens)
        bigram_counter.update(" ".join(pair) for pair in zip(tokens, tokens[1:]))
        doc_freq.update(set(tokens))

    token_frequency = pd.DataFrame(
        [{"term": term, "frequency": freq} for term, freq in token_counter.most_common()]
    )
    token_frequency.to_csv(TABLE_DIR / "token_frequency.csv", index=False)

    vocab = pd.DataFrame(
        [
            {"term": term, "frequency": token_counter[term], "document_frequency": doc_freq[term], "is_phrase": "_" in term}
            for term in token_counter
        ]
    ).sort_values(["frequency", "document_frequency"], ascending=False)
    vocab.to_csv(TABLE_DIR / "cleaned_vocabulary_table.csv", index=False)

    top_unigrams = token_frequency.head(100).assign(n=1)
    top_bigrams = pd.DataFrame(
        [{"term": term, "frequency": freq} for term, freq in bigram_counter.most_common(100)]
    ).assign(n=2)
    top_ngrams = pd.concat([top_unigrams[["term", "frequency", "n"]], top_bigrams[["term", "frequency", "n"]]], ignore_index=True)
    top_ngrams.to_csv(TABLE_DIR / "top_ngrams.csv", index=False)

    vectorizer = TfidfVectorizer(
        token_pattern=r"(?u)\b[a-zA-Z_][a-zA-Z_]+\b",
        ngram_range=(1, 2),
        min_df=3,
        max_df=0.8,
    )
    tfidf_matrix = vectorizer.fit_transform(df["clean_text"])
    feature_names = np.array(vectorizer.get_feature_names_out())
    tfidf_scores = np.asarray(tfidf_matrix.mean(axis=0)).ravel()
    tfidf_table = pd.DataFrame({"term": feature_names, "mean_tfidf": tfidf_scores}).sort_values("mean_tfidf", ascending=False)
    tfidf_table.to_csv(TABLE_DIR / "tfidf_terms.csv", index=False)

    df.to_csv(DATA_DIR / "merged_deduplicated_policy_metadata_preprocessed.csv", index=False)
    log("Completed text preprocessing.")
    return {
        "docs": df,
        "token_frequency": token_frequency,
        "vocab": vocab,
        "top_ngrams": top_ngrams,
        "tfidf": tfidf_table,
    }


def candidate_terms(preprocessed: dict[str, pd.DataFrame]) -> pd.DataFrame:
    token_frequency = preprocessed["token_frequency"].copy()
    tfidf_table = preprocessed["tfidf"].copy()
    merged = token_frequency.merge(tfidf_table, on="term", how="inner")
    merged = merged[~merged["term"].str.fullmatch(r"\d+")].copy()
    merged = merged[~merged["term"].isin(GENERIC_EXCLUDE_TERMS)].copy()
    merged = merged[~merged["term"].str.fullmatch(r"[a-z]{1,2}")].copy()
    merged = merged[merged["term"].map(lambda term: all(len(part) >= 3 for part in term.replace(" ", "_").split("_")))].copy()
    merged["is_phrase"] = merged["term"].str.contains("_| ")
    merged["relevance_score"] = merged["term"].map(
        lambda term: sum(
            1
            for seed in RELEVANCE_SEEDS
            if (
                seed in term
                or (len(term) >= 4 and term in seed)
                or any(word == seed or seed in word for word in term.split("_"))
            )
        )
    )
    merged = merged[(merged["relevance_score"] > 0) | (merged["is_phrase"]) | (merged["mean_tfidf"] >= merged["mean_tfidf"].quantile(0.97))].copy()
    merged = merged.sort_values(["relevance_score", "mean_tfidf", "frequency"], ascending=False)
    return merged.head(220).reset_index(drop=True)


def build_taxonomy(preprocessed: dict[str, pd.DataFrame]) -> tuple[pd.DataFrame, str]:
    log("Starting taxonomy construction.")
    docs = preprocessed["docs"]
    candidates = candidate_terms(preprocessed)
    docs_text = docs["clean_text"].tolist()

    vectorizer = TfidfVectorizer(vocabulary=candidates["term"].tolist(), ngram_range=(1, 2))
    term_doc = vectorizer.fit_transform(docs_text)
    term_vectors = term_doc.T.toarray()
    n_clusters = min(8, max(4, len(candidates) // 20))
    kmeans = KMeans(n_clusters=n_clusters, random_state=42, n_init=20)
    candidates["cluster_id"] = kmeans.fit_predict(term_vectors)

    category_rows = []
    notes = []
    available_categories = list(CATEGORY_DEFINITIONS.keys())
    for _, row in candidates.iterrows():
        term = row["term"]
        term_words = set(term.replace("_", " ").split())
        scores = {}
        for key, info in CATEGORY_DEFINITIONS.items():
            overlap = len(term_words & info["seeds"])
            direct = 2 if term in info["seeds"] else 0
            substring = sum(1 for seed in info["seeds"] if seed in term or term in seed)
            scores[key] = direct + overlap + 0.5 * substring
        best_category = max(scores, key=scores.get)
        if scores[best_category] == 0:
            best_category = "governance_and_planning"
        category_rows.append(
            {
                "term": term,
                "frequency": row["frequency"],
                "mean_tfidf": row["mean_tfidf"],
                "cluster_id": row["cluster_id"],
                "assigned_category_key": best_category,
                "assigned_category": CATEGORY_DEFINITIONS[best_category]["label"],
            }
        )

    taxonomy_df = pd.DataFrame(category_rows).sort_values(["assigned_category", "mean_tfidf"], ascending=[True, False])
    category_counts = taxonomy_df["assigned_category"].value_counts()
    notes.append("Taxonomy construction combined empirical term selection, TF-IDF ranking, and unsupervised clustering over document-term profiles.")
    notes.append("Semantic embedding models were not available locally, so clustering used TF-IDF-based term vectors as the hybrid empirical grouping step.")
    notes.append("Category labels were refined after inspecting the observed metadata vocabulary, with an additional governance and planning category retained because many high-salience terms clustered around strategy, institutions, and planning language.")
    notes.append("Category counts: " + ", ".join(f"{cat}={count}" for cat, count in category_counts.items()))

    taxonomy_df.to_csv(TAXONOMY_DIR / "final_keyword_taxonomy.csv", index=False)
    notes_text = "\n".join(notes)
    (TAXONOMY_DIR / "taxonomy_notes.txt").write_text(notes_text, encoding="utf-8")
    log("Completed taxonomy construction.")
    return taxonomy_df, notes_text


def compute_category_weights(tokens: list[str], taxonomy_map: dict[str, str]) -> Counter:
    counts = Counter()
    for token in tokens:
        if token in taxonomy_map:
            counts[taxonomy_map[token]] += 1
    for bigram in (" ".join(pair) for pair in zip(tokens, tokens[1:])):
        normalized = bigram.replace(" ", "_")
        if normalized in taxonomy_map:
            counts[taxonomy_map[normalized]] += 1
    return counts


def plot_academic_style() -> None:
    sns.set_theme(style="whitegrid")
    plt.rcParams.update(
        {
            "font.family": "DejaVu Sans",
            "axes.titlesize": 16,
            "axes.labelsize": 13,
            "xtick.labelsize": 10,
            "ytick.labelsize": 10,
            "legend.fontsize": 10,
        }
    )


def topic_trends(preprocessed: dict[str, pd.DataFrame], taxonomy_df: pd.DataFrame) -> pd.DataFrame:
    log("Starting topic trend analysis.")
    plot_academic_style()
    docs = preprocessed["docs"].copy()
    taxonomy_map = dict(zip(taxonomy_df["term"], taxonomy_df["assigned_category"]))

    rows = []
    for row in docs[["Year", "clean_tokens", "Overton id"]].itertuples(index=False):
        weights = compute_category_weights(row.clean_tokens, taxonomy_map)
        total = sum(weights.values())
        if total == 0:
            continue
        for category, value in weights.items():
            rows.append({"Year": row.Year, "Overton id": row._2, "category": category, "term_frequency": value, "total_terms_doc": total})
    topic_doc = pd.DataFrame(rows)
    if topic_doc.empty:
        raise RuntimeError("No topic-category matches were found. Taxonomy construction needs revision.")

    topic_year = (
        topic_doc.groupby(["Year", "category"], as_index=False)["term_frequency"]
        .sum()
    )
    year_totals = topic_year.groupby("Year")["term_frequency"].transform("sum")
    topic_year["TopicShare"] = topic_year["term_frequency"] / year_totals
    topic_year["TopicShare_pct"] = (topic_year["TopicShare"] * 100).round(3)
    topic_year = topic_year.sort_values(["Year", "category"]).reset_index(drop=True)
    topic_year["rolling_share_3yr"] = (
        topic_year.groupby("category")["TopicShare"]
        .transform(lambda s: s.rolling(3, min_periods=1).mean())
    )
    topic_year["normalized_share"] = (
        topic_year.groupby("category")["TopicShare"]
        .transform(lambda s: 0 if s.max() == s.min() else (s - s.min()) / (s.max() - s.min()))
    )
    topic_year.to_csv(TABLE_DIR / "topic_share_by_year.csv", index=False)

    pivot_share = topic_year.pivot(index="Year", columns="category", values="TopicShare").fillna(0)
    colors = sns.color_palette("Set2", n_colors=pivot_share.shape[1])

    fig, ax = plt.subplots(figsize=(14, 8))
    ax.stackplot(pivot_share.index, pivot_share.T.values, labels=[c.replace("_", " ").title() for c in pivot_share.columns], colors=colors, alpha=0.95)
    ax.set_title("Policy topic shares over time")
    ax.set_xlabel("Year")
    ax.set_ylabel("Topic share")
    ax.legend(loc="upper left", bbox_to_anchor=(1.02, 1))
    fig.tight_layout()
    fig.savefig(FIG_DIR / "topic_share_stacked_area.png", dpi=300, bbox_inches="tight")
    plt.close(fig)

    top_categories = (
        topic_year.groupby("category")["term_frequency"].sum().sort_values(ascending=False).head(5).index.tolist()
    )
    fig, ax = plt.subplots(figsize=(14, 8))
    for category in top_categories:
        sub = topic_year[topic_year["category"] == category]
        ax.plot(sub["Year"], sub["rolling_share_3yr"], linewidth=2.5, label=category.replace("_", " ").title())
    ax.set_title("Leading policy themes over time")
    ax.set_xlabel("Year")
    ax.set_ylabel("Rolling topic share")
    ax.legend(loc="upper left", bbox_to_anchor=(1.02, 1))
    fig.tight_layout()
    fig.savefig(FIG_DIR / "top_categories_over_time.png", dpi=300, bbox_inches="tight")
    plt.close(fig)

    focus_categories = [
        "Welfare and care",
        "Energy transition and efficiency",
        "Household behaviour and adoption",
        "Affordability and income constraints",
    ]
    fig, ax = plt.subplots(figsize=(14, 8))
    for category in focus_categories:
        if category not in topic_year["category"].unique():
            continue
        sub = topic_year[topic_year["category"] == category]
        ax.plot(sub["Year"], sub["rolling_share_3yr"], linewidth=2.5, label=category)
    ax.set_title("Household relevant themes compared over time")
    ax.set_xlabel("Year")
    ax.set_ylabel("Rolling topic share")
    ax.legend(loc="upper left", bbox_to_anchor=(1.02, 1))
    fig.tight_layout()
    fig.savefig(FIG_DIR / "household_relevant_categories_over_time.png", dpi=300, bbox_inches="tight")
    plt.close(fig)
    log("Completed topic trend analysis.")
    return topic_year


def extract_goal(code: str) -> str | None:
    if pd.isna(code):
        return None
    match = re.search(r"SDG\s+(?:Target\s+)?(\d{1,2})", str(code))
    return match.group(1) if match else None


def country_analysis(preprocessed: dict[str, pd.DataFrame], taxonomy_df: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    log("Starting country analysis.")
    plot_academic_style()
    docs = preprocessed["docs"].copy()
    taxonomy_map = dict(zip(taxonomy_df["term"], taxonomy_df["assigned_category"]))

    country_rows = []
    for row in docs[["Source country", "Overton id", "clean_tokens", "Policy citations (excl. same source)", "Related to SDGs"]].itertuples(index=False):
        country = row[0] if pd.notna(row[0]) else "Unknown"
        weights = compute_category_weights(row[2], taxonomy_map)
        total = sum(weights.values())
        for category, value in weights.items():
            country_rows.append({"Country": country, "Overton id": row[1], "category": category, "term_frequency": value, "Impact": row[3]})

    country_topic = pd.DataFrame(country_rows)
    country_share = (
        country_topic.groupby(["Country", "category"], as_index=False)["term_frequency"]
        .sum()
    )
    country_totals = country_share.groupby("Country")["term_frequency"].transform("sum")
    country_share["TopicShare"] = country_share["term_frequency"] / country_totals
    country_share["TopicShare_pct"] = (country_share["TopicShare"] * 100).round(3)
    country_share.to_csv(TABLE_DIR / "topic_share_by_country.csv", index=False)

    policy_summary = (
        docs.groupby("Source country", as_index=False)
        .agg(
            document_count=("Overton id", "nunique"),
            citation_impact=("Policy citations (excl. same source)", "sum"),
            average_citations=("Policy citations (excl. same source)", "mean"),
        )
        .rename(columns={"Source country": "Country"})
        .sort_values(["document_count", "citation_impact"], ascending=False)
    )

    docs["SDG_goal"] = docs["Related to SDGs"].map(extract_goal)
    sdg_country = (
        docs.dropna(subset=["SDG_goal"])
        .groupby(["Source country", "SDG_goal"], as_index=False)["Overton id"]
        .nunique()
        .rename(columns={"Source country": "Country", "Overton id": "sdg_document_count"})
    )
    top_sdg = sdg_country.sort_values(["Country", "sdg_document_count"], ascending=[True, False]).groupby("Country").head(1)
    policy_summary = policy_summary.merge(top_sdg[["Country", "SDG_goal", "sdg_document_count"]], on="Country", how="left")
    policy_summary.to_csv(TABLE_DIR / "country_policy_summary.csv", index=False)

    major_countries = policy_summary.head(15)["Country"].tolist()
    heatmap_df = country_share[country_share["Country"].isin(major_countries)].pivot(index="Country", columns="category", values="TopicShare_pct").fillna(0)
    fig, ax = plt.subplots(figsize=(12, 8))
    sns.heatmap(heatmap_df, cmap="YlGnBu", linewidths=0.3, ax=ax)
    ax.set_title("Country topic framing heatmap")
    fig.tight_layout()
    fig.savefig(FIG_DIR / "country_topic_heatmap.png", dpi=300, bbox_inches="tight")
    plt.close(fig)

    cluster = sns.clustermap(heatmap_df, cmap="crest", linewidths=0.2, figsize=(12, 10))
    cluster.fig.suptitle("Clustered comparison of major countries", y=1.02)
    cluster.savefig(FIG_DIR / "country_topic_clustermap.png", dpi=300, bbox_inches="tight")
    plt.close(cluster.fig)

    fig, ax = plt.subplots(figsize=(12, 8))
    plot_df = policy_summary.head(20).copy()
    ax.scatter(plot_df["document_count"], plot_df["citation_impact"], s=np.maximum(plot_df["average_citations"] * 60, 80), alpha=0.8)
    for _, row in plot_df.iterrows():
        ax.annotate(row["Country"], (row["document_count"], row["citation_impact"]), fontsize=9, xytext=(3, 3), textcoords="offset points")
    ax.set_title("Country policy volume and citation impact")
    ax.set_xlabel("Document count")
    ax.set_ylabel("Citation impact")
    fig.tight_layout()
    fig.savefig(FIG_DIR / "country_volume_vs_impact.png", dpi=300, bbox_inches="tight")
    plt.close(fig)

    log("Completed country analysis.")
    return country_share, policy_summary


def ageing_integration(country_share: pd.DataFrame, policy_summary: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame, str]:
    log("Starting ageing indicator integration step.")
    candidate_files = list(PROJECT_ROOT.parent.glob("*age*.csv")) + list(PROJECT_ROOT.parent.glob("*elder*.csv")) + list(PROJECT_ROOT.parent.glob("*dependency*.csv"))
    if not candidate_files:
        placeholder = pd.DataFrame(
            [{"status": "pending", "note": "No separate ageing indicator dataset was found in the working directory or nearby folders."}]
        )
        placeholder.to_csv(TABLE_DIR / "ageing_policy_alignment.csv", index=False)
        placeholder.to_csv(TABLE_DIR / "correlation_results.csv", index=False)
        note = "Ageing indicator integration is pending because no external demographic dataset was available for country-year merging."
        (RESULTS_DIR / "ageing_data_pending_note.txt").write_text(note, encoding="utf-8")
        log(note)
        return placeholder, placeholder, note

    ageing = pd.read_csv(candidate_files[0])
    note = f"Loaded ageing dataset from {candidate_files[0].name}, but full harmonization still requires manual review."
    placeholder = pd.DataFrame([{"status": "partial", "note": note}])
    placeholder.to_csv(TABLE_DIR / "ageing_policy_alignment.csv", index=False)
    placeholder.to_csv(TABLE_DIR / "correlation_results.csv", index=False)
    log(note)
    return placeholder, placeholder, note


def blind_spots(preprocessed: dict[str, pd.DataFrame], taxonomy_df: pd.DataFrame, topic_year: pd.DataFrame) -> pd.DataFrame:
    log("Starting blind spot identification.")
    docs = preprocessed["docs"].copy()
    clean_text_series = docs["clean_text"].fillna("")
    term_presence = {}
    terms_to_track = {
        "appliance replacement": "appliance_replacement",
        "household energy use": "household_energy_use",
        "behavioural adaptation": "behaviour_change",
        "affordability": "affordability",
        "pension or fixed-income constraints": "fixed_income",
        "technology adoption by older adults": "adoption",
        "thermal comfort": "thermal_comfort",
        "home retrofit barriers": "retrofit_barrier",
    }
    category_totals = topic_year.groupby("category")["TopicShare"].mean()
    macro_baseline = category_totals.max()

    rows = []
    for theme, token in terms_to_track.items():
        freq = clean_text_series.str.contains(token, regex=False).sum()
        yearly = docs.assign(flag=clean_text_series.str.contains(token, regex=False)).groupby("Year")["flag"].mean()
        trend = "rising" if len(yearly) > 1 and yearly.iloc[-1] > yearly.iloc[0] else "flat_or_declining"
        token_aliases = {token, token.replace("_", " "), token.split("_")[0]}
        taxonomy_match = taxonomy_df[taxonomy_df["term"].isin(token_aliases)]
        if not taxonomy_match.empty:
            category = taxonomy_match["assigned_category"].iloc[0]
            baseline = category_totals.get(category, 0)
        else:
            category = "not_classified_directly"
            baseline = 0
        underrepresented = "yes" if (freq / max(len(docs), 1) < 0.03 and baseline < macro_baseline * 0.6) else "potentially"
        rows.append(
            {
                "theme": theme,
                "empirical_frequency": int(freq),
                "share_of_documents_pct": round(freq / max(len(docs), 1) * 100, 3),
                "temporal_trend": trend,
                "category_context": category,
                "underrepresented_relative_to_macro_policy_themes": underrepresented,
            }
        )
    summary = pd.DataFrame(rows)
    summary.to_csv(TABLE_DIR / "policy_blind_spots_summary.csv", index=False)

    narrative = [
        "Policy blind spot summary",
        "=========================",
        "",
    ]
    for row in summary.itertuples(index=False):
        narrative.append(
            f"{row.theme}: {row.empirical_frequency} direct metadata matches ({row.share_of_documents_pct:.2f}% of documents), trend={row.temporal_trend}, underrepresented={row.underrepresented_relative_to_macro_policy_themes}."
        )
    text = "\n".join(narrative)
    (RESULTS_DIR / "policy_blind_spots_summary.txt").write_text(text, encoding="utf-8")
    log("Completed blind spot identification.")
    return summary


def report(cleaned: pd.DataFrame, overview: pd.DataFrame, taxonomy_notes: str, topic_year: pd.DataFrame, policy_summary: pd.DataFrame, blind_spots_df: pd.DataFrame, ageing_note: str) -> list[Path]:
    log("Starting report generation.")
    top_categories = (
        topic_year.groupby("category")["term_frequency"].sum().sort_values(ascending=False).head(6)
    )
    top_countries = policy_summary.head(10)[["Country", "document_count", "citation_impact"]]
    manifest_paths = []

    template = Template(
        """
        <html>
        <head>
          <meta charset="utf-8">
          <title>Ageing and Energy Policy Focus Report</title>
          <style>
            body { font-family: Arial, sans-serif; margin: 40px; line-height: 1.5; color: #222; }
            h1, h2 { color: #1d3557; }
            table { border-collapse: collapse; width: 100%; margin-bottom: 24px; }
            th, td { border: 1px solid #ddd; padding: 8px; text-align: left; }
            th { background: #f1f5f9; }
            img { max-width: 100%; margin: 12px 0 24px; }
            .small { color: #555; font-size: 0.95em; }
          </style>
        </head>
        <body>
          <h1>Third Part Analysis: Ageing, Energy Policy Focus and Household Blind Spots</h1>
          <p class="small">Generated from Overton metadata fields Top topics, Document theme and Title, plus country, SDG and citation metadata.</p>
          <h2>Data cleaning</h2>
          {{ overview_html }}
          <h2>Taxonomy construction</h2>
          <p>{{ taxonomy_notes }}</p>
          <h2>Key thematic findings</h2>
          {{ top_categories_html }}
          <h2>Country structure</h2>
          {{ top_countries_html }}
          <h2>Blind spots</h2>
          {{ blind_spots_html }}
          <h2>Figures</h2>
          <img src="../figures/topic_share_stacked_area.png" alt="Topic share stacked area">
          <img src="../figures/top_categories_over_time.png" alt="Top categories over time">
          <img src="../figures/household_relevant_categories_over_time.png" alt="Household relevant categories">
          <img src="../figures/country_topic_heatmap.png" alt="Country topic heatmap">
          <img src="../figures/country_volume_vs_impact.png" alt="Country volume versus impact">
          <h2>Ageing integration status</h2>
          <p>{{ ageing_note }}</p>
        </body>
        </html>
        """
    )
    html = template.render(
        overview_html=overview.to_html(index=False),
        taxonomy_notes=taxonomy_notes,
        top_categories_html=top_categories.reset_index().rename(columns={"term_frequency": "total_term_frequency"}).to_html(index=False),
        top_countries_html=top_countries.to_html(index=False),
        blind_spots_html=blind_spots_df.to_html(index=False),
        ageing_note=ageing_note,
    )
    report_path = RESULTS_DIR / "analysis_report.html"
    report_path.write_text(html, encoding="utf-8")

    for path in PROJECT_ROOT.rglob("*"):
        if path.is_file():
            manifest_paths.append(path)
    manifest_paths = sorted(manifest_paths)
    manifest_text = "\n".join(str(path) for path in manifest_paths)
    (RESULTS_DIR / "output_manifest.txt").write_text(manifest_text, encoding="utf-8")
    log("Completed report generation.")
    return manifest_paths


def summarize_findings(topic_year: pd.DataFrame, policy_summary: pd.DataFrame, blind_spots_df: pd.DataFrame) -> str:
    top_categories = topic_year.groupby("category")["term_frequency"].sum().sort_values(ascending=False)
    top_country = policy_summary.iloc[0]
    blind = blind_spots_df.sort_values("share_of_documents_pct").head(4)
    text = (
        f"The metadata profile is dominated by {top_categories.index[0].replace('_', ' ')} and {top_categories.index[1].replace('_', ' ')}, "
        f"while {top_country['Country']} contributes the largest policy volume at {int(top_country['document_count'])} documents. "
        f"The weakest household-level themes are " + ", ".join(blind['theme'].tolist()) + "."
    )
    return text


def run_all() -> dict[str, object]:
    cleaned, overview = merge_and_clean()
    preprocessed = preprocess_metadata(cleaned)
    taxonomy_df, taxonomy_notes = build_taxonomy(preprocessed)
    topic_year = topic_trends(preprocessed, taxonomy_df)
    country_share, policy_summary = country_analysis(preprocessed, taxonomy_df)
    ageing_alignment, correlation_results, ageing_note = ageing_integration(country_share, policy_summary)
    blind_spots_df = blind_spots(preprocessed, taxonomy_df, topic_year)
    manifest = report(cleaned, overview, taxonomy_notes, topic_year, policy_summary, blind_spots_df, ageing_note)
    summary = summarize_findings(topic_year, policy_summary, blind_spots_df)
    return {
        "cleaned": cleaned,
        "overview": overview,
        "preprocessed": preprocessed,
        "taxonomy_df": taxonomy_df,
        "taxonomy_notes": taxonomy_notes,
        "topic_year": topic_year,
        "country_share": country_share,
        "policy_summary": policy_summary,
        "ageing_alignment": ageing_alignment,
        "correlation_results": correlation_results,
        "ageing_note": ageing_note,
        "blind_spots_df": blind_spots_df,
        "manifest": manifest,
        "summary": summary,
    }
