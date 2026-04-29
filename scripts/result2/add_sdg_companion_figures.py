from __future__ import annotations

import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parents[2]
OUTPUT_DIR = BASE_DIR / "outputs" / "result2"
os.environ.setdefault("MPLCONFIGDIR", str(OUTPUT_DIR / ".mplconfig"))

import matplotlib as mpl
import numpy as np
import pandas as pd
from matplotlib import pyplot as plt


WORKBOOK_PATH = OUTPUT_DIR / "overton_sdg_analysis.xlsx"
FIGURE_DIR = OUTPUT_DIR / "figures"
TOP10_DIR = FIGURE_DIR / "sdg_goal_top10_bars"

SDG_ORDER = list(range(1, 18))
YEARS = list(range(1972, 2025))
PHASES = ["Phase 3", "Phase 4"]
SMOOTHING_METHOD = "5-year centered rolling mean"
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
    TOP10_DIR.mkdir(parents=True, exist_ok=True)


def style_axis(ax: plt.Axes, transparent: bool = False) -> None:
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.grid(axis="x", color="#D7D7D7", linewidth=0.6, alpha=0.7)
    ax.set_axisbelow(True)
    if transparent:
        ax.set_facecolor((1, 1, 1, 0))


def rolling_smooth(df: pd.DataFrame, value_col: str) -> pd.DataFrame:
    out = df.sort_values(["SDG_goal", "Year"]).copy()
    out[f"{value_col}_smoothed"] = (
        out.groupby("SDG_goal")[value_col]
        .transform(lambda s: s.rolling(window=5, center=True, min_periods=1).mean())
    )
    return out


def load_tables() -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    country_phase = pd.read_excel(WORKBOOK_PATH, sheet_name="sdg_goal_country_phase_counts")
    country_count = pd.read_excel(WORKBOOK_PATH, sheet_name="sdg_goal_country_count_by_year")
    intensity = pd.read_excel(WORKBOOK_PATH, sheet_name="sdg_goal_diffusion_intensity_by_year")
    hhi_count = pd.read_excel(WORKBOOK_PATH, sheet_name="sdg_goal_hhi_count_by_year")
    hhi_impact = pd.read_excel(WORKBOOK_PATH, sheet_name="sdg_goal_hhi_impact_by_year")

    country_count = country_count[country_count["Year"].between(1972, 2024)].copy()
    intensity = intensity[intensity["Year"].between(1972, 2024)].copy()
    hhi_count = hhi_count[hhi_count["Year"].between(1972, 2024)].copy()
    hhi_impact = hhi_impact[hhi_impact["Year"].between(1972, 2024)].copy()

    for df in [country_phase, country_count, intensity, hhi_count, hhi_impact]:
        df["SDG_goal"] = df["SDG_goal"].astype(int)
    return country_phase, country_count, intensity, hhi_count, hhi_impact


def build_top10_table(country_phase: pd.DataFrame) -> pd.DataFrame:
    top10 = (
        country_phase.sort_values(["SDG_goal", "Phase", "Document_count", "Country"], ascending=[True, True, False, True])
        .groupby(["SDG_goal", "Phase"], group_keys=False)
        .head(10)
        .copy()
    )
    top10["Rank"] = top10.groupby(["SDG_goal", "Phase"])["Document_count"].rank(method="first", ascending=False).astype(int)
    return top10[["SDG_goal", "Phase", "Rank", "Country", "Document_count"]].rename(columns={"Document_count": "Count"})


