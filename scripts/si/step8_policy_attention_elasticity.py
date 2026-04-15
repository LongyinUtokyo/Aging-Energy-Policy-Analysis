from __future__ import annotations

import math
import os
import tempfile
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
os.environ.setdefault("MPLCONFIGDIR", tempfile.mkdtemp(prefix="mplcfg_"))

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import statsmodels.api as sm


ROOT = Path(__file__).resolve().parents[2]
TOPICSHARE_CSV = ROOT / "data" / "compact" / "result3" / "topicshare_by_window_clean.csv"
OADR_CSV = ROOT / "inputs" / "auxiliary" / "unpopulation_人口元数据.csv"
OUT_DIR = ROOT / "outputs" / "si" / "step8_pae"

WINDOW_ORDER = [
    "1972_1976",
    "1977_1981",
    "1982_1986",
    "1987_1991",
    "1992_1996",
    "1997_2001",
    "2002_2006",
    "2007_2011",
    "2012_2016",
    "2017_2020",
    "2021_2024",
]

HIGHLIGHT_CATEGORIES = {
    "housing and thermal comfort",
    "household behaviour and adoption",
    "affordability and income constraints",
    "energy transition and efficiency",
}

CATEGORY_COLORS = {
    "welfare and care": "#8fb7aa",
    "health and vulnerability": "#3a7d89",
    "housing and thermal comfort": "#d8a15d",
    "energy transition and efficiency": "#4f6d7a",
    "household behaviour and adoption": "#b07aa1",
    "affordability and income constraints": "#c35b5b",
}


def window_midyear(label: str) -> int:
    start, end = [int(x) for x in label.split("_")]
    return int((start + end) / 2)


def load_oadr_window_means() -> pd.DataFrame:
    oadr = pd.read_csv(OADR_CSV, usecols=["Location", "Iso3", "Time", "Value", "IndicatorShortName", "Sex"])
    oadr = oadr[
        (oadr["IndicatorShortName"] == "Old-age dependency ratio")
        & (oadr["Sex"] == "Both sexes")
        & oadr["Iso3"].notna()
        & (oadr["Iso3"].astype(str).str.len() == 3)
    ].copy()
    oadr["Time"] = pd.to_numeric(oadr["Time"], errors="coerce")
    oadr["Value"] = pd.to_numeric(oadr["Value"], errors="coerce")
    yearly = oadr.groupby("Time", as_index=False)["Value"].mean().rename(columns={"Time": "year", "Value": "mean_oadr"})

    rows = []
    for label in WINDOW_ORDER:
        start, end = [int(x) for x in label.split("_")]
        subset = yearly[yearly["year"].between(start, end)].copy()
        rows.append(
            {
                "time_window": label,
                "window_mean_oadr": float(subset["mean_oadr"].mean()),
                "window_start": start,
                "window_end": end,
                "window_midyear": window_midyear(label),
            }
        )
    return pd.DataFrame(rows)


