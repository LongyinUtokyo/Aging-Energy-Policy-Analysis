from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd
from matplotlib.lines import Line2D
from matplotlib.patches import Patch


ROOT = Path("/Users/longlab/Desktop/Aging Energy/working_project/07_figures_working/figure3_updated_panels")
PANEL_B = ROOT / "panel_b"
PANEL_C = ROOT / "panel_c"
PANEL_LEGEND = ROOT / "shared_legends"
PANEL_LEGEND.mkdir(parents=True, exist_ok=True)

CATEGORY_ORDER = [
    "welfare and care",
    "health and vulnerability",
    "housing and thermal comfort",
    "energy transition and efficiency",
    "household behaviour and adoption",
    "affordability and income constraints",
]

CATEGORY_LABELS = {
    "welfare and care": "Welfare and care",
    "health and vulnerability": "Health and vulnerability",
    "housing and thermal comfort": "Housing and thermal comfort",
    "energy transition and efficiency": "Energy transition and efficiency",
    "household behaviour and adoption": "Household behaviour and adoption",
    "affordability and income constraints": "Affordability and income constraints",
}

COLORS = {
    "welfare and care": "#3C5488",
    "health and vulnerability": "#00A087",
    "housing and thermal comfort": "#D4A017",
    "energy transition and efficiency": "#4DBBD5",
    "household behaviour and adoption": "#7B3294",
    "affordability and income constraints": "#E64B35",
}


def save_transparent(fig, path):
    fig.savefig(path, dpi=300, bbox_inches="tight", transparent=True)
    plt.close(fig)


def draw_panel_b():
    df = pd.read_csv(PANEL_B / "panel_b_topicshare_share_wide.csv")
    x_labels = [x.replace("_", "-") for x in df["time_window"]]

    plt.rcParams.update(
        {
            "font.family": "Arial",
            "axes.titlesize": 28,
            "axes.labelsize": 24,
            "xtick.labelsize": 18,
            "ytick.labelsize": 20,
        }
    )

    fig, ax = plt.subplots(figsize=(13.5, 7.0))
    bottom = [0.0] * len(df)
    x = range(len(df))
    for cat in CATEGORY_ORDER:
        vals = df[cat].values * 100
        ax.bar(
            x,
            vals,
            bottom=bottom,
            color=COLORS[cat],
            edgecolor="white",
            linewidth=0.8,
            width=0.78,
        )
        bottom = [b + v for b, v in zip(bottom, vals)]

    ax.set_ylim(0, 100)
    ax.set_ylabel("")
    ax.set_xlabel("")
    ax.set_yticks([0, 25, 50, 75, 100])
    ax.set_yticklabels(["0%", "25%", "50%", "75%", "100%"])
    ax.set_xticks(list(x))
    ax.set_xticklabels(x_labels, rotation=90, ha="center", va="top")
    ax.spines[["top", "right"]].set_visible(False)
    ax.grid(False)
    ax.tick_params(axis="x", pad=6)
    fig.subplots_adjust(left=0.08, right=0.98, top=0.96, bottom=0.25)
    save_transparent(fig, PANEL_B / "figure3a_topic_evolution.png")


def draw_panel_c():
    df = pd.read_csv(PANEL_C / "panel_c_top5_countries_by_category.csv")

    plt.rcParams.update(
        {
            "font.family": "Arial",
            "axes.titlesize": 22,
            "axes.labelsize": 27,
            "xtick.labelsize": 20,
            "ytick.labelsize": 30,
        }
    )

    fig, axes = plt.subplots(2, 3, figsize=(26, 13.2))
    axes = axes.flatten()

    for ax, cat in zip(axes, CATEGORY_ORDER):
        sub = (
            df[df["category"] == cat]
            .sort_values("mention_count", ascending=True)
            .reset_index(drop=True)
        )
        y = range(len(sub))
        xmax = sub["mention_count"].max() * 1.16
        color = COLORS[cat]

        ax.hlines(y=y, xmin=0, xmax=sub["mention_count"], color=color, linewidth=4.8, alpha=0.62)
        ax.scatter(sub["mention_count"], y, s=255, color=color, edgecolor="white", linewidth=2.0, zorder=3)
        ax.set_yticks(list(y))
        ax.set_yticklabels(sub["Source country"])
        ax.set_xlim(0, xmax)
        ax.set_title(CATEGORY_LABELS[cat], loc="left", fontweight="bold", pad=38)
        ax.set_xlabel("")
        ax.set_ylabel("")
        ax.spines[["top", "right", "left"]].set_visible(False)
        ax.tick_params(axis="y", length=0, pad=10)
        ax.tick_params(axis="x", labelsize=20, width=1.8, length=6)
        ax.grid(False)

        for val, yy in zip(sub["mention_count"], y):
            ax.text(val + xmax * 0.024, yy, f"{int(val):,}", va="center", ha="left", fontsize=26)

    for ax in axes[len(CATEGORY_ORDER):]:
        ax.axis("off")

    fig.subplots_adjust(left=0.08, right=0.985, top=0.965, bottom=0.045, wspace=0.50, hspace=0.86)
    save_transparent(fig, PANEL_C / "figure3_panel_c_top_countries_by_category_clean.png")


def draw_shared_legend():
    handles = [
        Line2D(
            [0],
            [0],
            marker="o",
            linestyle="None",
            markerfacecolor=COLORS[c],
            markeredgecolor="none",
            markersize=18,
            label=CATEGORY_LABELS[c].replace("\n", " "),
        )
        for c in CATEGORY_ORDER
    ]
    fig, ax = plt.subplots(figsize=(22.0, 2.4))
    ax.axis("off")
    ax.legend(
        handles=handles,
        loc="center",
        ncol=3,
        frameon=False,
        fontsize=24,
        handlelength=0.9,
        handleheight=1.0,
        columnspacing=1.8,
        labelspacing=0.9,
    )
    save_transparent(fig, PANEL_LEGEND / "figure3_panel_b_c_shared_legend.png")


def main():
    draw_panel_b()
    draw_panel_c()
    draw_shared_legend()
    print(ROOT)


if __name__ == "__main__":
    main()
