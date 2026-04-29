from __future__ import annotations

import itertools
import math
import re
from collections import Counter, defaultdict
import os
import tempfile
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
os.environ.setdefault("MPLCONFIGDIR", tempfile.mkdtemp(prefix="mplcfg_"))

import matplotlib.pyplot as plt
import networkx as nx
import numpy as np
import pandas as pd


ROOT = Path(__file__).resolve().parents[2]
DOC_CSV = ROOT / "inputs" / "auxiliary" / "merged_policy_metadata_clean.csv"
TAXONOMY_CSV = ROOT / "data" / "compact" / "result3" / "keyword_taxonomy_mapping_clean.csv"
OUT_DIR = ROOT / "outputs" / "si" / "step9_network"

PHASES = {
    "Phase 1": (1869, 1947),
    "Phase 2": (1948, 1971),
    "Phase 3": (1972, 1993),
    "Phase 4": (1994, 2024),
}

CATEGORY_COLORS = {
    "welfare and care": "#8fb7aa",
    "health and vulnerability": "#3a7d89",
    "housing and thermal comfort": "#d8a15d",
    "energy transition and efficiency": "#4f6d7a",
    "household behaviour and adoption": "#b07aa1",
    "affordability and income constraints": "#c35b5b",
}

KEY_TERMS = [
    "household",
    "technology adoption",
    "thermal comfort",
    "energy poverty",
    "fuel poverty",
    "retrofit",
    "accessibility",
    "affordable housing",
    "climate change",
    "health",
    "social",
    "care",
]


def phase_from_year(year: int) -> str | None:
    for phase, (start, end) in PHASES.items():
        if start <= year <= end:
            return phase
    return None


def normalize_text(text: str) -> str:
    text = str(text).lower()
    text = re.sub(r"[^a-z0-9\\s]+", " ", text)
    text = re.sub(r"\\s+", " ", text).strip()
    return text


def compile_patterns(keywords: list[str]) -> dict[str, re.Pattern[str]]:
    patterns = {}
    for keyword in keywords:
        parts = [re.escape(part) for part in keyword.lower().split()]
        escaped = r"\s+".join(parts)
        patterns[keyword] = re.compile(rf"(?<!\w){escaped}(?!\w)")
    return patterns


def doc_keyword_set(text: str, patterns: dict[str, re.Pattern[str]]) -> set[str]:
    norm = normalize_text(text)
    return {kw for kw, pattern in patterns.items() if pattern.search(norm)}


def build_phase_graph(df: pd.DataFrame, keywords: list[str], patterns: dict[str, re.Pattern[str]]):
    node_freq = Counter()
    edge_weights = Counter()
    for text in df["Combined_metadata_text"].fillna(""):
        matched = sorted(doc_keyword_set(text, patterns))
        if not matched:
            continue
        node_freq.update(matched)
        for a, b in itertools.combinations(matched, 2):
            edge_weights[(a, b)] += 1
    graph = nx.Graph()
    for keyword, freq in node_freq.items():
        graph.add_node(keyword, frequency=freq)
    for (a, b), weight in edge_weights.items():
        graph.add_edge(a, b, weight=weight)
    return graph, node_freq


def top_label_nodes(metrics: pd.DataFrame) -> list[str]:
    top = metrics.sort_values(["eigenvector_centrality", "frequency"], ascending=[False, False]).head(12)
    return top["keyword"].tolist()


