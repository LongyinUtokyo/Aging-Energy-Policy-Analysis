# GitHub Upload Manifest for Results 1–3 Package

This manifest records which notes, scripts, and SI support files were intentionally organized into the unified GitHub-ready package and which large working outputs were left outside the package.

## Included in the package

### Core analysis scripts

- `scripts/result1/`
  - Figure 1 / temporal segmentation package
- `scripts/result2/`
  - SDG analysis, figure rebuilding, and compact keyword/Sankey utilities
- `scripts/result3/`
  - staged workflow for metadata cleaning, preprocessing, taxonomy construction, topic trends, country analysis, and blind-spot analysis
- `scripts/methods/`
  - ageing-energy SDG weighting, validation, and final framework scripts
- `scripts/si/`
  - Step 8 policy attention elasticity
  - Step 9 network path dependency and semantic centrality
  - Step 10 KL divergence
  - SI markdown assembly
  - SI Word assembly

### Notes and SI documentation

- `docs/ageing_energy_final_methods.txt`
- `docs/ageing_energy_index_methods.txt`
- `docs/ageing_energy_sdg_validation_methods.txt`
- `docs/si/supplementary_information_results123.md`
- `docs/si/supplementary_manifest.md`
- `docs/si/summaries/`
  - Result 1 quantitative interpretation note
  - Result 2 SDG methods note
  - Result 3 Step 8 summary
  - Result 3 Step 9 summary
  - Result 3 Step 10 summary

### Compact SI tables

- `docs/si/tables/`
  - Table S1 to Table S13b as CSV

These tables were included because they are lightweight, readable on GitHub, and directly support the SI notes and scripts.

## Important portability note

The scripts in this package now use repository-relative path structure. However, several of them still expect auxiliary inputs that are not bundled by default. They are therefore:

- useful as reproducible research records
- appropriate for GitHub archival and transparency
- runnable after the expected input files are placed under `inputs/`

This package organization step did not rewrite their analytical logic or methods.

## Intentionally not copied into the package by default

### Large binary working outputs

- Word drafts from the live project
- Full figure directories from the live project
- Temporary Office lock files
- Intermediate working outputs outside the curated SI table set

### Raw inputs

- Original Overton CSV exports
- Auxiliary demographic input files

These should be added only if you decide the repository should include data or if a separate data-access statement is prepared.

## Recommended upload scope

For a clean public repository, the following structure is recommended:

1. keep all code in `scripts/`
2. keep methods notes and SI markdown in `docs/`
3. keep compact SI CSV tables in `docs/si/tables/`
4. keep raw inputs out of the repository unless licensing and size constraints are cleared
5. keep heavy result figures and Word drafts out of the default repository unless a dedicated release asset strategy is used

## Source of these organized files

These files were copied from the live project under:

- `analysis/SI/`
- `analysis/result3_si/`
- `results_1/`
- `results_2/`

No analysis was rerun during this packaging step. This was a structure-and-documentation cleanup only.
