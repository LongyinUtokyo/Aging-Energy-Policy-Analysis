# Repository Manifest

This manifest describes how the unified `github_results123_policy_package` repository was assembled from the live project.

## Result 1

### Added

- `scripts/result1/build_figure1_quantitative_package.py`
- `docs/result1/figure1_quantitative_interpretation.txt`
- `data/compact/result1/figure1_quantitative_analysis.xlsx`
- `docs/result1/macro_policy_framing_clean.png`

### Purpose

These files preserve the Figure 1 quantitative package logic, the saved interpretation note, and one retained figure asset relevant to the structural framing discussion.

## Result 2

### Added

- `scripts/result2/*.py`
- `data/compact/result2/fig_sdg_target_weight_*.csv`
- `data/compact/result2/fig_sdg_target_weight_*.txt`
- `data/compact/result2/fig2_2_*.csv`
- `data/compact/result2/summary.txt`

### Purpose

These files preserve the SDG analysis scripts, target-weight extraction outputs, and Fig. 2.2 plotting tables in a lightweight form suitable for GitHub.

## Result 3

### Added

- `scripts/result3/*.py`
- `docs/result3/Result3_step8_pae_summary.md`
- `docs/result3/Result3_step9_network_summary.md`
- `docs/result3/Result3_step10_kl_summary.md`
- `data/compact/result3/keyword_taxonomy_mapping_clean.csv`
- `data/compact/result3/topicshare_by_window_clean.csv`

### Purpose

These files preserve the main third-part pipeline logic together with compact Result 3 inputs and SI-level summaries.

## Methods

### Retained

- `scripts/methods/*.py`
- `docs/ageing_energy_*.txt`

These files were already present in the earlier third-part GitHub package and were preserved as the common methodological layer.

## Supplementary information layer

### Retained and expanded

- `scripts/si/*.py`
- `docs/si/supplementary_information_results123.md`
- `docs/si/supplementary_manifest.md`
- `docs/si/summaries/*`
- `docs/si/tables/*.csv`

### Purpose

This layer preserves the structured SI draft, SI notes, compact SI tables, and the scripts used to assemble them from existing saved outputs.

## Not copied by default

- full working-directory figure trees
- Word drafts
- heavy binary output bundles
- raw Overton exports
- temporary cache files

These were left out to keep the repository lighter and cleaner for upload.
