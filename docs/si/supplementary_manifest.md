# Supplementary Manifest

## Overview

This manifest records the files used to assemble the Results 1–3 supplementary information package. The SI assembly step reused existing project outputs and did not rerun the substantive analyses.

## Result 1 files

### Used
- `/Users/longlab/Documents/New project/results_1/figure1_quantitative_analysis.xlsx`
  - Used for Table S2 and supporting panel-level quantitative values.
- `/Users/longlab/Documents/New project/results_1/figure1_quantitative_interpretation.txt`
  - Used as the saved narrative interpretation source for Supplementary Note 1.
- `/Users/longlab/Documents/New project/results_1/scripts/build_figure1_quantitative_package.py`
  - Used to verify the retained breakpoint structure (1948, 1972, 1994 transitions).

### Ignored old version
- `/Users/longlab/Documents/New project/archive_old/...`
  - Ignored because archived outputs do not correspond to the current Figure 1 package.

### Missing
- Exact candidate-model BIC comparison table for the segmentation search was not found among saved outputs.
  - SI therefore uses the retained breakpoint structure and phase statistics, but does not reproduce a full model-selection table with BIC values.
- Missing saved Figure 1 panel image files:
- expected `Figure_SA1_panels_ab_quantitative.png` from `/Users/longlab/Documents/New project/outputs/figures/figure1_quantitative/figure1_panels_ab_quantitative.png` but file was not found
- expected `Figure_SA2_panel_c_quantitative.png` from `/Users/longlab/Documents/New project/outputs/figures/figure1_quantitative/figure1_panel_c_quantitative.png` but file was not found
- expected `Figure_SA3_panels_dg_quantitative.png` from `/Users/longlab/Documents/New project/outputs/figures/figure1_quantitative/figure1_panels_dg_quantitative.png` but file was not found
- expected `Figure_SA4_panel_h_quantitative.png` from `/Users/longlab/Documents/New project/outputs/figures/figure1_quantitative/figure1_panel_h_quantitative.png` but file was not found

## Result 2 files

### Used
- `/Users/longlab/Documents/New project/outputs/overton_sdg_analysis.xlsx`
  - Latest non-archived SDG workbook; used for diffusion, concentration, HHI, and phase-level SDG tables.
- `/Users/longlab/Documents/New project/outputs/overton_sdg_methods_note.txt`
  - Used for the saved SDG parsing and metric definitions.
- `/Users/longlab/Documents/New project/common/weights/sdg_target_weights_final_v2.xlsx`
  - Used for Table S5 target weights.
- `/Users/longlab/Documents/New project/common/data/ageing_energy_index_final_v2.xlsx`
  - Used as the validated final v2 index source.
- `/Users/longlab/Documents/New project/ageing_energy_story_analysis.xlsx`
  - Used for the saved pooled/fixed-effects and policy influence regressions, plus inequality outputs.
- `/Users/longlab/Documents/New project/outputs/figures/figure2_goal_phase_stacked.png`
- `/Users/longlab/Documents/New project/outputs/figures/figure5_goal_inequality_phase3_vs_phase4.png`
- `/Users/longlab/Documents/New project/outputs/figures/ageing_energy_story/scatter_oadr_vs_index.png`
- `/Users/longlab/Documents/New project/outputs/figures/ageing_energy_story/scatter_index_vs_logimpact_bubble_count.png`
- `/Users/longlab/Documents/New project/outputs/figures/ageing_energy_story/scatter_index_vs_efficiency.png`
- `/Users/longlab/Documents/New project/outputs/figures/ageing_energy_story/inequality_timeseries_gini_hhi.png`

### Ignored old version
- `/Users/longlab/Documents/New project/archive_old/...`
  - Ignored because archived SDG and ageing-energy outputs predate the current final_v2 framework.
- Previously named panel workbooks such as `sdg_diffusion_concentration_data.xlsx`, `sdg_all_non_map_data.xlsx`, and `sdg_figure_panel_data.xlsx`
  - Not found in the current project tree; the current consolidated source is `outputs/overton_sdg_analysis.xlsx`.

### Missing
- Separate saved OADR-to-count and OADR-to-impact regression output tables were not found.
  - The current SI therefore uses the saved `ageing_energy_story_analysis.xlsx` regression tables and notes the missing saved extensions.

## Result 3 files

### Used
- `/Users/longlab/Documents/New project/keyword_taxonomy_mapping_clean.csv`
- `/Users/longlab/Documents/New project/topicshare_by_window_clean.csv`
- `/Users/longlab/Documents/New project/analysis/result3_si/step8_pae/step8_pae_results.csv`
- `/Users/longlab/Documents/New project/analysis/result3_si/step8_pae/step8_pae_ranked.csv`
- `/Users/longlab/Documents/New project/analysis/result3_si/step8_pae/step8_pae_summary.md`
- `/Users/longlab/Documents/New project/analysis/result3_si/step9_network/phase1_network_metrics.csv`
- `/Users/longlab/Documents/New project/analysis/result3_si/step9_network/phase2_network_metrics.csv`
- `/Users/longlab/Documents/New project/analysis/result3_si/step9_network/phase3_network_metrics.csv`
- `/Users/longlab/Documents/New project/analysis/result3_si/step9_network/phase4_network_metrics.csv`
- `/Users/longlab/Documents/New project/analysis/result3_si/step9_network/step9_centrality_comparison.csv`
- `/Users/longlab/Documents/New project/analysis/result3_si/step9_network/step9_network_summary.md`
- `/Users/longlab/Documents/New project/analysis/result3_si/step10_kl/step10_kl_timeseries.csv`
- `/Users/longlab/Documents/New project/analysis/result3_si/step10_kl/step10_kl_phase_summary.csv`
- `/Users/longlab/Documents/New project/analysis/result3_si/step10_kl/step10_kl_summary.md`
- `/Users/longlab/Documents/New project/analysis/result3_si/step8_pae/figureS1_topic_elasticity_ranking.png`
- `/Users/longlab/Documents/New project/analysis/result3_si/step9_network/figureS2_centrality_comparison.png`
- `/Users/longlab/Documents/New project/analysis/result3_si/step9_network/phase1_network.png`
- `/Users/longlab/Documents/New project/analysis/result3_si/step9_network/phase2_network.png`
- `/Users/longlab/Documents/New project/analysis/result3_si/step9_network/phase3_network.png`
- `/Users/longlab/Documents/New project/analysis/result3_si/step9_network/phase4_network.png`
- `/Users/longlab/Documents/New project/analysis/result3_si/step10_kl/figureS3_kl_divergence_trend.png`

