from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd
from scipy.stats import pearsonr, spearmanr

from build_ageing_energy_index import build_doc_index


ROOT = Path(__file__).resolve().parents[2]
OUTPUT_DIR = ROOT / "outputs" / "methods"

TFIDF_WEIGHTS_XLSX = OUTPUT_DIR / "ageing_energy_target_weights.xlsx"
EMBED_WEIGHTS_XLSX = OUTPUT_DIR / "sdg_target_weights_embedding.xlsx"
EMBED_INDEX_XLSX = OUTPUT_DIR / "ageing_energy_index_embedding.xlsx"

FINAL_WEIGHTS_XLSX = OUTPUT_DIR / "sdg_target_weights_final.xlsx"
FINAL_INDEX_XLSX = OUTPUT_DIR / "ageing_energy_index_final.xlsx"
FINAL_STABILITY_XLSX = OUTPUT_DIR / "sdg_final_stability_check.xlsx"
FILTER_DIAGNOSTICS_XLSX = OUTPUT_DIR / "sdg_filter_diagnostics.xlsx"
METHODS_TXT = OUTPUT_DIR / "ageing_energy_final_methods.txt"

POLICY_TERMS = [
    "age",
    "ageing",
    "aging",
    "elderly",
    "older persons",
    "vulnerability",
    "disability",
    "inclusion",
    "health",
    "care",
    "accessibility",
    "social protection",
    "energy",
    "electricity",
    "fuel",
    "heating",
    "cooling",
    "energy access",
    "energy poverty",
    "infrastructure",
    "climate",
    "resilience",
    "adaptation",
    "pollution",
    "air quality",
]


def summarize(grouped: pd.core.groupby.generic.DataFrameGroupBy) -> pd.DataFrame:
    return (
        grouped["AgeingEnergy_SDG_Index"]
        .agg(
            document_count="count",
            mean_index="mean",
            median_index="median",
            std_index="std",
            sum_index="sum",
        )
        .reset_index()
    )


def top10_overlap(df_a: pd.DataFrame, col_a: str, df_b: pd.DataFrame, col_b: str) -> tuple[float, list[str]]:
    top_a = set(df_a.sort_values([col_a, "SDG_target"], ascending=[False, True]).head(10)["SDG_target"])
    top_b = set(df_b.sort_values([col_b, "SDG_target"], ascending=[False, True]).head(10)["SDG_target"])
    common = sorted(top_a & top_b, key=lambda x: (float(x.split(".")[0]), x))
    return len(common) / 10.0, common


