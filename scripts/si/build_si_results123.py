from __future__ import annotations

import shutil
from pathlib import Path

import pandas as pd


ROOT = Path(__file__).resolve().parents[2]
SI_ROOT = ROOT / "docs" / "si"
TABLE_DIR = SI_ROOT / "tables"
FIG_DIR = SI_ROOT / "figures"


def ensure_dirs() -> None:
    for path in [SI_ROOT, TABLE_DIR, FIG_DIR, SI_ROOT / "scripts"]:
        path.mkdir(parents=True, exist_ok=True)


def copy_file(src: Path, dst: Path) -> None:
    dst.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(src, dst)


def write_csv(df: pd.DataFrame, filename: str) -> Path:
    path = TABLE_DIR / filename
    df.to_csv(path, index=False)
    return path


def read_xlsx(path: Path, sheet: str) -> pd.DataFrame:
    return pd.read_excel(path, sheet_name=sheet)


def build_tables() -> dict[str, Path]:
    paths: dict[str, Path] = {}

    # Result 1
    r1_xlsx = ROOT / "data" / "compact" / "result1" / "figure1_quantitative_analysis.xlsx"
    ab = read_xlsx(r1_xlsx, "A_B_trend_statistics")
    phase_stats = ab[ab["section"] == "phase_statistics"].copy()
    phase_stats = phase_stats[
        [
            "phase",
            "start_year",
            "end_year",
            "total_documents",
            "average_annual_count",
            "annual_growth_rate_cagr",
            "participating_countries",
            "peak_year",
            "peak_year_count",
            "count_increase_from_previous_phase",
            "country_increase_from_previous_phase",
            "phase4_to_phase3_growth_ratio",
        ]
    ]
    breakpoints = pd.DataFrame(
        {
            "breakpoint_end_year": [1947, 1971, 1993],
            "next_phase_start_year": [1948, 1972, 1994],
            "transition": ["Phase 1→2", "Phase 2→3", "Phase 3→4"],
            "source": [
                "scripts/result1/build_figure1_quantitative_package.py",
                "scripts/result1/build_figure1_quantitative_package.py",
                "scripts/result1/build_figure1_quantitative_package.py",
            ],
            "bic_comparison_available": [False, False, False],
            "note": [
                "Exact candidate-model BIC table was not found among saved outputs.",
                "Exact candidate-model BIC table was not found among saved outputs.",
                "Exact candidate-model BIC table was not found among saved outputs.",
            ],
        }
    )
    paths["Table_S1_phase_breakpoints.csv"] = write_csv(breakpoints, "Table_S1_phase_breakpoints.csv")
    paths["Table_S2_quantitative_characteristics_of_phases.csv"] = write_csv(
        phase_stats, "Table_S2_quantitative_characteristics_of_phases.csv"
    )

    # Result 2
    sdg_xlsx = ROOT / "inputs" / "auxiliary" / "overton_sdg_analysis.xlsx"
    diffusion_count = read_xlsx(sdg_xlsx, "sdg_goal_country_count_by_year")
    diffusion_intensity = read_xlsx(sdg_xlsx, "sdg_goal_diffusion_intensity_by_year")
    diffusion_speed = read_xlsx(sdg_xlsx, "sdg_goal_diffusion_speed_by_year")
    table_s3 = diffusion_count.merge(
        diffusion_intensity[["SDG_goal", "Year", "Diffusion_intensity"]],
        on=["SDG_goal", "Year"],
        how="left",
    ).merge(
        diffusion_speed[["SDG_goal", "Year", "Diffusion_speed"]],
        on=["SDG_goal", "Year"],
        how="left",
    )
    paths["Table_S3_SDG_diffusion_statistics.csv"] = write_csv(table_s3, "Table_S3_SDG_diffusion_statistics.csv")

    hhi_count = read_xlsx(sdg_xlsx, "sdg_goal_hhi_count_phase3_phase4")
    hhi_impact = read_xlsx(sdg_xlsx, "sdg_goal_hhi_impact_phase3_phase4")
    table_s4 = hhi_count.merge(
        hhi_impact[["SDG_goal", "Year", "HHI_impact"]],
        on=["SDG_goal", "Year"],
        how="left",
    )
    paths["Table_S4_concentration_and_inequality_metrics.csv"] = write_csv(
        table_s4, "Table_S4_concentration_and_inequality_metrics.csv"
    )

    weights_xlsx = ROOT / "outputs" / "methods" / "sdg_target_weights_final_v2.xlsx"
    weights = pd.read_excel(weights_xlsx)
    paths["Table_S5_ageing_energy_target_weights.csv"] = write_csv(
        weights, "Table_S5_ageing_energy_target_weights.csv"
    )

    story_xlsx = ROOT / "inputs" / "auxiliary" / "inputs/auxiliary/ageing_energy_story_analysis.xlsx"
    reg_age = read_xlsx(story_xlsx, "regression_ageing_index")
    reg_pooled = reg_age[reg_age["model_group"] == "ageing_alignment"].copy()
    reg_fe = reg_age[reg_age["model_group"].str.contains("fe", case=False)].copy()
    reg_imp = read_xlsx(story_xlsx, "regression_impact_index")
    paths["Table_S6_pooled_regression_results.csv"] = write_csv(
        reg_pooled, "Table_S6_pooled_regression_results.csv"
    )
    paths["Table_S7_fixed_effects_regression_results.csv"] = write_csv(
        reg_fe, "Table_S7_fixed_effects_regression_results.csv"
    )
    paths["Table_S8_policy_influence_and_efficiency_regressions.csv"] = write_csv(
        reg_imp, "Table_S8_policy_influence_and_efficiency_regressions.csv"
    )

    # Result 3
    taxonomy = pd.read_csv(ROOT / "data" / "compact" / "result3" / "data/compact/result3/keyword_taxonomy_mapping_clean.csv")
    paths["Table_S9_keyword_taxonomy.csv"] = write_csv(taxonomy, "Table_S9_keyword_taxonomy.csv")

    topicshare = pd.read_csv(ROOT / "data" / "compact" / "result3" / "data/compact/result3/topicshare_by_window_clean.csv")
    paths["Table_S10_topic_share_by_period.csv"] = write_csv(topicshare, "Table_S10_topic_share_by_period.csv")

    step8 = pd.read_csv(ROOT / "outputs" / "si" / "step8_pae" / "step8_pae_results.csv")
    paths["Table_S11_policy_attention_elasticity.csv"] = write_csv(
        step8, "Table_S11_policy_attention_elasticity.csv"
    )

    step9 = pd.read_csv(ROOT / "outputs" / "si" / "step9_network" / "step9_centrality_comparison.csv")
    paths["Table_S12_centrality_comparison_of_key_terms.csv"] = write_csv(
        step9, "Table_S12_centrality_comparison_of_key_terms.csv"
    )

    step10_t = pd.read_csv(ROOT / "outputs" / "si" / "step10_kl" / "step10_kl_timeseries.csv")
    step10_p = pd.read_csv(ROOT / "outputs" / "si" / "step10_kl" / "step10_kl_phase_summary.csv")
    paths["Table_S13a_KL_divergence_by_window.csv"] = write_csv(
        step10_t, "Table_S13a_KL_divergence_by_window.csv"
    )
    paths["Table_S13b_KL_divergence_by_phase.csv"] = write_csv(
        step10_p, "Table_S13b_KL_divergence_by_phase.csv"
    )

    return paths


