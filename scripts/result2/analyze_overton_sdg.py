from __future__ import annotations

import math
import re
import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parents[2]
INPUT_FILES = [
    BASE_DIR / "inputs" / "raw" / "export-2026-04-01.csv",
    BASE_DIR / "inputs" / "raw" / "export-2026-04-01 (1).csv",
]
OUTPUT_DIR = BASE_DIR / "outputs" / "result2"
FIGURE_DIR = OUTPUT_DIR / "figures"
os.environ.setdefault("MPLCONFIGDIR", str(OUTPUT_DIR / ".mplconfig"))

import numpy as np
import pandas as pd
import seaborn as sns
from matplotlib import pyplot as plt

WORKBOOK_PATH = OUTPUT_DIR / "overton_sdg_analysis.xlsx"
CLEANED_CSV_PATH = OUTPUT_DIR / "overton_sdg_cleaned_merged.csv"
SUMMARY_PATH = OUTPUT_DIR / "overton_sdg_summary.txt"
METHODS_PATH = OUTPUT_DIR / "overton_sdg_methods_note.txt"

PHASE_LABELS = ["Phase 1", "Phase 2", "Phase 3", "Phase 4"]
GOAL_NAME_MAP = {
    "1": "No Poverty",
    "2": "Zero Hunger",
    "3": "Good Health and Well-being",
    "4": "Quality Education",
    "5": "Gender Equality",
    "6": "Clean Water and Sanitation",
    "7": "Affordable and Clean Energy",
    "8": "Decent Work and Economic Growth",
    "9": "Industry, Innovation and Infrastructure",
    "10": "Reduced Inequality",
    "11": "Sustainable Cities and Communities",
    "12": "Responsible Consumption and Production",
    "13": "Climate Action",
    "14": "Life Below Water",
    "15": "Life on Land",
    "16": "Peace, Justice and Strong Institutions",
    "17": "Partnerships for the Goals",
}

GOAL_TOKEN_PATTERN = re.compile(r"^SDG\s+(\d{1,2})(?:\s*:.*)?$")
TARGET_TOKEN_PATTERN = re.compile(r"^SDG\s+Target\s+(\d{1,2}(?:\.[0-9a-z]+)?)$", re.IGNORECASE)


def ensure_dirs() -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    FIGURE_DIR.mkdir(parents=True, exist_ok=True)


def phase_from_year(year: float) -> str | None:
    if pd.isna(year):
        return None
    year = int(year)
    if 1869 <= year <= 1947:
        return "Phase 1"
    if 1948 <= year <= 1971:
        return "Phase 2"
    if 1972 <= year <= 1993:
        return "Phase 3"
    if 1994 <= year <= 2024:
        return "Phase 4"
    return None


def goal_label(goal_code: str) -> str:
    return f"SDG {goal_code}: {GOAL_NAME_MAP.get(str(goal_code), 'Unknown Goal')}"


def format_pct(series: pd.Series) -> pd.Series:
    return (series * 100).round(2)


def clean_country(value: object) -> str:
    if pd.isna(value):
        return "Unknown"
    text = str(value).strip()
    return text if text else "Unknown"


def parse_sdg_tokens(value: object) -> list[dict[str, str]]:
    if pd.isna(value):
        return []

    text = str(value).strip()
    if not text:
        return []

    parsed: list[dict[str, str]] = []
    seen_codes: set[str] = set()

    for token in text.split("|"):
        token = token.strip()
        if not token:
            continue

        goal_match = GOAL_TOKEN_PATTERN.match(token)
        if goal_match:
            code = goal_match.group(1)
            if code not in seen_codes:
                parsed.append(
                    {
                        "sdg_target": code,
                        "sdg_goal": code,
                        "sdg_level": "goal",
                        "original_token": token,
                    }
                )
                seen_codes.add(code)
            continue

        target_match = TARGET_TOKEN_PATTERN.match(token)
        if target_match:
            code = target_match.group(1)
            if code not in seen_codes:
                parsed.append(
                    {
                        "sdg_target": code,
                        "sdg_goal": code.split(".")[0],
                        "sdg_level": "target",
                        "original_token": token,
                    }
                )
                seen_codes.add(code)

    return parsed


def gini(values: list[float]) -> float:
    values = [float(v) for v in values if pd.notna(v)]
    if not values:
        return float("nan")
    mean_value = sum(values) / len(values)
    if mean_value == 0:
        return 0.0
    total_diff = 0.0
    for left in values:
        for right in values:
            total_diff += abs(left - right)
    return total_diff / (2 * (len(values) ** 2) * mean_value)


def top_k_share(values: list[float], k: int) -> float:
    values = [float(v) for v in values if pd.notna(v)]
    total = sum(values)
    if total == 0 or not values:
        return float("nan")
    return sum(sorted(values, reverse=True)[:k]) / total


def inequality_table(df: pd.DataFrame, value_col: str, scope_name: str) -> pd.DataFrame:
    values = df[value_col].tolist()
    return pd.DataFrame(
        [
            {
                "Scope": scope_name,
                "Basis": value_col,
                "N_categories": int(len(values)),
                "Total": float(np.sum(values)),
                "Top1_share_pct": round(top_k_share(values, 1) * 100, 2),
                "Top5_share_pct": round(top_k_share(values, 5) * 100, 2),
                "Top10_share_pct": round(top_k_share(values, 10) * 100, 2),
                "Gini_coefficient": round(gini(values), 4),
            }
        ]
    )


