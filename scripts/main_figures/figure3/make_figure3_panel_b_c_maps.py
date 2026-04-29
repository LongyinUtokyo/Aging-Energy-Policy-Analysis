from pathlib import Path
import zipfile

import matplotlib.pyplot as plt
from matplotlib.collections import PatchCollection
from matplotlib.colors import LinearSegmentedColormap, ListedColormap, Normalize
from matplotlib.cm import ScalarMappable
from matplotlib.patches import Patch, Polygon
import pandas as pd
import pyproj
import shapefile


ROOT = Path("/Users/longlab/Desktop/Aging Energy/working_project/07_figures_working/current_manuscript_figures/figure3_sdg_diffusion_inequality")
PANEL_B = ROOT / "panel_b_ageing_energy_index_map"
PANEL_C = ROOT / "panel_c_ageing_alignment_quadrants"

WORLD_ZIP = Path("/Users/longlab/Desktop/DietaryG/organized_pdf_json/step17_basemap_upgrade/basemaps/ne_110m_admin_0_countries.zip")
WORLD_DIR = Path("/tmp/ne_110m_admin_0_countries")

NO_DATA = "#D9D9D9"
EDGE = "white"
LINE_COLOR = "#555555"

INDEX_CMAP = LinearSegmentedColormap.from_list(
    "soft_teal_index",
    ["#EEF6F4", "#BFDCD9", "#73AAA6", "#1F6F78"],
)
INDEX_NORM = Normalize(vmin=0.0, vmax=0.85, clip=True)
INDEX_LINE_COLOR = "#1F6F78"
INDEX_LIGHT_COLOR = "#7FB8B3"
INEQUALITY_ALT_COLOR = "#D8A24A"

QUADRANT_COLORS = {
    "High ageing / High index": "#7FAAD4",
    "High ageing / Low index": "#D9867C",
    "Low ageing / High index": "#8FBF8A",
    "Low ageing / Low index": "#E3B862",
}

COUNTRY_LABELS = {
    "USA": {"lonlat": (-98, 39), "label_lonlat": (-82, 43), "ha": "left"},
    "Germany": {"lonlat": (10.5, 51), "label_lonlat": (21, 54), "ha": "left"},
    "Italy": {"lonlat": (12.5, 42.5), "label_lonlat": (22, 43), "ha": "left"},
    "China": {"lonlat": (104, 35), "label_lonlat": (124, 44), "ha": "left"},
    "Japan": {"lonlat": (139, 36), "label_lonlat": (148, 34), "ha": "left"},
}

NAME_FIX = {
    "United States of America": "USA",
    "United States": "USA",
    "United Kingdom": "UK",
    "Bosnia and Herz.": "Bosnia and Herzegovina",
    "Côte d'Ivoire": "Ivory Coast",
    "Czechia": "Czech Republic",
    "Dem. Rep. Congo": "Democratic Republic of the Congo",
    "Congo": "Republic of the Congo",
    "Dominican Rep.": "Dominican Republic",
    "Eq. Guinea": "Equatorial Guinea",
    "eSwatini": "Swaziland",
    "Kyrgyz Republic": "Kyrgyzstan",
    "Lao PDR": "Laos",
    "North Macedonia": "Macedonia",
    "Palestine": "Palestinian Territory",
    "S. Sudan": "South Sudan",
    "Solomon Is.": "Solomon Islands",
    "Timor-Leste": "East Timor",
    "Trinidad and Tobago": "Trinidad & Tobago",
}


def ensure_world():
    WORLD_DIR.mkdir(parents=True, exist_ok=True)
    if not any(WORLD_DIR.glob("*.shp")):
        with zipfile.ZipFile(WORLD_ZIP) as z:
            z.extractall(WORLD_DIR)
    return next(WORLD_DIR.glob("*.shp"))


def project_points(lons, lats):
    transformer = pyproj.Transformer.from_crs("EPSG:4326", "+proj=robin", always_xy=True)
    return transformer.transform(lons, lats)


