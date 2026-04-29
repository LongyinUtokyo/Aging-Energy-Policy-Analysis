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
FINAL_V1_STABILITY_XLSX = OUTPUT_DIR / "sdg_final_stability_check.xlsx"

FINAL_V2_WEIGHTS_XLSX = OUTPUT_DIR / "sdg_target_weights_final_v2.xlsx"
FINAL_V2_INDEX_XLSX = OUTPUT_DIR / "ageing_energy_index_final_v2.xlsx"

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
FORCE_INCLUDE = {"11.1", "11.5", "1.4"}
EPSILON = 0.05


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


def top10_overlap(
    a: pd.DataFrame, col_a: str, b: pd.DataFrame, col_b: str
) -> tuple[float, list[str]]:
    top_a = set(a.sort_values([col_a, "SDG_target"], ascending=[False, True]).head(10)["SDG_target"])
    top_b = set(b.sort_values([col_b, "SDG_target"], ascending=[False, True]).head(10)["SDG_target"])
    common = sorted(top_a & top_b, key=lambda x: (float(x.split(".")[0]), x))
    return len(common) / 10.0, common


def main() -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    tfidf_df = pd.read_excel(TFIDF_WEIGHTS_XLSX, sheet_name="target_relevance_weights")
    embed_df = pd.read_excel(EMBED_WEIGHTS_XLSX, sheet_name="target_relevance_weights")

    v2 = embed_df[["SDG_target", "official text", "relevance_weight"]].rename(
        columns={"relevance_weight": "weight_embedding"}
    )
    v2["filter"] = v2.apply(
        lambda row: int(
            row["SDG_target"] in FORCE_INCLUDE
            or any(term in str(row["official text"]).lower() for term in POLICY_TERMS)
        ),
        axis=1,
    )
    v2["weight_pre_norm"] = v2["weight_embedding"] * v2["filter"] + EPSILON
    min_w = float(v2["weight_pre_norm"].min())
    max_w = float(v2["weight_pre_norm"].max())
    if np.isclose(min_w, max_w):
        v2["weight_final"] = 1.0
    else:
        v2["weight_final"] = (v2["weight_pre_norm"] - min_w) / (max_w - min_w)

    v2["rank_embedding"] = v2["weight_embedding"].rank(method="min", ascending=False).astype(int)
    v2["rank_final_v2"] = v2["weight_final"].rank(method="min", ascending=False).astype(int)
    v2["rank_change"] = v2["rank_final_v2"] - v2["rank_embedding"]

    with pd.ExcelWriter(FINAL_V2_WEIGHTS_XLSX, engine="openpyxl") as writer:
        v2[
            [
                "SDG_target",
                "official text",
                "weight_embedding",
                "filter",
                "weight_pre_norm",
                "weight_final",
                "rank_embedding",
                "rank_final_v2",
                "rank_change",
            ]
        ].sort_values(["weight_final", "SDG_target"], ascending=[False, True]).to_excel(
            writer, sheet_name="target_relevance_weights", index=False
        )

    final_weight_input = v2[["SDG_target", "weight_final", "official text"]].rename(
        columns={"weight_final": "relevance_weight", "official text": "target_text"}
    )
    doc_index, _goal_long = build_doc_index(final_weight_input)
    scored_docs = doc_index[doc_index["Has_matched_target"]].copy()

    doc_index_v2 = doc_index.rename(
        columns={
            "AgeingEnergy_SDG_RawSum": "AgeingEnergy_SDG_RawSum_final_v2",
            "AgeingEnergy_SDG_Index": "AgeingEnergy_SDG_Index_final_v2",
        }
    )
    country_index_v2 = summarize(scored_docs.groupby("Source country")).rename(columns={"Source country": "Country"})
    year_index_v2 = summarize(scored_docs.groupby("Year")).sort_values("Year")
    phase_index_v2 = summarize(scored_docs.groupby("Phase"))

    with pd.ExcelWriter(FINAL_V2_INDEX_XLSX, engine="openpyxl") as writer:
        doc_index_v2.to_excel(writer, sheet_name="doc_index_final_v2", index=False)
        country_index_v2.to_excel(writer, sheet_name="country_index_final_v2", index=False)
        year_index_v2.to_excel(writer, sheet_name="year_index_final_v2", index=False)
        phase_index_v2.to_excel(writer, sheet_name="phase_index_final_v2", index=False)

    compare = tfidf_df[["SDG_target", "relevance_weight"]].rename(columns={"relevance_weight": "weight_tfidf"})
    compare = compare.merge(
        embed_df[["SDG_target", "relevance_weight"]].rename(columns={"relevance_weight": "weight_embedding"}),
        on="SDG_target",
        how="inner",
    ).merge(
        v2[["SDG_target", "weight_final"]],
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
        v2,
        "weight_final",
    )
    overlap_tfidf_final, common_tfidf_final = top10_overlap(
        tfidf_df.rename(columns={"relevance_weight": "weight_tfidf"}),
        "weight_tfidf",
        v2,
        "weight_final",
    )

    previous = pd.read_excel(FINAL_V1_STABILITY_XLSX, sheet_name="stability_summary")
    prev_map = dict(zip(previous["metric"], previous["value"]))
    improved = (
        spearman_embed_final > float(prev_map.get("spearman_embedding_vs_final", -np.inf))
        or overlap_embed_final > float(prev_map.get("top10_overlap_embedding_vs_final", -np.inf))
    )

    top10 = v2.sort_values(["weight_final", "SDG_target"], ascending=[False, True]).head(10)[
        ["SDG_target", "weight_final"]
    ].copy()

    print(f"SPEARMAN_EMBEDDING_VS_FINAL_V2={spearman_embed_final:.6f}")
    print(f"SPEARMAN_TFIDF_VS_FINAL_V2={spearman_tfidf_final:.6f}")
    print(f"PEARSON_EMBEDDING_VS_FINAL_V2={pearson_embed_final:.6f}")
    print(f"PEARSON_TFIDF_VS_FINAL_V2={pearson_tfidf_final:.6f}")
    print(f"TOP10_OVERLAP_EMBEDDING_VS_FINAL_V2={overlap_embed_final:.6f}")
    print(f"TOP10_OVERLAP_TFIDF_VS_FINAL_V2={overlap_tfidf_final:.6f}")
    print("COMMON_TOP10_EMBEDDING_FINAL_V2=" + ",".join(common_embed_final))
    print("COMMON_TOP10_TFIDF_FINAL_V2=" + ",".join(common_tfidf_final))
    print(f"TARGETS_RETAINED_V2={int(v2['filter'].sum())}")
    print(f"STABILITY_IMPROVED_VS_V1={'yes' if improved else 'no'}")
    print("TOP10_TARGETS_FINAL_V2")
    print(top10.to_csv(index=False).strip())
    print("OUTPUT_FILES")
    print(FINAL_V2_WEIGHTS_XLSX)
    print(FINAL_V2_INDEX_XLSX)


if __name__ == "__main__":
    main()