def build_long_tables(cleaned: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame, int]:
    target_rows: list[dict[str, object]] = []
    missing_sdg_docs = 0

    base_columns = [
        "Overton id",
        "Title",
        "Document type",
        "Published_on",
        "Year",
        "Phase",
        "Country",
        "Policy citations (excl. same source)",
        "Related to SDGs",
    ]

    for row in cleaned[base_columns].itertuples(index=False):
        parsed = parse_sdg_tokens(row._8)
        if not parsed:
            missing_sdg_docs += 1
            continue

        for item in parsed:
            target_rows.append(
                {
                    "Overton id": row[0],
                    "Title": row[1],
                    "Document type": row[2],
                    "Published_on": row[3],
                    "Year": row[4],
                    "Phase": row[5],
                    "Country": row[6],
                    "Impact": row[7],
                    "Related to SDGs": row[8],
                    "SDG_target": item["sdg_target"],
                    "SDG_target_label": (
                        f"SDG {item['sdg_target']}"
                        if item["sdg_level"] == "goal"
                        else f"SDG Target {item['sdg_target']}"
                    ),
                    "SDG_goal": item["sdg_goal"],
                    "SDG_goal_label": goal_label(item["sdg_goal"]),
                    "SDG_level_as_recorded": item["sdg_level"],
                    "Original_SDG_token": item["original_token"],
                }
            )

    target_long = pd.DataFrame(target_rows).drop_duplicates(subset=["Overton id", "SDG_target"])
    goal_long = (
        target_long[
            [
                "Overton id",
                "Title",
                "Document type",
                "Published_on",
                "Year",
                "Phase",
                "Country",
                "Impact",
                "Related to SDGs",
                "SDG_goal",
                "SDG_goal_label",
            ]
        ]
        .drop_duplicates(subset=["Overton id", "SDG_goal"])
        .reset_index(drop=True)
    )

    target_long = target_long.reset_index(drop=True)
    return target_long, goal_long, missing_sdg_docs


def distribution_table(
    df: pd.DataFrame,
    code_col: str,
    label_col: str,
    scope_label: str,
) -> pd.DataFrame:
    grouped = (
        df.groupby([code_col, label_col], dropna=False)
        .size()
        .reset_index(name="Document_count")
        .sort_values("Document_count", ascending=False)
        .reset_index(drop=True)
    )
    total_pairs = grouped["Document_count"].sum()
    total_unique_docs = df["Overton id"].nunique()
    grouped["Share_of_SDG_links_pct"] = format_pct(grouped["Document_count"] / total_pairs)
    grouped["Share_of_all_documents_pct"] = format_pct(grouped["Document_count"] / total_unique_docs)
    grouped["Rank"] = np.arange(1, len(grouped) + 1)
    grouped["Scope"] = scope_label
    return grouped[
        [
            "Scope",
            code_col,
            label_col,
            "Document_count",
            "Share_of_SDG_links_pct",
            "Share_of_all_documents_pct",
            "Rank",
        ]
    ]


def phase_distribution_table(
    df: pd.DataFrame,
    code_col: str,
    label_col: str,
) -> pd.DataFrame:
    phase_df = df[df["Phase"].notna()].copy()
    grouped = (
        phase_df.groupby(["Phase", code_col, label_col], dropna=False)
        .size()
        .reset_index(name="Document_count")
    )
    phase_totals = grouped.groupby("Phase")["Document_count"].transform("sum")
    grouped["Share_within_phase_pct"] = format_pct(grouped["Document_count"] / phase_totals)
    grouped["Phase_order"] = grouped["Phase"].map({phase: idx + 1 for idx, phase in enumerate(PHASE_LABELS)})
    grouped = grouped.sort_values(["Phase_order", "Document_count"], ascending=[True, False]).reset_index(drop=True)
    return grouped.drop(columns=["Phase_order"])


def country_distribution_table(
    df: pd.DataFrame,
    code_col: str,
    label_col: str,
) -> pd.DataFrame:
    grouped = (
        df.groupby(["Country", code_col, label_col], dropna=False)
        .size()
        .reset_index(name="Document_count")
    )
    country_totals = grouped.groupby("Country")["Document_count"].transform("sum")
    grouped["Share_within_country_pct"] = format_pct(grouped["Document_count"] / country_totals)
    grouped["Country_total_sdg_links"] = country_totals
    grouped = grouped.sort_values(["Country", "Document_count"], ascending=[True, False]).reset_index(drop=True)
    return grouped


def top_countries_by_goal(goal_country: pd.DataFrame, top_n: int = 10) -> pd.DataFrame:
    df = goal_country.copy()
    goal_totals = df.groupby("SDG_goal")["Document_count"].transform("sum")
    df["Share_within_goal_pct"] = format_pct(df["Document_count"] / goal_totals)
    df["Rank_within_goal"] = df.groupby("SDG_goal")["Document_count"].rank(method="dense", ascending=False).astype(int)
    return df[df["Rank_within_goal"] <= top_n].sort_values(["SDG_goal", "Rank_within_goal", "Country"])


def top_targets_within_goal(target_dist: pd.DataFrame) -> pd.DataFrame:
    df = target_dist.copy()
    df["SDG_goal"] = df["SDG_target"].astype(str).str.split(".").str[0]
    df["Is_detailed_target"] = df["SDG_target"].astype(str).str.contains(r"\.")
    detailed = df[df["Is_detailed_target"]].copy()
    detailed["Rank_within_goal"] = (
        detailed.groupby("SDG_goal")["Document_count"].rank(method="dense", ascending=False).astype(int)
    )
    return detailed.sort_values(["SDG_goal", "Rank_within_goal", "SDG_target"]).drop(columns=["Is_detailed_target"])


