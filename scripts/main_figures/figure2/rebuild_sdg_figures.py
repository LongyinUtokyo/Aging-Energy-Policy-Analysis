from __future__ import annotations

import json
import os
import re
from pathlib import Path

BASE_DIR = Path("/Users/longlab/Documents/New project")
OUTPUT_DIR = BASE_DIR / "outputs"
os.environ.setdefault("MPLCONFIGDIR", str(OUTPUT_DIR / ".mplconfig"))

import matplotlib as mpl
import numpy as np
import pandas as pd
import pycountry
from matplotlib import colors as mcolors
from matplotlib import pyplot as plt
from matplotlib.patches import Polygon
from matplotlib.collections import PatchCollection


FIGURE_DIR = OUTPUT_DIR / "figures"
MAP_DIR = FIGURE_DIR / "maps"
WORKBOOK_PATH = OUTPUT_DIR / "overton_sdg_analysis.xlsx"
CSV_PATH = OUTPUT_DIR / "overton_sdg_cleaned_merged.csv"
WORLD_GEOJSON_PATH = OUTPUT_DIR / "world_countries.geojson"

PHASES = ["Phase 3", "Phase 4"]
YEARS = list(range(1972, 2025))
SDG_ORDER = list(range(1, 18))
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
NON_COUNTRY_ENTITIES = {"EU", "IGO"}
GOAL_TOKEN_PATTERN = re.compile(r"^SDG\s+(\d{1,2})(?:\s*:.*)?$")
TARGET_TOKEN_PATTERN = re.compile(r"^SDG\s+Target\s+(\d{1,2}(?:\.[0-9a-z]+)?)$", re.IGNORECASE)
COUNTRY_ALIASES = {
    "UK": "GBR",
    "USA": "USA",
    "South Korea": "KOR",
    "North Korea": "PRK",
    "Russia": "RUS",
    "Turkey": "TUR",
    "Laos": "LAO",
    "Vietnam": "VNM",
    "Iran": "IRN",
    "Venezuela": "VEN",
    "Tanzania": "TZA",
    "Bolivia": "BOL",
    "Moldova": "MDA",
    "Syria": "SYR",
    "Palestine": "PSE",
    "Taiwan": "TWN",
    "Czech Republic": "CZE",
    "Cape Verde": None,
    "Timor Leste": "TLS",
    "Kosovo": "CS-KM",
    "Micronesia": "FSM",
    "Eswatini": "SWZ",
}


def ensure_dirs() -> None:
    FIGURE_DIR.mkdir(parents=True, exist_ok=True)
    MAP_DIR.mkdir(parents=True, exist_ok=True)


def load_goal_data() -> pd.DataFrame:
    cleaned = pd.read_csv(
        CSV_PATH,
        usecols=["Overton id", "Year", "Phase", "Country", "Impact", "Related to SDGs"],
    )
    cleaned = cleaned[["Overton id", "Year", "Phase", "Country", "Impact", "Related to SDGs"]]
    cleaned = cleaned[cleaned["Phase"].isin(PHASES)].copy()
    cleaned = cleaned[cleaned["Year"].between(1972, 2024)].copy()
    cleaned["Year"] = cleaned["Year"].astype(int)

    rows: list[dict[str, object]] = []
    for row in cleaned.itertuples(index=False):
        seen_goals: set[int] = set()
        raw_value = "" if pd.isna(row[5]) else str(row[5])
        for token in raw_value.split("|"):
            token = token.strip()
            if not token:
                continue
            goal_match = GOAL_TOKEN_PATTERN.match(token)
            if goal_match:
                seen_goals.add(int(goal_match.group(1)))
                continue
            target_match = TARGET_TOKEN_PATTERN.match(token)
            if target_match:
                seen_goals.add(int(target_match.group(1).split(".")[0]))
        for goal in sorted(seen_goals):
            rows.append(
                {
                    "Overton id": row[0],
                    "Year": row[1],
                    "Phase": row[2],
                    "Country": row[3],
                    "Impact": float(row[4]),
                    "SDG_goal": goal,
                    "SDG_goal_label": goal_label(goal),
                }
            )
    return pd.DataFrame(rows)


def goal_label(goal: int) -> str:
    return f"SDG {goal}"


