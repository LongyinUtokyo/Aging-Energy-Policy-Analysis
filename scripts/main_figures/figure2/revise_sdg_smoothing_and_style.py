from __future__ import annotations

import os
from pathlib import Path

BASE_DIR = Path("/Users/longlab/Documents/New project")
OUTPUT_DIR = BASE_DIR / "outputs"
os.environ.setdefault("MPLCONFIGDIR", str(OUTPUT_DIR / ".mplconfig"))

import numpy as np
import pandas as pd
from matplotlib import pyplot as plt
from matplotlib import ticker as mticker
import matplotlib as mpl


WORKBOOK_PATH = OUTPUT_DIR / "overton_sdg_analysis.xlsx"
FIGURE_DIR = OUTPUT_DIR / "figures"

SDG_ORDER = list(range(1, 18))
YEARS = list(range(1972, 2025))
LOWESS_FRAC = 0.35
LIGHT_SMOOTH_FRAC = 0.18
SDG_COLOR_MAP = {
    1: "#E5243B",
    2: "#DDA63A",
    3: "#4C9F38",
    4: "#C5192D",
    5: "#FF3A21",
    6: "#26BDE2",
    7: "#FCC30B",
    8: "#A21942",
    9: "#FD6925",
    10: "#DD1367",
    11: "#FD9D24",
    12: "#BF8B2E",
    13: "#3F7E44",
    14: "#0A97D9",
    15: "#56C02B",
    16: "#00689D",
    17: "#19486A",
}


def ensure_dirs() -> None:
    FIGURE_DIR.mkdir(parents=True, exist_ok=True)


def lowess_numpy(x: np.ndarray, y: np.ndarray, frac: float) -> np.ndarray:
    x = np.asarray(x, dtype=float)
    y = np.asarray(y, dtype=float)
    mask = np.isfinite(x) & np.isfinite(y)
    x_valid = x[mask]
    y_valid = y[mask]
    result = np.full_like(y, np.nan, dtype=float)
    if len(x_valid) == 0:
        return result
    if len(x_valid) == 1:
        result[mask] = y_valid[0]
        return result

    span = max(3, int(np.ceil(frac * len(x_valid))))
    span = min(span, len(x_valid))

    smoothed = np.empty(len(x_valid), dtype=float)
    for i, x0 in enumerate(x_valid):
        distances = np.abs(x_valid - x0)
        bandwidth = np.partition(distances, span - 1)[span - 1]
        if bandwidth == 0:
            same_x = distances == 0
            smoothed[i] = float(np.mean(y_valid[same_x]))
            continue

        u = distances / bandwidth
        weights = np.where(u < 1, (1 - u**3) ** 3, 0.0)
        X = np.column_stack([np.ones(len(x_valid)), x_valid - x0])
        W = np.diag(weights)
        XtWX = X.T @ W @ X
        XtWy = X.T @ W @ y_valid
        try:
            beta = np.linalg.solve(XtWX, XtWy)
            smoothed[i] = beta[0]
        except np.linalg.LinAlgError:
            smoothed[i] = np.average(y_valid, weights=np.where(weights > 0, weights, 1))

    result[mask] = smoothed
    return result


def load_tables() -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame, pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    goal_dist = pd.read_excel(WORKBOOK_PATH, sheet_name="sdg_goal_overall_distribution")
    goal_impact = pd.read_excel(WORKBOOK_PATH, sheet_name="sdg_goal_impact")
    country_count = pd.read_excel(WORKBOOK_PATH, sheet_name="sdg_goal_country_count_by_year")
    intensity = pd.read_excel(WORKBOOK_PATH, sheet_name="sdg_goal_diffusion_intensity_by_year")
    hhi_count = pd.read_excel(WORKBOOK_PATH, sheet_name="sdg_goal_hhi_count_by_year")
    hhi_impact = pd.read_excel(WORKBOOK_PATH, sheet_name="sdg_goal_hhi_impact_by_year")

    for df in [goal_dist, goal_impact, country_count, intensity, hhi_count, hhi_impact]:
        df["SDG_goal"] = df["SDG_goal"].astype(int)

    country_count = country_count[country_count["Year"].between(1972, 2024)].copy()
    intensity = intensity[intensity["Year"].between(1972, 2024)].copy()
    hhi_count = hhi_count[hhi_count["Year"].between(1972, 2024)].copy()
    hhi_impact = hhi_impact[hhi_impact["Year"].between(1972, 2024)].copy()
    return goal_dist, goal_impact, country_count, intensity, hhi_count, hhi_impact