def impact_table(df: pd.DataFrame, code_col: str, label_col: str) -> pd.DataFrame:
    grouped = (
        df.groupby([code_col, label_col], dropna=False)
        .agg(Document_count=("Overton id", "size"), Total_impact=("Impact", "sum"))
        .reset_index()
    )
    grouped["Average_impact_per_document"] = (grouped["Total_impact"] / grouped["Document_count"]).round(4)
    return grouped.sort_values(["Total_impact", "Document_count"], ascending=[False, False]).reset_index(drop=True)


def efficiency_table(df: pd.DataFrame, code_col: str, label_col: str) -> pd.DataFrame:
    full_table = impact_table(df, code_col, label_col)
    full_table["Scope"] = "Full dataset"

    phase4 = impact_table(df[df["Phase"] == "Phase 4"], code_col, label_col)
    phase4["Scope"] = "Phase 4"

    combined = pd.concat([full_table, phase4], ignore_index=True)
    combined["Efficiency"] = combined["Average_impact_per_document"]
    return combined[
        [
            "Scope",
            code_col,
            label_col,
            "Document_count",
            "Total_impact",
            "Average_impact_per_document",
            "Efficiency",
        ]
    ]


def inequality_bundle(df: pd.DataFrame, code_col: str, label_col: str, scope_name: str) -> pd.DataFrame:
    summary = impact_table(df, code_col, label_col)
    count_metrics = inequality_table(summary, "Document_count", scope_name)
    impact_metrics = inequality_table(summary, "Total_impact", scope_name)
    return pd.concat([count_metrics, impact_metrics], ignore_index=True)


def build_goal_diffusion_tables(goal_long: pd.DataFrame, cleaned: pd.DataFrame) -> dict[str, pd.DataFrame]:
    time_goal = goal_long[goal_long["Phase"].notna()].dropna(subset=["Year"]).copy()
    time_goal["Year"] = time_goal["Year"].astype(int)

    time_cleaned = cleaned[cleaned["Time_series_included"]].dropna(subset=["Year"]).copy()
    time_cleaned["Year"] = time_cleaned["Year"].astype(int)

    years = sorted(time_goal["Year"].unique().tolist())
    goal_frame = pd.DataFrame({"SDG_goal": sorted(GOAL_NAME_MAP.keys(), key=lambda x: int(x))})
    goal_frame["SDG_goal_label"] = goal_frame["SDG_goal"].map(goal_label)
    year_frame = pd.DataFrame({"Year": years})
    base_grid = goal_frame.merge(year_frame, how="cross")

    country_count = (
        time_goal.groupby(["SDG_goal", "SDG_goal_label", "Year"])["Country"]
        .nunique()
        .reset_index(name="Country_count")
    )
    country_count = base_grid.merge(country_count, on=["SDG_goal", "SDG_goal_label", "Year"], how="left")
    country_count["Country_count"] = country_count["Country_count"].fillna(0).astype(int)
    country_count = country_count.sort_values(["SDG_goal", "Year"]).reset_index(drop=True)
    country_count["Diffusion_speed"] = (
        country_count.groupby("SDG_goal")["Country_count"].diff().fillna(country_count["Country_count"]).astype(int)
    )

    first_country_year = (
        time_goal.groupby(["SDG_goal", "Country"], dropna=False)["Year"]
        .min()
        .reset_index(name="Year")
    )
    new_country = (
        first_country_year.groupby(["SDG_goal", "Year"])
        .size()
        .reset_index(name="New_country_count")
    )
    new_country = base_grid.merge(new_country, on=["SDG_goal", "Year"], how="left")
    new_country["New_country_count"] = new_country["New_country_count"].fillna(0).astype(int)
    new_country = new_country.sort_values(["SDG_goal", "Year"]).reset_index(drop=True)

    total_countries = (
        time_cleaned.groupby("Year")["Country"]
        .nunique()
        .reset_index(name="Total_countries_t")
    )
    diffusion_intensity = country_count.merge(total_countries, on="Year", how="left")
    diffusion_intensity["Diffusion_intensity"] = diffusion_intensity["Country_count"] / diffusion_intensity["Total_countries_t"]
    diffusion_intensity["Diffusion_intensity_pct"] = (diffusion_intensity["Diffusion_intensity"] * 100).round(2)

    country_goal_year = (
        time_goal.groupby(["SDG_goal", "SDG_goal_label", "Year", "Country"], dropna=False)
        .agg(Document_count=("Overton id", "size"), Impact=("Impact", "sum"))
        .reset_index()
    )

    def hhi_from_values(values: pd.Series) -> float:
        total = float(values.sum())
        if total == 0:
            return float("nan")
        shares = values / total
        return float((shares ** 2).sum())

    hhi_summary = (
        country_goal_year.groupby(["SDG_goal", "SDG_goal_label", "Year"])
        .agg(
            Countries_in_goal_year=("Country", "nunique"),
            Goal_year_document_count=("Document_count", "sum"),
            Goal_year_total_impact=("Impact", "sum"),
            HHI_count=("Document_count", hhi_from_values),
            HHI_impact=("Impact", hhi_from_values),
        )
        .reset_index()
    )
    hhi_summary = base_grid.merge(hhi_summary, on=["SDG_goal", "SDG_goal_label", "Year"], how="left")
    hhi_summary["Countries_in_goal_year"] = hhi_summary["Countries_in_goal_year"].fillna(0).astype(int)
    hhi_summary["Goal_year_document_count"] = hhi_summary["Goal_year_document_count"].fillna(0).astype(int)
    hhi_summary["Goal_year_total_impact"] = hhi_summary["Goal_year_total_impact"].fillna(0.0)

    return {
        "sdg_goal_country_count_by_year": country_count[["SDG_goal", "SDG_goal_label", "Year", "Country_count"]],
        "sdg_goal_diffusion_speed_by_year": country_count[["SDG_goal", "SDG_goal_label", "Year", "Country_count", "Diffusion_speed"]],
        "sdg_goal_new_country_by_year": new_country[["SDG_goal", "SDG_goal_label", "Year", "New_country_count"]],
        "sdg_goal_diffusion_intensity_by_year": diffusion_intensity[
            ["SDG_goal", "SDG_goal_label", "Year", "Country_count", "Total_countries_t", "Diffusion_intensity", "Diffusion_intensity_pct"]
        ],
        "sdg_goal_hhi_count_by_year": hhi_summary[
            ["SDG_goal", "SDG_goal_label", "Year", "Countries_in_goal_year", "Goal_year_document_count", "HHI_count"]
        ],
        "sdg_goal_hhi_impact_by_year": hhi_summary[
            ["SDG_goal", "SDG_goal_label", "Year", "Countries_in_goal_year", "Goal_year_total_impact", "HHI_impact"]
        ],
    }


