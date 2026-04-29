from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from scipy.interpolate import PchipInterpolator


PANEL_E = Path("/Users/longlab/Desktop/Aging Energy/working_project/07_figures_working/figure3_updated_panels/panel_e")
DATA = PANEL_E / "panel_e_macro_vs_mechanism.csv"
OUT = PANEL_E / "figure3b_macro_vs_mechanism.png"

MACRO_COLOR = "#3C5488"
MECHANISM_COLOR = "#E69F00"


def smooth_xy(x, y):
    xs = np.linspace(x.min(), x.max(), 260)
    ys = PchipInterpolator(x, y)(xs)
    return xs, ys


def main():
    df = pd.read_csv(DATA)
    labels = [v.replace("_", "-") for v in df["time_window"]]
    x = np.arange(len(df), dtype=float)
    macro = df["macro_share"].to_numpy(dtype=float)
    mechanism = df["mechanism_share"].to_numpy(dtype=float)
    xm, ym = smooth_xy(x, macro)
    xh, yh = smooth_xy(x, mechanism)

    plt.rcParams.update(
        {
            "font.family": "Arial",
            "axes.labelsize": 30,
            "xtick.labelsize": 25,
            "ytick.labelsize": 26,
        }
    )

    fig, ax = plt.subplots(figsize=(11.5, 6.8), dpi=300)
    fig.patch.set_alpha(0)
    ax.set_facecolor("none")

    ax.plot(xm, ym, color=MACRO_COLOR, linewidth=6.0, solid_capstyle="round")
    ax.plot(xh, yh, color=MECHANISM_COLOR, linewidth=6.0, solid_capstyle="round")
    ax.scatter(x, macro, s=90, color=MACRO_COLOR, edgecolor="white", linewidth=1.0, zorder=3)
    ax.scatter(x, mechanism, s=90, color=MECHANISM_COLOR, edgecolor="white", linewidth=1.0, zorder=3)

    ax.text(
        x[-1] - 1.95,
        0.395,
        "Macro attention",
        color=MACRO_COLOR,
        fontsize=27,
        fontweight="bold",
        va="top",
        ha="left",
    )
    ax.text(
        x[-1] - 1.95,
        0.665,
        "Mechanism attention",
        color=MECHANISM_COLOR,
        fontsize=27,
        fontweight="bold",
        va="bottom",
        ha="left",
    )

    ax.set_xlim(-0.55, len(df) - 0.15)
    ax.set_ylim(0.0, 1.02)
    ax.set_ylabel("Share", labelpad=20, fontweight="bold")
    ax.set_xlabel("")
    ax.set_xticks(x)
    ax.set_xticklabels(labels, rotation=90, ha="center", va="top")
    ax.set_yticks(np.linspace(0, 1.0, 6))
    ax.spines[["top", "right"]].set_visible(False)
    ax.spines["left"].set_linewidth(2.0)
    ax.spines["bottom"].set_linewidth(2.0)
    ax.tick_params(axis="x", width=1.8, length=6, pad=8)
    ax.tick_params(axis="y", width=1.8, length=6, pad=8)
    ax.grid(False)

    fig.subplots_adjust(left=0.10, right=0.98, top=0.98, bottom=0.37)
    fig.savefig(OUT, transparent=True, bbox_inches="tight", pad_inches=0.02)
    plt.close(fig)
    print(OUT)


if __name__ == "__main__":
    main()