def smooth_table(df: pd.DataFrame, value_col: str, frac: float) -> pd.DataFrame:
    out = df.sort_values(["SDG_goal", "Year"]).copy()
    out[f"{value_col}_smooth"] = (
        out.groupby("SDG_goal", group_keys=False)
        .apply(lambda g: pd.Series(lowess_numpy(g["Year"].to_numpy(), g[value_col].to_numpy(), frac), index=g.index))
    )
    return out


def style_axis(ax: plt.Axes) -> None:
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.grid(axis="y", color="#D8D8D8", linewidth=0.6, alpha=0.7)
    ax.set_axisbelow(True)


def style_time_axis(ax: plt.Axes) -> None:
    style_axis(ax)
    ax.set_xlim(1972, 2024)
    tick_years = [year for year in YEARS if year % 4 == 0]
    ax.set_xticks(tick_years)
    ax.set_xticklabels(tick_years, rotation=45, ha="right")


def draw_strong_smoothed(df: pd.DataFrame, value_col: str, ylabel: str, title: str, filename: str, frac: float) -> Path:
    smoothed = smooth_table(df, value_col, frac)
    fig, ax = plt.subplots(figsize=(16, 8))
    for goal in SDG_ORDER:
        subset = smoothed[smoothed["SDG_goal"] == goal].sort_values("Year")
        ax.plot(
            subset["Year"],
            subset[f"{value_col}_smooth"],
            color=SDG_COLOR_MAP[goal],
            linewidth=2.4,
            label=f"SDG {goal}",
        )
    ax.set_title(f"{title}\nCustom LOWESS-style local linear smoothing (frac={frac:.2f})", fontsize=16, weight="bold")
    ax.set_xlabel("Year")
    ax.set_ylabel(ylabel)
    style_time_axis(ax)
    ax.legend(ncol=3, bbox_to_anchor=(1.02, 1), loc="upper left", frameon=False)
    fig.tight_layout()
    out = FIGURE_DIR / filename
    fig.savefig(out, dpi=300, bbox_inches="tight")
    plt.close(fig)
    return out


def draw_phase_hhi(df: pd.DataFrame, value_col: str, filename: str, title: str, frac: float) -> Path:
    smoothed = smooth_table(df, value_col, frac)
    fig, axes = plt.subplots(1, 2, figsize=(18, 7), sharey=True)
    for ax, (label, start, end) in zip(axes, [("Phase 3", 1972, 1993), ("Phase 4", 1994, 2024)]):
        panel = smoothed[smoothed["Year"].between(start, end)]
        for goal in SDG_ORDER:
            subset = panel[panel["SDG_goal"] == goal].sort_values("Year")
            ax.plot(subset["Year"], subset[f"{value_col}_smooth"], color=SDG_COLOR_MAP[goal], linewidth=2.4)
        ax.set_title(label, fontsize=14, weight="bold")
        ax.set_xlabel("Year")
        ax.set_xlim(start, end)
        ticks = [year for year in range(start, end + 1) if year % 4 == 0 or year in {start, end}]
        ax.set_xticks(sorted(set(ticks)))
        ax.set_xticklabels(sorted(set(ticks)), rotation=45, ha="right")
        style_axis(ax)
    axes[0].set_ylabel("HHI")
    handles = [mpl.lines.Line2D([0], [0], color=SDG_COLOR_MAP[g], lw=2.4, label=f"SDG {g}") for g in SDG_ORDER]
    fig.legend(handles=handles, ncol=3, bbox_to_anchor=(0.5, 1.04), loc="upper center", frameon=False)
    fig.suptitle(f"{title}\nCustom LOWESS-style local linear smoothing (frac={frac:.2f})", fontsize=16, weight="bold", y=1.10)
    fig.tight_layout()
    out = FIGURE_DIR / filename
    fig.savefig(out, dpi=300, bbox_inches="tight")
    plt.close(fig)
    return out


