from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd


PANEL_D = Path("/Users/longlab/Desktop/Aging Energy/working_project/07_figures_working/figure3_updated_panels/panel_d")
DATA = PANEL_D / "panel_d_blind_spot_country_map.csv"
OUT = PANEL_D / "figure3_panel_d_blind_spot_distribution_inset.png"
OUT_CSV = PANEL_D / "figure3_panel_d_blind_spot_distribution_summary.csv"

NEG_COLOR = "#2C7FB8"
POS_COLOR = "#C85A4A"
ZERO_COLOR = "#111111"
TEXT_COLOR = "#111111"


def main():
    df = pd.read_csv(DATA)
    values = df["blind_spot_index"].dropna().to_numpy(dtype=float)
    clipped = np.clip(values, -0.10, 0.41)
    q1, med, q3 = np.quantile(values, [0.25, 0.5, 0.75])
    share_positive = (values > 0).mean() * 100
    share_negative = (values < 0).mean() * 100

    summary = pd.DataFrame(
        [
            {
                "n_countries": len(values),
                "mean": values.mean(),
                "median": med,
                "q1": q1,
                "q3": q3,
                "min": values.min(),
                "max": values.max(),
                "share_positive_pct": share_positive,
                "share_negative_pct": share_negative,
                "display_min": -0.10,
                "display_max": 0.41,
            }
        ]
    )
    summary.to_csv(OUT_CSV, index=False)

    plt.rcParams.update(
        {
            "font.family": "Arial",
            "axes.titlesize": 16,
            "xtick.labelsize": 11,
            "ytick.labelsize": 10,
        }
    )

    fig, ax = plt.subplots(figsize=(4.25, 2.05), dpi=300)
    fig.patch.set_alpha(0)
    ax.set_facecolor("none")

    bins = np.linspace(-0.10, 0.41, 18)
    counts, edges = np.histogram(clipped, bins=bins)
    centers = (edges[:-1] + edges[1:]) / 2
    widths = np.diff(edges) * 0.86
    colors = [NEG_COLOR if c < 0 else POS_COLOR for c in centers]
    ax.bar(centers, counts, width=widths, color=colors, alpha=0.86, edgecolor="white", linewidth=0.5)

    ax.axvline(0, color=ZERO_COLOR, lw=1.4)
    ax.axvspan(q1, q3, color="#F0C9A4", alpha=0.36, lw=0)
    ax.axvline(med, color="#7A3E2A", lw=1.6)

    ax.text(0, counts.max() * 1.02, "0", ha="center", va="bottom", fontsize=9.5, color=ZERO_COLOR)
    ax.text(med + 0.014, counts.max() * 1.02, "median", ha="left", va="bottom", fontsize=8.8, color="#7A3E2A")
    ax.text((q1 + q3) / 2, counts.max() * 1.15, "IQR", ha="center", va="bottom", fontsize=8.8, color="#7A3E2A")

    ax.text(
        0.0,
        1.22,
        "Blind spot index distribution",
        transform=ax.transAxes,
        ha="left",
        va="bottom",
        fontsize=16,
        fontweight="bold",
        color=TEXT_COLOR,
    )

    ax.text(
        0.985,
        0.86,
        f"{share_positive:.0f}% > 0",
        transform=ax.transAxes,
        ha="right",
        va="top",
        fontsize=11,
        fontweight="bold",
        color=POS_COLOR,
    )
    ax.text(
        0.985,
        0.72,
        f"{share_negative:.0f}% < 0",
        transform=ax.transAxes,
        ha="right",
        va="top",
        fontsize=11,
        fontweight="bold",
        color=NEG_COLOR,
    )

    ax.set_xlim(-0.105, 0.415)
    ax.set_ylim(0, counts.max() * 1.34)
    ax.set_xlabel("Blind spot index", fontsize=11.5, labelpad=3)
    ax.set_ylabel("Countries", fontsize=11.5, labelpad=3)
    ax.set_xticks([-0.10, 0, 0.20, 0.41])
    ax.set_xticklabels(["-0.10", "0", "0.20", "0.41"])
    ax.spines[["top", "right"]].set_visible(False)
    ax.spines["left"].set_linewidth(0.8)
    ax.spines["bottom"].set_linewidth(0.8)
    ax.tick_params(width=0.8, length=3, pad=2)
    ax.grid(False)

    fig.savefig(OUT, transparent=True, bbox_inches="tight", pad_inches=0.02)
    plt.close(fig)
    print(OUT)
    print(OUT_CSV)


if __name__ == "__main__":
    main()
