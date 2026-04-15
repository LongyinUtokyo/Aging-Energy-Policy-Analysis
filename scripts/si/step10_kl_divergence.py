from __future__ import annotations

from pathlib import Path

import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd


ROOT = Path(__file__).resolve().parents[2]
TOPICSHARE_CSV = ROOT / "data" / "compact" / "result3" / "topicshare_by_window_clean.csv"
OUT_DIR = ROOT / "outputs" / "si" / "step10_kl"

WINDOW_ORDER = [
    "1972_1976",
    "1977_1981",
    "1982_1986",
    "1987_1991",
    "1992_1996",
    "1997_2001",
    "2002_2006",
    "2007_2011",
    "2012_2016",
    "2017_2020",
    "2021_2024",
]

PHASE_MAP = {
    "1972_1976": "Phase 3",
    "1977_1981": "Phase 3",
    "1982_1986": "Phase 3",
    "1987_1991": "Phase 3",
    "1992_1996": "Phase 3",
    "1997_2001": "Phase 4",
    "2002_2006": "Phase 4",
    "2007_2011": "Phase 4",
    "2012_2016": "Phase 4",
    "2017_2020": "Phase 4",
    "2021_2024": "Phase 4",
}


def window_midyear(label: str) -> int:
    start, end = [int(x) for x in label.split("_")]
    return int((start + end) / 2)


def kl_divergence(p: np.ndarray, q: np.ndarray) -> float:
    return float(np.sum(p * np.log(p / q)))


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)

    topicshare = pd.read_csv(TOPICSHARE_CSV)
    topicshare = topicshare[topicshare["time_window"].isin(WINDOW_ORDER)].copy()
    topicshare["phase"] = topicshare["time_window"].map(PHASE_MAP)

    categories = topicshare["category"].drop_duplicates().tolist()
    q = np.repeat(1 / len(categories), len(categories))

    rows = []
    for time_window, subset in topicshare.groupby("time_window", sort=False):
        subset = subset.set_index("category").reindex(categories).reset_index()
        p = subset["share"].astype(float).to_numpy()
        rows.append(
            {
                "time_window": time_window,
                "phase": PHASE_MAP[time_window],
                "window_midyear": window_midyear(time_window),
                "kl_divergence": kl_divergence(p, q),
                "q_definition": "equal-weight baseline across the six taxonomy categories",
            }
        )

    timeseries = pd.DataFrame(rows).sort_values("window_midyear").reset_index(drop=True)
    timeseries.to_csv(OUT_DIR / "step10_kl_timeseries.csv", index=False)

    phase_summary = (
        timeseries.groupby("phase", as_index=False)
        .agg(
            mean_kl=("kl_divergence", "mean"),
            min_kl=("kl_divergence", "min"),
            max_kl=("kl_divergence", "max"),
            window_n=("kl_divergence", "size"),
        )
    )
    phase_summary.to_csv(OUT_DIR / "step10_kl_phase_summary.csv", index=False)

    plt.rcParams.update(
        {
            "font.family": "Arial",
            "font.size": 12,
            "axes.labelsize": 13,
            "figure.facecolor": "white",
            "axes.facecolor": "white",
            "savefig.facecolor": "white",
        }
    )
    fig, ax = plt.subplots(figsize=(8.6, 4.8))
    ax.plot(timeseries["window_midyear"], timeseries["kl_divergence"], color="#9c3d3d", lw=2.4, marker="o", ms=5)
    ax.axvspan(1997, 2024.5, color="#f1e4e4", alpha=0.45)
    ax.set_xlabel("Window mid-year")
    ax.set_ylabel("KL(P_t || Q)")
    ax.grid(False)
    for spine in ["top", "right"]:
        ax.spines[spine].set_visible(False)
    fig.tight_layout()
    fig.savefig(OUT_DIR / "step10_kl_trend.png", dpi=320, bbox_inches="tight")
    plt.close(fig)

    rapid = timeseries[timeseries["phase"] == "Phase 4"].copy()
    slope = np.polyfit(rapid["window_midyear"], rapid["kl_divergence"], 1)[0] if len(rapid) >= 2 else np.nan
    lines = [
        "# Step 10 KL Divergence",
        "",
        "Observed distribution P_t was taken directly from Step 7 topic-share windows.",
        "Theoretical reference distribution Q uses the default equal-weight baseline across the six taxonomy categories because no explicit numeric balanced mechanism vector was available in the project files.",
        "",
        "## Window-level KL divergence",
    ]
    for row in timeseries.itertuples(index=False):
        lines.append(f"- {row.time_window}: KL={row.kl_divergence:.6f} ({row.phase})")
    lines.extend(
        [
            "",
            "## Phase averages",
        ]
    )
    for row in phase_summary.itertuples(index=False):
        lines.append(
            f"- {row.phase}: mean={row.mean_kl:.6f}, min={row.min_kl:.6f}, max={row.max_kl:.6f}, windows={int(row.window_n)}"
        )
    lines.extend(
        [
            "",
            "## Rapid Expansion trend",
            f"- Phase 4 linear slope of KL over window mid-year: {slope:.8f}",
        ]
    )
    (OUT_DIR / "step10_kl_summary.md").write_text("\n".join(lines), encoding="utf-8")


if __name__ == "__main__":
    main()