def draw_top10_chart(goal: int, phase: str, top10: pd.DataFrame) -> Path:
    subset = top10[(top10["SDG_goal"] == goal) & (top10["Phase"] == phase)].sort_values("Count", ascending=True)
    fig, ax = plt.subplots(figsize=(8.5, 5.6))
    fig.patch.set_alpha(0)
    color = SDG_COLOR_MAP[goal]

    bars = ax.barh(
        subset["Country"],
        subset["Count"],
        color=color,
        edgecolor="none",
        height=0.65,
    )
    max_count = max(subset["Count"].max(), 1)
    for bar, value in zip(bars, subset["Count"]):
        if value > 0:
            ax.text(
                value + max_count * 0.02,
                bar.get_y() + bar.get_height() / 2,
                f"{int(value)}",
                va="center",
                ha="left",
                fontsize=9,
                color="#222222",
            )

    ax.set_title(f"SDG {goal} {phase}: Top 10 Countries", color=color, fontsize=15, weight="bold", pad=10)
    ax.set_xlabel("Document count")
    ax.set_ylabel("")
    ax.tick_params(axis="y", labelsize=10)
    style_axis(ax, transparent=True)
    ax.set_xlim(0, max_count * 1.18)
    fig.tight_layout()

    filename = f"sdg{goal}_{phase.lower().replace(' ', '')}_top10.png"
    out = TOP10_DIR / filename
    fig.savefig(out, dpi=300, bbox_inches="tight", transparent=True)
    plt.close(fig)
    return out


def multi_line_smoothed(df: pd.DataFrame, raw_col: str, smoothed_col: str, ylabel: str, title: str, filename: str) -> Path:
    fig, ax = plt.subplots(figsize=(16, 8))
    for goal in SDG_ORDER:
        subset = df[df["SDG_goal"] == goal].sort_values("Year")
        ax.plot(
            subset["Year"],
            subset[smoothed_col],
            color=SDG_COLOR_MAP[goal],
            linewidth=2,
            label=f"SDG {goal}",
        )
    ax.set_title(f"{title}\nSmoothed with {SMOOTHING_METHOD}", fontsize=16, weight="bold")
    ax.set_xlabel("Year")
    ax.set_ylabel(ylabel)
    ax.set_xlim(YEARS[0], YEARS[-1])
    tick_years = [year for year in YEARS if year % 4 == 0]
    ax.set_xticks(tick_years)
    ax.set_xticklabels(tick_years, rotation=45, ha="right")
    style_axis(ax)
    ax.legend(ncol=3, bbox_to_anchor=(1.02, 1), loc="upper left", frameon=False)
    fig.tight_layout()
    out = FIGURE_DIR / filename
    fig.savefig(out, dpi=300, bbox_inches="tight")
    plt.close(fig)
    return out


def phase_split_hhi_figure(df: pd.DataFrame, value_col: str, smoothed_col: str, title: str, filename: str) -> Path:
    fig, axes = plt.subplots(1, 2, figsize=(18, 7), sharey=True)
    panels = [("Phase 3", 1972, 1993), ("Phase 4", 1994, 2024)]
    for ax, (label, start, end) in zip(axes, panels):
        panel_df = df[df["Year"].between(start, end)]
        for goal in SDG_ORDER:
            subset = panel_df[panel_df["SDG_goal"] == goal].sort_values("Year")
            ax.plot(subset["Year"], subset[smoothed_col], color=SDG_COLOR_MAP[goal], linewidth=2)
        ax.set_title(label, fontsize=14, weight="bold")
        ax.set_xlabel("Year")
        ax.set_xlim(start, end)
        ticks = [year for year in range(start, end + 1) if year % 4 == 0 or year in {start, end}]
        ax.set_xticks(sorted(set(ticks)))
        ax.set_xticklabels(sorted(set(ticks)), rotation=45, ha="right")
        style_axis(ax)
    axes[0].set_ylabel("HHI")
    handles = [mpl.lines.Line2D([0], [0], color=SDG_COLOR_MAP[g], lw=2, label=f"SDG {g}") for g in SDG_ORDER]
    fig.legend(handles=handles, ncol=3, bbox_to_anchor=(0.5, 1.04), loc="upper center", frameon=False)
    fig.suptitle(f"{title}\nSmoothed with {SMOOTHING_METHOD}", fontsize=16, weight="bold", y=1.10)
    fig.tight_layout()
    out = FIGURE_DIR / filename
    fig.savefig(out, dpi=300, bbox_inches="tight")
    plt.close(fig)
    return out


