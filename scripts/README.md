# Script guide

This folder is organized by analytical layer rather than by programming language.

## Main result scripts

### `result1/`

- `build_figure1_quantitative_package.py`
  - builds the quantitative package supporting Figure 1 and related structural-evolution outputs

### `result2/`

- `analyze_overton_sdg.py`
  - core SDG diffusion, concentration, and goal-level analysis
- `add_sdg_companion_figures.py`
  - additional figure generation around the SDG result set
- `rebuild_sdg_figures.py`
  - figure rebuilding utility for SDG visuals
- `extract_sdg_target_weight_matrix.py`
  - exports the structured SDG target-weight matrix
- `make_keyword_sankey.py`
  - keyword-evolution Sankey generation
- `make_keyword_sankey_top10.py`
  - top-keyword Sankey variant

### `result3/`

- `01_merge_clean.py`
  - merge and deduplicate the policy metadata exports
- `02_text_preprocess.py`
  - lowercasing, token cleaning, lemmatization, and keyword preprocessing
- `03_taxonomy_build.py`
  - taxonomy construction from clean keyword outputs
- `04_topic_trends.py`
  - topic-share and trend analysis
- `05_country_analysis.py`
  - country-level analysis and blind-spot supporting tables
- `06_blind_spots.py`
  - blind-spot index analysis
- `07_run_all.py`
  - convenience runner for the staged Result 3 pipeline
- `pipeline.py`
  - pipeline orchestration helper

## Shared method scripts

### `methods/`

- `build_ageing_energy_index.py`
- `build_ageing_energy_embedding_validation.py`
- `build_ageing_energy_final_framework.py`
- `build_ageing_energy_final_framework_v2.py`

These scripts define and validate the ageing–energy SDG relevance framework used downstream.

## Supplementary scripts

### `si/`

- `step8_policy_attention_elasticity.py`
- `step9_network_path_dependency.py`
- `step10_kl_divergence.py`
- `build_si_results123.py`
- `build_si_results123_word.py`
- `build_result3_si_word.py`

These scripts assemble the supplementary diagnostic layer and the SI document outputs.