def main() -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    tfidf_df = pd.read_excel(TFIDF_WEIGHTS_XLSX, sheet_name="target_relevance_weights")
    embed_df = pd.read_excel(EMBED_WEIGHTS_XLSX, sheet_name="target_relevance_weights")

    final_df = embed_df[["SDG_target", "official text", "relevance_weight"]].rename(
        columns={"relevance_weight": "weight_embedding"}
    )
    final_df["filter"] = final_df["official text"].str.lower().apply(
        lambda text: int(any(term in text for term in POLICY_TERMS))
    )
    final_df["weight_filtered"] = final_df["weight_embedding"] * final_df["filter"]

    positive = final_df.loc[final_df["filter"] == 1, "weight_filtered"]
    if positive.empty or np.isclose(float(positive.max()), float(positive.min())):
        final_df["weight_final"] = final_df["weight_filtered"]
    else:
        min_pos = float(positive.min())
        max_pos = float(positive.max())
        final_df["weight_final"] = np.where(
            final_df["filter"] == 1,
            (final_df["weight_filtered"] - min_pos) / (max_pos - min_pos),
            0.0,
        )

    final_df["rank_embedding"] = final_df["weight_embedding"].rank(method="min", ascending=False).astype(int)
    final_df["rank_final"] = final_df["weight_final"].rank(method="min", ascending=False).astype(int)
    final_df["rank_change"] = final_df["rank_final"] - final_df["rank_embedding"]
    final_df["SDG_goal"] = final_df["SDG_target"].astype(str).str.split(".").str[0]
    final_df = final_df.sort_values(["weight_final", "SDG_target"], ascending=[False, True]).reset_index(drop=True)

    with pd.ExcelWriter(FINAL_WEIGHTS_XLSX, engine="openpyxl") as writer:
        final_df[["SDG_target", "weight_embedding", "filter", "weight_final", "official text"]].to_excel(
            writer, sheet_name="target_relevance_weights", index=False
        )

    with pd.ExcelWriter(FILTER_DIAGNOSTICS_XLSX, engine="openpyxl") as writer:
        final_df[
            [
                "SDG_target",
                "weight_embedding",
                "filter",
                "weight_final",
                "rank_embedding",
                "rank_final",
                "rank_change",
                "official text",
            ]
        ].to_excel(writer, sheet_name="sdg_filter_diagnostics", index=False)

    final_weight_input = final_df[["SDG_target", "weight_final", "official text"]].rename(
        columns={"weight_final": "relevance_weight", "official text": "target_text"}
    )
    doc_index, _goal_long = build_doc_index(final_weight_input)
    scored_docs = doc_index[doc_index["Has_matched_target"]].copy()

    doc_index_final = doc_index.rename(
        columns={
            "AgeingEnergy_SDG_RawSum": "AgeingEnergy_SDG_RawSum_final",
            "AgeingEnergy_SDG_Index": "AgeingEnergy_SDG_Index_final",
        }
    )
    country_index_final = summarize(scored_docs.groupby("Source country")).rename(columns={"Source country": "Country"})
    year_index_final = summarize(scored_docs.groupby("Year")).sort_values("Year")
    phase_index_final = summarize(scored_docs.groupby("Phase"))

    with pd.ExcelWriter(FINAL_INDEX_XLSX, engine="openpyxl") as writer:
        doc_index_final.to_excel(writer, sheet_name="doc_index_final", index=False)
        country_index_final.to_excel(writer, sheet_name="country_index_final", index=False)
        year_index_final.to_excel(writer, sheet_name="year_index_final", index=False)
        phase_index_final.to_excel(writer, sheet_name="phase_index_final", index=False)

    compare = tfidf_df[["SDG_target", "relevance_weight"]].rename(columns={"relevance_weight": "weight_tfidf"})
    compare = compare.merge(
        embed_df[["SDG_target", "relevance_weight"]].rename(columns={"relevance_weight": "weight_embedding"}),
        on="SDG_target",
        how="inner",
    ).merge(
        final_df[["SDG_target", "weight_final", "rank_change", "filter"]],
        on="SDG_target",
        how="inner",
    )

    spearman_embed_final = float(spearmanr(compare["weight_embedding"], compare["weight_final"]).statistic)
    spearman_tfidf_final = float(spearmanr(compare["weight_tfidf"], compare["weight_final"]).statistic)
    pearson_embed_final = float(pearsonr(compare["weight_embedding"], compare["weight_final"]).statistic)
    pearson_tfidf_final = float(pearsonr(compare["weight_tfidf"], compare["weight_final"]).statistic)

    overlap_embed_final, common_embed_final = top10_overlap(
        embed_df.rename(columns={"relevance_weight": "weight_embedding"}),
        "weight_embedding",
        final_df,
        "weight_final",
    )
    overlap_tfidf_final, common_tfidf_final = top10_overlap(
        tfidf_df.rename(columns={"relevance_weight": "weight_tfidf"}),
        "weight_tfidf",
        final_df,
        "weight_final",
    )

    embed_country = pd.read_excel(EMBED_INDEX_XLSX, sheet_name="country_index_embedding")
    country_compare = embed_country[["Country", "mean_index"]].rename(
        columns={"mean_index": "mean_index_embedding"}
    ).merge(
        country_index_final[["Country", "mean_index"]].rename(columns={"mean_index": "mean_index_final"}),
        on="Country",
        how="inner",
    )
    pearson_country = float(pearsonr(country_compare["mean_index_embedding"], country_compare["mean_index_final"]).statistic)
    spearman_country = float(spearmanr(country_compare["mean_index_embedding"], country_compare["mean_index_final"]).statistic)

    stability_summary = pd.DataFrame(
        {
            "metric": [
                "spearman_embedding_vs_final",
                "pearson_embedding_vs_final",
                "spearman_tfidf_vs_final",
                "pearson_tfidf_vs_final",
                "top10_overlap_embedding_vs_final",
                "top10_overlap_tfidf_vs_final",
                "pearson_country_embedding_vs_final",
                "spearman_country_embedding_vs_final",
                "targets_retained_after_filter",
            ],
            "value": [
                spearman_embed_final,
                pearson_embed_final,
                spearman_tfidf_final,
                pearson_tfidf_final,
                overlap_embed_final,
                overlap_tfidf_final,
                pearson_country,
                spearman_country,
                int(final_df["filter"].sum()),
            ],
        }
    )
    overlap_tables = {
        "embed_final_common_top10": pd.DataFrame({"SDG_target": common_embed_final}),
        "tfidf_final_common_top10": pd.DataFrame({"SDG_target": common_tfidf_final}),
    }

    with pd.ExcelWriter(FINAL_STABILITY_XLSX, engine="openpyxl") as writer:
        compare.sort_values("weight_final", ascending=False).to_excel(
            writer, sheet_name="weight_comparison", index=False
        )
        country_compare.sort_values("mean_index_final", ascending=False).to_excel(
            writer, sheet_name="country_index_comparison", index=False
        )
        stability_summary.to_excel(writer, sheet_name="stability_summary", index=False)
        overlap_tables["embed_final_common_top10"].to_excel(writer, sheet_name="embed_final_top10", index=False)
        overlap_tables["tfidf_final_common_top10"].to_excel(writer, sheet_name="tfidf_final_top10", index=False)

    previous_spearman = 0.352717
    previous_overlap = 0.5
    improved = (spearman_tfidf_final > previous_spearman) or (overlap_tfidf_final > previous_overlap)

    methods = "\n".join(
        [
            "Final ageing-energy SDG relevance framework",
            "",
            "Embedding-based similarity:",
            "Base semantic relevance weights were taken from the embedding model all-MiniLM-L6-v2.",
            "Each SDG target text was embedded and compared to the combined ageing-energy reference corpus using cosine similarity.",
            "Embedding similarities were normalized to [0,1].",
            "",
            "Policy constraint filter:",
            "A binary policy filter was applied to each SDG target text.",
            "Targets were retained if the official target text contained at least one ageing/vulnerability policy concept or at least one energy/environment policy concept from the predefined dictionary.",
            "The filter ensures semantic similarity is constrained by interpretable policy relevance conditions.",
            "",
            "Final weight construction:",
            "weight_final = weight_embedding * filter",
            "Filtered weights were then re-normalized across retained targets to [0,1], while excluded targets were assigned 0.",
            "",
            "Index formula:",
            "A_d = sum(w_j^(final) * I_dj) / sum(I_dj)",
            "where I_dj = 1 when document d is associated with target j and 0 otherwise.",
            "Documents with no matched retained targets were kept in the document table with missing normalized final index values.",
            "",
            "Stability checks:",
            f"Spearman embedding vs final = {spearman_embed_final:.4f}",
            f"Spearman TF-IDF vs final = {spearman_tfidf_final:.4f}",
            f"Top-10 overlap embedding vs final = {overlap_embed_final:.2f}",
            f"Top-10 overlap TF-IDF vs final = {overlap_tfidf_final:.2f}",
            f"Country-level Spearman embedding index vs final index = {spearman_country:.4f}",
            "",
            "Interpretation:",
            "The final framework does not replace semantic similarity. It constrains the embedding-based relevance model using explicit policy relevance conditions to improve interpretability and reduce unstable rankings driven by semantically broad but policy-irrelevant targets.",
            f"Targets retained after filtering: {int(final_df['filter'].sum())}",
            f"Stability improvement relative to the previous embedding comparison: {'yes' if improved else 'limited'}",
        ]
    )
    METHODS_TXT.write_text(methods, encoding="utf-8")

    print(f"SPEARMAN_EMBEDDING_VS_FINAL={spearman_embed_final:.6f}")
    print(f"SPEARMAN_TFIDF_VS_FINAL={spearman_tfidf_final:.6f}")
    print(f"TOP10_OVERLAP_EMBEDDING_VS_FINAL={overlap_embed_final:.6f}")
    print(f"TOP10_OVERLAP_TFIDF_VS_FINAL={overlap_tfidf_final:.6f}")
    print(f"TARGETS_RETAINED={int(final_df['filter'].sum())}")
    print(f"STABILITY_IMPROVED={'yes' if improved else 'no'}")
    print("OUTPUT_FILES")
    for p in [
        FINAL_WEIGHTS_XLSX,
        FINAL_INDEX_XLSX,
        FINAL_STABILITY_XLSX,
        FILTER_DIAGNOSTICS_XLSX,
        METHODS_TXT,
    ]:
        print(p)


if __name__ == "__main__":
    main()