def copy_figures() -> tuple[dict[str, Path], list[tuple[str, Path]]]:
    chosen = {
        "Figure_SA1_panels_ab_quantitative.png": ROOT / "outputs" / "figures" / "figure1_quantitative" / "figure1_panels_ab_quantitative.png",
        "Figure_SA2_panel_c_quantitative.png": ROOT / "outputs" / "figures" / "figure1_quantitative" / "figure1_panel_c_quantitative.png",
        "Figure_SA3_panels_dg_quantitative.png": ROOT / "outputs" / "figures" / "figure1_quantitative" / "figure1_panels_dg_quantitative.png",
        "Figure_SA4_panel_h_quantitative.png": ROOT / "outputs" / "figures" / "figure1_quantitative" / "figure1_panel_h_quantitative.png",
        "Figure_SB1_sdg_goal_phase_stacked.png": ROOT / "inputs" / "auxiliary" / "figure2_goal_phase_stacked.png",
        "Figure_SB2_sdg_goal_inequality_phase3_vs_phase4.png": ROOT / "inputs" / "auxiliary" / "figure5_goal_inequality_phase3_vs_phase4.png",
        "Figure_SB3_scatter_oadr_vs_index.png": ROOT / "inputs" / "auxiliary" / "scatter_oadr_vs_index.png",
        "Figure_SB4_scatter_index_vs_logimpact.png": ROOT / "inputs" / "auxiliary" / "scatter_index_vs_logimpact_bubble_count.png",
        "Figure_SB5_scatter_index_vs_efficiency.png": ROOT / "inputs" / "auxiliary" / "scatter_index_vs_efficiency.png",
        "Figure_SB6_inequality_timeseries.png": ROOT / "inputs" / "auxiliary" / "inequality_timeseries_gini_hhi.png",
        "Figure_SC1_topic_elasticity_ranking.png": ROOT / "outputs" / "si" / "step8_pae" / "figureS1_topic_elasticity_ranking.png",
        "Figure_SC2_centrality_comparison.png": ROOT / "outputs" / "si" / "step9_network" / "figureS2_centrality_comparison.png",
        "Figure_SC3_phase1_network.png": ROOT / "outputs" / "si" / "step9_network" / "phase1_network.png",
        "Figure_SC4_phase2_network.png": ROOT / "outputs" / "si" / "step9_network" / "phase2_network.png",
        "Figure_SC5_phase3_network.png": ROOT / "outputs" / "si" / "step9_network" / "phase3_network.png",
        "Figure_SC6_phase4_network.png": ROOT / "outputs" / "si" / "step9_network" / "phase4_network.png",
        "Figure_SC7_KL_divergence_trend.png": ROOT / "outputs" / "si" / "step10_kl" / "figureS3_kl_divergence_trend.png",
    }
    out: dict[str, Path] = {}
    missing: list[tuple[str, Path]] = []
    for name, src in chosen.items():
        if src.exists():
            dst = FIG_DIR / name
            copy_file(src, dst)
            out[name] = dst
        else:
            missing.append((name, src))
    return out, missing


