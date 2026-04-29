from __future__ import annotations

import json
import math
import os
import tempfile
from pathlib import Path

os.environ.setdefault("MPLCONFIGDIR", tempfile.mkdtemp(prefix="mplcfg_"))

import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt
from matplotlib import cm, colors
from matplotlib.collections import PatchCollection
from matplotlib.gridspec import GridSpec
from matplotlib.patches import FancyBboxPatch, Polygon as MplPolygon
import numpy as np
import pandas as pd


ROOT = Path(__file__).resolve().parents[2]
DATA_CSV = ROOT / "inputs" / "auxiliary" / "overton_sdg_cleaned_merged.csv"
INDEX_V2_XLSX = ROOT / "outputs" / "methods" / "ageing_energy_index_final_v2.xlsx"
OADR_CSV = ROOT / "inputs" / "auxiliary" / "unpopulation_人口元数据.csv"
WORLD_GEOJSON = ROOT / "inputs" / "auxiliary" / "world_countries.geojson"

OUTDIR = ROOT / "outputs" / "result1" / "figures" / "figure1_quantitative"
OUTDIR.mkdir(parents=True, exist_ok=True)

WORKBOOK = ROOT / "outputs" / "result1" / "figure1_quantitative_analysis.xlsx"
INTERP = ROOT / "outputs" / "result1" / "figure1_quantitative_interpretation.txt"

PHASES = {
    "Phase 1": (1869, 1947),
    "Phase 2": (1948, 1971),
    "Phase 3": (1972, 1993),
    "Phase 4": (1994, 2024),
}
PHASE_COLORS = {
    "Phase 1": "#bdbdbd",
    "Phase 2": "#74a9cf",
    "Phase 3": "#4c78a8",
    "Phase 4": "#d04f4f",
}
SOURCE_COLORS = {
    "USA": "#1f78b4",
    "UK": "#4c78a8",
    "France": "#74a9cf",
    "EU": "#f28e2b",
    "IGO": "#ffbe7d",
    "Other": "#bdbdbd",
}
COUNTRY_MAP = {
    "USA": "United States of America",
    "UK": "United Kingdom",
    "South Korea": "South Korea",
    "Russia": "Russia",
    "Iran": "Iran",
    "Taiwan": "Taiwan",
    "Turkey": "Turkey",
    "Czechia": "Czech Republic",
    "Brunei Darussalam": "Brunei",
    "Viet Nam": "Vietnam",
    "Bolivia (Plurinational State of)": "Bolivia",
    "Lao People's Democratic Republic": "Laos",
    "United Republic of Tanzania": "Tanzania",
    "Cabo Verde": "Cape Verde",
    "Timor-Leste": "East Timor",
    "Republic of Korea": "South Korea",
    "Russian Federation": "Russia",
}
REGION_MAP = {
    # Europe
    "Albania": "Europe", "Andorra": "Europe", "Austria": "Europe", "Belarus": "Europe", "Belgium": "Europe",
    "Bosnia and Herzegovina": "Europe", "Bulgaria": "Europe", "Croatia": "Europe", "Cyprus": "Europe",
    "Czech Republic": "Europe", "Denmark": "Europe", "Estonia": "Europe", "Finland": "Europe", "France": "Europe",
    "Germany": "Europe", "Greece": "Europe", "Hungary": "Europe", "Iceland": "Europe", "Ireland": "Europe",
    "Italy": "Europe", "Kosovo": "Europe", "Latvia": "Europe", "Lithuania": "Europe", "Luxembourg": "Europe",
    "Malta": "Europe", "Moldova": "Europe", "Monaco": "Europe", "Montenegro": "Europe", "Netherlands": "Europe",
    "North Macedonia": "Europe", "Norway": "Europe", "Poland": "Europe", "Portugal": "Europe", "Romania": "Europe",
    "Russia": "Europe", "San Marino": "Europe", "Serbia": "Europe", "Slovakia": "Europe", "Slovenia": "Europe",
    "Spain": "Europe", "Sweden": "Europe", "Switzerland": "Europe", "UK": "Europe", "Ukraine": "Europe",
    # North America
    "USA": "North America", "Canada": "North America", "Mexico": "North America", "Bahamas": "North America",
    "Barbados": "North America", "Belize": "North America", "Costa Rica": "North America", "Cuba": "North America",
    "Dominican Republic": "North America", "El Salvador": "North America", "Guatemala": "North America",
    "Haiti": "North America", "Honduras": "North America", "Jamaica": "North America", "Nicaragua": "North America",
    "Panama": "North America", "Trinidad and Tobago": "North America",
    # Latin America
    "Argentina": "Latin America", "Bolivia": "Latin America", "Brazil": "Latin America", "Chile": "Latin America",
    "Colombia": "Latin America", "Ecuador": "Latin America", "Guyana": "Latin America", "Paraguay": "Latin America",
    "Peru": "Latin America", "Suriname": "Latin America", "Uruguay": "Latin America", "Venezuela": "Latin America",
    # Africa
    "Algeria": "Africa", "Angola": "Africa", "Benin": "Africa", "Botswana": "Africa", "Burkina Faso": "Africa",
    "Burundi": "Africa", "Cameroon": "Africa", "Cape Verde": "Africa", "Central African Republic": "Africa",
    "Chad": "Africa", "Comoros": "Africa", "Djibouti": "Africa", "Egypt": "Africa", "Equatorial Guinea": "Africa",
    "Eritrea": "Africa", "Eswatini": "Africa", "Ethiopia": "Africa", "Gabon": "Africa", "Gambia": "Africa",
    "Ghana": "Africa", "Guinea": "Africa", "Guinea-Bissau": "Africa", "Ivory Coast": "Africa", "Kenya": "Africa",
    "Lesotho": "Africa", "Liberia": "Africa", "Libya": "Africa", "Madagascar": "Africa", "Malawi": "Africa",
    "Mali": "Africa", "Mauritania": "Africa", "Mauritius": "Africa", "Morocco": "Africa", "Mozambique": "Africa",
    "Namibia": "Africa", "Niger": "Africa", "Nigeria": "Africa", "Rwanda": "Africa", "Senegal": "Africa",
    "Seychelles": "Africa", "Sierra Leone": "Africa", "Somalia": "Africa", "South Africa": "Africa",
    "South Sudan": "Africa", "Sudan": "Africa", "Tanzania": "Africa", "Togo": "Africa", "Tunisia": "Africa",
    "Uganda": "Africa", "Zambia": "Africa", "Zimbabwe": "Africa",
    # Asia
    "Afghanistan": "Asia", "Armenia": "Asia", "Azerbaijan": "Asia", "Bahrain": "Asia", "Bangladesh": "Asia",
    "Bhutan": "Asia", "Brunei": "Asia", "Cambodia": "Asia", "China": "Asia", "Georgia": "Asia", "India": "Asia",
    "Indonesia": "Asia", "Iran": "Asia", "Iraq": "Asia", "Israel": "Asia", "Japan": "Asia", "Jordan": "Asia",
    "Kazakhstan": "Asia", "Kuwait": "Asia", "Kyrgyzstan": "Asia", "Laos": "Asia", "Lebanon": "Asia",
    "Malaysia": "Asia", "Maldives": "Asia", "Mongolia": "Asia", "Myanmar": "Asia", "Nepal": "Asia",
    "Oman": "Asia", "Pakistan": "Asia", "Palestine": "Asia", "Philippines": "Asia", "Qatar": "Asia",
    "Saudi Arabia": "Asia", "Singapore": "Asia", "South Korea": "Asia", "Sri Lanka": "Asia", "Syria": "Asia",
    "Taiwan": "Asia", "Tajikistan": "Asia", "Thailand": "Asia", "Timor Leste": "Asia", "Turkey": "Asia",
    "Turkmenistan": "Asia", "United Arab Emirates": "Asia", "Uzbekistan": "Asia", "Vietnam": "Asia",
    # Oceania
    "Australia": "Oceania", "New Zealand": "Oceania", "Fiji": "Oceania", "Kiribati": "Oceania",
    "Marshall Islands": "Oceania", "Micronesia": "Oceania", "Palau": "Oceania", "Papua New Guinea": "Oceania",
    "Samoa": "Oceania", "Solomon Islands": "Oceania", "Tonga": "Oceania", "Vanuatu": "Oceania",
}

