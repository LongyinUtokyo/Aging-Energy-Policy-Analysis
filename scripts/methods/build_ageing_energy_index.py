from __future__ import annotations

import re
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


ROOT = Path(__file__).resolve().parents[2]
OUTPUT_DIR = ROOT / "outputs" / "methods"
INPUT_CSV = ROOT / "inputs" / "auxiliary" / "overton_sdg_cleaned_merged.csv"
WEIGHTS_XLSX = OUTPUT_DIR / "ageing_energy_target_weights.xlsx"
OUTPUT_XLSX = OUTPUT_DIR / "ageing_energy_index_full.xlsx"
OUTPUT_CSV = OUTPUT_DIR / "ageing_energy_doc_index.csv"
METHODS_TXT = OUTPUT_DIR / "ageing_energy_index_methods.txt"

TARGET_PATTERN = re.compile(r"^SDG Target\s+(\d+(?:\.[0-9a-zA-Z]+)?)$", re.IGNORECASE)

TARGET_TEXTS = {
    "1.3": "Implement nationally appropriate social protection systems and measures for all, including floors, and by 2030 achieve substantial coverage of the poor and the vulnerable",
    "1.4": "By 2030, ensure that all men and women, in particular the poor and the vulnerable, have equal rights to economic resources, as well as access to basic services, ownership and control over land and other forms of property, inheritance, natural resources, appropriate new technology and financial services, including microfinance",
    "1.5": "By 2030, build the resilience of the poor and those in vulnerable situations and reduce their exposure and vulnerability to climate-related extreme events and other economic, social and environmental shocks and disasters",
    "2.2": "By 2030, end all forms of malnutrition, including achieving internationally agreed targets, and address the nutritional needs of adolescent girls, pregnant and lactating women and older persons",
    "3.4": "By 2030, reduce by one third premature mortality from non-communicable diseases through prevention and treatment and promote mental health and well-being",
    "3.8": "Achieve universal health coverage, including financial risk protection, access to quality essential health-care services and access to safe, effective, quality and affordable essential medicines and vaccines for all",
    "3.9": "By 2030, substantially reduce the number of deaths and illnesses from hazardous chemicals and air, water and soil pollution and contamination",
    "3.d": "Strengthen the capacity of all countries for early warning, risk reduction and management of national and global health risks",
    "6.1": "By 2030, achieve universal and equitable access to safe and affordable drinking water for all",
    "6.2": "By 2030, achieve access to adequate and equitable sanitation and hygiene for all and end open defecation, paying special attention to the needs of women and girls and those in vulnerable situations",
    "6.4": "By 2030, substantially increase water-use efficiency across all sectors and ensure sustainable withdrawals and supply of freshwater to address water scarcity and substantially reduce the number of people suffering from water scarcity",
    "7.1": "By 2030, ensure universal access to affordable, reliable and modern energy services",
    "7.2": "By 2030, increase substantially the share of renewable energy in the global energy mix",
    "7.3": "By 2030, double the global rate of improvement in energy efficiency",
    "7.a": "By 2030, enhance international cooperation to facilitate access to clean energy research and technology, including renewable energy, energy efficiency and cleaner fossil-fuel technology, and promote investment in energy infrastructure and clean energy technology",
    "7.b": "By 2030, expand infrastructure and upgrade technology for supplying modern and sustainable energy services for all in developing countries",
    "9.1": "Develop quality, reliable, sustainable and resilient infrastructure to support economic development and human well-being, with a focus on affordable and equitable access for all",
    "9.4": "By 2030, upgrade infrastructure and retrofit industries to make them sustainable, with increased resource-use efficiency and greater adoption of clean and environmentally sound technologies and industrial processes",
    "10.2": "By 2030, empower and promote the social, economic and political inclusion of all, irrespective of age, sex, disability, race, ethnicity, origin, religion or economic or other status",
    "10.4": "Adopt policies, especially fiscal, wage and social protection policies, and progressively achieve greater equality",
    "11.1": "By 2030, ensure access for all to adequate, safe and affordable housing and basic services and upgrade slums",
    "11.2": "By 2030, provide access to safe, affordable, accessible and sustainable transport systems for all, improving road safety, notably by expanding public transport, with special attention to the needs of those in vulnerable situations, women, children, persons with disabilities and older persons",
    "11.5": "By 2030, significantly reduce the number of deaths and the number of people affected and substantially decrease the direct economic losses caused by disasters, with a focus on protecting the poor and people in vulnerable situations",
    "11.6": "By 2030, reduce the adverse per capita environmental impact of cities, including by paying special attention to air quality and municipal and other waste management",
    "11.7": "By 2030, provide universal access to safe, inclusive and accessible, green and public spaces, in particular for women and children, older persons and persons with disabilities",
    "11.b": "By 2020, substantially increase the number of cities and human settlements adopting and implementing integrated policies and plans towards inclusion, resource efficiency, mitigation and adaptation to climate change, resilience to disasters, and holistic disaster risk management",
    "12.c": "Rationalize inefficient fossil-fuel subsidies that encourage wasteful consumption while protecting the poor and the affected communities",
    "13.1": "Strengthen resilience and adaptive capacity to climate-related hazards and natural disasters in all countries",
    "13.2": "Integrate climate change measures into national policies, strategies and planning",
    "13.3": "Improve education, awareness-raising and human and institutional capacity on climate change mitigation, adaptation, impact reduction and early warning",
    "16.6": "Develop effective, accountable and transparent institutions at all levels",
    "16.7": "Ensure responsive, inclusive, participatory and representative decision-making at all levels",
    "16.b": "Promote and enforce non-discriminatory laws and policies for sustainable development",
    "17.18": "Enhance support to increase significantly the availability of high-quality, timely and reliable data disaggregated by income, gender, age, race, ethnicity, migratory status, disability and geographic location",
}

