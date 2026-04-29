from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd
from scipy.stats import pearsonr, spearmanr
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity

from build_ageing_energy_index import (
    AGEING_CORPUS,
    ENERGY_CORPUS,
    TARGET_TEXTS,
    build_doc_index,
)


ROOT = Path(__file__).resolve().parents[2]
OUTPUT_DIR = ROOT / "outputs" / "methods"
TFIDF_WEIGHTS_XLSX = OUTPUT_DIR / "ageing_energy_target_weights.xlsx"
TFIDF_INDEX_XLSX = OUTPUT_DIR / "ageing_energy_index_full.xlsx"

EMBED_WEIGHTS_XLSX = OUTPUT_DIR / "sdg_target_weights_embedding.xlsx"
EMBED_INDEX_XLSX = OUTPUT_DIR / "ageing_energy_index_embedding.xlsx"
VALIDATION_XLSX = OUTPUT_DIR / "sdg_method_validation.xlsx"
WEIGHT_COMPARISON_XLSX = OUTPUT_DIR / "sdg_weight_comparison.xlsx"
METHODS_TXT = OUTPUT_DIR / "ageing_energy_sdg_validation_methods.txt"

MODEL_NAME = "all-MiniLM-L6-v2"
COMBINED_CORPUS = f"{AGEING_CORPUS} {ENERGY_CORPUS}"


MANUAL_LABELS = {
    "1.3": 1,
    "1.4": 1,
    "1.5": 1,
    "2.2": 1,
    "3.4": 1,
    "3.8": 1,
    "3.9": 1,
    "3.d": 1,
    "6.1": 0,
    "6.2": 0,
    "6.4": 1,
    "7.1": 1,
    "7.2": 1,
    "7.3": 1,
    "7.a": 1,
    "7.b": 1,
    "9.1": 1,
    "9.4": 1,
    "10.2": 1,
    "10.4": 1,
    "11.1": 1,
    "11.2": 1,
    "11.5": 1,
    "11.6": 1,
    "11.7": 1,
    "11.b": 1,
    "12.c": 1,
    "13.1": 1,
    "13.2": 0,
    "13.3": 0,
    "16.6": 0,
    "16.7": 0,
    "16.b": 0,
    "17.18": 0,
}


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


def resolve_local_model_path() -> str:
    hub_root = Path.home() / ".cache" / "huggingface" / "hub" / "models--sentence-transformers--all-MiniLM-L6-v2" / "snapshots"
    if not hub_root.exists():
        return MODEL_NAME
    snapshots = sorted([p for p in hub_root.iterdir() if p.is_dir()])
    if not snapshots:
        return MODEL_NAME
    return str(snapshots[-1])


def build_embedding_weights() -> pd.DataFrame:
    model = SentenceTransformer(resolve_local_model_path())

    target_df = pd.DataFrame(
        {
            "SDG_target": list(TARGET_TEXTS.keys()),
            "official text": list(TARGET_TEXTS.values()),
        }
    )

    embeddings = model.encode(
        [COMBINED_CORPUS] + target_df["official text"].tolist(),
        normalize_embeddings=True,
        show_progress_bar=False,
    )
    reference = embeddings[0:1]
    target_embeds = embeddings[1:]
    sims = cosine_similarity(target_embeds, reference).ravel()

    sim_min = float(sims.min())
    sim_max = float(sims.max())
    if np.isclose(sim_max, sim_min):
        normalized = np.ones_like(sims)
    else:
        normalized = (sims - sim_min) / (sim_max - sim_min)

    target_df["embedding_similarity"] = sims
    target_df["relevance_weight"] = normalized
    target_df["SDG_goal"] = target_df["SDG_target"].str.split(".").str[0]
    target_df = target_df.sort_values(
        ["relevance_weight", "SDG_target"], ascending=[False, True]
    ).reset_index(drop=True)
    target_df["rank_embedding"] = np.arange(1, len(target_df) + 1)
    return target_df