plt.rcParams.update(
    {
        "font.family": "Arial",
        "font.size": 12,
        "axes.titlesize": 15,
        "axes.labelsize": 13,
        "xtick.labelsize": 10,
        "ytick.labelsize": 10,
        "legend.fontsize": 10,
        "figure.facecolor": "none",
        "axes.facecolor": "none",
        "savefig.facecolor": "none",
        "savefig.edgecolor": "none",
    }
)


def phase_from_year(year: int) -> str | None:
    for phase, (start, end) in PHASES.items():
        if start <= year <= end:
            return phase
    return None


def transparent_axes(ax):
    ax.set_facecolor("none")
    ax.grid(False)
    for spine in ax.spines.values():
        spine.set_color("#444444")
        spine.set_linewidth(0.8)
    ax.tick_params(colors="#333333")


def save(fig, name: str):
    fig.patch.set_alpha(0)
    for ax in fig.axes:
        ax.set_facecolor("none")
    fig.savefig(OUTDIR / f"{name}.png", dpi=320, bbox_inches="tight", transparent=True)
    fig.savefig(OUTDIR / f"{name}.svg", bbox_inches="tight", transparent=True)
    plt.close(fig)


def growth_rate(series: pd.Series) -> float:
    s = series.sort_index()
    positive = s[s > 0]
    if len(positive) < 2:
        return np.nan
    start_year, end_year = positive.index[0], positive.index[-1]
    start_val, end_val = positive.iloc[0], positive.iloc[-1]
    periods = max(end_year - start_year, 1)
    return float((end_val / start_val) ** (1 / periods) - 1)


def gini(arr: pd.Series) -> float:
    x = np.asarray(arr.dropna(), dtype=float)
    x = x[x >= 0]
    if len(x) == 0:
        return np.nan
    if np.allclose(x.sum(), 0):
        return 0.0
    x = np.sort(x)
    n = len(x)
    idx = np.arange(1, n + 1)
    return float((2 * np.sum(idx * x) / (n * x.sum())) - (n + 1) / n)


def hhi(arr: pd.Series) -> float:
    x = np.asarray(arr.dropna(), dtype=float)
    if len(x) == 0:
        return np.nan
    total = x.sum()
    if np.isclose(total, 0):
        return 0.0
    s = x / total
    return float(np.sum(s ** 2))


