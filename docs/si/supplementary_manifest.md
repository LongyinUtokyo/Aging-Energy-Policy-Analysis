# Supplementary manifest

This manifest records the supplementary files retained in the GitHub package for Results 1-3. The SI files are organized as processed documentation and table outputs, not as raw policy exports.

## SI document files

| File | Purpose |
|---|---|
| `docs/si/supplementary_information_results123.md` | Main SI draft for Results 1-3. |
| `docs/si/supplementary_manifest.md` | This SI inventory file. |
| `docs/si/README.md` | Short guide to the SI folder. |

## SI summaries

| File | Result block |
|---|---|
| `docs/si/summaries/Result1_figure1_quantitative_interpretation.txt` | Result 1 / Figure 1 phase interpretation. |
| `docs/si/summaries/Result2_overton_sdg_methods_note.txt` | Result 2 SDG parsing and metric notes. |
| `docs/si/summaries/Result3_step8_pae_summary.md` | Result 3 Step 8 policy attention elasticity. |
| `docs/si/summaries/Result3_step9_network_summary.md` | Result 3 Step 9 network path dependency and semantic centrality. |
| `docs/si/summaries/Result3_step10_kl_summary.md` | Result 3 Step 10 KL divergence and mechanism mismatch. |

## SI tables

| Table file | Content |
|---|---|
| `docs/si/tables/Table_S1_phase_breakpoints.csv` | Result 1 phase breakpoints. |
| `docs/si/tables/Table_S2_quantitative_characteristics_of_phases.csv` | Result 1 phase counts and growth characteristics. |
| `docs/si/tables/Table_S3_SDG_diffusion_statistics.csv` | Result 2 SDG diffusion statistics. |
| `docs/si/tables/Table_S4_concentration_and_inequality_metrics.csv` | Result 2 concentration and inequality metrics. |
| `docs/si/tables/Table_S5_ageing_energy_target_weights.csv` | Ageing-energy SDG target weights. |
| `docs/si/tables/Table_S6_pooled_regression_results.csv` | Pooled regression outputs. |
| `docs/si/tables/Table_S7_fixed_effects_regression_results.csv` | Fixed-effects regression outputs. |
| `docs/si/tables/Table_S8_policy_influence_and_efficiency_regressions.csv` | Policy influence and efficiency regressions. |
| `docs/si/tables/Table_S9_keyword_taxonomy.csv` | Result 3 clean keyword taxonomy. |
| `docs/si/tables/Table_S10_topic_share_by_period.csv` | Result 3 topic share by period. |
| `docs/si/tables/Table_S11_policy_attention_elasticity.csv` | Step 8 elasticity estimates. |
| `docs/si/tables/Table_S12_centrality_comparison_of_key_terms.csv` | Step 9 centrality comparison. |
| `docs/si/tables/Table_S13a_KL_divergence_by_window.csv` | Step 10 KL divergence by window. |
| `docs/si/tables/Table_S13b_KL_divergence_by_phase.csv` | Step 10 KL divergence by phase. |

## SI analysis scripts

| Script | Purpose |
|---|---|
| `scripts/si/step8_policy_attention_elasticity.py` | Estimates policy attention elasticity. |
| `scripts/si/step9_network_path_dependency.py` | Computes phase-wise keyword network centrality. |
| `scripts/si/step10_kl_divergence.py` | Computes KL divergence for mechanism mismatch. |
| `scripts/si/build_si_results123.py` | Builds the Results 1-3 SI markdown structure. |
| `scripts/si/build_si_results123_word.py` | Builds the SI Word document. |
| `scripts/si/build_result3_si_word.py` | Builds the Result 3 SI Word document. |

## Current relationship to main figures

| SI block | Main figure connection |
|---|---|
| Supplementary Note 1 | Supports Figure 1 with phase and segmentation details. |
| Supplementary Note 2 | Supports Figure 2 and Figure 3 with SDG diffusion, concentration, index construction, and regression tables. |
| Supplementary Note 3 | Supports Figure 4 with taxonomy, topic shares, elasticity, network centrality, and KL divergence diagnostics. |

## Sync note

This SI manifest was refreshed for the desktop GitHub package on 2026-04-29. It uses repository-relative paths so the file remains readable after upload to GitHub.