def save_figure(path_stem: Path) -> None:
    plt.tight_layout()
    plt.savefig(path_stem.with_suffix(".png"), dpi=300, bbox_inches="tight")
    plt.savefig(path_stem.with_suffix(".svg"), bbox_inches="tight")
    plt.close()


def create_figures(goal_dist: pd.DataFrame, goal_by_phase: pd.DataFrame, goal_country: pd.DataFrame, goal_impact: pd.DataFrame,
                   goal_ineq_p3: pd.DataFrame, goal_ineq_p4: pd.DataFrame, target_dist: pd.DataFrame, target_impact: pd.DataFrame,
                   diffusion_tables: dict[str, pd.DataFrame]) -> list[str]:
    sns.set_theme(style="whitegrid")
    plt.rcParams["font.family"] = "DejaVu Sans"
    created: list[str] = []

    # Figure 1
    fig, ax = plt.subplots(figsize=(12, 7))
    plot_df = goal_dist.sort_values("Document_count", ascending=True)
    ax.barh(plot_df["SDG_goal_label"], plot_df["Document_count"], color=sns.color_palette("viridis", len(plot_df)))
    ax.set_title("Overall SDG Goal Distribution")
    ax.set_xlabel("Document-SDG goal links")
    ax.set_ylabel("")
    save_figure(FIGURE_DIR / "figure1_goal_overall_distribution")
    created.extend(["figure1_goal_overall_distribution.png", "figure1_goal_overall_distribution.svg"])

    # Figure 2
    fig, ax = plt.subplots(figsize=(13, 7))
    phase_pivot = goal_by_phase.pivot(index="Phase", columns="SDG_goal_label", values="Share_within_phase_pct").fillna(0)
    phase_pivot = phase_pivot.reindex(PHASE_LABELS)
    phase_pivot.plot(kind="bar", stacked=True, ax=ax, colormap="tab20")
    ax.set_title("SDG Goal Shares Across Policy Phases")
    ax.set_xlabel("")
    ax.set_ylabel("Share within phase (%)")
    ax.legend(title="SDG Goal", bbox_to_anchor=(1.02, 1), loc="upper left", frameon=False)
    save_figure(FIGURE_DIR / "figure2_goal_phase_stacked")
    created.extend(["figure2_goal_phase_stacked.png", "figure2_goal_phase_stacked.svg"])

    # Figure 3
    fig, ax = plt.subplots(figsize=(14, 9))
    top_countries = (
        goal_country.groupby("Country")["Document_count"].sum().sort_values(ascending=False).head(15).index.tolist()
    )
    heatmap_df = goal_country[goal_country["Country"].isin(top_countries)]
    heatmap_pivot = heatmap_df.pivot_table(
        index="Country", columns="SDG_goal_label", values="Document_count", aggfunc="sum", fill_value=0
    )
    sns.heatmap(heatmap_pivot, cmap="YlGnBu", linewidths=0.3, ax=ax)
    ax.set_title("Major Countries by SDG Goal Counts")
    ax.set_xlabel("")
    ax.set_ylabel("")
    save_figure(FIGURE_DIR / "figure3_goal_country_heatmap")
    created.extend(["figure3_goal_country_heatmap.png", "figure3_goal_country_heatmap.svg"])

    # Figure 4
    fig, ax = plt.subplots(figsize=(11, 7))
    scatter = ax.scatter(
        goal_impact["Document_count"],
        goal_impact["Total_impact"],
        s=np.maximum(goal_impact["Average_impact_per_document"] * 20, 80),
        c=pd.to_numeric(goal_impact["SDG_goal"], errors="coerce"),
        cmap="viridis",
        alpha=0.85,
        edgecolor="black",
        linewidth=0.5,
    )
    for _, row in goal_impact.iterrows():
        ax.annotate(row["SDG_goal"], (row["Document_count"], row["Total_impact"]), fontsize=9, xytext=(4, 4), textcoords="offset points")
    ax.set_title("SDG Goal Document Count vs Impact")
    ax.set_xlabel("Document count")
    ax.set_ylabel("Total policy citations")
    plt.colorbar(scatter, ax=ax, label="SDG goal")
    save_figure(FIGURE_DIR / "figure4_goal_count_vs_impact")
    created.extend(["figure4_goal_count_vs_impact.png", "figure4_goal_count_vs_impact.svg"])

    # Figure 5
    fig, ax = plt.subplots(figsize=(12, 7))
    ineq_compare = pd.concat([goal_ineq_p3, goal_ineq_p4], ignore_index=True)
    tidy = ineq_compare.melt(
        id_vars=["Scope", "Basis"],
        value_vars=["Top1_share_pct", "Top5_share_pct", "Top10_share_pct", "Gini_coefficient"],
        var_name="Metric",
        value_name="Value",
    )
    sns.barplot(data=tidy, x="Metric", y="Value", hue="Scope", palette="Set2", ax=ax)
    ax.set_title("Inequality Metrics at SDG Goal Level: Phase 3 vs Phase 4")
    ax.set_xlabel("")
    ax.set_ylabel("Value")
    save_figure(FIGURE_DIR / "figure5_goal_inequality_phase3_vs_phase4")
    created.extend(["figure5_goal_inequality_phase3_vs_phase4.png", "figure5_goal_inequality_phase3_vs_phase4.svg"])

    # Supplementary target-level figures
    fig, ax = plt.subplots(figsize=(12, 8))
    top_targets = target_dist.head(20).sort_values("Document_count", ascending=True)
    ax.barh(top_targets["SDG_target_label"], top_targets["Document_count"], color=sns.color_palette("magma", len(top_targets)))
    ax.set_title("Supplementary: Top 20 SDG Targets by Document Count")
    ax.set_xlabel("Document-SDG target links")
    ax.set_ylabel("")
    save_figure(FIGURE_DIR / "supplementary_target_top20_distribution")
    created.extend(["supplementary_target_top20_distribution.png", "supplementary_target_top20_distribution.svg"])

    fig, ax = plt.subplots(figsize=(11, 7))
    supp_scatter = target_impact.head(40)
    ax.scatter(
        supp_scatter["Document_count"],
        supp_scatter["Total_impact"],
        s=np.maximum(supp_scatter["Average_impact_per_document"] * 18, 60),
        color="#B33F62",
        alpha=0.8,
        edgecolor="black",
        linewidth=0.4,
    )
    for _, row in supp_scatter.iterrows():
        ax.annotate(row["SDG_target"], (row["Document_count"], row["Total_impact"]), fontsize=8, xytext=(3, 3), textcoords="offset points")
    ax.set_title("Supplementary: Top 40 SDG Targets by Count vs Impact")
    ax.set_xlabel("Document count")
    ax.set_ylabel("Total policy citations")
    save_figure(FIGURE_DIR / "supplementary_target_count_vs_impact")
    created.extend(["supplementary_target_count_vs_impact.png", "supplementary_target_count_vs_impact.svg"])

    country_count = diffusion_tables["sdg_goal_country_count_by_year"]
    speed = diffusion_tables["sdg_goal_diffusion_speed_by_year"]
    new_country = diffusion_tables["sdg_goal_new_country_by_year"]
    intensity = diffusion_tables["sdg_goal_diffusion_intensity_by_year"]
    hhi_count = diffusion_tables["sdg_goal_hhi_count_by_year"]
    hhi_impact = diffusion_tables["sdg_goal_hhi_impact_by_year"]

    def lineplot_all_goals(df: pd.DataFrame, value_col: str, title: str, ylabel: str, path_stem: str) -> None:
        fig, ax = plt.subplots(figsize=(14, 8))
        sns.lineplot(data=df, x="Year", y=value_col, hue="SDG_goal_label", palette="tab20", linewidth=1.7, ax=ax)
        ax.set_title(title)
        ax.set_xlabel("Year")
        ax.set_ylabel(ylabel)
        ax.legend(title="SDG Goal", bbox_to_anchor=(1.02, 1), loc="upper left", frameon=False)
        save_figure(FIGURE_DIR / path_stem)

    lineplot_all_goals(country_count, "Country_count", "SDG Goal Country Count Over Time", "Distinct countries", "figure6_goal_country_count_by_year")
    created.extend(["figure6_goal_country_count_by_year.png", "figure6_goal_country_count_by_year.svg"])

    lineplot_all_goals(intensity, "Diffusion_intensity", "SDG Goal Diffusion Intensity Over Time", "Country_count / Total_countries_t", "figure7_goal_diffusion_intensity_by_year")
    created.extend(["figure7_goal_diffusion_intensity_by_year.png", "figure7_goal_diffusion_intensity_by_year.svg"])

    lineplot_all_goals(speed, "Diffusion_speed", "SDG Goal Diffusion Speed Over Time", "Annual change in countries", "figure8_goal_diffusion_speed_by_year")
    created.extend(["figure8_goal_diffusion_speed_by_year.png", "figure8_goal_diffusion_speed_by_year.svg"])

    lineplot_all_goals(new_country, "New_country_count", "New Country Entry by SDG Goal Over Time", "New countries", "figure9_goal_new_country_by_year")
    created.extend(["figure9_goal_new_country_by_year.png", "figure9_goal_new_country_by_year.svg"])

    lineplot_all_goals(hhi_count, "HHI_count", "SDG Goal HHI by Document Count Over Time", "HHI_count", "figure10_goal_hhi_count_by_year")
    created.extend(["figure10_goal_hhi_count_by_year.png", "figure10_goal_hhi_count_by_year.svg"])

    lineplot_all_goals(hhi_impact, "HHI_impact", "SDG Goal HHI by Citation Impact Over Time", "HHI_impact", "figure11_goal_hhi_impact_by_year")
    created.extend(["figure11_goal_hhi_impact_by_year.png", "figure11_goal_hhi_impact_by_year.svg"])

    return created


