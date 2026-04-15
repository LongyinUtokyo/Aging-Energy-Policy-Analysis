# Global inequalities in ageing and energy policy influence across a century of transformation

This repository is the GitHub-ready code and compact-data package for the article-level workflow behind the main results and supplementary analyses.

It covers three linked result blocks:

- Result 1 / Figure 1: temporal segmentation and structural evolution
- Result 2 / Figures 2–3: SDG diffusion, concentration, alignment, and ageing–energy index analyses
- Result 3 / Figure 4: persistent blind spots in ageing-related low-carbon policy

The package is designed for transparent sharing of the analytical workflow, figure-generation logic, compact source tables, and manuscript support notes. It is not a fully containerized one-command reproduction bundle, because some large raw inputs and licensed source files are intentionally excluded.

## What to look at first

If you want the main paper figures and the code behind them, start here:

- `docs/manifests/main_text_figure_manifest.md`
- `scripts/README.md`
- `figures/main_text/`
- `data/compact/`

If you want the supplementary workflow, start here:

- `docs/si/supplementary_information_results123.md`
- `docs/si/supplementary_manifest.md`
- `scripts/si/`

## Repository structure

### `scripts/`

- `result1/`
  - Figure 1 and Result 1 analytical scripts
- `result2/`
  - SDG diffusion, concentration, alignment, and keyword-evolution scripts
- `result3/`
  - text-processing, taxonomy, topic-trend, country-analysis, and blind-spot scripts
- `methods/`
  - ageing–energy SDG weighting, validation, and final framework construction
- `si/`
  - supplementary diagnostics and SI assembly scripts

### `data/compact/`

- `result1/`
  - compact workbook outputs supporting Figure 1
- `result2/`
  - compact SDG/figure tables, including the Fig. 2.2 panel data and SDG target-weight tables
- `result3/`
  - compact topic-share inputs and the clean Figure 3 panel data package

### `data/shareable/`

- `result1/`
  - shareable processed data supporting the main Result 1 figure logic
- `result2/`
  - shareable processed figure tables for SDG diffusion, concentration, and target-weight outputs
- `result3/`
  - shareable processed topic, taxonomy, and clean Figure 3 panel data

### `figures/main_text/`

- `result1/`
  - main-text figure assets retained for Result 1
- `result2/`
  - main-text figure assets retained for Result 2
- `result3/`
  - main-text figure assets retained for Result 3

### `docs/`

- `result1/`, `result2/`, `result3/`
  - result-specific notes and interpretation files
- `manifests/`
  - repository assembly records and main-text figure mapping
- `si/`
  - supplementary information draft, manifest, tables, and summaries
- `publish_to_github.md`
  - practical upload instructions

### `inputs/`

- `raw/`
  - placeholder for original Overton exports
- `auxiliary/`
  - placeholder for demographic inputs and other external support files

### `outputs/`

- placeholder for regenerated outputs if the repository is rerun in a fresh clone

## Important reproducibility note

This repository is organized for code preservation and transparent sharing. Some scripts still depend on files that are not bundled by default, especially:

- original Overton exports
- auxiliary demographic files
- some large intermediate outputs used during live iteration

The scripts are now organized around repository-relative paths, but a fresh clone still requires the expected inputs to be placed under `inputs/`.

## What is included

- all organized scripts for Results 1–3
- shared method scripts
- compact data tables needed to understand the figure logic
- a separate shareable processed-data layer for public upload
- a clean Figure 3 panel-data package
- SI notes, tables, and assembly scripts
- selected main-text figure assets

## What is intentionally excluded

- heavy raw data files by default
- Word drafts
- temporary cache files
- large working directories that are not needed to understand the analysis pipeline

## Related documentation

- `docs/manifests/repository_manifest.md`
- `docs/manifests/main_text_figure_manifest.md`
- `docs/github_upload_manifest.md`
- `docs/shareable_data_manifest.md`
- `docs/data_availability_note.md`
- `docs/publish_to_github.md`
- `docs/si/supplementary_manifest.md`