def topk_share(arr: pd.Series, k: int) -> float:
    x = np.sort(np.asarray(arr.dropna(), dtype=float))[::-1]
    if len(x) == 0:
        return np.nan
    total = x.sum()
    if np.isclose(total, 0):
        return 0.0
    return float(x[:k].sum() / total)


def add_box(ax, text: str, xy=(0.01, 0.99), fontsize=10.5, ha="left", va="top"):
    ax.text(
        xy[0],
        xy[1],
        text,
        transform=ax.transAxes,
        ha=ha,
        va=va,
        fontsize=fontsize,
        fontname="Arial",
        bbox=dict(boxstyle="round,pad=0.35", fc=(1, 1, 1, 0.78), ec="#666666", lw=0.7),
    )


def load_geo_features():
    with open(WORLD_GEOJSON, "r", encoding="utf-8") as f:
        return json.load(f)["features"]


def geom_to_patches(geometry):
    patches = []
    gtype = geometry["type"]
    coords = geometry["coordinates"]
    if gtype == "Polygon":
        polys = [coords]
    elif gtype == "MultiPolygon":
        polys = coords
    else:
        return patches
    for poly in polys:
        if not poly:
            continue
        arr = np.asarray(poly[0])
        if arr.ndim == 2 and arr.shape[0] >= 3:
            patches.append(MplPolygon(arr, closed=True))
    return patches


def draw_map(ax, data_map: dict[str, float], title: str, cmap_name="Blues", vmin=None, vmax=None):
    features = load_geo_features()
    valid = [v for v in data_map.values() if pd.notna(v)]
    if vmin is None:
        vmin = min(valid) if valid else 0
    if vmax is None:
        vmax = max(valid) if valid else 1
    cmap = cm.get_cmap(cmap_name)
    norm = colors.Normalize(vmin=vmin, vmax=vmax)
    mapped = set()
    for feat in features:
        name = feat["properties"]["name"]
        patches = geom_to_patches(feat["geometry"])
        if not patches:
            continue
        value = data_map.get(name)
        face = cmap(norm(value)) if pd.notna(value) else (0.93, 0.93, 0.93, 1.0)
        pc = PatchCollection(patches, facecolor=face, edgecolor="white", linewidth=0.35)
        ax.add_collection(pc)
        if pd.notna(value):
            mapped.add(name)
    ax.autoscale_view()
    ax.axis("off")
    ax.set_title(title, fontsize=13.5, fontname="Arial")
    sm = cm.ScalarMappable(norm=norm, cmap=cmap)
    sm.set_array([])
    return mapped, sm


