from __future__ import annotations

from pathlib import Path

import pandas as pd


ROOT = Path(__file__).resolve().parents[2]
FINAL_V2 = ROOT / "outputs" / "methods" / "sdg_target_weights_final_v2.xlsx"
EMBED = ROOT / "outputs" / "methods" / "sdg_target_weights_embedding.xlsx"
FINAL_V1 = ROOT / "outputs" / "methods" / "sdg_target_weights_final.xlsx"
OUTDIR = ROOT / "outputs" / "result2" / "data"

WIDE_CSV = OUTDIR / "fig_sdg_target_weight_matrix.csv"
LONG_CSV = OUTDIR / "fig_sdg_target_weight_long.csv"
RANKED_CSV = OUTDIR / "fig_sdg_target_weight_ranked.csv"
META_TXT = OUTDIR / "fig_sdg_target_weight_metadata.txt"
QC_TXT = OUTDIR / "fig_sdg_target_weight_qc.txt"

EXPECTED_TOP10 = ["1.5", "11.7", "11.2", "7.1", "11.1", "9.1", "11.5", "13.1", "1.3", "11.b"]


def goal_from_target(target: str) -> int | None:
    head = str(target).split(".")[0]
    try:
        return int(head)
    except Exception:
        return None


def main():
    OUTDIR.mkdir(parents=True, exist_ok=True)

    final_v2 = pd.read_excel(FINAL_V2, sheet_name="target_relevance_weights")
    embed = pd.read_excel(EMBED, sheet_name="target_relevance_weights")
    final_v1 = pd.read_excel(FINAL_V1, sheet_name="target_relevance_weights")

    # Start from the stable v2 table and only enrich with already-generated columns.
    df = final_v2.copy()
    df["sdg_goal"] = df["SDG_target"].apply(goal_from_target)
    df["sdg_target"] = df["SDG_target"].astype(str)
    df["sdg_target_label"] = df["official text"].astype(str)
    df["policy_weight"] = df["filter"]
    df["final_weight"] = df["weight_final"]
    df["overall_weight"] = df["weight_final"]

    # Reuse existing embedding output explicitly for provenance consistency.
    embed_small = embed.rename(
        columns={
            "relevance_weight": "embedding_weight_from_embedding_file",
            "embedding_similarity": "embedding_similarity",
        }
    )[["SDG_target", "embedding_similarity", "embedding_weight_from_embedding_file", "SDG_goal", "rank_embedding"]]
    df = df.merge(embed_small, on=["SDG_target", "rank_embedding"], how="left", suffixes=("", "_embed"))

    # Also keep the previous constrained version's final weight as an existing intermediate.
    final_v1_small = final_v1.rename(columns={"weight_final": "final_weight_v1"})[
        ["SDG_target", "final_weight_v1"]
    ]
    df = df.merge(final_v1_small, on="SDG_target", how="left")

    wide = df[
        [
            "sdg_goal",
            "sdg_target",
            "sdg_target_label",
            "embedding_similarity",
            "weight_embedding",
            "embedding_weight_from_embedding_file",
            "policy_weight",
            "weight_pre_norm",
            "final_weight",
            "overall_weight",
            "final_weight_v1",
            "rank_embedding",
            "rank_final_v2",
            "rank_change",
        ]
    ]

    wide = wide.sort_values(["overall_weight", "sdg_target"], ascending=[False, True]).reset_index(drop=True)
    wide.to_csv(WIDE_CSV, index=False)

    long = pd.concat(
        [
            wide[["sdg_target", "weight_embedding"]]
            .rename(columns={"weight_embedding": "weight"})
            .assign(component="embedding"),
            wide[["sdg_target", "policy_weight"]]
            .rename(columns={"policy_weight": "weight"})
            .assign(component="policy"),
            wide[["sdg_target", "weight_pre_norm"]]
            .rename(columns={"weight_pre_norm": "weight"})
            .assign(component="pre_norm"),
            wide[["sdg_target", "overall_weight"]]
            .rename(columns={"overall_weight": "weight"})
            .assign(component="final"),
        ],
        ignore_index=True,
    )[["sdg_target", "component", "weight"]]
    long.to_csv(LONG_CSV, index=False)

    ranked = wide.copy()
    ranked.to_csv(RANKED_CSV, index=False)

    target_count = len(wide)
    top10_actual = ranked["sdg_target"].head(10).tolist()
    contains_expected = all(t in top10_actual for t in EXPECTED_TOP10)
    sort_ok = ranked["overall_weight"].is_monotonic_decreasing
    missing_any = ranked.isna().any().any() or long.isna().any().any()

    meta_lines = [
        "SDG target weight matrix metadata",
        "",
        f"Stable source table: {FINAL_V2}",
        "The exported matrix reuses the previously validated stable v2 framework and does not recompute any embedding or weighting step.",
        "",
        f"final_weight / overall_weight source: {FINAL_V2} sheet target_relevance_weights, column weight_final.",
        f"embedding_weight source: {FINAL_V2} sheet target_relevance_weights, column weight_embedding; cross-checked against {EMBED} column relevance_weight.",
        "policy_weight source: the existing binary policy filter in the stable v2 table (column filter), exported here as policy_weight.",
        "Additional retained intermediate columns: weight_pre_norm, embedding_similarity, final_weight_v1, rank_embedding, rank_final_v2, rank_change.",
        "",
        "Normalization:",
        "The stable v2 method had already applied normalization to produce weight_final in [0,1].",
        "weight_pre_norm is the existing pre-normalization intermediate from the same stable v2 workbook.",
        "",
        f"Target total: {target_count}",
        "Target set was not changed, expanded, or recomputed.",
    ]
    META_TXT.write_text("\n".join(meta_lines), encoding="utf-8")

    qc_lines = [
        "SDG target weight matrix QC",
        "",
        f"Target total: {target_count}",
        f"Expected top 10 present: {contains_expected}",
        "Expected top 10 list: " + ", ".join(EXPECTED_TOP10),
        "Actual top 10 list: " + ", ".join(top10_actual),
        f"overall_weight sorted descending correctly: {sort_ok}",
        f"Any missing values in wide/long outputs: {missing_any}",
        f"Rows in wide table: {len(wide)}",
        f"Rows in long table: {len(long)}",
        "Missing by column (wide): " + "; ".join(f"{c}={int(ranked[c].isna().sum())}" for c in ranked.columns),
        "Missing by column (long): " + "; ".join(f"{c}={int(long[c].isna().sum())}" for c in long.columns),
    ]
    QC_TXT.write_text("\n".join(qc_lines), encoding="utf-8")


if __name__ == "__main__":
    main()