def update_workbook(new_sheets: dict[str, pd.DataFrame]) -> None:
    with pd.ExcelWriter(WORKBOOK_PATH, engine="openpyxl", mode="a", if_sheet_exists="replace") as writer:
        for sheet_name, df in new_sheets.items():
            df.to_excel(writer, sheet_name=sheet_name, index=False)


def main() -> None:
    ensure_dirs()
    print("Loading existing SDG output tables...", flush=True)
    country_phase, country_count, intensity, hhi_count, hhi_impact = load_tables()

    print("Preparing top-10 country rankings...", flush=True)
    top10_table = build_top10_table(country_phase)

    ranking_paths: list[Path] = []
    for goal in SDG_ORDER:
        for phase in PHASES:
            ranking_paths.append(draw_top10_chart(goal, phase, top10_table))

    print("Preparing smoothed time-series figures...", flush=True)
    country_count_smoothed = rolling_smooth(country_count, "Country_count")
    intensity_smoothed = rolling_smooth(intensity, "Diffusion_intensity")
    hhi_count_smoothed = rolling_smooth(hhi_count, "HHI_count")
    hhi_impact_smoothed = rolling_smooth(hhi_impact, "HHI_impact")

    smoothed_figures = [
        multi_line_smoothed(
            country_count_smoothed,
            "Country_count",
            "Country_count_smoothed",
            "Number of countries",
            "SDG Diffusion Country Count",
            "fig_diffusion_country_count_smoothed.png",
        ),
        multi_line_smoothed(
            intensity_smoothed,
            "Diffusion_intensity",
            "Diffusion_intensity_smoothed",
            "Diffusion intensity",
            "SDG Diffusion Intensity",
            "fig_diffusion_intensity_smoothed.png",
        ),
        multi_line_smoothed(
            hhi_count_smoothed,
            "HHI_count",
            "HHI_count_smoothed",
            "HHI",
            "SDG Concentration by Document Count",
            "fig_hhi_count_smoothed.png",
        ),
        multi_line_smoothed(
            hhi_impact_smoothed,
            "HHI_impact",
            "HHI_impact_smoothed",
            "HHI",
            "SDG Concentration by Citation Impact",
            "fig_hhi_impact_smoothed.png",
        ),
        phase_split_hhi_figure(
            hhi_count_smoothed,
            "HHI_count",
            "HHI_count_smoothed",
            "SDG HHI by Document Count, Phase 3 and Phase 4",
            "fig_hhi_count_phase3_phase4_smoothed.png",
        ),
        phase_split_hhi_figure(
            hhi_impact_smoothed,
            "HHI_impact",
            "HHI_impact_smoothed",
            "SDG HHI by Citation Impact, Phase 3 and Phase 4",
            "fig_hhi_impact_phase3_phase4_smoothed.png",
        ),
    ]

    hhi_count_phase = hhi_count[hhi_count["Year"].between(1972, 2024)].copy()
    hhi_count_phase["Phase"] = np.where(hhi_count_phase["Year"] <= 1993, "Phase 3", "Phase 4")
    hhi_impact_phase = hhi_impact[hhi_impact["Year"].between(1972, 2024)].copy()
    hhi_impact_phase["Phase"] = np.where(hhi_impact_phase["Year"] <= 1993, "Phase 3", "Phase 4")

    print("Updating workbook with new companion tables...", flush=True)
    new_sheets = {
        "sdg_goal_phase_top10_countries": top10_table.sort_values(["SDG_goal", "Phase", "Rank"]),
        "sdg_goal_hhi_count_phase3_phase4": hhi_count_phase.sort_values(["SDG_goal", "Year"]),
        "sdg_goal_hhi_impact_phase3_phase4": hhi_impact_phase.sort_values(["SDG_goal", "Year"]),
    }
    update_workbook(new_sheets)

    print(f"Top-10 ranking charts created: {len(ranking_paths)}")
    print("New smoothed figures:")
    for path in smoothed_figures:
        print(path.name)
    print("New Excel sheets added:")
    for sheet in new_sheets:
        print(sheet)
    print(f"Smoothing method used: {SMOOTHING_METHOD}")


if __name__ == "__main__":
    main()
