from pathlib import Path
import zipfile

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.collections import PatchCollection
from matplotlib.colors import Normalize
from matplotlib.cm import ScalarMappable
from matplotlib.patches import Circle, Patch, Polygon, Wedge
import pandas as pd
import pyproj
import shapefile


FIG4_ROOT = Path("/Users/longlab/Desktop/Aging Energy/working_project/07_figures_working/current_manuscript_figures/figure4_policy_blind_spots")
PANEL_D = FIG4_ROOT / "panel_d_blind_spot_map"
LEGEND_DIR = FIG4_ROOT / "legends"
LEGEND_DIR.mkdir(parents=True, exist_ok=True)

WORLD_ZIP = Path("/Users/longlab/Desktop/DietaryG/organized_pdf_json/step17_basemap_upgrade/basemaps/ne_110m_admin_0_countries.zip")
WORLD_DIR = Path("/tmp/ne_110m_admin_0_countries")
MAP_DATA = PANEL_D / "figure4_panel_d_blind_spot_country_map.csv"
DONUT_DATA = PANEL_D / "figure4_panel_d_donut_overlay_data.csv"
PANEL_E_DATA = FIG4_ROOT / "panel_e_macro_mechanism" / "figure4_panel_e_macro_vs_mechanism.csv"

OUT_MAP = PANEL_D / "figure4_panel_d_blind_spot_map.png"
OUT_DONUT_LEGEND = LEGEND_DIR / "figure4_panel_d_macro_mechanism_legend.png"
OUT_COLORBAR = LEGEND_DIR / "figure4_panel_d_blind_spot_colorbar.png"

MACRO_COLOR = "#3C5488"
MECHANISM_COLOR = "#E69F00"
NO_DATA = "#D9D9D9"
EDGE = "white"
LINE_COLOR = "#6A6A6A"
BLIND_VMIN = -0.10
BLIND_VMAX = 0.41