def projected_polygon(points):
    lons = [p[0] for p in points]
    lats = [p[1] for p in points]
    xs, ys = project_points(lons, lats)
    return list(zip(xs, ys))


def country_name(record, fields):
    values = dict(zip(fields, record))
    name = values.get("NAME") or values.get("ADMIN") or values.get("SOVEREIGNT")
    return NAME_FIX.get(name, name)


def base_world_colors(value_by_country, color_func):
    shp_path = ensure_world()
    reader = shapefile.Reader(str(shp_path), encoding="latin1")
    fields = [f[0] for f in reader.fields[1:]]
    patches, colors = [], []
    for shape, rec in zip(reader.shapes(), reader.records()):
        name = country_name(rec, fields)
        if name == "Antarctica":
            continue
        parts = list(shape.parts) + [len(shape.points)]
        for start, end in zip(parts[:-1], parts[1:]):
            pts = shape.points[start:end]
            if len(pts) < 3:
                continue
            patches.append(Polygon(projected_polygon(pts), closed=True))
            colors.append(color_func(value_by_country.get(name)))
    return patches, colors


def setup_map(figsize=(13.6, 6.0)):
    fig, ax = plt.subplots(figsize=figsize, dpi=300)
    fig.patch.set_alpha(0)
    ax.set_facecolor("none")
    ax.set_aspect("equal")
    ax.set_xlim(-17_200_000, 17_200_000)
    ax.set_ylim(-6_000_000, 8_700_000)
    ax.axis("off")
    return fig, ax


def add_country_labels(ax, include_sweden=False, values=None):
    labels = COUNTRY_LABELS.copy()
    if include_sweden:
        labels["Sweden"] = {"lonlat": (16, 62), "label_lonlat": (30, 65), "ha": "left"}
    for country, spec in labels.items():
        x, y = project_points([spec["lonlat"][0]], [spec["lonlat"][1]])
        lx, ly = project_points([spec["label_lonlat"][0]], [spec["label_lonlat"][1]])
        x, y, lx, ly = x[0], y[0], lx[0], ly[0]
        ax.scatter([x], [y], s=32, color="black", edgecolor="white", linewidth=0.7, zorder=5)
        ax.plot([x, lx], [y, ly], color=LINE_COLOR, lw=1.0, zorder=4)
        if values and country in values and pd.notna(values[country]):
            ax.text(
                lx,
                ly + 280_000,
                country,
                fontsize=18,
                fontweight="bold",
                ha=spec["ha"],
                va="center",
                color="#111111",
                bbox=dict(facecolor="white", edgecolor="none", alpha=0.88, pad=1.2),
                zorder=6,
            )
            ax.text(
                lx,
                ly - 620_000,
                f"{values[country]:.2f}",
                fontsize=11,
                fontweight="normal",
                ha=spec["ha"],
                va="center",
                color="#111111",
                bbox=dict(facecolor="white", edgecolor="none", alpha=0.88, pad=0.8),
                zorder=6,
            )
        else:
            ax.text(
                lx,
                ly,
                country,
                fontsize=18,
                fontweight="bold",
                ha=spec["ha"],
                va="center",
                color="#111111",
                bbox=dict(facecolor="white", edgecolor="none", alpha=0.88, pad=1.6),
                zorder=6,
            )


def save(fig, path):
    fig.savefig(path, transparent=True, bbox_inches="tight", pad_inches=0.02)
    plt.close(fig)
    print(path)


def draw_panel_b_map():
    df = pd.read_csv(PANEL_B / "figure3_panel_b_country_mean_ageing_energy_index_map_data.csv")
    values = dict(zip(df["country"], df["mean_ageing_energy_index"]))
    patches, colors = base_world_colors(values, lambda v: INDEX_CMAP(INDEX_NORM(v)) if v is not None and pd.notna(v) else NO_DATA)
    fig, ax = setup_map()
    ax.add_collection(PatchCollection(patches, facecolor=colors, edgecolor=EDGE, linewidths=0.35, zorder=1))
    add_country_labels(ax, values=values)
    save(fig, PANEL_B / "figure3_panel_b_mean_ageing_energy_index_map.png")