def copy_summaries() -> dict[str, Path]:
    summaries = {
        "Result1_figure1_quantitative_interpretation.txt": ROOT / "docs" / "result1" / "figure1_quantitative_interpretation.txt",
        "Result2_overton_sdg_methods_note.txt": ROOT / "docs" / "result2" / "Result2_overton_sdg_methods_note.txt",
        "Result3_step8_pae_summary.md": ROOT / "docs" / "result3" / "Result3_step8_pae_summary.md",
        "Result3_step9_network_summary.md": ROOT / "docs" / "result3" / "Result3_step9_network_summary.md",
        "Result3_step10_kl_summary.md": ROOT / "docs" / "result3" / "Result3_step10_kl_summary.md",
    }
    out = {}
    summary_dir = SI_ROOT / "summaries"
    summary_dir.mkdir(parents=True, exist_ok=True)
    for name, src in summaries.items():
        dst = summary_dir / name
        copy_file(src, dst)
        out[name] = dst
    return out


def build_markdown(
    tables: dict[str, Path],
    figs: dict[str, Path],
    summaries: dict[str, Path],
    missing_figs: list[tuple[str, Path]],
) -> None:
    r1_interp = (ROOT / "docs" / "result1" / "figure1_quantitative_interpretation.txt").read_text(encoding="utf-8")
    overton_note = (ROOT / "docs" / "result2" / "Result2_overton_sdg_methods_note.txt").read_text(encoding="utf-8")
    step8_note = (ROOT / "docs" / "result3" / "Result3_step8_pae_summary.md").read_text(encoding="utf-8")
    step9_note = (ROOT / "docs" / "result3" / "Result3_step9_network_summary.md").read_text(encoding="utf-8")
    step10_note = (ROOT / "docs" / "result3" / "Result3_step10_kl_summary.md").read_text(encoding="utf-8")

    phase_table = pd.read_csv(tables["Table_S2_quantitative_characteristics_of_phases.csv"])
    step8 = pd.read_csv(tables["Table_S11_policy_attention_elasticity.csv"])
    step10_phase = pd.read_csv(tables["Table_S13b_KL_divergence_by_phase.csv"])

    md = f"""# Supplementary Information

## Supplementary Note 1. Temporal segmentation and structural evolution

This note documents the temporal segmentation and structural evolution results supporting Result 1. The retained four-phase structure is the one used throughout the current Figure 1 quantitative package. The saved project outputs identify transition years at 1948, 1972, and 1994, corresponding to end-of-phase breakpoints at 1947, 1971, and 1993. The exact candidate-model BIC comparison table is not present among the saved outputs, so the current SI reports the retained breakpoints and phase-level quantitative characteristics from the validated quantitative package rather than reconstructing a model-selection table.

Table S1 reports the retained breakpoint structure and records the absence of a saved candidate-model BIC table. Table S2 reports the quantitative characteristics of the four phases, including total documents, average annual counts, annual growth rates, participating countries, and phase-specific peak years. In the current outputs, Phase 4 contains {int(phase_table.loc[phase_table['phase']=='Phase 4','total_documents'].iloc[0]):,} documents with an average annual count of {phase_table.loc[phase_table['phase']=='Phase 4','average_annual_count'].iloc[0]:.1f}, compared with {int(phase_table.loc[phase_table['phase']=='Phase 3','total_documents'].iloc[0]):,} documents and an average annual count of {phase_table.loc[phase_table['phase']=='Phase 3','average_annual_count'].iloc[0]:.1f} in Phase 3. The existing quantitative interpretation file further records a Phase 4 annual growth rate of {phase_table.loc[phase_table['phase']=='Phase 4','annual_growth_rate_cagr'].iloc[0]*100:.2f}% and a Phase 4 to Phase 3 growth-rate ratio of {phase_table.loc[phase_table['phase']=='Phase 4','phase4_to_phase3_growth_ratio'].iloc[0]:.4f}.

The principal supporting figures for this note are the saved Figure 1 quantitative panels that remain available in the current project tree. Where a Figure 1 panel image is missing from the saved outputs, the SI retains the supporting workbook and interpretation note and flags the missing image in the manifest rather than recreating it. The companion interpretation note is retained in the SI summaries directory for traceability.

## Supplementary Note 2. SDG alignment, diffusion and concentration

This note consolidates the supplementary outputs supporting Result 2. All SDG-level tables are drawn from the current `overton_sdg_analysis.xlsx` workbook, which is the latest non-archived SDG analysis file found in the project directory. The saved methods note confirms the retained phase definitions (Phase 1: 1869–1947; Phase 2: 1948–1971; Phase 3: 1972–1993; Phase 4: 1994–2024), the SDG parsing rules, the exclusion of 2025–2026 from time-series analyses, and the use of concentration metrics such as HHI and Top-k shares.

Table S3 combines yearly diffusion breadth, diffusion intensity, and diffusion speed at the SDG-goal level. Table S4 combines HHI-based concentration metrics for counts and impact in Phase 3 and Phase 4. Table S5 reports the final v2 ageing–energy SDG target weights, including the embedding weight, the policy filter indicator, the pre-normalization score, and the final normalized weight. The current weight table contains 34 SDG targets. Table S6 reports the pooled ageing-alignment regressions available in the saved results workbook, while Table S7 isolates the fixed-effects row currently saved for the OADR-to-index model. Table S8 reports the saved policy influence and efficiency regressions linking the final v2 index to impact and efficiency.

The SDG and alignment figures retained for SI are Figure SB1 through Figure SB6. These include the saved SDG goal composition plot, the SDG inequality plot, and the current ageing–energy index supplementary plots linking OADR, impact, efficiency, and inequality to the validated final v2 index. No additional regressions were run during this SI assembly step. Results requested elsewhere but not found as saved outputs include separate OADR-to-count and OADR-to-impact regression tables beyond the correlations embedded in the Figure 1 quantitative package and the panel-level story workbook.

## Supplementary Note 3. Blind spots in policy attention

### 3.1 Taxonomy and thematic classification

Table S9 reproduces the clean keyword taxonomy mapping currently used for Result 3. The retained taxonomy excludes low-relevance keywords from the classified set and does not introduce a generic governance category. The six active categories are welfare and care, health and vulnerability, housing and thermal comfort, energy transition and efficiency, household behaviour and adoption, and affordability and income constraints. This table is copied directly from the current `data/compact/result3/keyword_taxonomy_mapping_clean.csv` file.

### 3.2 Topic intensity and temporal composition

Table S10 reproduces the window-level topic-share results currently used in Figure 4 and subsequent supplementary diagnostics. These values are drawn directly from `data/compact/result3/topicshare_by_window_clean.csv`, where shares are computed only over classified keywords. The table therefore reflects the clean taxonomy denominator rather than the full token set.

### 3.3 Policy Attention Elasticity

Table S11 reproduces the elasticity estimates from Step 8. The saved summary identifies housing and thermal comfort as the largest positive elasticity estimate (epsilon = {step8.loc[step8['category']=='housing and thermal comfort','epsilon_k'].iloc[0]:.4f}) and household behaviour and adoption as weak and statistically non-significant (epsilon = {step8.loc[step8['category']=='household behaviour and adoption','epsilon_k'].iloc[0]:.4f}, p = {step8.loc[step8['category']=='household behaviour and adoption','p_value'].iloc[0]:.4f}). Figure SC1 provides the publication-style ranking plot generated directly from the saved Step 8 results.

### 3.4 Network path dependency and semantic centrality

Table S12 reproduces the cross-phase centrality comparison of key mechanism and macro terms from Step 9. The saved Step 9 summary shows that household appears only at rank 28 in Phase 3 and rank 34 in Phase 4, thermal comfort appears only once at rank 35 in Phase 3, energy poverty appears only in Phase 4 at rank 36, fuel poverty appears only in Phase 4 at rank 38, and retrofit appears only in Phase 4 at rank 39. By contrast, the saved phase-level network metrics place macro terms such as economic and social near the top of the centrality hierarchy in Phases 2 and 3, and climate/climate change at the core in Phase 4. Figure SC2 reproduces the saved centrality comparison plot, while Figure SC3–SC6 retain the four saved phase-wise network plots.

### 3.5 Mechanism mismatch quantified by KL divergence

Table S13a reports the saved window-level KL divergence series, and Table S13b reports the saved phase averages. The current Step 10 summary defines the theoretical reference distribution Q as the equal-weight six-category baseline, because no explicit numeric balanced mechanism vector was found among the project files. In the saved results, Phase 3 has a mean KL divergence of {step10_phase.loc[step10_phase['phase']=='Phase 3','mean_kl'].iloc[0]:.6f}, whereas Phase 4 has a lower mean KL divergence of {step10_phase.loc[step10_phase['phase']=='Phase 4','mean_kl'].iloc[0]:.6f}. Figure SC7 reproduces the saved KL trend plot, which is retained here as a supplementary diagnostic rather than a standalone main-text result.

## Supplementary Tables

- Table S1. Retained phase breakpoints and segmentation support: [`tables/Table_S1_phase_breakpoints.csv`](tables/Table_S1_phase_breakpoints.csv)
- Table S2. Quantitative characteristics of phases: [`tables/Table_S2_quantitative_characteristics_of_phases.csv`](tables/Table_S2_quantitative_characteristics_of_phases.csv)
- Table S3. SDG diffusion statistics: [`tables/Table_S3_SDG_diffusion_statistics.csv`](tables/Table_S3_SDG_diffusion_statistics.csv)
- Table S4. Concentration and inequality metrics: [`tables/Table_S4_concentration_and_inequality_metrics.csv`](tables/Table_S4_concentration_and_inequality_metrics.csv)
- Table S5. Ageing–energy SDG target weights (final v2): [`tables/Table_S5_ageing_energy_target_weights.csv`](tables/Table_S5_ageing_energy_target_weights.csv)
- Table S6. Pooled regression results: [`tables/Table_S6_pooled_regression_results.csv`](tables/Table_S6_pooled_regression_results.csv)
- Table S7. Fixed-effects regression results: [`tables/Table_S7_fixed_effects_regression_results.csv`](tables/Table_S7_fixed_effects_regression_results.csv)
- Table S8. Policy influence and efficiency regressions: [`tables/Table_S8_policy_influence_and_efficiency_regressions.csv`](tables/Table_S8_policy_influence_and_efficiency_regressions.csv)
- Table S9. Keyword taxonomy: [`tables/Table_S9_keyword_taxonomy.csv`](tables/Table_S9_keyword_taxonomy.csv)
- Table S10. Topic share by period: [`tables/Table_S10_topic_share_by_period.csv`](tables/Table_S10_topic_share_by_period.csv)
- Table S11. Policy attention elasticity results: [`tables/Table_S11_policy_attention_elasticity.csv`](tables/Table_S11_policy_attention_elasticity.csv)
- Table S12. Centrality comparison of key terms: [`tables/Table_S12_centrality_comparison_of_key_terms.csv`](tables/Table_S12_centrality_comparison_of_key_terms.csv)
- Table S13a. KL divergence by window: [`tables/Table_S13a_KL_divergence_by_window.csv`](tables/Table_S13a_KL_divergence_by_window.csv)
- Table S13b. KL divergence by phase: [`tables/Table_S13b_KL_divergence_by_phase.csv`](tables/Table_S13b_KL_divergence_by_phase.csv)

## Supplementary Figures

- Figure SA1–SA4. Figure 1 quantitative panel images were expected from the saved output set; available images were copied to the SI figures directory, and missing ones are listed in the manifest.
- Figure SB1. SDG goal composition over time: [`figures/Figure_SB1_sdg_goal_phase_stacked.png`](figures/Figure_SB1_sdg_goal_phase_stacked.png)
- Figure SB2. SDG inequality comparison: [`figures/Figure_SB2_sdg_goal_inequality_phase3_vs_phase4.png`](figures/Figure_SB2_sdg_goal_inequality_phase3_vs_phase4.png)
- Figure SB3. OADR versus ageing–energy index: [`figures/Figure_SB3_scatter_oadr_vs_index.png`](figures/Figure_SB3_scatter_oadr_vs_index.png)
- Figure SB4. Ageing–energy index versus impact: [`figures/Figure_SB4_scatter_index_vs_logimpact.png`](figures/Figure_SB4_scatter_index_vs_logimpact.png)
- Figure SB5. Ageing–energy index versus efficiency: [`figures/Figure_SB5_scatter_index_vs_efficiency.png`](figures/Figure_SB5_scatter_index_vs_efficiency.png)
- Figure SB6. Inequality time series: [`figures/Figure_SB6_inequality_timeseries.png`](figures/Figure_SB6_inequality_timeseries.png)
- Figure SC1. Topic elasticity ranking: [`figures/Figure_SC1_topic_elasticity_ranking.png`](figures/Figure_SC1_topic_elasticity_ranking.png)
- Figure SC2. Centrality comparison of key terms: [`figures/Figure_SC2_centrality_comparison.png`](figures/Figure_SC2_centrality_comparison.png)
- Figure SC3. Phase 1 network: [`figures/Figure_SC3_phase1_network.png`](figures/Figure_SC3_phase1_network.png)
- Figure SC4. Phase 2 network: [`figures/Figure_SC4_phase2_network.png`](figures/Figure_SC4_phase2_network.png)
- Figure SC5. Phase 3 network: [`figures/Figure_SC5_phase3_network.png`](figures/Figure_SC5_phase3_network.png)
- Figure SC6. Phase 4 network: [`figures/Figure_SC6_phase4_network.png`](figures/Figure_SC6_phase4_network.png)
- Figure SC7. KL divergence trend: [`figures/Figure_SC7_KL_divergence_trend.png`](figures/Figure_SC7_KL_divergence_trend.png)
"""

    (SI_ROOT / "supplementary_information_results123.md").write_text(md, encoding="utf-8")

    missing_section = "\n".join(f"- expected `{name}` from `{src}` but file was not found" for name, src in missing_figs) or "- none"

    manifest = f"""# Supplementary Manifest

## Overview

This manifest records the files used to assemble the Results 1–3 supplementary information package. The SI assembly step reused existing project outputs and did not rerun the substantive analyses.

## Result 1 files

### Used
- `data/compact/result1/figure1_quantitative_analysis.xlsx`
  - Used for Table S2 and supporting panel-level quantitative values.
- `docs/result1/figure1_quantitative_interpretation.txt`
  - Used as the saved narrative interpretation source for Supplementary Note 1.
- `scripts/result1/build_figure1_quantitative_package.py`
  - Used to verify the retained breakpoint structure (1948, 1972, 1994 transitions).

### Ignored old version
- `archive_old/...`
  - Ignored because archived outputs do not correspond to the current Figure 1 package.

### Missing
- Exact candidate-model BIC comparison table for the segmentation search was not found among saved outputs.
  - SI therefore uses the retained breakpoint structure and phase statistics, but does not reproduce a full model-selection table with BIC values.
- Missing saved Figure 1 panel image files:
{missing_section}

## Result 2 files

### Used
- `inputs/auxiliary/overton_sdg_analysis.xlsx`
  - Latest non-archived SDG workbook; used for diffusion, concentration, HHI, and phase-level SDG tables.
- `docs/result2/Result2_overton_sdg_methods_note.txt`
  - Used for the saved SDG parsing and metric definitions.
- `outputs/methods/sdg_target_weights_final_v2.xlsx`
  - Used for Table S5 target weights.
- `inputs/auxiliary/ageing_energy_index_final_v2.xlsx`
  - Used as the validated final v2 index source.
- `inputs/auxiliary/ageing_energy_story_analysis.xlsx`
  - Used for the saved pooled/fixed-effects and policy influence regressions, plus inequality outputs.
- `inputs/auxiliary/figure2_goal_phase_stacked.png`
- `inputs/auxiliary/figure5_goal_inequality_phase3_vs_phase4.png`
- `inputs/auxiliary/scatter_oadr_vs_index.png`
- `inputs/auxiliary/scatter_index_vs_logimpact_bubble_count.png`
- `inputs/auxiliary/scatter_index_vs_efficiency.png`
- `inputs/auxiliary/inequality_timeseries_gini_hhi.png`

### Ignored old version
- `archive_old/...`
  - Ignored because archived SDG and ageing-energy outputs predate the current final_v2 framework.
- Previously named panel workbooks such as `sdg_diffusion_concentration_data.xlsx`, `sdg_all_non_map_data.xlsx`, and `sdg_figure_panel_data.xlsx`
  - Not found in the current project tree; the current consolidated source is `inputs/auxiliary/overton_sdg_analysis.xlsx`.

### Missing
- Separate saved OADR-to-count and OADR-to-impact regression output tables were not found.
  - The current SI therefore uses the saved `inputs/auxiliary/ageing_energy_story_analysis.xlsx` regression tables and notes the missing saved extensions.

## Result 3 files

### Used
- `data/compact/result3/keyword_taxonomy_mapping_clean.csv`
- `data/compact/result3/topicshare_by_window_clean.csv`
- `outputs/si/step8_pae/step8_pae_results.csv`
- `outputs/si/step8_pae/step8_pae_ranked.csv`
- `outputs/si/step8_pae/step8_pae_summary.md`
- `outputs/si/step9_network/phase1_network_metrics.csv`
- `outputs/si/step9_network/phase2_network_metrics.csv`
- `outputs/si/step9_network/phase3_network_metrics.csv`
- `outputs/si/step9_network/phase4_network_metrics.csv`
- `outputs/si/step9_network/step9_centrality_comparison.csv`
- `outputs/si/step9_network/step9_network_summary.md`
- `outputs/si/step10_kl/step10_kl_timeseries.csv`
- `outputs/si/step10_kl/step10_kl_phase_summary.csv`
- `outputs/si/step10_kl/step10_kl_summary.md`
- `outputs/si/step8_pae/figureS1_topic_elasticity_ranking.png`
- `outputs/si/step9_network/figureS2_centrality_comparison.png`
- `outputs/si/step9_network/phase1_network.png`
- `outputs/si/step9_network/phase2_network.png`
- `outputs/si/step9_network/phase3_network.png`
- `outputs/si/step9_network/phase4_network.png`
- `outputs/si/step10_kl/figureS3_kl_divergence_trend.png`

### Ignored old version
- `archive_old/third_part_ageing_energy_policy_focus_v2/...`
  - Ignored because the current Result 3 workflow is the cleaned post-stepwise version reflected in `outputs/si/`.

## Files generated by SI assembly

### Main documents
- `docs/si/supplementary_information_results123.md`
- `docs/si/supplementary_manifest.md`

### Tables
{chr(10).join(f'- `{p}`' for p in sorted(str(v) for v in tables.values()))}

### Figures
{chr(10).join(f'- `{p}`' for p in sorted(str(v) for v in figs.values()))}

### Summaries copied into SI
{chr(10).join(f'- `{p}`' for p in sorted(str(v) for v in summaries.values()))}
"""

    (SI_ROOT / "supplementary_manifest.md").write_text(manifest, encoding="utf-8")


def main() -> None:
    ensure_dirs()
    tables = build_tables()
    figs, missing_figs = copy_figures()
    summaries = copy_summaries()
    build_markdown(tables, figs, summaries, missing_figs)


if __name__ == "__main__":
    main()