AGEING_CORPUS = (
    "ageing aging older persons elderly later-life old age dependency frailty disability "
    "health vulnerability care accessibility inclusion social protection affordable housing "
    "transport public services dignity"
)
ENERGY_CORPUS = (
    "energy transition electricity fuel heating cooling clean energy modern energy services "
    "energy efficiency renewable energy affordability energy poverty infrastructure climate "
    "resilience adaptation pollution air quality disaster risk"
)
COMBINED_CORPUS = f"{AGEING_CORPUS} {ENERGY_CORPUS}"


def parse_sdg_targets(value: object) -> list[str]:
    if pd.isna(value):
        return []
    text = str(value).strip()
    if not text:
        return []

    codes: list[str] = []
    seen: set[str] = set()
    for token in text.split("|"):
        token = token.strip()
        match = TARGET_PATTERN.match(token)
        if not match:
            continue
        code = match.group(1)
        if code not in seen:
            codes.append(code)
            seen.add(code)
    return codes


def phase_from_year(year: object) -> str | None:
    if pd.isna(year):
        return None
    year = int(year)
    if 1869 <= year <= 1947:
        return "Phase 1"
    if 1948 <= year <= 1971:
        return "Phase 2"
    if 1972 <= year <= 1993:
        return "Phase 3"
    if 1994 <= year <= 2024:
        return "Phase 4"
    return None


def build_weights() -> pd.DataFrame:
    target_df = pd.DataFrame(
        {
            "SDG_target": list(TARGET_TEXTS.keys()),
            "target_text": list(TARGET_TEXTS.values()),
        }
    )

    corpus = [COMBINED_CORPUS] + target_df["target_text"].tolist()
    vectorizer = TfidfVectorizer(stop_words="english", ngram_range=(1, 2))
    matrix = vectorizer.fit_transform(corpus)
    reference_vector = matrix[0]
    target_matrix = matrix[1:]
    similarities = cosine_similarity(target_matrix, reference_vector).ravel()

    sim_min = similarities.min()
    sim_max = similarities.max()
    if np.isclose(sim_max, sim_min):
        normalized = np.ones_like(similarities)
    else:
        normalized = (similarities - sim_min) / (sim_max - sim_min)

    target_df["raw_similarity"] = similarities
    target_df["relevance_weight"] = normalized
    target_df["SDG_goal"] = target_df["SDG_target"].str.split(".").str[0]
    target_df = target_df.sort_values(
        ["relevance_weight", "SDG_target"], ascending=[False, True]
    ).reset_index(drop=True)
    return target_df