def draw_panel_b_colorbar():
    fig, ax = plt.subplots(figsize=(3.2, 0.42), dpi=300)
    fig.patch.set_alpha(0)
    sm = ScalarMappable(norm=INDEX_NORM, cmap=INDEX_CMAP)
    cb = fig.colorbar(sm, cax=ax, orientation="horizontal")
    cb.set_ticks([0.0, 0.4, 0.85])
    cb.set_ticklabels(["0", "0.4", "0.85"])
    cb.outline.set_visible(False)
    cb.ax.tick_params(labelsize=12, length=0, pad=2)
    fig.savefig(PANEL_B / "figure3_panel_b_mean_ageing_energy_index_colorbar.png", transparent=True, bbox_inches="tight", pad_inches=0.02)
    plt.close(fig)


def draw_panel_b_smallplots():
    idx = pd.read_csv(PANEL_B / "figure3_panel_b_global_mean_index_timeseries.csv")
    ineq = pd.read_csv(PANEL_B / "figure3_panel_b_inequality_timeseries.csv")
    phase = pd.read_csv(PANEL_B / "figure3_panel_b_phase_inequality_summary.csv")

    fig, ax = plt.subplots(figsize=(3.2, 1.9), dpi=300)
    fig.patch.set_alpha(0)
    ax.plot(idx["year"], idx["global_mean_index"], color=INDEX_LINE_COLOR, lw=2.2)
    ax.axvline(1993, color="#999999", lw=1.1, ls="--")
    ax.set_ylabel("Mean index", fontsize=10)
    ax.tick_params(labelsize=8, width=0.8, length=3)
    ax.spines[["top", "right"]].set_visible(False)
    ax.grid(False)
    save(fig, PANEL_B / "figure3_panel_b_global_mean_index_timeseries.png")

    fig, ax = plt.subplots(figsize=(3.2, 1.9), dpi=300)
    fig.patch.set_alpha(0)
    ax.plot(ineq["year"], ineq["gini"], color=INEQUALITY_ALT_COLOR, lw=2.0, label="Gini")
    ax.plot(ineq["year"], ineq["hhi"], color=INDEX_LINE_COLOR, lw=2.0, label="HHI")
    ax.axvline(1993, color="#999999", lw=1.1, ls="--")
    ax.set_ylabel("Value", fontsize=10)
    ax.tick_params(labelsize=8, width=0.8, length=3)
    ax.spines[["top", "right"]].set_visible(False)
    ax.legend(frameon=False, fontsize=8, loc="upper right")
    ax.grid(False)
    save(fig, PANEL_B / "figure3_panel_b_inequality_timeseries.png")

    long = phase.melt(id_vars="phase", value_vars=["gini", "hhi"], var_name="metric", value_name="value")
    colors = {"gini": "#E1B66A", "hhi": INDEX_LIGHT_COLOR}
    fig, ax = plt.subplots(figsize=(1.7, 1.5), dpi=300)
    fig.patch.set_alpha(0)
    xpos = {"Phase 3": 0, "Phase 4": 1}
    offset = {"gini": -0.18, "hhi": 0.18}
    for row in long.itertuples(index=False):
        ax.bar(xpos[row.phase] + offset[row.metric], row.value, width=0.34, color=colors[row.metric])
    ax.set_xticks([0, 1])
    ax.set_xticklabels(["P3", "P4"], fontsize=8)
    ax.tick_params(axis="y", labelsize=8, width=0.8, length=3)
    ax.spines[["top", "right"]].set_visible(False)
    ax.grid(False)
    save(fig, PANEL_B / "figure3_panel_b_phase_inequality_bars.png")