def build_year_tables(df: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    counts = (
        df.groupby(["Year", "SDG_goal"], as_index=False)
        .size()
        .rename(columns={"size": "Document_count"})
    )
    base = pd.MultiIndex.from_product([YEARS, SDG_ORDER], names=["Year", "SDG_goal"]).to_frame(index=False)
    counts = base.merge(counts, on=["Year", "SDG_goal"], how="left").fillna({"Document_count": 0})
    counts["Document_count"] = counts["Document_count"].astype(int)
    counts["SDG_goal_label"] = counts["SDG_goal"].map(goal_label)

    year_totals = counts.groupby("Year")["Document_count"].transform("sum")
    counts["Share"] = np.where(year_totals > 0, counts["Document_count"] / year_totals, 0.0)
    counts["Share_pct"] = (counts["Share"] * 100).round(2)

    share = counts[["Year", "SDG_goal", "SDG_goal_label", "Document_count", "Share", "Share_pct"]].copy()
    count = counts[["Year", "SDG_goal", "SDG_goal_label", "Document_count"]].copy()
    return count, share


def country_to_geo_id(country: str, available_ids: set[str], available_names: dict[str, str]) -> str | None:
    if country in NON_COUNTRY_ENTITIES:
        return None
    if country in COUNTRY_ALIASES:
        alias = COUNTRY_ALIASES[country]
        return alias if alias in available_ids else None

    try:
        result = pycountry.countries.search_fuzzy(country)[0]
        if result.alpha_3 in available_ids:
            return result.alpha_3
    except Exception:
        pass

    lowered = country.lower()
    if lowered in available_names:
        return available_names[lowered]
    return None


def build_country_tables(df: pd.DataFrame, world_data: dict) -> tuple[pd.DataFrame, pd.DataFrame]:
    available_ids = {feature["id"] for feature in world_data["features"]}
    available_names = {feature["properties"]["name"].lower(): feature["id"] for feature in world_data["features"]}

    country_df = df[~df["Country"].isin(NON_COUNTRY_ENTITIES)].copy()
    country_lookup = {
        country: country_to_geo_id(country, available_ids, available_names)
        for country in sorted(country_df["Country"].dropna().unique())
    }
    country_df["geo_id"] = country_df["Country"].map(country_lookup)
    country_df["is_mappable_country"] = country_df["geo_id"].notna()

    country_phase = (
        country_df[country_df["is_mappable_country"]]
        .groupby(["Phase", "SDG_goal", "Country", "geo_id"], as_index=False)
        .size()
        .rename(columns={"size": "Document_count"})
    )
    country_phase["SDG_goal_label"] = country_phase["SDG_goal"].map(goal_label)

    return country_df, country_phase


def build_diffusion_tables(country_df: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    active = country_df[country_df["is_mappable_country"]].copy()

    country_count = (
        active.groupby(["Year", "SDG_goal"], as_index=False)["geo_id"]
        .nunique()
        .rename(columns={"geo_id": "Country_count"})
    )
    base = pd.MultiIndex.from_product([YEARS, SDG_ORDER], names=["Year", "SDG_goal"]).to_frame(index=False)
    country_count = base.merge(country_count, on=["Year", "SDG_goal"], how="left").fillna({"Country_count": 0})
    country_count["Country_count"] = country_count["Country_count"].astype(int)
    country_count["SDG_goal_label"] = country_count["SDG_goal"].map(goal_label)

    total_active = (
        active.groupby("Year", as_index=False)["geo_id"]
        .nunique()
        .rename(columns={"geo_id": "Total_active_countries"})
    )
    intensity = country_count.merge(total_active, on="Year", how="left")
    intensity["Diffusion_intensity"] = np.where(
        intensity["Total_active_countries"] > 0,
        intensity["Country_count"] / intensity["Total_active_countries"],
        0.0,
    )

    country_goal_year = (
        active.groupby(["Year", "SDG_goal", "geo_id"], as_index=False)
        .agg(Document_count=("geo_id", "size"), Impact=("Impact", "sum"))
    )

    def hhi(series: pd.Series) -> float:
        total = series.sum()
        if total <= 0:
            return np.nan
        shares = series / total
        return float((shares ** 2).sum())

    hhi_count = (
        country_goal_year.groupby(["Year", "SDG_goal"], as_index=False)
        .agg(HHI_count=("Document_count", hhi))
    )
    hhi_impact = (
        country_goal_year.groupby(["Year", "SDG_goal"], as_index=False)
        .agg(HHI_impact=("Impact", hhi))
    )

    hhi_count = base.merge(hhi_count, on=["Year", "SDG_goal"], how="left")
    hhi_count["SDG_goal_label"] = hhi_count["SDG_goal"].map(goal_label)
    hhi_impact = base.merge(hhi_impact, on=["Year", "SDG_goal"], how="left")
    hhi_impact["SDG_goal_label"] = hhi_impact["SDG_goal"].map(goal_label)

    return country_count, intensity, (hhi_count, hhi_impact)


def style_axes(ax: plt.Axes, years: list[int]) -> None:
    ax.set_xlim(years[0] - 0.5, years[-1] + 0.5)
    tick_years = [year for year in years if year % 4 == 0]
    ax.set_xticks(tick_years)
    ax.set_xticklabels(tick_years, rotation=45, ha="right")
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)


def stacked_bar_figures(year_count: pd.DataFrame, year_share: pd.DataFrame) -> list[Path]:
    created: list[Path] = []
    mpl.rcParams.update({"font.size": 11, "axes.titleweight": "bold", "axes.labelweight": "bold"})

    count_pivot = (
        year_count.pivot(index="Year", columns="SDG_goal", values="Document_count")
        .reindex(index=YEARS, columns=SDG_ORDER, fill_value=0)
    )
    share_pivot = (
        year_share.pivot(index="Year", columns="SDG_goal", values="Share")
        .reindex(index=YEARS, columns=SDG_ORDER, fill_value=0)
    )

    for pivot, ylabel, title, filename, value_format in [
        (count_pivot, "Document count", "SDG Goal Composition by Year (Counts)", "fig1_sdg_stacked_count.png", None),
        (share_pivot, "Share of yearly SDG links", "SDG Goal Composition by Year (Shares)", "fig2_sdg_stacked_share.png", "percent"),
    ]:
        fig, ax = plt.subplots(figsize=(18, 8))
        bottom = np.zeros(len(pivot))
        x = pivot.index.to_numpy()
        for goal in SDG_ORDER:
            values = pivot[goal].to_numpy()
            ax.bar(
                x,
                values,
                bottom=bottom,
                color=SDG_COLOR_MAP[goal],
                width=0.85,
                edgecolor="white",
                linewidth=0.2,
                label=f"SDG {goal}",
            )
            bottom = bottom + values
        ax.set_title(title)
        ax.set_xlabel("Year")
        ax.set_ylabel(ylabel)
        if value_format == "percent":
            ax.set_ylim(0, 1)
            ax.yaxis.set_major_formatter(mpl.ticker.PercentFormatter(1.0))
        style_axes(ax, YEARS)
        ax.legend(ncol=3, bbox_to_anchor=(1.02, 1), loc="upper left", frameon=False)
        fig.tight_layout()
        out = FIGURE_DIR / filename
        fig.savefig(out, dpi=300, bbox_inches="tight")
        plt.close(fig)
        created.append(out)
    return created


def multi_line_figure(df: pd.DataFrame, value_col: str, ylabel: str, title: str, filename: str) -> Path:
    fig, ax = plt.subplots(figsize=(18, 8))
    for goal in SDG_ORDER:
        sub = df[df["SDG_goal"] == goal].sort_values("Year")
        ax.plot(
            sub["Year"],
            sub[value_col],
            color=SDG_COLOR_MAP[goal],
            linewidth=2.0,
            label=f"SDG {goal}",
        )
    ax.set_title(title)
    ax.set_xlabel("Year")
    ax.set_ylabel(ylabel)
    style_axes(ax, YEARS)
    ax.legend(ncol=3, bbox_to_anchor=(1.02, 1), loc="upper left", frameon=False)
    fig.tight_layout()
    out = FIGURE_DIR / filename
    fig.savefig(out, dpi=300, bbox_inches="tight")
    plt.close(fig)
    return out


def lighten(color: str, amount: float = 0.85) -> tuple[float, float, float]:
    rgb = np.array(mcolors.to_rgb(color))
    return tuple(1 - (1 - rgb) * (1 - amount))


def extract_patches(geometry: dict) -> list[np.ndarray]:
    patches: list[np.ndarray] = []
    if geometry["type"] == "Polygon":
        for ring in geometry["coordinates"][:1]:
            patches.append(np.asarray(ring))
    elif geometry["type"] == "MultiPolygon":
        for polygon in geometry["coordinates"]:
            for ring in polygon[:1]:
                patches.append(np.asarray(ring))
    return patches


def map_figure(goal: int, phase: str, phase_counts: pd.DataFrame, world_data: dict) -> Path:
    phase_label = phase.lower().replace(" ", "")
    out = MAP_DIR / f"sdg{goal}_{phase_label}.png"
    sdg_phase = phase_counts[(phase_counts["SDG_goal"] == goal) & (phase_counts["Phase"] == phase)]
    both_phases = phase_counts[phase_counts["SDG_goal"] == goal]
    value_map = dict(zip(sdg_phase["geo_id"], sdg_phase["Document_count"]))
    vmax = max(float(both_phases["Document_count"].max()), 1.0) if not both_phases.empty else 1.0

    cmap = mcolors.LinearSegmentedColormap.from_list(
        f"sdg{goal}_map",
        [lighten(SDG_COLOR_MAP[goal], 0.96), SDG_COLOR_MAP[goal]],
    )
    norm = mpl.colors.Normalize(vmin=0, vmax=vmax)

    fig, ax = plt.subplots(figsize=(13, 7.5))
    patches = []
    patch_colors = []
    for feature in world_data["features"]:
        feature_id = feature["id"]
        if feature_id == "ATA":
            continue
        value = value_map.get(feature_id, 0)
        fill = cmap(norm(value)) if value > 0 else (0.94, 0.94, 0.94, 1.0)
        for patch_coords in extract_patches(feature["geometry"]):
            patches.append(Polygon(patch_coords[:, :2], closed=True))
            patch_colors.append(fill)

    collection = PatchCollection(
        patches,
        facecolor=patch_colors,
        edgecolor="#9A9A9A",
        linewidth=0.35,
        match_original=False,
    )
    ax.add_collection(collection)
    ax.set_xlim(-180, 180)
    ax.set_ylim(-60, 90)
    ax.set_aspect("equal")
    ax.axis("off")
    ax.set_title(f"SDG {goal} {phase}: Country Document Counts", color=SDG_COLOR_MAP[goal], pad=14, fontsize=18, weight="bold")

    sm = mpl.cm.ScalarMappable(norm=norm, cmap=cmap)
    sm.set_array([])
    cbar = fig.colorbar(sm, ax=ax, fraction=0.025, pad=0.02)
    cbar.set_label("Document count")
    cbar.outline.set_visible(False)

    fig.tight_layout()
    fig.savefig(out, dpi=300, bbox_inches="tight", facecolor="white")
    plt.close(fig)
    return out


def update_workbook(sheets: dict[str, pd.DataFrame]) -> None:
    with pd.ExcelWriter(WORKBOOK_PATH, engine="openpyxl", mode="a", if_sheet_exists="replace") as writer:
        for sheet_name, df in sheets.items():
            df.to_excel(writer, sheet_name=sheet_name, index=False)


def main() -> None:
    ensure_dirs()
    print("Loading Phase 3/Phase 4 SDG goal data...", flush=True)
    goal_df = load_goal_data()
    with open(WORLD_GEOJSON_PATH, encoding="utf-8") as f:
        world_data = json.load(f)

    print("Building yearly and country-level figure tables...", flush=True)
    year_count, year_share = build_year_tables(goal_df)
    country_df, country_phase_counts = build_country_tables(goal_df, world_data)
    diffusion_count, diffusion_intensity, (hhi_count, hhi_impact) = build_diffusion_tables(country_df)

    figures: list[Path] = []
    print("Rendering stacked bars and line figures...", flush=True)
    figures.extend(stacked_bar_figures(year_count, year_share))
    figures.append(
        multi_line_figure(
            diffusion_count,
            "Country_count",
            "Number of countries",
            "SDG Diffusion by Country Participation, 1972-2024",
            "fig3_diffusion_country_count.png",
        )
    )
    figures.append(
        multi_line_figure(
            diffusion_intensity,
            "Diffusion_intensity",
            "Diffusion intensity",
            "SDG Diffusion Intensity, 1972-2024",
            "fig4_diffusion_intensity.png",
        )
    )
    figures.append(
        multi_line_figure(
            hhi_count,
            "HHI_count",
            "HHI",
            "SDG Concentration by Document Count, 1972-2024",
            "fig5_hhi_count.png",
        )
    )
    figures.append(
        multi_line_figure(
            hhi_impact,
            "HHI_impact",
            "HHI",
            "SDG Concentration by Citation Impact, 1972-2024",
            "fig6_hhi_impact.png",
        )
    )

    maps: list[Path] = []
    print("Rendering 34 phase maps...", flush=True)
    for goal in SDG_ORDER:
        for phase in PHASES:
            maps.append(map_figure(goal, phase, country_phase_counts, world_data))

    print("Updating Excel workbook with corrected figure tables...", flush=True)
    new_sheets = {
        "sdg_goal_year_count_phase3_phase4": year_count,
        "sdg_goal_year_share_phase3_phase4": year_share,
        "sdg_goal_country_phase_counts": country_phase_counts.sort_values(["SDG_goal", "Phase", "Document_count"], ascending=[True, True, False]),
    }
    update_workbook(new_sheets)

    print(f"Figures generated: {len(figures)}")
    print(f"Maps generated: {len(maps)}")
    print(f"SDG order confirmed: {SDG_ORDER == list(range(1, 18))}")
    for path in figures + maps:
        print(path)


if __name__ == "__main__":
    main()
