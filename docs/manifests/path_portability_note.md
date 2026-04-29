# Path Portability Note

This repository package was assembled from a live working directory. As a result, some scripts remain **provenance scripts** rather than fully portable public scripts.

## Scripts that may still require path refactoring

### Supplementary-information scripts

- `scripts/si/build_si_results123.py`
- `scripts/si/build_si_results123_word.py`
- `scripts/si/build_result3_si_word.py`
- `scripts/si/step8_policy_attention_elasticity.py`
- `scripts/si/step9_network_path_dependency.py`
- `scripts/si/step10_kl_divergence.py`

### Possible additional live-project dependencies

- parts of `scripts/result2/`
- parts of `scripts/methods/`

## Why these were kept

They were preserved because they document the actual analytical workflow used in the project and are useful for:

- transparency
- reproducibility auditing
- future cleanup into a public rerunnable version

## What to do before public rerun claims

Before claiming one-command reproducibility from a fresh clone, review these scripts and replace:

- absolute local root paths
- machine-specific Desktop paths
- references to files that are not included in the repository

This packaging step intentionally did **not** alter the analytical logic of those scripts.