def write_text_outputs(
    cleaned: pd.DataFrame,
    target_long: pd.DataFrame,
    goal_long: pd.DataFrame,
    goal_dist: pd.DataFrame,
    target_dist: pd.DataFrame,
    goal_impact: pd.DataFrame,
    missing_sdg_docs: int,
    diffusion_tables: dict[str, pd.DataFrame],
    output_files: list[Path],
) -> None:
    total_docs = len(cleaned)
    sdg_docs = cleaned["Has_SDG"].sum()
    missing_pct = (missing_sdg_docs / total_docs) * 100 if total_docs else 0
    excluded_recent_docs = cleaned["Time_series_included"].eq(False).sum()

    top_goal = goal_dist.iloc[0]
    top_recorded_code = target_dist.iloc[0]
    detailed_targets_only = target_dist[target_dist["SDG_target"].astype(str).str.contains(r"\.")]
    top_detailed_target = detailed_targets_only.iloc[0] if not detailed_targets_only.empty else None
    most_impactful_goal = goal_impact.iloc[0]
    intensity = diffusion_tables["sdg_goal_diffusion_intensity_by_year"]
    hhi_count = diffusion_tables["sdg_goal_hhi_count_by_year"]
    hhi_impact = diffusion_tables["sdg_goal_hhi_impact_by_year"]

    diffusion_summary = (
        intensity.groupby(["SDG_goal", "SDG_goal_label"], as_index=False)
        .agg(Mean_diffusion_intensity=("Diffusion_intensity", "mean"))
    )
    concentration_summary = (
        hhi_count.groupby(["SDG_goal", "SDG_goal_label"], as_index=False)
        .agg(Mean_HHI_count=("HHI_count", "mean"))
        .merge(
            hhi_impact.groupby(["SDG_goal", "SDG_goal_label"], as_index=False).agg(Mean_HHI_impact=("HHI_impact", "mean")),
            on=["SDG_goal", "SDG_goal_label"],
            how="left",
        )
    )
    diffusion_concentration = diffusion_summary.merge(concentration_summary, on=["SDG_goal", "SDG_goal_label"], how="left")
    high_diffusion_low_conc = diffusion_concentration.sort_values(
        ["Mean_diffusion_intensity", "Mean_HHI_count"], ascending=[False, True]
    ).iloc[0]
    high_diffusion_high_conc_candidates = diffusion_concentration[
        diffusion_concentration["SDG_goal"] != high_diffusion_low_conc["SDG_goal"]
    ]
    high_diffusion_high_conc = high_diffusion_high_conc_candidates.sort_values(
        ["Mean_diffusion_intensity", "Mean_HHI_count"], ascending=[False, False]
    ).iloc[0]
    most_concentrated_impact = diffusion_concentration.sort_values("Mean_HHI_impact", ascending=False).iloc[0]

    summary_text = f"""Overton SDG analysis summary
================================

Merged and deduplicated records: {total_docs:,}
Documents with at least one parsable SDG token: {sdg_docs:,}
Documents with missing or empty SDG field: {missing_sdg_docs:,} ({missing_pct:.2f}%)
Target-level document-SDG pairs: {len(target_long):,}
Goal-level document-SDG pairs: {len(goal_long):,}
Documents excluded from time-series phase analysis because they fall in 2025-2026 or have no valid year: {excluded_recent_docs:,}

Interpretation paragraph
------------------------
The detailed SDG target structure is more granular than the goal-level structure used in the main paper figures. In the exact-as-recorded target table, the largest single code is {top_recorded_code['SDG_target_label']} with {int(top_recorded_code['Document_count']):,} document-target links ({top_recorded_code['Share_of_SDG_links_pct']:.2f}% of all recorded target links).""" + (
f""" Among genuinely detailed targets, {top_detailed_target['SDG_target_label']} appears most often with {int(top_detailed_target['Document_count']):,} document-target links ({top_detailed_target['Share_of_SDG_links_pct']:.2f}% of all recorded target links)."""
if top_detailed_target is not None
else ""
) + f""" For the publication-facing main figures, these detailed targets were aggregated to parent goals, where {top_goal['SDG_goal_label']} ranks first with {int(top_goal['Document_count']):,} document-goal links ({top_goal['Share_of_SDG_links_pct']:.2f}% of all goal links). This aggregation simplifies cross-phase and cross-country interpretation while preserving a separate supplementary layer that keeps the finer target structure visible. In impact terms, {most_impactful_goal['SDG_goal_label']} has the largest total citation impact with {most_impactful_goal['Total_impact']:.0f} policy citations across {int(most_impactful_goal['Document_count']):,} linked documents.

Diffusion and concentration
---------------------------
The yearly goal-level diffusion module shows that diffusion and concentration are related but not identical. {high_diffusion_low_conc['SDG_goal_label']} pairs the highest average diffusion intensity with a relatively low mean document-count concentration (HHI_count {high_diffusion_low_conc['Mean_HHI_count']:.3f}), making it the clearest case where broad international spread also comes with comparatively dispersed participation. By contrast, {high_diffusion_high_conc['SDG_goal_label']} also diffuses widely but remains more concentrated across countries (HHI_count {high_diffusion_high_conc['Mean_HHI_count']:.3f}), showing that some SDGs can expand globally while still being led by a narrower core of countries. On the impact side, {most_concentrated_impact['SDG_goal_label']} has the highest average HHI_impact ({most_concentrated_impact['Mean_HHI_impact']:.3f}), indicating that citation influence can remain more concentrated than document production.

Output files
------------
""" + "\n".join(f"- {path}" for path in output_files)

    methods_text = f"""Methods note: Overton SDG analysis
=================================

1. Data loading and deduplication
- Two Overton CSV exports were loaded and concatenated.
- Duplicate records were removed using `Overton id`, keeping the first occurrence.
- `Published_on` was parsed as a date and converted into a numeric `Year` variable.
- The cleaned full dataset retains all years, including 2025 and 2026.

2. Phase definition
- Phase 1: 1869-1947
- Phase 2: 1948-1971
- Phase 3: 1972-1993
- Phase 4: 1994-2024
- Documents from 2025-2026 were retained in the cleaned data but excluded from phase-based time-series analyses by leaving `Phase` empty and setting `Time_series_included = False`.

3. SDG parsing
- The `Related to SDGs` field was split on the pipe delimiter (`|`).
- Tokens matching `SDG X: ...` were treated as goal-level codes and stored as `X`.
- Tokens matching `SDG Target X.Y` or `SDG Target X.a` were treated as detailed target-level codes and stored exactly as the extracted code (for example `1.1`, `11.2`, `1.a`).
- The goal-level variable `SDG_goal` was created by mapping each parsed code to its parent goal number. For detailed targets, the parent goal is the substring before the first period. Examples: `1.1 -> SDG 1`, `1.2 -> SDG 1`, `11.2 -> SDG 11`.
- Goal-level long tables were deduplicated to one document-goal pair, so repeated references to the same goal within a single document do not inflate goal counts.

4. Missing SDG handling
- Empty or missing `Related to SDGs` cells were treated as missing SDG data.
- Documents with missing SDG information were kept in `cleaned_data` but excluded from the SDG long tables and all SDG-based calculations.
- In this dataset, {missing_sdg_docs:,} of {total_docs:,} deduplicated documents had missing or empty SDG information.

5. Metrics
- Distribution tables report document-SDG pair counts and percentage shares.
- Impact is the sum of `Policy citations (excl. same source)`.
- Average impact per document equals total impact divided by document count.
- Efficiency is defined as impact divided by count and is numerically identical to average impact per document.
- Concentration metrics include Top1, Top5, Top10 shares and the Gini coefficient, computed separately for document counts and citation-based impact.

6. Diffusion and HHI module
- The diffusion module uses SDG goal level only.
- Yearly diffusion calculations use the time-series subset, excluding 2025 and 2026 because those years may be incomplete.
- `Country_count_(g,t)` is the number of distinct countries with at least one document linked to SDG goal `g` in year `t`.
- `Diffusion_speed_(g,t)` is the annual change in country participation relative to year `t-1`.
- `New_country_count_(g,t)` counts first-time country entries into SDG goal `g` across the full observed time series.
- `Diffusion_intensity_(g,t)` equals `Country_count_(g,t) / Total_countries_t`, where `Total_countries_t` is the number of distinct countries appearing anywhere in the dataset in year `t`.
- `HHI_count` and `HHI_impact` are computed within each goal-year using country shares based on document counts and citation impact, respectively.
"""

    SUMMARY_PATH.write_text(summary_text, encoding="utf-8")
    METHODS_PATH.write_text(methods_text, encoding="utf-8")


