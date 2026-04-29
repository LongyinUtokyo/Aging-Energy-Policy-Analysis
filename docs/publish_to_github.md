# Publish to GitHub

Repository URL:

`https://github.com/LongyinUtokyo/Aging-Energy-Policy-Analysis.git`

Current local package:

`/Users/longlab/Desktop/Aging Energy/github_results123_policy_package/`

## Simplest web upload

Open the GitHub repository page in the browser and use the upload box.

Upload these six files first:

| File to drag into GitHub |
|---|
| `README.md` |
| `docs/manifests/repository_manifest.md` |
| `docs/manifests/main_text_figure_manifest.md` |
| `docs/manifests/doc_sync_log.md` |
| `docs/si/supplementary_manifest.md` |
| `docs/publish_to_github.md` |

At the bottom of the GitHub upload page:

| Field | What to type |
|---|---|
| Commit message | `Doc sync` |
| Commit button | Click the green `Commit changes` button. |

## If GitHub says too many files

Upload in small batches.

| Batch | Suggested files |
|---|---|
| Batch 1 | The six documentation files listed above. |
| Batch 2 | `scripts/main_figures/` |
| Batch 3 | `scripts/result1/`, `scripts/result2/`, `scripts/result3/`, `scripts/methods/`, `scripts/si/` |
| Batch 4 | `data/compact/` and `data/shareable/` |
| Batch 5 | `figures/main_text/` |

Suggested commit messages:

| Batch | Commit message |
|---|---|
| Documentation | `Doc sync` |
| Code | `Update figure scripts` |
| Processed data | `Add processed figure data` |
| Figures | `Add manuscript figure assets` |

## What changed in this desktop sync

| Item | Current location |
|---|---|
| Updated Figure 1 code | `scripts/main_figures/figure1/` |
| Updated Figure 2 code | `scripts/main_figures/figure2/` |
| Updated Figure 3 code | `scripts/main_figures/figure3/` |
| Updated Figure 4 code | `scripts/main_figures/figure4/` |
| Updated manifest files | `docs/manifests/` |
| Updated SI manifest | `docs/si/supplementary_manifest.md` |

## Terminal option

If you use terminal later, run:

```bash
cd "/Users/longlab/Desktop/Aging Energy/github_results123_policy_package"
git add README.md docs/manifests/repository_manifest.md docs/manifests/main_text_figure_manifest.md docs/manifests/doc_sync_log.md docs/si/supplementary_manifest.md docs/publish_to_github.md
git commit -m "Doc sync"
git push
```