def build_validation_table(embed_df: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    ranked = embed_df.sort_values(
        ["relevance_weight", "SDG_target"], ascending=[False, True]
    ).reset_index(drop=True)
    ranked["rank"] = np.arange(1, len(ranked) + 1)

    top15 = ranked.head(15).copy()
    top15["validation_group"] = "top15"
    top15["predicted_label"] = 1

    bottom15 = ranked.tail(15).copy()
    bottom15["validation_group"] = "bottom15"
    bottom15["predicted_label"] = 0

    validation = pd.concat([top15, bottom15], ignore_index=True)
    validation["manual_label"] = validation["SDG_target"].map(MANUAL_LABELS)
    validation["manual_match"] = validation["manual_label"] == validation["predicted_label"]

    validation_table = validation[
        [
            "SDG_target",
            "official text",
            "relevance_weight",
            "rank",
            "validation_group",
            "predicted_label",
            "manual_label",
            "manual_match",
        ]
    ].sort_values("rank")

    accuracy = float(validation_table["manual_match"].mean())
    summary = pd.DataFrame(
        {
            "metric": [
                "validated_targets",
                "manual_validation_accuracy",
                "top15_true_positive_rate",
                "bottom15_true_negative_rate",
            ],
            "value": [
                int(validation_table.shape[0]),
                accuracy,
                float(validation_table[validation_table["validation_group"] == "top15"]["manual_match"].mean()),
                float(validation_table[validation_table["validation_group"] == "bottom15"]["manual_match"].mean()),
            ],
        }
    )
    return validation_table, summary


def main() -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    embed_df = build_embedding_weights()
    with pd.ExcelWriter(EMBED_WEIGHTS_XLSX, engine="openpyxl") as writer:
        embed_df.to_excel(writer, sheet_name="target_relevance_weights", index=False)

    tfidf_df = pd.read_excel(TFIDF_WEIGHTS_XLSX, sheet_name="target_relevance_weights")
    tfidf_comp = tfidf_df[["SDG_target", "relevance_weight"]].rename(
        columns={"relevance_weight": "weight_tfidf"}
    )
    embed_comp = embed_df[["SDG_target", "relevance_weight"]].rename(
        columns={"relevance_weight": "weight_embedding"}
    )

    comparison = tfidf_comp.merge(embed_comp, on="SDG_target", how="inner")
    comparison["rank_tfidf"] = comparison["weight_tfidf"].rank(
        method="min", ascending=False
    ).astype(int)
    comparison["rank_embedding"] = comparison["weight_embedding"].rank(
        method="min", ascending=False
    ).astype(int)
    comparison = comparison.sort_values("rank_embedding").reset_index(drop=True)

    pearson_val = float(pearsonr(comparison["weight_tfidf"], comparison["weight_embedding"]).statistic)
    spearman_val = float(spearmanr(comparison["weight_tfidf"], comparison["weight_embedding"]).statistic)

    top10_tfidf = set(
        comparison.sort_values(["rank_tfidf", "SDG_target"]).head(10)["SDG_target"]
    )
    top10_embed = set(
        comparison.sort_values(["rank_embedding", "SDG_target"]).head(10)["SDG_target"]
    )
    common_targets = sorted(top10_tfidf & top10_embed, key=lambda x: (float(x.split(".")[0]), x))
    overlap_ratio = len(common_targets) / 10.0

    correlation_summary = pd.DataFrame(
        {
            "metric": ["pearson_weight_correlation", "spearman_weight_correlation", "top10_overlap_ratio"],
            "value": [pearson_val, spearman_val, overlap_ratio],
        }
    )
    top10_overlap_table = pd.DataFrame({"common_top10_targets": common_targets})

    with pd.ExcelWriter(WEIGHT_COMPARISON_XLSX, engine="openpyxl") as writer:
        comparison.to_excel(writer, sheet_name="sdg_weight_comparison", index=False)
        correlation_summary.to_excel(writer, sheet_name="correlation_summary", index=False)
        top10_overlap_table.to_excel(writer, sheet_name="top10_overlap", index=False)

    validation_table, validation_summary = build_validation_table(embed_df)
    with pd.ExcelWriter(VALIDATION_XLSX, engine="openpyxl") as writer:
        validation_table.to_excel(writer, sheet_name="sdg_validation_table", index=False)
        validation_summary.to_excel(writer, sheet_name="validation_summary", index=False)
        top10_overlap_table.to_excel(writer, sheet_name="top10_overlap", index=False)

    doc_index, _goal_long = build_doc_index(
        embed_df.rename(columns={"official text": "target_text"})
    )
    scored_docs = doc_index[doc_index["Has_matched_target"]].copy()

    doc_index_embedding = doc_index.rename(
        columns={
            "AgeingEnergy_SDG_RawSum": "AgeingEnergy_SDG_RawSum_embedding",
            "AgeingEnergy_SDG_Index": "AgeingEnergy_SDG_Index_embedding",
        }
    )
    country_index_embedding = summarize(scored_docs.groupby("Source country")).rename(
        columns={"Source country": "Country"}
    )
    year_index_embedding = summarize(scored_docs.groupby("Year")).sort_values("Year")
    phase_index_embedding = summarize(scored_docs.groupby("Phase"))

    tfidf_country = pd.read_excel(TFIDF_INDEX_XLSX, sheet_name="country_index")
    method_compare = tfidf_country[["Country", "mean_index"]].rename(
        columns={"mean_index": "mean_index_tfidf"}
    ).merge(
        country_index_embedding[["Country", "mean_index"]].rename(
            columns={"mean_index": "mean_index_embedding"}
        ),
        on="Country",
        how="inner",
    )
    pearson_country = float(
        pearsonr(method_compare["mean_index_tfidf"], method_compare["mean_index_embedding"]).statistic
    )
    spearman_country = float(
        spearmanr(method_compare["mean_index_tfidf"], method_compare["mean_index_embedding"]).statistic
    )
    method_compare = method_compare.sort_values(
        "mean_index_embedding", ascending=False
    ).reset_index(drop=True)
    method_compare_summary = pd.DataFrame(
        {
            "metric": ["pearson_country_mean_index", "spearman_country_mean_index"],
            "value": [pearson_country, spearman_country],
        }
    )

    with pd.ExcelWriter(EMBED_INDEX_XLSX, engine="openpyxl") as writer:
        doc_index_embedding.to_excel(writer, sheet_name="doc_index_embedding", index=False)
        country_index_embedding.to_excel(writer, sheet_name="country_index_embedding", index=False)
        year_index_embedding.to_excel(writer, sheet_name="year_index_embedding", index=False)
        phase_index_embedding.to_excel(writer, sheet_name="phase_index_embedding", index=False)
        method_compare.to_excel(writer, sheet_name="index_method_comparison", index=False)
        method_compare_summary.to_excel(writer, sheet_name="index_method_summary", index=False)

    stable = spearman_val >= 0.8 and overlap_ratio >= 0.6
    methods_note = "\n".join(
        [
            "Ageing-energy SDG validation methods",
            "",
            f"Embedding model used: {MODEL_NAME} via sentence-transformers.",
            "Each SDG target text was encoded into a sentence embedding vector.",
            "The reference query vector was built by encoding the combined ageing corpus and energy corpus as a single text.",
            "Embedding relevance was computed as cosine similarity between each target embedding and the reference corpus embedding.",
            "Embedding similarities were min-max normalized to [0,1] to form relevance weights.",
            "",
            "TF-IDF comparison:",
            "Previous TF-IDF weights were loaded from ageing_energy_target_weights.xlsx and compared target-by-target.",
            f"Pearson correlation between TF-IDF and embedding weights: {pearson_val:.4f}.",
            f"Spearman correlation between TF-IDF and embedding weights: {spearman_val:.4f}.",
            "",
            "Robustness:",
            f"Top-10 overlap ratio between methods: {overlap_ratio:.2f}.",
            f"Common top-10 targets: {', '.join(common_targets)}.",
            "",
            "Manual validation procedure:",
            "The 15 highest-weight and 15 lowest-weight embedding targets were selected for validation.",
            "Manual labels were assigned as 1 for ageing-energy relevant and 0 for not relevant, based on substantive relevance to ageing-sensitive energy access, efficiency, housing, transport, vulnerability, affordability, and resilience.",
            f"Validation accuracy across the selected 30 targets: {float(validation_summary.loc[validation_summary['metric'] == 'manual_validation_accuracy', 'value'].iloc[0]):.4f}.",
            "",
            "Embedding index recomputation:",
            "The document-level index was recomputed as the normalized weighted average of matched embedding-based target weights.",
            "Documents with no matched weighted targets were retained with missing normalized index values and excluded from aggregate mean/median summaries.",
            "",
            "Index-method comparison:",
            f"Pearson correlation for country mean index between TF-IDF and embedding methods: {pearson_country:.4f}.",
            f"Spearman correlation for country mean index between TF-IDF and embedding methods: {spearman_country:.4f}.",
            f"Ranking stability assessment: {'stable' if stable else 'partially stable'}.",
        ]
    )
    METHODS_TXT.write_text(methods_note, encoding="utf-8")

    print(f"SPEARMAN_TFIDF_VS_EMBEDDING={spearman_val:.6f}")
    print(f"TOP10_OVERLAP={overlap_ratio:.6f}")
    print(f"TARGETS_VALIDATED={int(validation_table.shape[0])}")
    print(f"RANKINGS_STABLE={'yes' if stable else 'no'}")
    print("COMMON_TOP10_TARGETS=" + ",".join(common_targets))
    print("OUTPUT_FILES")
    for p in [EMBED_WEIGHTS_XLSX, EMBED_INDEX_XLSX, VALIDATION_XLSX, WEIGHT_COMPARISON_XLSX, METHODS_TXT]:
        print(p)


if __name__ == "__main__":
    main()