def draw_goal_distribution(goal_dist: pd.DataFrame) -> Path:
    plot_df = goal_dist.sort_values("SDG_goal").copy()
    fig, ax = plt.subplots(figsize=(15, 8))
    ax.bar(
        plot_df["SDG_goal_label"],
        plot_df["Document_count"],
        color=[SDG_COLOR_MAP[g] for g in plot_df["SDG_goal"]],
        edgecolor="none",
    )
    ax.set_title("Overall SDG Goal Distribution", fontsize=16, weight="bold")
    ax.set_xlabel("")
    ax.set_ylabel("Document-SDG goal links")
    ax.tick_params(axis="x", rotation=45, labelsize=10)
    style_axis(ax)
    fig.tight_layout()
    out = FIGURE_DIR / "fig1_goal_overall_distribution_fixed_palette.png"
    fig.savefig(out, dpi=300, bbox_inches="tight")
    plt.close(fig)
    return out


def draw_goal_count_vs_impact(goal_impact: pd.DataFrame) -> Path:
    plot_df = goal_impact.sort_values("SDG_goal").copy()
    fig, ax = plt.subplots(figsize=(12, 8))
    bubble_sizes = np.maximum(plot_df["Average_impact_per_document"] * 110, 350)
    for _, row in plot_df.iterrows():
        goal = int(row["SDG_goal"])
        ax.scatter(
            row["Document_count"],
            row["Total_impact"],
            s=bubble_sizes.loc[row.name],
            color=SDG_COLOR_MAP[goal],
            alpha=0.82,
            edgecolor="white",
            linewidth=1.0,
            zorder=3,
        )
        ax.text(
            row["Document_count"],
            row["Total_impact"],
            f"SDG {goal}",
            ha="center",
            va="center",
            fontsize=9,
            color="white" if goal not in {7, 11, 12} else "#222222",
            weight="bold",
            zorder=4,
        )
    ax.set_title("SDG Goal Document Count vs Impact", fontsize=16, weight="bold")
    ax.set_xlabel("Document count")
    ax.set_ylabel("Total policy citations")
    style_axis(ax)
    fig.tight_layout()
    out = FIGURE_DIR / "fig4_goal_count_vs_impact_fixed_palette.png"
    fig.savefig(out, dpi=300, bbox_inches="tight")
    plt.close(fig)
    return out


def main() -> None:
    ensure_dirs()
    print("Loading existing SDG tables...", flush=True)
    goal_dist, goal_impact, country_count, intensity, hhi_count, hhi_impact = load_tables()

    outputs = [
        draw_strong_smoothed(
            country_count,
            "Country_count",
            "Number of countries",
            "SDG Diffusion Country Count",
            "fig_diffusion_country_count_strong_smooth.png",
            LOWESS_FRAC,
        ),
        draw_strong_smoothed(
            intensity,
            "Diffusion_intensity",
            "Diffusion intensity",
            "SDG Diffusion Intensity",
            "fig_diffusion_intensity_strong_smooth.png",
            LOWESS_FRAC,
        ),
        draw_strong_smoothed(
            hhi_count,
            "HHI_count",
            "HHI",
            "SDG Concentration by Document Count",
            "fig_hhi_count_strong_smooth.png",
            LOWESS_FRAC,
        ),
        draw_strong_smoothed(
            hhi_impact,
            "HHI_impact",
            "HHI",
            "SDG Concentration by Citation Impact",
            "fig_hhi_impact_strong_smooth.png",
            LOWESS_FRAC,
        ),
        draw_phase_hhi(
            hhi_count,
            "HHI_count",
            "fig_hhi_count_phase3_phase4_strong_smooth.png",
            "SDG HHI by Document Count, Phase 3 and Phase 4",
            LOWESS_FRAC,
        ),
        draw_phase_hhi(
            hhi_impact,
            "HHI_impact",
            "fig_hhi_impact_phase3_phase4_strong_smooth.png",
            "SDG HHI by Citation Impact, Phase 3 and Phase 4",
            LOWESS_FRAC,
        ),
        draw_goal_distribution(goal_dist),
        draw_goal_count_vs_impact(goal_impact),
    ]

    print("Smoothing method used: custom LOWESS-style local linear smoothing")
    print(f"Smoothing parameter used: frac={LOWESS_FRAC:.2f}")
    print("Final SDG color mapping used:")
    for goal in SDG_ORDER:
        print(f"SDG {goal}: {SDG_COLOR_MAP[goal]}")
    print("Output file names:")
    for path in outputs:
        print(path.name)


if __name__ == "__main__":
    main()