def autosize_worksheet(ws, df: pd.DataFrame) -> None:
    sample = df.head(1000)
    for idx, column_name in enumerate(df.columns, start=1):
        sample_values = sample[column_name].astype(str).tolist()
        max_length = max([len(str(column_name))] + [len(str(value)) for value in sample_values] + [12])
        col_letter = ws.cell(row=1, column=idx).column_letter
        ws.column_dimensions[col_letter].width = min(max_length + 2, 40)
    ws.freeze_panes = "A2"


def main() -> None:
    ensure_dirs()

    raw = pd.concat([pd.read_csv(path) for path in INPUT_FILES], ignore_index=True)
    cleaned = raw.drop_duplicates(subset=["Overton id"], keep="first").copy()

    cleaned["Published_on"] = pd.to_datetime(cleaned["Published_on"], errors="coerce")
    cleaned["Year"] = cleaned["Published_on"].dt.year
    cleaned["Country"] = cleaned["Source country"].map(clean_country)
    cleaned["Impact"] = pd.to_numeric(cleaned["Policy citations (excl. same source)"], errors="coerce").fillna(0).astype(float)
    cleaned["Phase"] = cleaned["Year"].apply(phase_from_year)
    cleaned["Time_series_included"] = cleaned["Phase"].notna()
    cleaned["Has_SDG"] = cleaned["Related to SDGs"].fillna("").astype(str).str.strip().ne("")

    target_long, goal_long, missing_sdg_docs = build_long_tables(cleaned)
    target_long["Time_series_included"] = target_long["Phase"].notna()
    goal_long["Time_series_included"] = goal_long["Phase"].notna()

    goal_dist = distribution_table(goal_long, "SDG_goal", "SDG_goal_label", "Full dataset")
    target_dist = distribution_table(target_long, "SDG_target", "SDG_target_label", "Full dataset")

    goal_by_phase = phase_distribution_table(goal_long, "SDG_goal", "SDG_goal_label")
    target_by_phase = phase_distribution_table(target_long, "SDG_target", "SDG_target_label")

    goal_by_country = country_distribution_table(goal_long, "SDG_goal", "SDG_goal_label")
    target_by_country = country_distribution_table(target_long, "SDG_target", "SDG_target_label")

    goal_impact = impact_table(goal_long, "SDG_goal", "SDG_goal_label")
    target_impact = impact_table(target_long, "SDG_target", "SDG_target_label")

    goal_efficiency = efficiency_table(goal_long, "SDG_goal", "SDG_goal_label")
    target_efficiency = efficiency_table(target_long, "SDG_target", "SDG_target_label")

    goal_ineq_overall = inequality_bundle(goal_long, "SDG_goal", "SDG_goal_label", "Full dataset")
    goal_ineq_phase3 = inequality_bundle(goal_long[goal_long["Phase"] == "Phase 3"], "SDG_goal", "SDG_goal_label", "Phase 3")
    goal_ineq_phase4 = inequality_bundle(goal_long[goal_long["Phase"] == "Phase 4"], "SDG_goal", "SDG_goal_label", "Phase 4")

    target_ineq_overall = inequality_bundle(target_long, "SDG_target", "SDG_target_label", "Full dataset")
    target_ineq_phase3 = inequality_bundle(target_long[target_long["Phase"] == "Phase 3"], "SDG_target", "SDG_target_label", "Phase 3")
    target_ineq_phase4 = inequality_bundle(target_long[target_long["Phase"] == "Phase 4"], "SDG_target", "SDG_target_label", "Phase 4")

    top_country_table = top_countries_by_goal(goal_by_country, top_n=10)
    top_targets_table = top_targets_within_goal(target_dist)
    diffusion_tables = build_goal_diffusion_tables(goal_long, cleaned)

    figure_files = create_figures(
        goal_dist,
        goal_by_phase,
        goal_by_country,
        goal_impact,
        goal_ineq_phase3,
        goal_ineq_phase4,
        target_dist,
        target_impact,
        diffusion_tables,
    )

    cleaned_export = cleaned.copy()
    cleaned_export["Published_on"] = cleaned_export["Published_on"].dt.strftime("%Y-%m-%d")
    cleaned_export.to_csv(CLEANED_CSV_PATH, index=False)

    sheet_map = {
        "cleaned_data": cleaned_export,
        "sdg_target_long": target_long,
        "sdg_goal_long": goal_long,
        "sdg_goal_overall_distribution": goal_dist,
        "sdg_target_overall_distribution": target_dist,
        "sdg_goal_by_phase": goal_by_phase,
        "sdg_target_by_phase": target_by_phase,
        "sdg_goal_by_country": goal_by_country,
        "sdg_target_by_country": target_by_country,
        "sdg_goal_impact": goal_impact,
        "sdg_target_impact": target_impact,
        "sdg_goal_efficiency": goal_efficiency,
        "sdg_target_efficiency": target_efficiency,
        "sdg_goal_inequality_overall": goal_ineq_overall,
        "sdg_goal_inequality_phase3": goal_ineq_phase3,
        "sdg_goal_inequality_phase4": goal_ineq_phase4,
        "sdg_target_inequality_overall": target_ineq_overall,
        "sdg_target_inequality_phase3": target_ineq_phase3,
        "sdg_target_inequality_phase4": target_ineq_phase4,
        "top_countries_by_sdg_goal": top_country_table,
        "top_targets_within_each_goal": top_targets_table,
        "sdg_goal_country_count_by_year": diffusion_tables["sdg_goal_country_count_by_year"],
        "sdg_goal_diffusion_speed_by_year": diffusion_tables["sdg_goal_diffusion_speed_by_year"],
        "sdg_goal_new_country_by_year": diffusion_tables["sdg_goal_new_country_by_year"],
        "sdg_goal_diffusion_intensity_by_year": diffusion_tables["sdg_goal_diffusion_intensity_by_year"],
        "sdg_goal_hhi_count_by_year": diffusion_tables["sdg_goal_hhi_count_by_year"],
        "sdg_goal_hhi_impact_by_year": diffusion_tables["sdg_goal_hhi_impact_by_year"],
    }

    with pd.ExcelWriter(WORKBOOK_PATH, engine="openpyxl") as writer:
        for sheet_name, df in sheet_map.items():
            df.to_excel(writer, sheet_name=sheet_name, index=False)

        for sheet_name, df in sheet_map.items():
            autosize_worksheet(writer.book[sheet_name], df)

    output_files = [WORKBOOK_PATH, CLEANED_CSV_PATH, SUMMARY_PATH, METHODS_PATH]
    output_files.extend(FIGURE_DIR / name for name in figure_files)
    write_text_outputs(
        cleaned,
        target_long,
        goal_long,
        goal_dist,
        target_dist,
        goal_impact,
        missing_sdg_docs,
        diffusion_tables,
        output_files,
    )

    print("Created output files:")
    for path in output_files:
        print(path)


if __name__ == "__main__":
    main()
