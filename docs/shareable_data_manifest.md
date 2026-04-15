# Shareable processed data manifest

This file lists the processed datasets that are appropriate to share publicly in the GitHub repository.

These files are derived outputs, figure tables, compact summaries, or clean panel packages. They do not include the original Overton export files.

## Result 1

Location:

- `data/shareable/result1/figure1_quantitative_analysis.xlsx`

Purpose:

- quantitative structural summary used to support the Figure 1 main-text logic

## Result 2

Location:

- `data/shareable/result2/fig_sdg_target_weight_matrix.csv`
- `data/shareable/result2/fig_sdg_target_weight_long.csv`
- `data/shareable/result2/fig_sdg_target_weight_ranked.csv`
- `data/shareable/result2/fig2_2_a_total_diffusion.csv`
- `data/shareable/result2/fig2_2_a1_developed_diffusion.csv`
- `data/shareable/result2/fig2_2_a2_developing_diffusion.csv`
- `data/shareable/result2/fig2_2_a3_other_diffusion.csv`
- `data/shareable/result2/fig2_2_b_doc_concentration.csv`
- `data/shareable/result2/fig2_2_b1_developed_doc_concentration.csv`
- `data/shareable/result2/fig2_2_b2_developing_doc_concentration.csv`
- `data/shareable/result2/fig2_2_b3_other_doc_concentration.csv`
- `data/shareable/result2/fig2_2_c_citation_concentration.csv`
- `data/shareable/result2/fig2_2_c1_developed_citation_concentration.csv`
- `data/shareable/result2/fig2_2_c2_developing_citation_concentration.csv`
- `data/shareable/result2/fig2_2_c3_other_citation_concentration.csv`
- `data/shareable/result2/fig2_2_d1_ageing_energy_index.csv`
- `data/shareable/result2/fig2_2_d2_inequality_metrics.csv`
- `data/shareable/result2/fig2_2_e1_country_classification.csv`
- `data/shareable/result2/fig2_2_e2_scatter_data.csv`
- `data/shareable/result2/summary.txt`

Purpose:

- processed figure tables for Figure 2 / Figure 3 style SDG diffusion and concentration panels
- target-weight outputs used for the ageing–energy SDG relevance framework presentation

## Result 3

Location:

- `data/shareable/result3/keyword_taxonomy_mapping_clean.csv`
- `data/shareable/result3/topicshare_by_window_clean.csv`
- `data/shareable/result3/figure3_panel_data_clean/`

Purpose:

- clean keyword taxonomy
- topic-share time-window table
- full processed panel package for Figure 3, including:
  - panel-level CSV files
  - panel-level Excel workbooks
  - panel-level PNG assets
  - panel d map rebuild script and map source tables

## Explicitly excluded

The following are intentionally not included in this shareable data layer:

- original Overton export CSV files
- raw merged metadata exports that retain the full underlying document-level source distribution
- private manuscript drafts
- external reference PDFs

## Recommended public data scope

If you want a conservative public release, you can upload:

- everything under `data/shareable/`
- everything under `data/compact/`

and keep raw inputs outside the repository.