def draw_panel_c_map():
    df = pd.read_csv(PANEL_C / "figure3_panel_c_country_quadrant_map_data.csv")
    values = dict(zip(df["country"], df["quadrant"]))
    patches, colors = base_world_colors(values, lambda v: QUADRANT_COLORS.get(v, NO_DATA))
    fig, ax = setup_map()
    ax.add_collection(PatchCollection(patches, facecolor=colors, edgecolor=EDGE, linewidths=0.35, zorder=1))
    add_country_labels(ax, include_sweden=True)
    save(fig, PANEL_C / "figure3_panel_c_oadr_index_quadrant_map.png")


def draw_panel_c_legend():
    handles = [Patch(facecolor=color, edgecolor="none", label=label) for label, color in QUADRANT_COLORS.items()]
    handles.append(Patch(facecolor=NO_DATA, edgecolor="none", label="No data"))
    fig, ax = plt.subplots(figsize=(8.8, 0.7), dpi=300)
    fig.patch.set_alpha(0)
    ax.axis("off")
    ax.legend(handles=handles, loc="center", ncol=5, frameon=False, fontsize=11, handlelength=1.5, columnspacing=1.3)
    save(fig, PANEL_C / "figure3_panel_c_quadrant_legend.png")


def draw_panel_c_smallplots():
    scatter = pd.read_csv(PANEL_C / "figure3_panel_c_oadr_index_scatter_data.csv")
    counts_path = PANEL_C / "figure3_panel_c_quadrant_actor_counts.csv"
    counts = pd.read_csv(counts_path) if counts_path.exists() else pd.DataFrame()

    actor_colors = {
        "Developed countries": "#4D4D4D",
        "Developing countries": "#F2A65A",
        "Organizations": "#8FBF8A",
        "Organization": "#8FBF8A",
    }
    fig, ax = plt.subplots(figsize=(3.0, 2.25), dpi=300)
    fig.patch.set_alpha(0)
    for actor, sub in scatter.groupby("actor_type"):
        ax.scatter(
            sub["mean_old_age_dependency_ratio"],
            sub["mean_ageing_energy_index"],
            s=18,
            color=actor_colors.get(actor, "#777777"),
            alpha=0.72,
            edgecolor="white",
            linewidth=0.3,
            label=actor.replace(" countries", ""),
        )
    ax.axvline(20, color="#A0A0A0", lw=1.0, ls="--")
    ax.axhline(0.55, color="#A0A0A0", lw=1.0, ls="--")
    ax.set_xlabel("Mean OADR", fontsize=10)
    ax.set_ylabel("Mean index", fontsize=10)
    ax.tick_params(labelsize=8, width=0.8, length=3)
    ax.spines[["top", "right"]].set_visible(False)
    ax.legend(frameon=False, fontsize=7.5, loc="lower right", markerscale=1.3)
    ax.grid(False)
    save(fig, PANEL_C / "figure3_panel_c_oadr_index_scatter.png")

    if not counts.empty:
        pivot = counts.pivot_table(index="quadrant_plot", columns="actor_type", values="n", fill_value=0)
        pivot.to_csv(PANEL_C / "figure3_panel_c_quadrant_actor_counts_wide.csv")
        fig, ax = plt.subplots(figsize=(4.2, 1.8), dpi=300)
        fig.patch.set_alpha(0)
        ax.axis("off")
        y = 0.92
        for quadrant, row in pivot.iterrows():
            color = QUADRANT_COLORS.get(quadrant, "#333333")
            ax.text(0.0, y, quadrant, color=color, fontsize=10, fontweight="bold", ha="left", va="top")
            line = "  ".join([f"{col.replace(' countries','')}: {int(val)}" for col, val in row.items() if int(val) > 0])
            ax.text(0.0, y - 0.12, line, color=color, fontsize=9, ha="left", va="top")
            y -= 0.24
        save(fig, PANEL_C / "figure3_panel_c_quadrant_actor_counts_text.png")


def main():
    draw_panel_b_map()
    draw_panel_b_colorbar()
    draw_panel_b_smallplots()
    draw_panel_c_map()
    draw_panel_c_legend()
    draw_panel_c_smallplots()


if __name__ == "__main__":
    main()
