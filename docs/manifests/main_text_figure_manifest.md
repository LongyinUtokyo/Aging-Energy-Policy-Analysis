# Main-text figure manifest

This file maps the figures used in the main paper to the scripts and compact data retained in this repository.

It is intended to answer three practical questions:

1. Which script generated the figure logic?
2. Which compact tables support the figure?
3. Which figure asset or panel package is retained in the repository?

## Figure 1

### Topic

Temporal segmentation and structural evolution of policy attention.

### Main script

- `scripts/result1/build_figure1_quantitative_package.py`

### Compact data

- `data/compact/result1/figure1_quantitative_analysis.xlsx`

### Notes

- `docs/result1/figure1_quantitative_interpretation.txt`

### Retained figure asset

- `figures/main_text/result1/macro_policy_framing_clean.png`

### Comment

The Figure 1 logic is preserved through the quantitative workbook and figure-building script. The final manuscript layout may combine elements from this package with editorial composition outside the repository.

## Figure 2

### Topic

SDG diffusion, concentration, and cross-goal comparison.

### Main scripts

- `scripts/result2/analyze_overton_sdg.py`
- `scripts/result2/add_sdg_companion_figures.py`
- `scripts/result2/rebuild_sdg_figures.py`

### Compact data

- `data/compact/result2/fig2_2_a_total_diffusion.csv`
- `data/compact/result2/fig2_2_a1_developed_diffusion.csv`
- `data/compact/result2/fig2_2_a2_developing_diffusion.csv`
- `data/compact/result2/fig2_2_a3_other_diffusion.csv`
- `data/compact/result2/fig2_2_b_doc_concentration.csv`
- `data/compact/result2/fig2_2_c_citation_concentration.csv`
- `data/compact/result2/fig2_2_d1_ageing_energy_index.csv`
- `data/compact/result2/fig2_2_d2_inequality_metrics.csv`
- `data/compact/result2/fig2_2_e1_country_classification.csv`
- `data/compact/result2/fig2_2_e2_scatter_data.csv`

### Retained figure assets

- `figures/main_text/result2/figure1_goal_overall_distribution.png`
- `figures/main_text/result2/figure2_goal_phase_stacked.png`
- `figures/main_text/result2/fig4_goal_count_vs_impact_final.png`
- `figures/main_text/result2/figure5_goal_inequality_phase3_vs_phase4.png`

### Comment

These files preserve the goal-level main-text figure logic and the panel-level data tables used in the SDG section.

## Figure 3

### Topic

Blind spots in ageing-related low-carbon policy.

### Main scripts

- `scripts/result3/01_merge_clean.py`
- `scripts/result3/02_text_preprocess.py`
- `scripts/result3/03_taxonomy_build.py`
- `scripts/result3/04_topic_trends.py`
- `scripts/result3/05_country_analysis.py`
- `scripts/result3/06_blind_spots.py`

### Compact data

- `data/compact/result3/keyword_taxonomy_mapping_clean.csv`
- `data/compact/result3/topicshare_by_window_clean.csv`
- `data/compact/result3/figure3_panel_data_clean/`

### Retained figure assets

- `figures/main_text/result3/scatter_oadr_vs_index.png`
- `figures/main_text/result3/scatter_index_vs_logimpact_bubble_count.png`
- `figures/main_text/result3/country_quadrant_scatter_actor_type_labeled.png`
- `figures/main_text/result3/map_global_index_phase4.png`

### Comment

The full clean Figure 3 panel package is retained under `data/compact/result3/figure3_panel_data_clean/`, including panel-level CSV files, Excel workbooks, panel images, and the map rebuild script for panel d.

## Shared methodological layer

The ageing–energy SDG relevance framework used across Results 2 and 3 is defined in:

- `scripts/methods/build_ageing_energy_index.py`
- `scripts/methods/build_ageing_energy_embedding_validation.py`
- `scripts/methods/build_ageing_energy_final_framework.py`
- `scripts/methods/build_ageing_energy_final_framework_v2.py`

Supporting notes:

- `docs/ageing_energy_index_methods.txt`
- `docs/ageing_energy_final_methods.txt`
- `docs/ageing_energy_sdg_validation_methods.txt`