def build_doc_index(weights_df: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    df = pd.read_csv(INPUT_CSV)
    df["Year"] = pd.to_numeric(df["Year"], errors="coerce")
    df["Phase"] = df["Year"].apply(phase_from_year)
    df["Impact"] = pd.to_numeric(df["Impact"], errors="coerce").fillna(0.0)
    df["Source country"] = df["Country"].fillna("Unknown").replace("", "Unknown")

    weight_map = dict(
        zip(weights_df["SDG_target"].astype(str), weights_df["relevance_weight"].astype(float))
    )

    parsed_targets = df["Related to SDGs"].apply(parse_sdg_targets)
    matched_targets = parsed_targets.apply(lambda codes: [code for code in codes if code in weight_map])
    target_weights = matched_targets.apply(lambda codes: [float(weight_map[code]) for code in codes])

    doc_index = pd.DataFrame(
        {
            "Overton id": df["Overton id"],
            "Title": df["Title"],
            "Source country": df["Source country"],
            "Published_on": df["Published_on"],
            "Year": df["Year"],
            "Phase": df["Phase"],
            "Related to SDGs": df["Related to SDGs"],
            "Impact": df["Impact"],
            "matched SDG targets": matched_targets.apply(lambda xs: "|".join(xs)),
            "target weights used": target_weights.apply(
                lambda xs: "|".join(f"{x:.6f}" for x in xs)
            ),
        }
    )
    doc_index["matched_target_count"] = matched_targets.apply(len)
    doc_index["AgeingEnergy_SDG_RawSum"] = target_weights.apply(sum).astype(float)
    doc_index["AgeingEnergy_SDG_Index"] = np.where(
        doc_index["matched_target_count"] > 0,
        doc_index["AgeingEnergy_SDG_RawSum"] / doc_index["matched_target_count"],
        np.nan,
    )
    doc_index["Has_matched_target"] = doc_index["matched_target_count"] > 0

    goal_records: list[dict[str, object]] = []
    for overton_id, country, year, phase, impact, doc_score, codes in zip(
        doc_index["Overton id"],
        doc_index["Source country"],
        doc_index["Year"],
        doc_index["Phase"],
        df["Impact"],
        doc_index["AgeingEnergy_SDG_Index"],
        matched_targets,
    ):
        for code in codes:
            goal_records.append(
                {
                    "Overton id": overton_id,
                    "Source country": country,
                    "Year": year,
                    "Phase": phase,
                    "SDG_target": code,
                    "SDG_goal": code.split(".")[0],
                    "relevance_weight": weight_map[code],
                    "Impact": impact,
                    "AgeingEnergy_SDG_Index": doc_score,
                }
            )

    goal_long = pd.DataFrame(goal_records)
    return doc_index, goal_long


def summarize(grouped: pd.core.groupby.generic.DataFrameGroupBy, key_name: str) -> pd.DataFrame:
    summary = (
        grouped["AgeingEnergy_SDG_Index"]
        .agg(document_count="count", mean_index="mean", median_index="median", std_index="std", sum_index="sum")
        .reset_index()
    )
    if key_name == "Phase":
        phase_order = {"Phase 1": 1, "Phase 2": 2, "Phase 3": 3, "Phase 4": 4}
        summary["_order"] = summary["Phase"].map(phase_order)
        summary = summary.sort_values("_order").drop(columns="_order")
    return summary


def main() -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    weights_df = build_weights()
    with pd.ExcelWriter(WEIGHTS_XLSX, engine="openpyxl") as writer:
        weights_df.to_excel(writer, sheet_name="target_relevance_weights", index=False)

    doc_index, goal_long = build_doc_index(weights_df)
    scored_docs = doc_index[doc_index["Has_matched_target"]].copy()

    country_index = summarize(scored_docs.groupby("Source country"), "Source country").rename(
        columns={"Source country": "Country"}
    )
    year_index = summarize(scored_docs.groupby("Year"), "Year").sort_values("Year")
    phase_index = summarize(scored_docs.groupby("Phase"), "Phase")
    country_phase_index = summarize(scored_docs.groupby(["Source country", "Phase"]), "Source country").rename(
        columns={"Source country": "Country"}
    )
    country_year_index = summarize(scored_docs.groupby(["Source country", "Year"]), "Source country").rename(
        columns={"Source country": "Country"}
    ).sort_values(["Country", "Year"])

    top_country_mean = country_index.sort_values(
        ["mean_index", "document_count", "Country"], ascending=[False, False, True]
    ).reset_index(drop=True)
    top_country_sum = country_index.sort_values(
        ["sum_index", "document_count", "Country"], ascending=[False, False, True]
    ).reset_index(drop=True)
    top_year_mean = year_index.sort_values(
        ["mean_index", "document_count", "Year"], ascending=[False, False, True]
    ).reset_index(drop=True)
    top_phase_mean = phase_index.sort_values(
        ["mean_index", "document_count"], ascending=[False, False]
    ).reset_index(drop=True)

    country_index_vs_impact = (
        scored_docs.groupby("Source country")
        .agg(
            mean_index=("AgeingEnergy_SDG_Index", "mean"),
            total_impact=("Impact", "sum"),
            average_impact=("Impact", "mean"),
        )
        .reset_index()
        .rename(columns={"Source country": "Country"})
        .sort_values(["mean_index", "total_impact", "Country"], ascending=[False, False, True])
        .reset_index(drop=True)
    )

    country_index_vs_count = (
        scored_docs.groupby("Source country")
        .agg(
            mean_index=("AgeingEnergy_SDG_Index", "mean"),
            document_count=("Overton id", "count"),
        )
        .reset_index()
        .rename(columns={"Source country": "Country"})
        .sort_values(["mean_index", "document_count", "Country"], ascending=[False, False, True])
        .reset_index(drop=True)
    )

    if goal_long.empty:
        goal_index_summary = pd.DataFrame(
            columns=[
                "SDG_goal",
                "document_count",
                "matched_target_links",
                "mean_target_weight",
                "median_target_weight",
                "sum_target_weight",
                "mean_doc_index",
                "total_impact",
                "average_impact",
            ]
        )
    else:
        goal_index_summary = (
            goal_long.groupby("SDG_goal")
            .agg(
                document_count=("Overton id", "nunique"),
                matched_target_links=("SDG_target", "count"),
                mean_target_weight=("relevance_weight", "mean"),
                median_target_weight=("relevance_weight", "median"),
                sum_target_weight=("relevance_weight", "sum"),
                mean_doc_index=("AgeingEnergy_SDG_Index", "mean"),
                total_impact=("Impact", "sum"),
                average_impact=("Impact", "mean"),
            )
            .reset_index()
        )
        goal_index_summary["_goal_order"] = pd.to_numeric(goal_index_summary["SDG_goal"], errors="coerce")
        goal_index_summary = goal_index_summary.sort_values("_goal_order").drop(columns="_goal_order")

    doc_export = doc_index[
        [
            "Overton id",
            "Title",
            "Source country",
            "Published_on",
            "Year",
            "Phase",
            "Related to SDGs",
            "Impact",
            "matched SDG targets",
            "target weights used",
            "matched_target_count",
            "AgeingEnergy_SDG_RawSum",
            "AgeingEnergy_SDG_Index",
            "Has_matched_target",
        ]
    ].copy()

    with pd.ExcelWriter(OUTPUT_XLSX, engine="openpyxl") as writer:
        doc_export.to_excel(writer, sheet_name="doc_index", index=False)
        country_index.to_excel(writer, sheet_name="country_index", index=False)
        year_index.to_excel(writer, sheet_name="year_index", index=False)
        phase_index.to_excel(writer, sheet_name="phase_index", index=False)
        country_phase_index.to_excel(writer, sheet_name="country_phase_index", index=False)
        country_year_index.to_excel(writer, sheet_name="country_year_index", index=False)
        top_country_mean.to_excel(writer, sheet_name="top_country_mean", index=False)
        top_country_sum.to_excel(writer, sheet_name="top_country_sum", index=False)
        top_year_mean.to_excel(writer, sheet_name="top_year_mean", index=False)
        top_phase_mean.to_excel(writer, sheet_name="top_phase_mean", index=False)
        country_index_vs_impact.to_excel(writer, sheet_name="country_index_vs_impact", index=False)
        country_index_vs_count.to_excel(writer, sheet_name="country_index_vs_count", index=False)
        goal_index_summary.to_excel(writer, sheet_name="goal_index_summary", index=False)

    doc_export.to_csv(OUTPUT_CSV, index=False)

    methods_note = "\n".join(
        [
            "Ageing-energy SDG index methods",
            "",
            "Formula used:",
            "A_d = [sum_j (w_j * I_dj)] / [sum_j I_dj]",
            "where w_j is the SDG target relevance weight and I_dj = 1 when document d is linked to weighted target j.",
            "",
            "Weight construction:",
            "Weights were generated locally using TF-IDF with English stop words and 1-2 grams.",
            "A combined reference corpus was formed by concatenating the supplied ageing corpus and energy corpus.",
            "Cosine similarity was computed between each SDG target text and the combined reference corpus, then min-max normalized to [0,1].",
            "",
            "Handling of documents with no matched targets:",
            "Documents with no SDG targets present in the weighted target set received AgeingEnergy_SDG_RawSum = 0 and AgeingEnergy_SDG_Index = missing (NaN).",
            "These documents were retained in the document-level sheet but excluded from aggregated mean/median/std/sum calculations.",
            "",
            "Normalization rule:",
            "The main index is the normalized weighted average across matched targets in each document.",
            "The raw sum of matched target weights was also computed and retained at document level.",
            "",
            "Phase definition:",
            "Phase 1 = 1869-1947",
            "Phase 2 = 1948-1971",
            "Phase 3 = 1972-1993",
            "Phase 4 = 1994-2024",
            "",
            "Aggregations:",
            "Country, year, phase, country-phase, and country-year summaries are based on documents with non-missing normalized index values.",
        ]
    )
    METHODS_TXT.write_text(methods_note, encoding="utf-8")

    top10 = weights_df.nlargest(10, "relevance_weight")[
        ["SDG_target", "relevance_weight"]
    ].copy()
    print(f"WEIGHTS_FILE={WEIGHTS_XLSX}")
    print("TOP10_TARGETS_BY_WEIGHT")
    print(top10.to_csv(index=False).strip())
    print(f"DOCUMENTS_SCORED={int(scored_docs.shape[0])}")
    print(f"COUNTRIES_SCORED={int(country_index.shape[0])}")
    print("OUTPUT_FILES")
    for path in [WEIGHTS_XLSX, OUTPUT_XLSX, OUTPUT_CSV, METHODS_TXT]:
        print(path)
    print("SHEET_NAMES")
    for sheet in [
        "doc_index",
        "country_index",
        "year_index",
        "phase_index",
        "country_phase_index",
        "country_year_index",
        "top_country_mean",
        "top_country_sum",
        "top_year_mean",
        "top_phase_mean",
        "country_index_vs_impact",
        "country_index_vs_count",
        "goal_index_summary",
    ]:
        print(sheet)


if __name__ == "__main__":
    main()
