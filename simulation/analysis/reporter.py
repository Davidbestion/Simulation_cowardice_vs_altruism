"""
simulation/analysis/reporter.py
=================================
Text summaries and matplotlib plots for ExperimentResult objects.

Functions
---------
print_summary(result)
    Print a concise text report with gene frequency history table.

plot_results(results, save_path, show)
    Draw population-size and gene-frequency plots for one or more
    experiments.  Requires matplotlib (``pip install matplotlib``).
"""

from __future__ import annotations

import os
from typing import List, Optional

from simulation.experiments.base import ExperimentResult


# ---------------------------------------------------------------------------
# Text report
# ---------------------------------------------------------------------------

def print_summary(result: ExperimentResult) -> None:
    """Print a formatted text summary of an experiment result."""
    reports = result.reports
    if not reports:
        print(f"No data for experiment: {result.name}")
        return

    fr = reports[-1]
    width = 62

    print(f"\n{'─' * width}")
    print(f"  SUMMARY  {result.name}")
    print(f"{'─' * width}")
    print(f"  Generations completed : {len(reports)}")
    print(f"  Final population      : {fr.population_end}")

    if fr.gene_frequencies:
        print(f"\n  Final gene frequencies:")
        for gene, freq in sorted(fr.gene_frequencies.items()):
            bar = "█" * int(freq * 35)
            empty = "░" * (35 - int(freq * 35))
            print(f"    {gene:25s} {freq:5.1%}  {bar}{empty}")
    else:
        print("  (No genes in final population)")

    # Trajectory table (every 10 gens)
    history = result.gene_frequency_history()
    if history:
        genes_sorted = sorted(history)
        header_genes = "  ".join(f"{g[:10]:>10}" for g in genes_sorted)
        print(f"\n  Gene frequency trajectory (sampled every 10 generations):")
        print(f"    {'Gen':>5}  {header_genes}")
        print(f"    {'---':>5}  {'  '.join(['----------'] * len(genes_sorted))}")
        for i, r in enumerate(reports):
            if i % 10 == 0 or i == len(reports) - 1:
                row_vals = "  ".join(
                    f"{r.gene_frequencies.get(g, 0.0):>10.1%}"
                    for g in genes_sorted
                )
                print(f"    {i:>5}  {row_vals}")
    print()


# ---------------------------------------------------------------------------
# Matplotlib plots
# ---------------------------------------------------------------------------

_GENE_COLORS = [
    "#e41a1c",  # red
    "#377eb8",  # blue
    "#4daf4a",  # green
    "#984ea3",  # purple
    "#ff7f00",  # orange
    "#a65628",  # brown
    "#f781bf",  # pink
    "#999999",  # grey
]


def plot_results(
    results: List[ExperimentResult],
    save_path: Optional[str] = None,
    show: bool = True,
) -> None:
    """
    Plot population size and gene frequencies for each experiment.

    Parameters
    ----------
    results:
        List of ExperimentResult objects to plot.
    save_path:
        If provided, save the figure to this file path (PNG/SVG/PDF).
    show:
        If True, display the figure interactively (calls ``plt.show()``).
    """
    try:
        import matplotlib.pyplot as plt
        import matplotlib.gridspec as gridspec
    except ImportError:
        print(
            "[reporter] matplotlib not found.  "
            "Install it with:  pip install matplotlib"
        )
        return

    n = len(results)
    if n == 0:
        return

    fig = plt.figure(figsize=(14, 5 * n))
    gs = gridspec.GridSpec(n, 2, figure=fig, hspace=0.45, wspace=0.35)

    for row, result in enumerate(results):
        reports = result.reports
        gens = list(range(len(reports)))

        # ── Population size ──────────────────────────────────────────
        ax_pop = fig.add_subplot(gs[row, 0])
        pop = [r.population_end for r in reports]
        survived = [r.survived for r in reports]
        eaten = [r.eaten for r in reports]
        starved = [r.starved for r in reports]

        ax_pop.plot(gens, pop, color="black", linewidth=2, label="Population (end)")
        ax_pop.plot(gens, survived, color="#4daf4a", linewidth=1,
                    linestyle="--", label="Survived")
        ax_pop.plot(gens, eaten, color="#e41a1c", linewidth=1,
                    linestyle=":", label="Eaten")
        ax_pop.plot(gens, starved, color="#ff7f00", linewidth=1,
                    linestyle="-.", label="Starved")
        ax_pop.set_title(f"{result.name}\nPopulation dynamics", fontsize=10)
        ax_pop.set_xlabel("Generation")
        ax_pop.set_ylabel("Count")
        ax_pop.legend(fontsize=8, loc="upper right")
        ax_pop.grid(True, alpha=0.25)

        # ── Gene frequencies ─────────────────────────────────────────
        ax_genes = fig.add_subplot(gs[row, 1])
        history = result.gene_frequency_history()

        if history:
            # Group genes that have identical frequency trajectories so
            # we don't plot redundant overlapping lines (useful when
            # two genes always co-occur, e.g. green_beard + selective_altruist
            # in Exp03).  We round frequencies to avoid tiny FP differences.
            signature_map = {}  # signature -> list of (gene, freqs)
            for gene, freqs in sorted(history.items()):
                sig = tuple(round(x, 6) for x in freqs)
                signature_map.setdefault(sig, []).append((gene, freqs))

            # Sort groups by descending peak frequency so important lines get
            # stable colors near the front.
            groups = sorted(
                signature_map.items(), key=lambda kv: -max(kv[0]) if kv[0] else 0
            )

            for i, (sig, items) in enumerate(groups):
                genes_in_group = [g for g, _ in items]
                freqs = items[0][1]
                if len(genes_in_group) == 1:
                    label = genes_in_group[0]
                else:
                    # join short lists, or abbreviate if too many
                    if len(genes_in_group) <= 3:
                        label = "/".join(genes_in_group)
                    else:
                        label = f"{genes_in_group[0]} (+{len(genes_in_group)-1})"

                ax_genes.plot(
                    gens,
                    freqs,
                    color=_GENE_COLORS[i % len(_GENE_COLORS)],
                    linewidth=2,
                    label=label,
                )
        else:
            ax_genes.text(
                0.5, 0.5, "(no genes)",
                ha="center", va="center", transform=ax_genes.transAxes,
                fontsize=12, color="grey",
            )

        ax_genes.set_title(f"{result.name}\nGene frequencies", fontsize=10)
        ax_genes.set_xlabel("Generation")
        ax_genes.set_ylabel("Frequency")
        ax_genes.set_ylim(-0.02, 1.05)
        ax_genes.axhline(0.5, color="grey", linewidth=0.5, linestyle="--")
        ax_genes.legend(fontsize=9, loc="upper right")
        ax_genes.grid(True, alpha=0.25)

    if save_path:
        dir_name = os.path.dirname(save_path)
        if dir_name:
            os.makedirs(dir_name, exist_ok=True)
        plt.savefig(save_path, dpi=150, bbox_inches="tight")
        print(f"[reporter] Plot saved → {save_path}")

    if show:
        plt.show()
    else:
        plt.close(fig)