### Ignored old version
- `/Users/longlab/Documents/New project/archive_old/third_part_ageing_energy_policy_focus_v2/...`
  - Ignored because the current Result 3 workflow is the cleaned post-stepwise version in the root project and `analysis/result3_si`.

## Files generated by SI assembly

### Main documents
- `/Users/longlab/Documents/New project/analysis/SI/supplementary_information_results123.md`
- `/Users/longlab/Documents/New project/analysis/SI/supplementary_manifest.md`

### Tables
- `/Users/longlab/Documents/New project/analysis/SI/tables/Table_S10_topic_share_by_period.csv`
- `/Users/longlab/Documents/New project/analysis/SI/tables/Table_S11_policy_attention_elasticity.csv`
- `/Users/longlab/Documents/New project/analysis/SI/tables/Table_S12_centrality_comparison_of_key_terms.csv`
- `/Users/longlab/Documents/New project/analysis/SI/tables/Table_S13a_KL_divergence_by_window.csv`
- `/Users/longlab/Documents/New project/analysis/SI/tables/Table_S13b_KL_divergence_by_phase.csv`
- `/Users/longlab/Documents/New project/analysis/SI/tables/Table_S1_phase_breakpoints.csv`
- `/Users/longlab/Documents/New project/analysis/SI/tables/Table_S2_quantitative_characteristics_of_phases.csv`
- `/Users/longlab/Documents/New project/analysis/SI/tables/Table_S3_SDG_diffusion_statistics.csv`
- `/Users/longlab/Documents/New project/analysis/SI/tables/Table_S4_concentration_and_inequality_metrics.csv`
- `/Users/longlab/Documents/New project/analysis/SI/tables/Table_S5_ageing_energy_target_weights.csv`
- `/Users/longlab/Documents/New project/analysis/SI/tables/Table_S6_pooled_regression_results.csv`
- `/Users/longlab/Documents/New project/analysis/SI/tables/Table_S7_fixed_effects_regression_results.csv`
- `/Users/longlab/Documents/New project/analysis/SI/tables/Table_S8_policy_influence_and_efficiency_regressions.csv`
- `/Users/longlab/Documents/New project/analysis/SI/tables/Table_S9_keyword_taxonomy.csv`

### Figures
- `/Users/longlab/Documents/New project/analysis/SI/figures/Figure_SB1_sdg_goal_phase_stacked.png`
- `/Users/longlab/Documents/New project/analysis/SI/figures/Figure_SB2_sdg_goal_inequality_phase3_vs_phase4.png`
- `/Users/longlab/Documents/New project/analysis/SI/figures/Figure_SB3_scatter_oadr_vs_index.png`
- `/Users/longlab/Documents/New project/analysis/SI/figures/Figure_SB4_scatter_index_vs_logimpact.png`
- `/Users/longlab/Documents/New project/analysis/SI/figures/Figure_SB5_scatter_index_vs_efficiency.png`
- `/Users/longlab/Documents/New project/analysis/SI/figures/Figure_SB6_inequality_timeseries.png`
- `/Users/longlab/Documents/New project/analysis/SI/figures/Figure_SC1_topic_elasticity_ranking.png`
- `/Users/longlab/Documents/New project/analysis/SI/figures/Figure_SC2_centrality_comparison.png`
- `/Users/longlab/Documents/New project/analysis/SI/figures/Figure_SC3_phase1_network.png`
- `/Users/longlab/Documents/New project/analysis/SI/figures/Figure_SC4_phase2_network.png`
- `/Users/longlab/Documents/New project/analysis/SI/figures/Figure_SC5_phase3_network.png`
- `/Users/longlab/Documents/New project/analysis/SI/figures/Figure_SC6_phase4_network.png`
- `/Users/longlab/Documents/New project/analysis/SI/figures/Figure_SC7_KL_divergence_trend.png`

### Summaries copied into SI
- `/Users/longlab/Documents/New project/analysis/SI/summaries/Result1_figure1_quantitative_interpretation.txt`
- `/Users/longlab/Documents/New project/analysis/SI/summaries/Result2_overton_sdg_methods_note.txt`
- `/Users/longlab/Documents/New project/analysis/SI/summaries/Result3_step10_kl_summary.md`
- `/Users/longlab/Documents/New project/analysis/SI/summaries/Result3_step8_pae_summary.md`
- `/Users/longlab/Documents/New project/analysis/SI/summaries/Result3_step9_network_summary.md`