def fit_loglog(df: pd.DataFrame) -> dict[str, float]:
    clean = df.dropna(subset=["window_mean_oadr", "share"]).copy()
    clean = clean[(clean["window_mean_oadr"] > 0) & (clean["share"] > 0)].copy()
    x = np.log(clean["window_mean_oadr"].astype(float).to_numpy())
    y = np.log(clean["share"].astype(float).to_numpy())
    X = sm.add_constant(x)
    result = sm.OLS(y, X).fit(cov_type="HC1")
    ci = result.conf_int()
    ci_low, ci_high = ci[1] if isinstance(ci, np.ndarray) else ci.iloc[1].tolist()
    params = np.asarray(result.params)
    bse = np.asarray(result.bse)
    pvals = np.asarray(result.pvalues)
    return {
        "epsilon_k": float(params[1]),
        "standard_error": float(bse[1]),
        "p_value": float(pvals[1]),
        "ci_low_95": float(ci_low),
        "ci_high_95": float(ci_high),
        "r_squared": float(result.rsquared),
        "n_obs": int(result.nobs),
    }


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)

    topicshare = pd.read_csv(TOPICSHARE_CSV)
    topicshare = topicshare[topicshare["time_window"].isin(WINDOW_ORDER)].copy()
    oadr_windows = load_oadr_window_means()
    model_df = topicshare.merge(oadr_windows, on="time_window", how="left")
    model_df["additional_controls"] = "no additional controls used"

    results = []
    for category, subset in model_df.groupby("category", sort=False):
        subset = subset.sort_values("window_midyear").copy()
        stats = fit_loglog(subset)
        stats["category"] = category
        stats["highlight_mechanism"] = category in HIGHLIGHT_CATEGORIES
        usable = subset.dropna(subset=["window_mean_oadr"]).copy()
        stats["window_count"] = usable["time_window"].nunique()
        stats["oadr_min"] = float(usable["window_mean_oadr"].min())
        stats["oadr_max"] = float(usable["window_mean_oadr"].max())
        results.append(stats)

    results_df = pd.DataFrame(results)
    ranked_df = results_df.sort_values("epsilon_k", ascending=False).reset_index(drop=True)
    results_df.to_csv(OUT_DIR / "step8_pae_results.csv", index=False)
    ranked_df.to_csv(OUT_DIR / "step8_pae_ranked.csv", index=False)

    plot_df = ranked_df.copy()
    plot_df = plot_df.sort_values("epsilon_k", ascending=True)

    plt.rcParams.update(
        {
            "font.family": "Arial",
            "font.size": 12,
            "axes.labelsize": 13,
            "xtick.labelsize": 11,
            "ytick.labelsize": 11,
            "figure.facecolor": "white",
            "axes.facecolor": "white",
            "savefig.facecolor": "white",
        }
    )
    fig, ax = plt.subplots(figsize=(9, 4.8))
    y = np.arange(len(plot_df))
    for i, row in enumerate(plot_df.itertuples(index=False)):
        color = CATEGORY_COLORS[row.category]
        alpha = 1.0 if row.highlight_mechanism else 0.8
        ax.hlines(i, row.ci_low_95, row.ci_high_95, color=color, lw=2.3, alpha=alpha)
        ax.scatter(
            row.epsilon_k,
            i,
            s=95 if row.highlight_mechanism else 65,
            color=color,
            edgecolor="#222222" if row.highlight_mechanism else "white",
            linewidth=0.9,
            zorder=3,
            alpha=alpha,
        )
    ax.axvline(0, color="#666666", lw=1.0, linestyle="--")
    ax.set_yticks(y)
    ax.set_yticklabels(plot_df["category"])
    ax.set_xlabel("Policy attention elasticity (epsilon)")
    ax.set_ylabel("")
    ax.grid(False)
    for spine in ["top", "right"]:
        ax.spines[spine].set_visible(False)
    fig.tight_layout()
    fig.savefig(OUT_DIR / "step8_pae_plot.png", dpi=320, bbox_inches="tight")
    plt.close(fig)

    focused = ranked_df[ranked_df["category"].isin(HIGHLIGHT_CATEGORIES)].copy()
    lines = [
        "# Step 8 Policy Attention Elasticity",
        "",
        "Model form: ln(TopicShare_k,t) = alpha_k + epsilon_k ln(OADR_t) + eta_t.",
        "Data basis: Step 7 topic-share windows merged with window-mean OADR.",
        "Controls: no additional controls used.",
        "Fixed effects: not used in the final estimates because the available structure is window-level and the usable OADR overlap begins only in 1990.",
        "Coverage note: windows without observed OADR values were dropped from estimation rather than imputed.",
        "",
        "## Ranked elasticity estimates",
    ]
    for row in ranked_df.itertuples(index=False):
        lines.append(
            f"- {row.category}: epsilon={row.epsilon_k:.4f}, SE={row.standard_error:.4f}, "
            f"p={row.p_value:.4g}, 95% CI [{row.ci_low_95:.4f}, {row.ci_high_95:.4f}]"
        )
    lines.extend(
        [
            "",
            "## Mechanism-focused comparison",
        ]
    )
    for row in focused.itertuples(index=False):
        lines.append(
            f"- {row.category}: epsilon={row.epsilon_k:.4f}, ranked {int(ranked_df.index[ranked_df['category'] == row.category][0]) + 1} of {len(ranked_df)}."
        )
    (OUT_DIR / "step8_pae_summary.md").write_text("\n".join(lines), encoding="utf-8")


if __name__ == "__main__":
    main()
