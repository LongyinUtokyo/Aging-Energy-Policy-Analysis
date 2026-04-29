# Main-text figure manifest

This manifest records the current manuscript figure numbering and the corresponding scripts, compact data, and retained figure assets.

## Current figure numbering

| Figure | Result block | Working folder |
|---|---|---|
| Figure 1 | Result 1 | `figure1_temporal_spatial_policy_expansion` |
| Figure 2 | Result 2 | `figure2_sdg_goal_distribution` |
| Figure 3 | Result 2 | `figure3_sdg_diffusion_inequality` |
| Figure 4 | Result 3 | `figure4_policy_blind_spots` |

## Figure 1

| Item | Path |
|---|---|
| Topic | Temporal-spatial expansion and structural phase dynamics of ageing-energy policy attention. |
| Current main-figure script | `scripts/main_figures/figure1/build_figure1_quantitative_package.py` |
| Result-level script | `scripts/result1/build_figure1_quantitative_package.py` |
| Compact data | `data/compact/result1/figure1_quantitative_analysis.xlsx` |
| Notes | `docs/result1/figure1_quantitative_interpretation.txt` |
| Retained figure asset | `figures/main_text/result1/macro_policy_framing_clean.png` |

## Figure 2

| Item | Path |
|---|---|
| Topic | SDG goal-level distribution, country contributions, annual SDG composition, and document-count versus impact comparison. |
| Current scripts | `scripts/main_figures/figure2/analyze_overton_sdg.py`; `scripts/main_figures/figure2/add_sdg_companion_figures.py`; `scripts/main_figures/figure2/rebuild_sdg_figures.py`; `scripts/main_figures/figure2/revise_sdg_smoothing_and_style.py` |
| Result-level scripts | `scripts/result2/*.py` |
| Compact SDG target-weight data | `data/compact/result2/fig_sdg_target_weight_*.csv` |
| Retained figure assets | `figures/main_text/result2/figure1_goal_overall_distribution.png`; `figures/main_text/result2/figure2_goal_phase_stacked.png`; `figures/main_text/result2/fig4_goal_count_vs_impact_final.png`; `figures/main_text/result2/figure5_goal_inequality_phase3_vs_phase4.png` |

## Figure 3

| Item | Path |
|---|---|
| Topic | SDG diffusion, document and impact concentration, mean ageing-energy index geography, and OADR-index quadrant alignment. |
| Current panel b-c script | `scripts/main_figures/figure3/make_figure3_panel_b_c_maps.py` |
| Panel a data family | `data/compact/result2/fig2_2_a*.csv`; `data/compact/result2/fig2_2_b*.csv`; `data/compact/result2/fig2_2_c*.csv` |
| Panel b data family | `data/compact/result2/fig2_2_d1_ageing_energy_index.csv`; `data/compact/result2/fig2_2_d2_inequality_metrics.csv` |
| Panel c data family | `data/compact/result2/fig2_2_e1_country_classification.csv`; `data/compact/result2/fig2_2_e2_scatter_data.csv` |
| Current working panel outputs | `working_project/07_figures_working/current_manuscript_figures/figure3_sdg_diffusion_inequality/` in the local desktop project. |

## Figure 4

| Item | Path |
|---|---|
| Topic | Policy blind spots in ageing-related energy policy. |
| Current panel scripts | `scripts/main_figures/figure4/build_panel_a_final_individual.py`; `scripts/main_figures/figure4/build_panel_b_c_redraw.py`; `scripts/main_figures/figure4/redraw_panel_d_overlay.py`; `scripts/main_figures/figure4/redraw_panel_e_macro_mechanism.py`; `scripts/main_figures/figure4/make_blind_spot_distribution_inset.py` |
| Supporting word-cloud scripts | `scripts/main_figures/figure4/build_clean_period_wordclouds.py`; `scripts/main_figures/figure4/build_full_keyword_wordclouds.py` |
| Result-level pipeline scripts | `scripts/result3/01_merge_clean.py` through `scripts/result3/07_run_all.py`; `scripts/result3/pipeline.py` |
| Compact data | `data/compact/result3/keyword_taxonomy_mapping_clean.csv`; `data/compact/result3/topicshare_by_window_clean.csv`; `data/compact/result3/figure3_panel_data_clean/` |
| Current working panel outputs | `working_project/07_figures_working/current_manuscript_figures/figure4_policy_blind_spots/` in the local desktop project. |

## Shared methods

| Method layer | Path |
|---|---|
| Ageing-energy SDG index construction | `scripts/methods/build_ageing_energy_index.py` |
| Embedding validation | `scripts/methods/build_ageing_energy_embedding_validation.py` |
| Final framework construction | `scripts/methods/build_ageing_energy_final_framework.py`; `scripts/methods/build_ageing_energy_final_framework_v2.py` |
| Methods notes | `docs/ageing_energy_index_methods.txt`; `docs/ageing_energy_final_methods.txt`; `docs/ageing_energy_sdg_validation_methods.txt` |

## Path audit

Audit date: 2026-04-29.

| Path | Status |
|---|---|
| `scripts/main_figures/figure1/build_figure1_quantitative_package.py` | present |
| `scripts/main_figures/figure2/analyze_overton_sdg.py` | present |
| `scripts/main_figures/figure2/add_sdg_companion_figures.py` | present |
| `scripts/main_figures/figure2/rebuild_sdg_figures.py` | present |
| `scripts/main_figures/figure2/revise_sdg_smoothing_and_style.py` | present |
| `scripts/main_figures/figure3/make_figure3_panel_b_c_maps.py` | present |
| `scripts/main_figures/figure4/build_panel_a_final_individual.py` | present |
| `scripts/main_figures/figure4/build_panel_b_c_redraw.py` | present |
| `scripts/main_figures/figure4/redraw_panel_d_overlay.py` | present |
| `scripts/main_figures/figure4/redraw_panel_e_macro_mechanism.py` | present |
| `scripts/main_figures/figure4/make_blind_spot_distribution_inset.py` | present |