def render_graph(phase: str, graph: nx.Graph, metrics: pd.DataFrame, taxonomy_lookup: dict[str, str]) -> None:
    plt.rcParams.update(
        {
            "font.family": "Arial",
            "font.size": 10,
            "figure.facecolor": "white",
            "axes.facecolor": "white",
            "savefig.facecolor": "white",
        }
    )
    if graph.number_of_nodes() == 0:
        fig, ax = plt.subplots(figsize=(8, 6))
        ax.text(0.5, 0.5, f"{phase}: no classified keywords", ha="center", va="center")
        ax.axis("off")
        fig.savefig(OUT_DIR / f"{phase.lower().replace(' ', '')}_network.png", dpi=320, bbox_inches="tight")
        plt.close(fig)
        return

    core_nodes = set(metrics.sort_values(["eigenvector_centrality", "frequency"], ascending=[False, False]).head(20)["keyword"])
    for term in KEY_TERMS:
        if term in graph.nodes:
            core_nodes.add(term)
    subgraph = graph.subgraph(core_nodes).copy()
    pos = nx.spring_layout(subgraph, seed=42, weight="weight", k=0.8 / max(math.sqrt(max(subgraph.number_of_nodes(), 1)), 1))

    fig, ax = plt.subplots(figsize=(8.6, 6.6))
    nx.draw_networkx_edges(
        subgraph,
        pos,
        ax=ax,
        edge_color="#bfbfbf",
        alpha=0.35,
        width=[0.3 + 0.18 * math.log1p(subgraph[u][v]["weight"]) for u, v in subgraph.edges()],
    )
    for category, color in CATEGORY_COLORS.items():
        nodes = [n for n in subgraph.nodes if taxonomy_lookup.get(n) == category]
        if not nodes:
            continue
        sizes = [50 + 40 * math.log1p(subgraph.nodes[n]["frequency"]) for n in nodes]
        nx.draw_networkx_nodes(
            subgraph,
            pos,
            nodelist=nodes,
            node_color=color,
            node_size=sizes,
            edgecolors="white",
            linewidths=0.8,
            alpha=0.9,
            ax=ax,
        )
    label_nodes = set(top_label_nodes(metrics))
    label_nodes.update(term for term in KEY_TERMS if term in subgraph.nodes)
    labels = {n: n for n in label_nodes if n in subgraph.nodes}
    nx.draw_networkx_labels(subgraph, pos, labels=labels, font_size=9, font_family="Arial", ax=ax)
    ax.set_xticks([])
    ax.set_yticks([])
    for spine in ax.spines.values():
        spine.set_visible(False)
    ax.set_title(phase)
    fig.tight_layout()
    fig.savefig(OUT_DIR / f"{phase.lower().replace(' ', '')}_network.png", dpi=320, bbox_inches="tight")
    plt.close(fig)


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)

    taxonomy = pd.read_csv(TAXONOMY_CSV)
    taxonomy = taxonomy[
        taxonomy["category"].notna() & taxonomy["mechanism_relevance"].isin(["high", "medium"])
    ].copy()
    taxonomy["keyword"] = taxonomy["keyword"].astype(str).str.lower()
    keywords = sorted(taxonomy["keyword"].unique().tolist(), key=lambda x: (-len(x), x))
    patterns = compile_patterns(keywords)
    taxonomy_lookup = dict(zip(taxonomy["keyword"], taxonomy["category"]))

    docs = pd.read_csv(DOC_CSV, usecols=["Year", "Combined_metadata_text"])
    docs["Year"] = pd.to_numeric(docs["Year"], errors="coerce")
    docs = docs.dropna(subset=["Year"]).copy()
    docs["Year"] = docs["Year"].astype(int)
    docs["Phase"] = docs["Year"].apply(phase_from_year)
    docs = docs[docs["Phase"].notna()].copy()

    comparison_rows = []
    summary_lines = ["# Step 9 Network Path Dependency and Semantic Centrality", ""]

    for phase in PHASES:
        subset = docs[docs["Phase"] == phase].copy()
        graph, node_freq = build_phase_graph(subset, keywords, patterns)
        if graph.number_of_nodes() > 0 and graph.number_of_edges() > 0:
            centrality = nx.eigenvector_centrality(graph, weight="weight", max_iter=5000, tol=1e-08)
        elif graph.number_of_nodes() > 0:
            centrality = {node: 0.0 for node in graph.nodes()}
        else:
            centrality = {}

        metrics = pd.DataFrame(
            {
                "keyword": list(graph.nodes()),
                "category": [taxonomy_lookup.get(node) for node in graph.nodes()],
                "frequency": [graph.nodes[node]["frequency"] for node in graph.nodes()],
                "eigenvector_centrality": [centrality.get(node, 0.0) for node in graph.nodes()],
                "degree": [graph.degree(node) for node in graph.nodes()],
            }
        )
        if not metrics.empty:
            metrics = metrics.sort_values(["eigenvector_centrality", "frequency"], ascending=[False, False]).reset_index(drop=True)
            metrics["centrality_rank"] = np.arange(1, len(metrics) + 1)
        else:
            metrics["centrality_rank"] = []
        metrics.to_csv(OUT_DIR / f"{phase.lower().replace(' ', '')}_network_metrics.csv", index=False)
        render_graph(phase, graph, metrics, taxonomy_lookup)

        summary_lines.append(f"## {phase}")
        summary_lines.append(f"- Nodes: {graph.number_of_nodes()}")
        summary_lines.append(f"- Edges: {graph.number_of_edges()}")
        if not metrics.empty:
            top_terms = ", ".join(
                f"{row.keyword} ({row.eigenvector_centrality:.4f})"
                for row in metrics.head(8).itertuples(index=False)
            )
            summary_lines.append(f"- Top central keywords: {top_terms}")
        else:
            summary_lines.append("- No classified keyword network could be estimated.")
        summary_lines.append("")

        for term in KEY_TERMS:
            row = metrics[metrics["keyword"] == term]
            if row.empty:
                comparison_rows.append(
                    {
                        "phase": phase,
                        "keyword": term,
                        "category": taxonomy_lookup.get(term),
                        "present_in_taxonomy": term in taxonomy_lookup,
                        "present_in_phase_network": False,
                        "frequency": 0,
                        "eigenvector_centrality": np.nan,
                        "centrality_rank": np.nan,
                    }
                )
            else:
                comparison_rows.append(
                    {
                        "phase": phase,
                        "keyword": term,
                        "category": row["category"].iloc[0],
                        "present_in_taxonomy": True,
                        "present_in_phase_network": True,
                        "frequency": int(row["frequency"].iloc[0]),
                        "eigenvector_centrality": float(row["eigenvector_centrality"].iloc[0]),
                        "centrality_rank": int(row["centrality_rank"].iloc[0]),
                    }
                )

    comparison = pd.DataFrame(comparison_rows)
    comparison.to_csv(OUT_DIR / "step9_centrality_comparison.csv", index=False)

    # Add a concise cross-phase interpretation.
    summary_lines.append("## Cross-phase mechanism diagnostics")
    for term in ["household", "thermal comfort", "energy poverty", "fuel poverty", "retrofit", "accessibility"]:
        rows = comparison[comparison["keyword"] == term].copy()
        if rows["present_in_phase_network"].any():
            present = rows[rows["present_in_phase_network"]]
            ranks = ", ".join(f"{r.phase}: {int(r.centrality_rank)}" for r in present.itertuples(index=False))
            summary_lines.append(f"- {term}: observed ranks -> {ranks}")
        else:
            summary_lines.append(f"- {term}: not observed as a central classified node in any phase-level network.")
    (OUT_DIR / "step9_network_summary.md").write_text("\n".join(summary_lines), encoding="utf-8")


if __name__ == "__main__":
    main()