COUNTRY_LONLAT = {
    "USA": {"lonlat": (-101, 38), "label_lonlat": (-94, 47), "ha": "left"},
    "Germany": {"lonlat": (10.5, 51), "label_lonlat": (18, 56), "ha": "left"},
    "China": {"lonlat": (104, 35), "label_lonlat": (113, 43), "ha": "left"},
    "Japan": {"lonlat": (139, 36), "label_lonlat": (147, 29), "ha": "left"},
    "India": {"lonlat": (78, 22), "label_lonlat": (70, 10), "ha": "right"},
    "Brazil": {"lonlat": (-52, -14), "label_lonlat": (-46, -25), "ha": "left"},
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


def country_shares():
    df = pd.read_csv(DONUT_DATA)
    macro = {"Welfare and care", "Health and vulnerability"}
    mechanism = {
        "Housing and thermal comfort",
        "Household behaviour and adoption",
        "Affordability and income constraints",
        "Energy transition and efficiency",
    }
    rows = {}
    for country, sub in df.groupby("Country"):
        macro_share = sub.loc[sub["category"].isin(macro), "TopicShare"].sum()
        mechanism_share = sub.loc[sub["category"].isin(mechanism), "TopicShare"].sum()
        total = macro_share + mechanism_share
        rows[country] = (macro_share / total, mechanism_share / total) if total > 0 else (0.5, 0.5)
    return rows


def draw_donut(ax, x, y, macro_share, mechanism_share, radius=520000, width=210000):
    ax.add_patch(Circle((x, y), radius + 85000, facecolor="white", edgecolor="white", lw=0, zorder=6))
    start = 90
    macro_angle = macro_share * 360
    ax.add_patch(
        Wedge((x, y), radius, start, start + macro_angle, width=width, facecolor=MACRO_COLOR, edgecolor="white", linewidth=1.8, zorder=8)
    )
    ax.add_patch(
        Wedge((x, y), radius, start + macro_angle, start + 360, width=width, facecolor=MECHANISM_COLOR, edgecolor="white", linewidth=1.8, zorder=8)
    )
    ax.add_patch(Circle((x, y), radius - width, facecolor="black", edgecolor="white", lw=1.2, zorder=9))


def add_context_elements(fig, ax):
    """Add compact in-map explanations without requiring a separate legend panel."""
    ax.text(
        0.055,
        0.205,
        "Temporal attention structure",
        transform=ax.transAxes,
        fontsize=12,
        fontweight="bold",
        color="#111111",
        ha="left",
        va="bottom",
        zorder=20,
    )

    if PANEL_E_DATA.exists():
        trend = pd.read_csv(PANEL_E_DATA)
        x = np.arange(len(trend), dtype=float)
        inset = ax.inset_axes([0.052, 0.055, 0.245, 0.145])
        inset.set_facecolor("none")
        inset.plot(x, trend["macro_share"], color=MACRO_COLOR, lw=2.2, marker="o", ms=2.2)
        inset.plot(x, trend["mechanism_share"], color=MECHANISM_COLOR, lw=2.2, marker="o", ms=2.2)
        inset.text(x[-1] + 0.18, trend["mechanism_share"].iloc[-1], "Mechanism", color=MECHANISM_COLOR, fontsize=9, fontweight="bold", va="center")
        inset.text(x[-1] + 0.18, trend["macro_share"].iloc[-1], "Macro", color=MACRO_COLOR, fontsize=9, fontweight="bold", va="center")
        inset.set_xlim(-0.2, len(trend) + 1.7)
        inset.set_ylim(0.2, 0.8)
        inset.axis("off")

    ax.text(
        0.52,
        0.087,
        "Country rings",
        transform=ax.transAxes,
        fontsize=11,
        fontweight="bold",
        color="#111111",
        ha="center",
        va="bottom",
        zorder=20,
    )
    ax.scatter([], [], color=MACRO_COLOR, label="Macro attention")
    ax.scatter([], [], color=MECHANISM_COLOR, label="Mechanism attention")
    legend = ax.legend(
        loc="lower center",
        bbox_to_anchor=(0.54, 0.020),
        ncol=2,
        frameon=False,
        fontsize=10.5,
        handlelength=1.3,
        columnspacing=1.8,
        handletextpad=0.5,
    )
    ax.add_artist(legend)

    cax = ax.inset_axes([0.755, 0.058, 0.105, 0.035])
    sm = ScalarMappable(norm=Normalize(vmin=BLIND_VMIN, vmax=BLIND_VMAX), cmap="RdBu_r")
    cb = fig.colorbar(sm, cax=cax, orientation="horizontal")
    cb.set_ticks([BLIND_VMIN, 0, BLIND_VMAX])
    cb.set_ticklabels(["-0.10", "0", "0.41"])
    cb.outline.set_visible(False)
    cb.ax.tick_params(labelsize=9.5, length=0, pad=1.5)
    cb.ax.xaxis.set_ticks_position("bottom")
    ax.text(
        0.807,
        0.101,
        "Blind spot index",
        transform=ax.transAxes,
        fontsize=11,
        fontweight="bold",
        color="#111111",
        ha="center",
        va="bottom",
        zorder=20,
    )


def redraw_map():
    shp_path = ensure_world()
    reader = shapefile.Reader(str(shp_path), encoding="latin1")
    fields = [f[0] for f in reader.fields[1:]]
    map_df = pd.read_csv(MAP_DATA)
    values = dict(zip(map_df["Country"], map_df["blind_spot_index"]))
    norm = Normalize(vmin=BLIND_VMIN, vmax=BLIND_VMAX, clip=True)
    cmap = plt.get_cmap("RdBu_r")

    patches = []
    colors = []
    for shape, rec in zip(reader.shapes(), reader.records()):
        name = country_name(rec, fields)
        if name == "Antarctica":
            continue
        parts = list(shape.parts) + [len(shape.points)]
        for start, end in zip(parts[:-1], parts[1:]):
            pts = shape.points[start:end]
            if len(pts) < 3:
                continue
            poly = projected_polygon(pts)
            patches.append(Polygon(poly, closed=True))
            if name in values:
                colors.append(cmap(norm(values[name])))
            else:
                colors.append(NO_DATA)

    fig, ax = plt.subplots(figsize=(15.8, 7.2), dpi=300)
    fig.patch.set_alpha(0)
    collection = PatchCollection(patches, facecolor=colors, edgecolor=EDGE, linewidths=0.35, zorder=1)
    ax.add_collection(collection)
    ax.set_aspect("equal")
    ax.set_xlim(-17_200_000, 17_200_000)
    ax.set_ylim(-6_000_000, 8_700_000)
    ax.axis("off")

    shares = country_shares()
    for country, spec in COUNTRY_LONLAT.items():
        x, y = project_points([spec["lonlat"][0]], [spec["lonlat"][1]])
        lx, ly = project_points([spec["label_lonlat"][0]], [spec["label_lonlat"][1]])
        x, y, lx, ly = x[0], y[0], lx[0], ly[0]
        macro_share, mechanism_share = shares.get(country, (0.5, 0.5))
        ax.plot([x, lx], [y, ly], color=LINE_COLOR, lw=1.4, zorder=7)
        draw_donut(ax, x, y, macro_share, mechanism_share)
        ax.text(
            lx,
            ly,
            country,
            fontsize=18,
            ha=spec["ha"],
            va="center",
            color="#111111",
            bbox=dict(facecolor="white", edgecolor="none", alpha=0.95, pad=2.2),
            zorder=10,
        )

    fig.savefig(OUT_MAP, transparent=True, bbox_inches="tight", pad_inches=0.02)
    plt.close(fig)


def draw_donut_legend():
    fig, ax = plt.subplots(figsize=(5.1, 0.8), dpi=300)
    fig.patch.set_alpha(0)
    ax.axis("off")
    handles = [
        Patch(facecolor=MACRO_COLOR, edgecolor="none", label="Macro share"),
        Patch(facecolor=MECHANISM_COLOR, edgecolor="none", label="Mechanism share"),
    ]
    ax.legend(handles=handles, loc="center", ncol=2, frameon=False, fontsize=16, handlelength=1.4, columnspacing=1.8)
    fig.savefig(OUT_DONUT_LEGEND, transparent=True, bbox_inches="tight", pad_inches=0.02)
    plt.close(fig)


def draw_colorbar():
    fig, ax = plt.subplots(figsize=(2.5, 0.52), dpi=300)
    fig.patch.set_alpha(0)
    sm = ScalarMappable(norm=Normalize(vmin=BLIND_VMIN, vmax=BLIND_VMAX), cmap="RdBu_r")
    cb = fig.colorbar(sm, cax=ax, orientation="horizontal")
    cb.set_ticks([BLIND_VMIN, 0, BLIND_VMAX])
    cb.set_ticklabels(["-0.10", "0", "0.41"])
    cb.outline.set_visible(False)
    cb.ax.tick_params(labelsize=15, length=0, pad=2)
    cb.ax.xaxis.set_ticks_position("top")
    fig.savefig(OUT_COLORBAR, transparent=True, bbox_inches="tight", pad_inches=0.02)
    plt.close(fig)


def main():
    redraw_map()
    draw_donut_legend()
    draw_colorbar()
    print(OUT_MAP)
    print(OUT_DONUT_LEGEND)
    print(OUT_COLORBAR)


if __name__ == "__main__":
    main()