def main():
    df = pd.read_csv(DATA_CSV)
    df = df[df["Year"].between(1869, 2024)].copy()
    df["Phase"] = df["Year"].apply(phase_from_year)
    df["Impact"] = pd.to_numeric(df["Impact"], errors="coerce").fillna(0.0)
    df["Country"] = df["Country"].replace({"": np.nan}).fillna("Unknown")
    df["geo_name"] = df["Country"].replace(COUNTRY_MAP)
    df["region"] = df["Country"].map(REGION_MAP)
    country_only = df[~df["Country"].isin(["EU", "IGO", "Unknown"])].copy()

    # OADR
    oadr = pd.read_csv(OADR_CSV, usecols=["Location", "Time", "Value"])
    oadr["Time"] = pd.to_numeric(oadr["Time"], errors="coerce")
    oadr["Value"] = pd.to_numeric(oadr["Value"], errors="coerce")
    phase4_oadr = (
        oadr[oadr["Time"].between(1994, 2024)]
        .groupby("Location", as_index=False)["Value"]
        .mean()
        .rename(columns={"Location": "geo_name", "Value": "phase4_mean_oadr"})
    )

    # A/B trend statistics
    annual = df.groupby("Year", as_index=False).agg(count=("Overton id", "count"))
    annual = annual.sort_values("Year")
    country_phase_counts = (
        country_only.groupby("Phase")["Country"].nunique().rename("participating_countries")
    )

    trend_rows = []
    for phase, (start, end) in PHASES.items():
        phase_years = annual[(annual["Year"] >= start) & (annual["Year"] <= end)].set_index("Year")["count"]
        total = int(phase_years.sum())
        years_n = end - start + 1
        avg = total / years_n
        gr = growth_rate(phase_years)
        peak_year = int(phase_years.idxmax()) if not phase_years.empty else np.nan
        peak_count = int(phase_years.max()) if not phase_years.empty else np.nan
        trend_rows.append(
            {
                "phase": phase,
                "start_year": start,
                "end_year": end,
                "total_documents": total,
                "average_annual_count": avg,
                "annual_growth_rate_cagr": gr,
                "participating_countries": int(country_phase_counts.get(phase, 0)),
                "peak_year": peak_year,
                "peak_year_count": peak_count,
            }
        )
    trend_stats = pd.DataFrame(trend_rows)
    trend_stats["count_increase_from_previous_phase"] = trend_stats["total_documents"].diff()
    trend_stats["country_increase_from_previous_phase"] = trend_stats["participating_countries"].diff()
    p3 = float(trend_stats.loc[trend_stats["phase"] == "Phase 3", "annual_growth_rate_cagr"].iloc[0])
    p4 = float(trend_stats.loc[trend_stats["phase"] == "Phase 4", "annual_growth_rate_cagr"].iloc[0])
    trend_stats["phase4_to_phase3_growth_ratio"] = np.where(trend_stats["phase"] == "Phase 4", p4 / p3 if p3 and not np.isnan(p3) else np.nan, np.nan)

    peak_years = annual.nlargest(5, "count")[["Year", "count"]].sort_values("count", ascending=False).reset_index(drop=True)
    breakpoint_df = pd.DataFrame({"breakpoint_year": [1948, 1972, 1994], "interpretation": ["Phase 1→2", "Phase 2→3", "Phase 3→4"]})
    ab_sheet = pd.concat(
        [
            trend_stats.assign(section="phase_statistics"),
            peak_years.rename(columns={"Year": "year", "count": "value"}).assign(section="top5_peak_years"),
        ],
        ignore_index=True,
        sort=False,
    )

    # C yearly metrics
    yearly_country = country_only.groupby(["Year", "Country"], as_index=False).agg(count=("Overton id", "count"), impact=("Impact", "sum"))
    yearly_metrics = (
        yearly_country.groupby("Year")
        .apply(
            lambda g: pd.Series(
                {
                    "annual_document_count": g["count"].sum(),
                    "annual_policy_impact": g["impact"].sum(),
                    "annual_country_count": g["Country"].nunique(),
                    "annual_gini": gini(g["count"]),
                    "annual_top1_share": topk_share(g["count"], 1),
                    "annual_top10_share": topk_share(g["count"], 10),
                }
            )
        )
        .reset_index()
    )
    yearly_metrics["phase"] = yearly_metrics["Year"].apply(phase_from_year)

    phase_summary = (
        yearly_metrics.groupby("phase")
        .agg(
            total_count=("annual_document_count", "sum"),
            mean_annual_count=("annual_document_count", "mean"),
            total_impact=("annual_policy_impact", "sum"),
            mean_annual_impact=("annual_policy_impact", "mean"),
            participating_countries=("annual_country_count", "max"),
            mean_gini=("annual_gini", "mean"),
            mean_top10_share=("annual_top10_share", "mean"),
        )
        .reset_index()
        .rename(columns={"phase": "Phase"})
    )

    source_group = df["Country"].where(df["Country"].isin(["USA", "UK", "France", "EU", "IGO"]), "Other")
    df["source_group"] = source_group
    source_phase = (
        df.groupby(["Phase", "source_group"]).size().reset_index(name="count")
    )
    totals = source_phase.groupby("Phase")["count"].sum().rename("phase_total").reset_index()
    source_phase = source_phase.merge(totals, on="Phase", how="left")
    source_phase["share"] = source_phase["count"] / source_phase["phase_total"]
    source_year = (
        df[df["Year"] >= 1972]
        .groupby(["Year", "source_group"]).size().reset_index(name="count")
        .pivot(index="Year", columns="source_group", values="count")
        .fillna(0)
        .reset_index()
    )

    phase4_years = annual[annual["Year"].between(1994, 2024)].copy()
    phase4_cagr = growth_rate(phase4_years.set_index("Year")["count"])
    phase4_years["diff"] = phase4_years["count"].diff()
    phase4_years["accel"] = phase4_years["diff"].diff()
    largest_jump_row = phase4_years.loc[phase4_years["diff"].idxmax()]
    accel_years = phase4_years.nlargest(3, "accel")[["Year", "accel"]]
    slowdown_years = phase4_years.nsmallest(3, "accel")[["Year", "accel"]]

    # D-G phase maps data and region summaries
    phase_country = (
        country_only.groupby(["Phase", "Country", "geo_name"], as_index=False)
        .agg(count=("Overton id", "count"))
    )
    phase_country = phase_country.merge(phase4_oadr, on="geo_name", how="left")
    phase_country["region"] = phase_country["Country"].map(REGION_MAP)

    phase_country_top10 = (
        phase_country.sort_values(["Phase", "count"], ascending=[True, False])
        .groupby("Phase")
        .head(10)
        .copy()
    )
    phase_totals = phase_country.groupby("Phase")["count"].sum().rename("phase_total")
    phase_country_top10 = phase_country_top10.merge(phase_totals, on="Phase", how="left")
    phase_country_top10["share"] = phase_country_top10["count"] / phase_country_top10["phase_total"]

    phase_region_summary = (
        phase_country.dropna(subset=["region"])
        .groupby(["Phase", "region"])
        .agg(active_countries=("Country", "nunique"), document_count=("count", "sum"))
        .reset_index()
    )
    phase_region_summary["phase_total_docs"] = phase_region_summary.groupby("Phase")["document_count"].transform("sum")
    phase_region_summary["document_share"] = phase_region_summary["document_count"] / phase_region_summary["phase_total_docs"]

    phase_meta = []
    for phase in PHASES:
        sub = phase_country[phase_country["Phase"] == phase]
        active = int(sub["Country"].nunique())
        top10_share = float(topk_share(sub["count"], 10))
        mean_oadr = float(sub["phase4_mean_oadr"].mean()) if sub["phase4_mean_oadr"].notna().any() else np.nan
        top10_list = sub.sort_values("count", ascending=False).head(10)["Country"].tolist()
        phase_meta.append({"Phase": phase, "active_countries": active, "top10_share": top10_share, "mean_oadr_active_countries": mean_oadr, "top10_countries": ", ".join(top10_list)})
    phase_meta_df = pd.DataFrame(phase_meta)

    # H global synthesis (Phase 4)
    phase4_country = (
        country_only[country_only["Phase"] == "Phase 4"]
        .groupby(["Country", "geo_name"], as_index=False)
        .agg(Count=("Overton id", "count"), Impact=("Impact", "sum"))
    )
    phase4_country["Efficiency"] = np.where(phase4_country["Count"] > 0, phase4_country["Impact"] / phase4_country["Count"], np.nan)
    phase4_country = phase4_country.merge(phase4_oadr, on="geo_name", how="left")

    doc_v2 = pd.read_excel(INDEX_V2_XLSX, sheet_name="doc_index_final_v2")
    doc_v2 = doc_v2[(doc_v2["Has_matched_target"] == True) & (doc_v2["Phase"] == "Phase 4")].copy()
    idx_phase4 = (
        doc_v2.groupby("Source country", as_index=False)
        .agg(mean_ageing_energy_index_final_v2=("AgeingEnergy_SDG_Index_final_v2", "mean"))
        .rename(columns={"Source country": "Country"})
    )
    idx_phase4["geo_name"] = idx_phase4["Country"].replace(COUNTRY_MAP)
    phase4_country = phase4_country.merge(idx_phase4[["Country", "mean_ageing_energy_index_final_v2"]], on="Country", how="left")

    global_count_summary = phase4_country.sort_values("Count", ascending=False).copy()
    global_count_summary["count_share"] = global_count_summary["Count"] / global_count_summary["Count"].sum()
    count_summary_stats = {
        "top10_combined_share": topk_share(global_count_summary["Count"], 10),
        "count_gini": gini(global_count_summary["Count"]),
        "count_hhi": hhi(global_count_summary["Count"]),
    }
    global_impact_summary = phase4_country.sort_values("Impact", ascending=False).copy()
    global_impact_summary["impact_share"] = global_impact_summary["Impact"] / global_impact_summary["Impact"].sum()
    impact_summary_stats = {
        "top10_combined_share": topk_share(global_impact_summary["Impact"], 10),
        "impact_gini": gini(global_impact_summary["Impact"]),
        "impact_hhi": hhi(global_impact_summary["Impact"]),
    }
    oadr_summary = phase4_country[["Country", "phase4_mean_oadr", "Count", "Impact", "mean_ageing_energy_index_final_v2"]].copy()
    oadr_summary = oadr_summary.dropna(subset=["phase4_mean_oadr"])
    oadr_summary = oadr_summary.sort_values("phase4_mean_oadr", ascending=False)
    corrs = {
        "corr_oadr_count": oadr_summary["phase4_mean_oadr"].corr(oadr_summary["Count"]),
        "corr_oadr_impact": oadr_summary["phase4_mean_oadr"].corr(oadr_summary["Impact"]),
        "corr_oadr_index": oadr_summary["phase4_mean_oadr"].corr(oadr_summary["mean_ageing_energy_index_final_v2"]),
    }

    q_count_hi = phase4_country["Count"].quantile(0.75)
    q_count_lo = phase4_country["Count"].quantile(0.25)
    q_imp_hi = phase4_country["Impact"].quantile(0.75)
    q_imp_lo = phase4_country["Impact"].quantile(0.25)
    q_oadr_hi = phase4_country["phase4_mean_oadr"].quantile(0.75)
    q_idx_hi = phase4_country["mean_ageing_energy_index_final_v2"].quantile(0.75)
    q_idx_lo = phase4_country["mean_ageing_energy_index_final_v2"].quantile(0.25)
    flags = []
    for _, row in phase4_country.iterrows():
        labels = []
        if row["Count"] >= q_count_hi and row["Impact"] <= q_imp_lo:
            labels.append("High count / low impact")
        if row["Impact"] >= q_imp_hi and row["Count"] <= q_count_lo:
            labels.append("High impact / low count")
        if pd.notna(row["phase4_mean_oadr"]) and row["phase4_mean_oadr"] >= q_oadr_hi and row["Count"] <= q_count_lo:
            labels.append("High OADR / low attention")
        if pd.notna(row["phase4_mean_oadr"]) and row["phase4_mean_oadr"] >= q_oadr_hi and row["Count"] >= q_count_hi:
            labels.append("High OADR / high attention")
        flags.append("|".join(labels))
    phase4_country["crosspanel_flags"] = flags
    crosspanel_flags = phase4_country[phase4_country["crosspanel_flags"] != ""].copy()

    # A/B figures
    fig = plt.figure(figsize=(15, 5.6))
    gs = GridSpec(1, 2, figure=fig, width_ratios=[1.2, 1.0])
    ax1 = fig.add_subplot(gs[0, 0])
    ax2 = fig.add_subplot(gs[0, 1])

    ax1.plot(annual["Year"], annual["count"], color="#376795", lw=2.0)
    for phase, (start, end) in PHASES.items():
        ax1.axvspan(start, end, color=PHASE_COLORS[phase], alpha=0.08)
    transparent_axes(ax1)
    ax1.set_title("A) Long-term annual count trend, 1869–2024")
    ax1.set_xlabel("Year")
    ax1.set_ylabel("Annual document count")
    text_a = "\n".join(
        [
            f"{r.phase}: total {int(r.total_documents):,}, avg/yr {r.average_annual_count:,.1f}, CAGR {r.annual_growth_rate_cagr*100 if pd.notna(r.annual_growth_rate_cagr) else np.nan:.2f}%"
            for r in trend_stats.itertuples()
        ]
        + [
            f"Breakpoints: 1948, 1972, 1994",
            f"Top peaks: " + ", ".join(f"{int(y)} ({int(c):,})" for y, c in peak_years.values),
        ]
    )
    add_box(ax1, text_a, fontsize=9.5)

    post94 = annual[annual["Year"] >= 1994].copy()
    ax2.plot(post94["Year"], post94["count"], color="#b44b3a", lw=2.0)
    transparent_axes(ax2)
    ax2.set_title("B) Post-1994 annual count trend")
    ax2.set_xlabel("Year")
    ax2.set_ylabel("Annual document count")
    text_b = "\n".join(
        [
            f"Phase 3 CAGR: {p3*100:.2f}%",
            f"Phase 4 CAGR: {p4*100:.2f}%",
            f"P4/P3 growth ratio: {(p4/p3):.2f}",
            f"Phase 4 countries: {int(trend_stats.loc[trend_stats['phase']=='Phase 4','participating_countries'].iloc[0])}",
            f"Largest jump: {int(largest_jump_row['Year'])} (+{int(largest_jump_row['diff']):,})",
        ]
    )
    add_box(ax2, text_b, fontsize=10)
    save(fig, "figure1_panels_ab_quantitative")

    # C figure
    fig = plt.figure(figsize=(15, 7.2))
    gs = GridSpec(2, 1, height_ratios=[1.05, 1.0], hspace=0.12, figure=fig)
    ax_top = fig.add_subplot(gs[0, 0])
    ax_bot = fig.add_subplot(gs[1, 0], sharex=ax_top)

    ax_top.plot(yearly_metrics["Year"], yearly_metrics["annual_document_count"], color="#333333", lw=1.8, label="Annual count")
    ax_top2 = ax_top.twinx()
    ax_top2.plot(yearly_metrics["Year"], yearly_metrics["annual_gini"], color="#d04f4f", lw=1.7, label="Country-level Gini")
    transparent_axes(ax_top)
    ax_top2.set_facecolor("none")
    ax_top2.grid(False)
    ax_top.set_title("C) Transition, rapid expansion, and concentration dynamics")
    ax_top.set_ylabel("Document count")
    ax_top2.set_ylabel("Country-level Gini")
    for yr, label in [(1982, "Vienna Plan of Action on Ageing"), (1991, "UN Principles for Older Persons"), (2002, "Madrid Plan of Action on Ageing"), (2015, "SDGs"), (2021, "UN Decade of Healthy Ageing")]:
        ax_top.axvline(yr, color="#888888", lw=0.8, ls="--")
        ax_top.text(yr + 0.3, ax_top.get_ylim()[1] * 0.92, label, fontsize=9, rotation=0, va="top")
    phase_box = "\n".join(
        [
            f"{r.Phase}: total {int(r.total_count):,}, impact {int(r.total_impact):,}, countries {int(r.participating_countries)}, mean Gini {r.mean_gini:.3f}, mean Top10 {r.mean_top10_share:.3f}"
            for r in phase_summary.itertuples()
        ]
    )
    add_box(ax_top, phase_box, xy=(0.01, 0.03), va="bottom", fontsize=9.3)

    year_comp = source_year.copy()
    bottoms = np.zeros(len(year_comp))
    for group in ["USA", "UK", "France", "EU", "IGO", "Other"]:
        vals = year_comp.get(group, pd.Series(0, index=year_comp.index)).to_numpy()
        ax_bot.bar(year_comp["Year"], vals, bottom=bottoms, color=SOURCE_COLORS[group], width=0.85, label=group)
        bottoms += vals
    transparent_axes(ax_bot)
    ax_bot.set_xlabel("Year")
    ax_bot.set_ylabel("Count by source group")
    ax_bot.legend(frameon=False, ncol=6, loc="upper left", bbox_to_anchor=(0, 1.03))
    c_box = "\n".join(
        [
            f"Post-1994 CAGR: {phase4_cagr*100:.2f}%",
            f"Avg annual increase: {phase4_years['diff'].mean():.1f}",
            f"Largest one-year jump: {int(largest_jump_row['Year'])} (+{int(largest_jump_row['diff']):,})",
            "Acceleration: " + ", ".join(f"{int(y)} ({a:+.0f})" for y, a in accel_years.values),
            "Slowdown: " + ", ".join(f"{int(y)} ({a:+.0f})" for y, a in slowdown_years.values),
        ]
    )
    add_box(ax_bot, c_box, xy=(0.68, 0.98), fontsize=9.3)
    save(fig, "figure1_panel_c_quantitative")

    # D-G maps composite
    fig = plt.figure(figsize=(16, 7.2))
    gs = GridSpec(2, 4, height_ratios=[1.0, 0.52], hspace=0.02, wspace=0.06, figure=fig)
    map_axes = [fig.add_subplot(gs[0, i]) for i in range(4)]
    table_axes = [fig.add_subplot(gs[1, i]) for i in range(4)]
    phase_map_stats = []
    for i, phase in enumerate(PHASES):
        ax = map_axes[i]
        t_ax = table_axes[i]
        sub = phase_country[phase_country["Phase"] == phase]
        data_map = dict(zip(sub["geo_name"], sub["count"]))
        mapped, sm = draw_map(ax, data_map, f"{chr(68+i)}) {phase}\n{PHASES[phase][0]}–{PHASES[phase][1]}", cmap_name="Blues")
        cb = fig.colorbar(sm, ax=ax, fraction=0.034, pad=0.01)
        cb.ax.tick_params(labelsize=8)
        meta = phase_meta_df[phase_meta_df["Phase"] == phase].iloc[0]
        top10 = phase_country_top10[phase_country_top10["Phase"] == phase].head(3)
        side = [
            f"Active countries: {int(meta.active_countries)}",
            f"Top10 share: {meta.top10_share:.2f}",
            f"Mean OADR: {meta.mean_oadr_active_countries:.2f}" if pd.notna(meta.mean_oadr_active_countries) else "Mean OADR: n/a",
            "Top countries: " + ", ".join(top10["Country"].tolist()),
        ]
        reg = phase_region_summary[phase_region_summary["Phase"] == phase]
        for _, r in reg.iterrows():
            side.append(f"{r.region}: {int(r.active_countries)} ctry, {r.document_share:.2f} share")
        t_ax.axis("off")
        add_box(t_ax, "\n".join(side), xy=(0.02, 0.98), fontsize=9.0)
        phase_map_stats.append({"Phase": phase, "mapped_countries": len(mapped)})
    save(fig, "figure1_panels_dg_quantitative")

    # H figure
    fig = plt.figure(figsize=(16, 8.8))
    gs = GridSpec(2, 3, width_ratios=[1.55, 1.0, 1.0], height_ratios=[1.0, 1.0], wspace=0.14, hspace=0.18, figure=fig)
    ax_map = fig.add_subplot(gs[:, 0])
    ax_imp = fig.add_subplot(gs[0, 1])
    ax_oadr = fig.add_subplot(gs[1, 1])
    ax_stats = fig.add_subplot(gs[:, 2])

    count_map = dict(zip(phase4_country["geo_name"], phase4_country["Count"]))
    mapped, sm = draw_map(ax_map, count_map, "H) Global synthesis: Phase 4 count distribution", cmap_name="Blues")
    cb = fig.colorbar(sm, ax=ax_map, fraction=0.03, pad=0.01)
    cb.ax.tick_params(labelsize=9)

    imp_map = dict(zip(phase4_country["geo_name"], phase4_country["Impact"]))
    _, sm_imp = draw_map(ax_imp, imp_map, "Impact", cmap_name="OrRd")
    fig.colorbar(sm_imp, ax=ax_imp, fraction=0.05, pad=0.01)
    oadr_map = dict(zip(phase4_country["geo_name"], phase4_country["phase4_mean_oadr"]))
    _, sm_o = draw_map(ax_oadr, oadr_map, "OADR", cmap_name="YlOrBr")
    fig.colorbar(sm_o, ax=ax_oadr, fraction=0.05, pad=0.01)

    ax_stats.axis("off")
    top10_count = global_count_summary.head(10)
    top10_impact = global_impact_summary.head(10)
    h_text = "\n".join(
        [
            f"Count top10 share: {count_summary_stats['top10_combined_share']:.2f}",
            f"Count Gini/HHI: {count_summary_stats['count_gini']:.3f} / {count_summary_stats['count_hhi']:.3f}",
            "Top counts: " + ", ".join(f"{r.Country} ({int(r.Count):,})" for r in top10_count.head(5).itertuples()),
            "",
            f"Impact top10 share: {impact_summary_stats['top10_combined_share']:.2f}",
            f"Impact Gini/HHI: {impact_summary_stats['impact_gini']:.3f} / {impact_summary_stats['impact_hhi']:.3f}",
            "Top impacts: " + ", ".join(f"{r.Country} ({int(r.Impact):,})" for r in top10_impact.head(5).itertuples()),
            "",
            f"Mean OADR: {oadr_summary['phase4_mean_oadr'].mean():.2f}",
            f"Corr(OADR, count): {corrs['corr_oadr_count']:.3f}",
            f"Corr(OADR, impact): {corrs['corr_oadr_impact']:.3f}",
            f"Corr(OADR, index): {corrs['corr_oadr_index']:.3f}",
            "",
            "High OADR/low attention: " + ", ".join(crosspanel_flags[crosspanel_flags["crosspanel_flags"].str.contains("High OADR / low attention")]["Country"].head(6).tolist()),
        ]
    )
    add_box(ax_stats, h_text, xy=(0.02, 0.98), fontsize=10.0)
    save(fig, "figure1_panel_h_quantitative")

    # Workbooks
    h_global_count_summary = global_count_summary.copy()
    for k, v in count_summary_stats.items():
        h_global_count_summary[k] = v
    h_global_impact_summary = global_impact_summary.copy()
    for k, v in impact_summary_stats.items():
        h_global_impact_summary[k] = v
    h_global_oadr_summary = oadr_summary.copy()
    for k, v in corrs.items():
        h_global_oadr_summary[k] = v

    with pd.ExcelWriter(WORKBOOK, engine="openpyxl") as writer:
        ab_sheet.to_excel(writer, sheet_name="A_B_trend_statistics", index=False)
        yearly_metrics.to_excel(writer, sheet_name="C_yearly_metrics", index=False)
        phase_summary.to_excel(writer, sheet_name="C_phase_summary", index=False)
        source_phase.to_excel(writer, sheet_name="C_source_composition", index=False)
        phase_country_top10.to_excel(writer, sheet_name="phase_country_top10", index=False)
        phase_region_summary.to_excel(writer, sheet_name="phase_region_summary", index=False)
        h_global_count_summary.to_excel(writer, sheet_name="H_global_count_summary", index=False)
        h_global_impact_summary.to_excel(writer, sheet_name="H_global_impact_summary", index=False)
        h_global_oadr_summary.to_excel(writer, sheet_name="H_global_oadr_summary", index=False)
        crosspanel_flags.to_excel(writer, sheet_name="H_crosspanel_country_flags", index=False)

    # Interpretation text
    eu_compare_text = ""
    eu_path = ROOT / "eu_vs_member_states_summary.txt"
    if eu_path.exists():
        eu_compare_text = eu_path.read_text(encoding="utf-8").strip()
    phase_lines = []
    for row in phase_summary.itertuples():
        phase_lines.append(
            f"{row.Phase}: {int(row.total_count):,} documents, {int(row.participating_countries)} active countries, mean Gini {row.mean_gini:.3f}. "
            f"This phase {'marks broad diffusion with persistent concentration' if row.Phase=='Phase 4' else 'reflects a smaller and more concentrated policy system'}."
        )
    interp_text = "\n\n".join(
        [
            "Figure 1 quantitative interpretation",
            "Panel A–B: Policy production expanded from low and fragmented levels before 1994 into a rapid growth regime after 1994. "
            f"Phase 4 contains {int(trend_stats.loc[trend_stats['phase']=='Phase 4','total_documents'].iloc[0]):,} documents with an average of "
            f"{trend_stats.loc[trend_stats['phase']=='Phase 4','average_annual_count'].iloc[0]:.1f} per year. "
            f"The five peak years are {', '.join(f'{int(y)} ({int(c):,})' for y, c in peak_years.values)}.",
            "Panel C: The post-1994 period shows a CAGR of "
            f"{phase4_cagr*100:.2f}% with the largest one-year jump in {int(largest_jump_row['Year'])} (+{int(largest_jump_row['diff']):,}). "
            "Output expanded rapidly while source composition remained structured around a limited set of major actors, especially USA, UK, EU, and IGO.",
            "Panels D–G: Spatial coverage widened sharply by Phase 4, but regional participation remained uneven. "
            "Earlier phases were sparse, while Phase 4 combined high country participation with strong regional asymmetry.",
            "Panel H: In Phase 4, policy production diffused more broadly than policy influence. "
            f"Count top-10 share is {count_summary_stats['top10_combined_share']:.2f}, whereas impact top-10 share is {impact_summary_stats['top10_combined_share']:.2f}. "
            f"Count Gini/HHI = {count_summary_stats['count_gini']:.3f}/{count_summary_stats['count_hhi']:.3f}; impact Gini/HHI = {impact_summary_stats['impact_gini']:.3f}/{impact_summary_stats['impact_hhi']:.3f}.",
            "Demographic mismatch: high-ageing countries with relatively weak policy attention include "
            + ", ".join(crosspanel_flags[crosspanel_flags["crosspanel_flags"].str.contains("High OADR / low attention")]["Country"].head(10).tolist())
            + ".",
            "EU / supranational explanation: " + eu_compare_text if eu_compare_text else "EU / supranational explanation: no external comparison text found.",
            "Suggested Results wording: Policy production expanded substantially after 1994 and diffused across a much wider set of countries, but influence remained more concentrated than output. "
            "High-ageing countries were not uniformly the most visible policy producers, indicating a persistent demographic-policy mismatch even in the mature phase of expansion.",
        ]
        + phase_lines
    )
    INTERP.write_text(interp_text, encoding="utf-8")

    # top 10 findings
    findings = [
        f"Phase 4 total documents: {int(trend_stats.loc[trend_stats['phase']=='Phase 4','total_documents'].iloc[0]):,}",
        f"Phase 4 average annual count: {trend_stats.loc[trend_stats['phase']=='Phase 4','average_annual_count'].iloc[0]:.1f}",
        f"Phase 4 CAGR: {phase4_cagr*100:.2f}%",
        f"Phase 4 participating countries: {int(trend_stats.loc[trend_stats['phase']=='Phase 4','participating_countries'].iloc[0])}",
        f"Largest post-1994 one-year jump: {int(largest_jump_row['Year'])} (+{int(largest_jump_row['diff']):,})",
        f"Phase 4 count top-10 share: {count_summary_stats['top10_combined_share']:.3f}",
        f"Phase 4 impact top-10 share: {impact_summary_stats['top10_combined_share']:.3f}",
        f"Phase 4 count Gini: {count_summary_stats['count_gini']:.3f}",
        f"Phase 4 impact Gini: {impact_summary_stats['impact_gini']:.3f}",
        f"Corr(OADR, ageing-energy index): {corrs['corr_oadr_index']:.3f}",
    ]

    print("OUTPUT_FILES")
    print(WORKBOOK)
    print(INTERP)
    for p in sorted(OUTDIR.glob("*")):
        print(p)
    print("SHEET_NAMES")
    for s in [
        "A_B_trend_statistics",
        "C_yearly_metrics",
        "C_phase_summary",
        "C_source_composition",
        "phase_country_top10",
        "phase_region_summary",
        "H_global_count_summary",
        "H_global_impact_summary",
        "H_global_oadr_summary",
        "H_crosspanel_country_flags",
    ]:
        print(s)
    print("TOP10_FINDINGS")
    for item in findings:
        print(f"- {item}")


if __name__ == "__main__":
    main()
