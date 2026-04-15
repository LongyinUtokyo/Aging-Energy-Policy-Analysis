# Supplementary Information

## Supplementary Note 1. Temporal segmentation and structural evolution

This note documents the temporal segmentation and structural evolution results supporting Result 1. The retained four-phase structure is the one used throughout the current Figure 1 quantitative package. The saved project outputs identify transition years at 1948, 1972, and 1994, corresponding to end-of-phase breakpoints at 1947, 1971, and 1993. The exact candidate-model BIC comparison table is not present among the saved outputs, so the current SI reports the retained breakpoints and phase-level quantitative characteristics from the validated quantitative package rather than reconstructing a model-selection table.

Table S1 reports the retained breakpoint structure and records the absence of a saved candidate-model BIC table. Table S2 reports the quantitative characteristics of the four phases, including total documents, average annual counts, annual growth rates, participating countries, and phase-specific peak years. In the current outputs, Phase 4 contains 153,454 documents with an average annual count of 4950.1, compared with 4,773 documents and an average annual count of 217.0 in Phase 3. The existing quantitative interpretation file further records a Phase 4 annual growth rate of 11.16% and a Phase 4 to Phase 3 growth-rate ratio of 4.2578.

The principal supporting figures for this note are the saved Figure 1 quantitative panels that remain available in the current project tree. Where a Figure 1 panel image is missing from the saved outputs, the SI retains the supporting workbook and interpretation note and flags the missing image in the manifest rather than recreating it. The companion interpretation note is retained in the SI summaries directory for traceability.

## Supplementary Note 2. SDG alignment, diffusion and concentration

This note consolidates the supplementary outputs supporting Result 2. All SDG-level tables are drawn from the current `overton_sdg_analysis.xlsx` workbook, which is the latest non-archived SDG analysis file found in the project directory. The saved methods note confirms the retained phase definitions (Phase 1: 1869–1947; Phase 2: 1948–1971; Phase 3: 1972–1993; Phase 4: 1994–2024), the SDG parsing rules, the exclusion of 2025–2026 from time-series analyses, and the use of concentration metrics such as HHI and Top-k shares.

Table S3 combines yearly diffusion breadth, diffusion intensity, and diffusion speed at the SDG-goal level. Table S4 combines HHI-based concentration metrics for counts and impact in Phase 3 and Phase 4. Table S5 reports the final v2 ageing–energy SDG target weights, including the embedding weight, the policy filter indicator, the pre-normalization score, and the final normalized weight. The current weight table contains 34 SDG targets. Table S6 reports the pooled ageing-alignment regressions available in the saved results workbook, while Table S7 isolates the fixed-effects row currently saved for the OADR-to-index model. Table S8 reports the saved policy influence and efficiency regressions linking the final v2 index to impact and efficiency.

The SDG and alignment figures retained for SI are Figure SB1 through Figure SB6. These include the saved SDG goal composition plot, the SDG inequality plot, and the current ageing–energy index supplementary plots linking OADR, impact, efficiency, and inequality to the validated final v2 index. No additional regressions were run during this SI assembly step. Results requested elsewhere but not found as saved outputs include separate OADR-to-count and OADR-to-impact regression tables beyond the correlations embedded in the Figure 1 quantitative package and the panel-level story workbook.

## Supplementary Note 3. Blind spots in policy attention

### 3.1 Taxonomy and thematic classification

Table S9 reproduces the clean keyword taxonomy mapping currently used for Result 3. The retained taxonomy excludes low-relevance keywords from the classified set and does not introduce a generic governance category. The six active categories are welfare and care, health and vulnerability, housing and thermal comfort, energy transition and efficiency, household behaviour and adoption, and affordability and income constraints. This table is copied directly from the current `keyword_taxonomy_mapping_clean.csv` file.

### 3.2 Topic intensity and temporal composition

Table S10 reproduces the window-level topic-share results currently used in Figure 4 and subsequent supplementary diagnostics. These values are drawn directly from `topicshare_by_window_clean.csv`, where shares are computed only over classified keywords. The table therefore reflects the clean taxonomy denominator rather than the full token set.

### 3.3 Policy Attention Elasticity

Table S11 reproduces the elasticity estimates from Step 8. The saved summary identifies housing and thermal comfort as the largest positive elasticity estimate (epsilon = 3.1657) and household behaviour and adoption as weak and statistically non-significant (epsilon = -0.1800, p = 0.6017). Figure SC1 provides the publication-style ranking plot generated directly from the saved Step 8 results.

### 3.4 Network path dependency and semantic centrality

Table S12 reproduces the cross-phase centrality comparison of key mechanism and macro terms from Step 9. The saved Step 9 summary shows that household appears only at rank 28 in Phase 3 and rank 34 in Phase 4, thermal comfort appears only once at rank 35 in Phase 3, energy poverty appears only in Phase 4 at rank 36, fuel poverty appears only in Phase 4 at rank 38, and retrofit appears only in Phase 4 at rank 39. By contrast, the saved phase-level network metrics place macro terms such as economic and social near the top of the centrality hierarchy in Phases 2 and 3, and climate/climate change at the core in Phase 4. Figure SC2 reproduces the saved centrality comparison plot, while Figure SC3–SC6 retain the four saved phase-wise network plots.

### 3.5 Mechanism mismatch quantified by KL divergence

Table S13a reports the saved window-level KL divergence series, and Table S13b reports the saved phase averages. The current Step 10 summary defines the theoretical reference distribution Q as the equal-weight six-category baseline, because no explicit numeric balanced mechanism vector was found among the project files. In the saved results, Phase 3 has a mean KL divergence of 0.347116, whereas Phase 4 has a lower mean KL divergence of 0.159120. Figure SC7 reproduces the saved KL trend plot, which is retained here as a supplementary diagnostic rather than a standalone main-text result.

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
