from __future__ import annotations

import os
import re
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns
from matplotlib.colors import to_hex
from matplotlib.path import Path as MplPath
from matplotlib.patches import PathPatch, Rectangle


WORKDIR = Path(__file__).resolve().parents[2]
OUTPUT_DIR = WORKDIR / "outputs" / "result2" / "keyword_sankey_outputs"
os.environ.setdefault("MPLCONFIGDIR", str(OUTPUT_DIR / ".mplconfig"))
INPUT_PATH = OUTPUT_DIR / "top30_keywords_rank_by_window_with_counts.csv"
BAD_KEYWORDS = {"hous", "analysi", "branche", "meet", "degree", "museum"}


def parse_keyword_count(cell: str) -> tuple[str, int]:
    value = str(cell).strip()
    match = re.match(r"^(.*?)\s*\((\d+)\)$", value)
    if not match:
        raise ValueError(f"Could not parse keyword cell: {value!r}")
    keyword = match.group(1).strip()
    count = int(match.group(2))
    return keyword, count


def load_top10() -> pd.DataFrame:
    df = pd.read_csv(INPUT_PATH)
    windows = [col for col in df.columns if col != "rank"]
    rows = []
    for window in windows:
        for rank, cell in zip(df["rank"], df[window]):
            if pd.isna(cell) or int(rank) > 10:
                continue
            keyword, count = parse_keyword_count(cell)
            rows.append(
                {
                    "time_window": window,
                    "rank": int(rank),
                    "keyword": keyword,
                    "count": count,
                }
            )
    long_df = pd.DataFrame(rows)
    if set(long_df["keyword"].str.lower()) & BAD_KEYWORDS:
        raise ValueError("Malformed keywords detected in Top 10 input")
    return long_df


def build_links(node_df: pd.DataFrame) -> pd.DataFrame:
    windows = list(node_df["time_window"].drop_duplicates())
    links = []
    for i in range(len(windows) - 1):
        left = node_df[node_df["time_window"] == windows[i]][["keyword", "rank", "count"]].rename(
            columns={"rank": "source_rank", "count": "source_count"}
        )
        right = node_df[node_df["time_window"] == windows[i + 1]][["keyword", "rank", "count"]].rename(
            columns={"rank": "target_rank", "count": "target_count"}
        )
        merged = left.merge(right, on="keyword", how="inner")
        merged["source_window"] = windows[i]
        merged["target_window"] = windows[i + 1]
        merged["link_width_count"] = merged[["source_count", "target_count"]].min(axis=1)
        links.append(merged)
    return pd.concat(links, ignore_index=True) if links else pd.DataFrame()


def build_color_map(keywords: list[str]) -> dict[str, str]:
    palette = sns.husl_palette(len(keywords), s=0.52, l=0.56)
    return {kw: to_hex(color) for kw, color in zip(sorted(keywords), palette)}


def initial_positions(long_df: pd.DataFrame) -> pd.DataFrame:
    windows = list(long_df["time_window"].drop_duplicates())
    x_map = {window: idx * 2.45 for idx, window in enumerate(windows)}
    max_count = long_df["count"].max()
    node_frames = []
    for window in windows:
        chunk = long_df[long_df["time_window"] == window].sort_values(["rank", "keyword"]).copy()
        chunk["node_height"] = 0.34 + np.sqrt(chunk["count"] / max_count) * 1.28
        gap = 0.26
        current_top = 0.0
        centers = []
        for height in chunk["node_height"]:
            centers.append(current_top - height / 2)
            current_top -= height + gap
        chunk["x"] = x_map[window]
        chunk["y"] = centers
        node_frames.append(chunk)
    node_df = pd.concat(node_frames, ignore_index=True)
    node_df["y"] = node_df["y"] - node_df["y"].min() + 1.2
    return node_df


def relax_positions(node_df: pd.DataFrame, iterations: int = 4) -> pd.DataFrame:
    windows = list(node_df["time_window"].drop_duplicates())
    adjusted = node_df.copy()
    gap = 0.26
    for _ in range(iterations):
        prev_lookup = {}
        new_frames = []
        for window in windows:
            chunk = adjusted[adjusted["time_window"] == window].sort_values("rank").copy().reset_index(drop=True)
            if prev_lookup:
                for idx in range(len(chunk)):
                    key = chunk.loc[idx, "keyword"]
                    if key in prev_lookup:
                        chunk.loc[idx, "y"] = 0.68 * chunk.loc[idx, "y"] + 0.32 * prev_lookup[key]
            # enforce rank order and minimum spacing
            for idx in range(1, len(chunk)):
                min_y = chunk.loc[idx - 1, "y"] + chunk.loc[idx - 1, "node_height"] / 2 + gap + chunk.loc[idx, "node_height"] / 2
                if chunk.loc[idx, "y"] < min_y:
                    chunk.loc[idx, "y"] = min_y
            for idx in range(len(chunk) - 2, -1, -1):
                max_y = chunk.loc[idx + 1, "y"] - chunk.loc[idx + 1, "node_height"] / 2 - gap - chunk.loc[idx, "node_height"] / 2
                if chunk.loc[idx, "y"] > max_y:
                    chunk.loc[idx, "y"] = max_y
            prev_lookup = dict(zip(chunk["keyword"], chunk["y"]))
            new_frames.append(chunk)
        adjusted = pd.concat(new_frames, ignore_index=True)
    return adjusted


def ribbon_patch(x0: float, y0: float, x1: float, y1: float, half_width: float, color: str, alpha: float) -> PathPatch:
    ctrl = 0.42 * (x1 - x0)
    top_verts = [
        (x0, y0 + half_width),
        (x0 + ctrl, y0 + half_width),
        (x1 - ctrl, y1 + half_width),
        (x1, y1 + half_width),
    ]
    bot_verts = [
        (x1, y1 - half_width),
        (x1 - ctrl, y1 - half_width),
        (x0 + ctrl, y0 - half_width),
        (x0, y0 - half_width),
    ]
    verts = [top_verts[0], top_verts[1], top_verts[2], top_verts[3], bot_verts[0], bot_verts[1], bot_verts[2], bot_verts[3], top_verts[0]]
    codes = [
        MplPath.MOVETO,
        MplPath.CURVE4,
        MplPath.CURVE4,
        MplPath.CURVE4,
        MplPath.LINETO,
        MplPath.CURVE4,
        MplPath.CURVE4,
        MplPath.CURVE4,
        MplPath.CLOSEPOLY,
    ]
    return PathPatch(
        MplPath(verts, codes),
        facecolor=color,
        edgecolor="none",
        alpha=alpha,
        zorder=1,
    )


def save_support_data(node_df: pd.DataFrame, links: pd.DataFrame, colors: dict[str, str]) -> None:
    links.to_csv(OUTPUT_DIR / "sankey_data_top10.csv", index=False)
    node_df.to_csv(OUTPUT_DIR / "node_positions_top10.csv", index=False)
    pd.DataFrame(
        {"keyword": list(colors.keys()), "color_hex": list(colors.values())}
    ).to_csv(OUTPUT_DIR / "keyword_color_map.csv", index=False)


def draw(node_df: pd.DataFrame, links: pd.DataFrame, colors: dict[str, str]) -> None:
    windows = list(node_df["time_window"].drop_duplicates())
    x_map = {window: node_df.loc[node_df["time_window"] == window, "x"].iloc[0] for window in windows}
    fig, ax = plt.subplots(figsize=(22, 12), facecolor="#fbfbf8")
    ax.set_facecolor("#fbfbf8")

    for window, x in x_map.items():
        ax.axvline(x, color="#dfdfdf", lw=0.8, zorder=0)
        ax.text(x, node_df["y"].max() + 2.0, window.replace("_", "-"), ha="center", va="bottom", fontsize=13.5, fontweight="semibold", color="#333333")

    pos_lookup = node_df.set_index(["time_window", "keyword"])[["x", "y", "rank"]].to_dict("index")
    max_count = node_df["count"].max()
    links = links.copy()
    links["ribbon_halfwidth"] = 0.08 + np.sqrt(links["link_width_count"] / max_count) * 0.34

    for row in links.sort_values(["link_width_count", "source_rank"], ascending=[False, True]).itertuples():
        src = pos_lookup[(row.source_window, row.keyword)]
        tgt = pos_lookup[(row.target_window, row.keyword)]
        rank_weight = min(row.source_rank, row.target_rank)
        alpha = 0.5 if rank_weight <= 3 else 0.28
        patch = ribbon_patch(
            src["x"] + 0.12,
            src["y"],
            tgt["x"] - 0.12,
            tgt["y"],
            row.ribbon_halfwidth * (1.18 if rank_weight <= 3 else 1.0),
            colors[row.keyword],
            alpha,
        )
        ax.add_patch(patch)

    node_w = 0.16
    for row in node_df.itertuples():
        is_top3 = row.rank <= 3
        alpha = 0.98 if is_top3 else 0.8
        rect = Rectangle(
            (row.x - node_w / 2, row.y - row.node_height / 2),
            node_w,
            row.node_height,
            facecolor=colors[row.keyword],
            edgecolor="white",
            lw=0.9 if is_top3 else 0.6,
            alpha=alpha,
            zorder=3,
        )
        ax.add_patch(rect)

        if row.rank <= 5:
            fontsize = 12.0 if row.rank <= 3 else 9.4
            weight = "bold" if row.rank <= 3 else "normal"
            alpha_text = 1.0
        else:
            fontsize = 7.8
            weight = "normal"
            alpha_text = 0.8

        if row.time_window == windows[-1]:
            label_x = row.x + 0.46
            ha = "left"
        else:
            label_x = row.x + 0.14
            ha = "left"

        if row.rank <= 5 or row.node_height >= 0.58:
            ax.text(
                label_x,
                row.y,
                row.keyword,
                ha=ha,
                va="center",
                fontsize=fontsize,
                fontweight=weight,
                color="#222222",
                alpha=alpha_text,
                zorder=4,
                clip_on=False,
            )

    ax.text(windows and x_map[windows[0]] - 0.7 or 0, node_df["y"].max() + 4.0, "Top 10 Keyword Evolution Across Policy Windows", ha="left", va="bottom", fontsize=18, fontweight="bold", color="#111111")
    ax.set_xlim(min(x_map.values()) - 0.85, max(x_map.values()) + 2.2)
    ax.set_ylim(0.0, node_df["y"].max() + 4.8)
    ax.axis("off")
    fig.tight_layout(pad=1.3)
    fig.savefig(OUTPUT_DIR / "keyword_sankey_top10_full.png", dpi=400, bbox_inches="tight", facecolor=fig.get_facecolor())
    fig.savefig(OUTPUT_DIR / "keyword_sankey_top10_full.pdf", bbox_inches="tight", facecolor=fig.get_facecolor())
    plt.close(fig)


def main() -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    long_df = load_top10()
    node_df = relax_positions(initial_positions(long_df))
    links = build_links(long_df)
    colors = build_color_map(long_df["keyword"].unique().tolist())
    save_support_data(node_df, links, colors)
    draw(node_df, links, colors)


if __name__ == "__main__":
    main()
