"""Plotting utilities for simulation reports.

Provides:
- `plot_population_stats(reports, save_path=None, show=False)`
- `plot_gene_frequencies(reports, save_path=None, show=False, relative=True)`

These functions import `matplotlib` locally so the module can be imported
even if `matplotlib` is not installed; attempting to plot will raise a
clear ImportError.
"""
from __future__ import annotations

from typing import List, Optional
import os
import statistics


def plot_population_stats(reports: List, save_path: Optional[str] = None, show: bool = False):
    try:
        import matplotlib.pyplot as plt
    except Exception as exc:
        raise ImportError("matplotlib is required for plotting") from exc

    gens = [r.generation for r in reports]
    population = [r.population_end for r in reports]
    eaten = [r.eaten for r in reports]
    starved = [r.starved for r in reports]
    survived = [r.survived for r in reports]

    fig, ax = plt.subplots(figsize=(10, 6))
    ax.plot(gens, population, label="Population (end)", marker="o")
    ax.plot(gens, eaten, label="Eaten", marker="x")
    ax.plot(gens, starved, label="Starved", marker="s")
    ax.plot(gens, survived, label="Survived", marker="^")
    ax.set_xlabel("Generation")
    ax.set_ylabel("Count")
    ax.set_title("Population outcomes per generation")
    ax.legend(loc="upper right")
    ax.grid(True)

    if save_path:
        os.makedirs(os.path.dirname(save_path), exist_ok=True)
        fig.savefig(save_path, bbox_inches="tight")
    if show:
        plt.show()
    plt.close(fig)
    return fig


def plot_aggregated_population_stats(all_reports: List[List], save_path: Optional[str] = None, show: bool = False, plot_individual: bool = True):
    try:
        import matplotlib.pyplot as plt
    except Exception as exc:
        raise ImportError("matplotlib is required for plotting") from exc

    if not all_reports:
        raise ValueError("No reports provided for aggregation")

    # Determine max generations across runs
    max_gens = max((len(r) for r in all_reports), default=0)
    if max_gens == 0:
        raise ValueError("No generation data found in reports")

    # Build padded series of population_end per run
    padded = []
    for reports in all_reports:
        series = [rep.population_end for rep in reports]
        if len(series) < max_gens:
            series = series + [0] * (max_gens - len(series))
        padded.append(series)

    gens = list(range(1, max_gens + 1))
    means = []
    stds = []
    for i in range(max_gens):
        vals = [run[i] for run in padded]
        means.append(statistics.mean(vals))
        stds.append(statistics.stdev(vals) if len(vals) > 1 else 0.0)

    fig, ax = plt.subplots(figsize=(10, 6))
    # plot individual runs first with low z-order so they stay beneath summary visuals
    if plot_individual:
        for run in padded:
            ax.plot(gens, run, color="gray", alpha=0.15, linewidth=0.8, zorder=1)

    lower = [m - s for m, s in zip(means, stds)]
    upper = [m + s for m, s in zip(means, stds)]
    # draw the std band above individual runs
    ax.fill_between(gens, lower, upper, color="red", alpha=0.18, label="±1 std", zorder=2)
    # outline the band so it remains visible when many faint runs overlap
    ax.plot(gens, lower, color="red", alpha=0.6, linewidth=0.8, linestyle="--", zorder=3)
    ax.plot(gens, upper, color="red", alpha=0.6, linewidth=0.8, linestyle="--", zorder=3)
    # finally draw the mean on top
    ax.plot(gens, means, color="red", lw=2, marker="o", markersize=4, label="Mean population (end)", zorder=4)
    ax.set_xlabel("Generation")
    ax.set_ylabel("Population (end)")
    ax.set_title("Aggregated population across runs")
    ax.legend(loc="upper right")
    ax.grid(True)

    if save_path:
        os.makedirs(os.path.dirname(save_path), exist_ok=True)
        fig.savefig(save_path, bbox_inches="tight")
    if show:
        plt.show()
    plt.close(fig)
    return fig


def plot_aggregated_gene_frequencies_final(all_reports: List[List], save_path: Optional[str] = None, show: bool = False, top_n: Optional[int] = None):
    try:
        import matplotlib.pyplot as plt
    except Exception as exc:
        raise ImportError("matplotlib is required for plotting") from exc

    if not all_reports:
        raise ValueError("No reports provided for aggregation")

    # Collect final gene frequency dicts from each run
    final_freqs = []
    for reports in all_reports:
        if not reports:
            continue
        final_freqs.append(reports[-1].gene_frequencies)

    if not final_freqs:
        raise ValueError("No final generation data found in reports")

    gene_set = set()
    for d in final_freqs:
        gene_set.update(d.keys())
    genes = sorted(gene_set)

    import math

    means = []
    stds = []
    for g in genes:
        vals = [d.get(g, 0.0) for d in final_freqs]
        means.append(statistics.mean(vals))
        stds.append(statistics.stdev(vals) if len(vals) > 1 else 0.0)

    # Optionally select top_n genes by mean frequency
    if top_n is not None and top_n < len(genes):
        combined = sorted(zip(genes, means, stds), key=lambda x: x[1], reverse=True)[:top_n]
        genes, means, stds = zip(*combined)

    x = list(range(len(genes)))
    fig, ax = plt.subplots(figsize=(10, 6))
    ax.bar(x, means, yerr=stds, align="center", alpha=0.8)
    ax.set_xticks(x)
    ax.set_xticklabels(genes, rotation=45, ha="right")
    ax.set_ylabel("Average relative frequency (final generation)")
    ax.set_title("Aggregated gene distribution (final generation)")
    ax.grid(True, axis="y")

    if save_path:
        os.makedirs(os.path.dirname(save_path), exist_ok=True)
        fig.savefig(save_path, bbox_inches="tight")
    if show:
        plt.show()
    plt.close(fig)
    return fig


def plot_aggregated_gene_evolution(all_reports: List[List], save_path: Optional[str] = None, show: bool = False, top_n: int = 6):
    try:
        import matplotlib.pyplot as plt
    except Exception as exc:
        raise ImportError("matplotlib is required for plotting") from exc

    if not all_reports:
        raise ValueError("No reports provided for aggregation")

    max_gens = max((len(r) for r in all_reports), default=0)
    if max_gens == 0:
        raise ValueError("No generation data found in reports")

    # Collect all gene names
    gene_set = set()
    for reports in all_reports:
        for rep in reports:
            gene_set.update(rep.gene_frequencies.keys())
    genes = sorted(gene_set)

    # Build per-generation mean frequency per gene
    mean_series = {g: [] for g in genes}
    for gen_idx in range(max_gens):
        for g in genes:
            vals = []
            for reports in all_reports:
                if gen_idx < len(reports):
                    vals.append(reports[gen_idx].gene_frequencies.get(g, 0.0))
                else:
                    vals.append(0.0)
            mean_series[g].append(statistics.mean(vals))

    # Select top_n genes by average over time
    avg_over_time = {g: statistics.mean(mean_series[g]) for g in genes}
    top_genes = sorted(avg_over_time.items(), key=lambda x: x[1], reverse=True)[:top_n]
    top_names = [g for g, _ in top_genes]

    gens = list(range(1, max_gens + 1))
    fig, ax = plt.subplots(figsize=(10, 6))
    for g in top_names:
        ax.plot(gens, mean_series[g], label=g)

    ax.set_xlabel("Generation")
    ax.set_ylabel("Average relative frequency")
    ax.set_title("Gene frequency evolution (aggregated)")
    ax.legend(loc="upper right")
    ax.grid(True)

    if save_path:
        os.makedirs(os.path.dirname(save_path), exist_ok=True)
        fig.savefig(save_path, bbox_inches="tight")
    if show:
        plt.show()
    plt.close(fig)
    return fig


def plot_aggregated_gene_distribution(all_reports: List[List], save_path: Optional[str] = None, show: bool = False, relative: bool = True, plot_individual: bool = False):
    """Plot stacked gene distribution per generation averaged across runs.

    For each generation index, compute the mean relative frequency of each gene
    across the provided runs, then create a stackplot like `plot_gene_frequencies`
    but using the averaged series.

    If plot_individual is True, overlay each individual run's gene boundary lines
    as faint semi-transparent lines. For two genes this produces exactly one
    boundary line per run (the frequency of the first gene); for N genes there
    are N-1 boundary lines (cumulative sums).
    """
    try:
        import matplotlib.pyplot as plt
    except Exception as exc:
        raise ImportError("matplotlib is required for plotting") from exc

    if not all_reports:
        raise ValueError("No reports provided for aggregation")

    max_gens = max((len(r) for r in all_reports), default=0)
    if max_gens == 0:
        raise ValueError("No generation data found in reports")

    # collect all gene names across all runs and gens
    gene_set = set()
    for reports in all_reports:
        for rep in reports:
            gene_set.update(rep.gene_frequencies.keys())
    genes = sorted(gene_set)

    # Build averaged series per gene per generation
    mean_series = {g: [] for g in genes}
    for gen_idx in range(max_gens):
        for g in genes:
            vals = []
            for reports in all_reports:
                if gen_idx < len(reports):
                    vals.append(reports[gen_idx].gene_frequencies.get(g, 0.0))
                else:
                    vals.append(0.0)
            mean_series[g].append(statistics.mean(vals))

    gens = list(range(1, max_gens + 1))

    # Prepare data for stackplot in the same gene order as `genes`
    data = [mean_series[g] for g in genes]

    fig, ax = plt.subplots(figsize=(10, 6))
    stack_polys = []
    if data:
        stack_polys = ax.stackplot(gens, *data, labels=genes)

    # Overlay individual run boundary lines
    if plot_individual and len(genes) >= 2:
        # Extract the fill color of each stacked area to tint the boundary lines
        colors = [poly.get_facecolor()[0] for poly in stack_polys]
        for reports in all_reports:
            cumsum = [0.0] * max_gens
            for k, g in enumerate(genes[:-1]):
                for gen_idx in range(max_gens):
                    val = (
                        reports[gen_idx].gene_frequencies.get(g, 0.0)
                        if gen_idx < len(reports)
                        else 0.0
                    )
                    cumsum[gen_idx] += val
                ax.plot(
                    gens,
                    list(cumsum),
                    color="black",
                    alpha=0.25,
                    linewidth=0.8,
                    zorder=3,
                )

    ax.set_xlabel("Generation")
    ax.set_ylabel("Relative frequency" if relative else "Counts")
    ax.set_title("Aggregated gene distribution per generation (mean across runs)")
    if genes:
        ax.legend(loc="upper right")
    ax.grid(True)

    if save_path:
        os.makedirs(os.path.dirname(save_path), exist_ok=True)
        fig.savefig(save_path, bbox_inches="tight")
    if show:
        plt.show()
    plt.close(fig)
    return fig


def plot_gene_frequencies(reports: List, save_path: Optional[str] = None, show: bool = False, relative: bool = True):
    try:
        import matplotlib.pyplot as plt
    except Exception as exc:
        raise ImportError("matplotlib is required for plotting") from exc

    if not reports:
        raise ValueError("No reports provided")

    gens = [r.generation for r in reports]
    # Collect gene names
    gene_set = set()
    for r in reports:
        gene_set.update(r.gene_frequencies.keys())
    genes = sorted(gene_set)

    if relative:
        data = [[r.gene_frequencies.get(g, 0.0) for r in reports] for g in genes]
        ylabel = "Relative frequency"
        title = "Gene distribution per generation (relative)"
    else:
        # Convert relative frequencies to counts using population_end
        data = [[int(round(r.gene_frequencies.get(g, 0.0) * r.population_end)) for r in reports] for g in genes]
        ylabel = "Counts"
        title = "Gene distribution per generation (counts)"

    fig, ax = plt.subplots(figsize=(10, 6))
    if data:
        ax.stackplot(gens, *data, labels=genes)
    ax.set_xlabel("Generation")
    ax.set_ylabel(ylabel)
    ax.set_title(title)
    if genes:
        ax.legend(loc="upper right")

    if save_path:
        os.makedirs(os.path.dirname(save_path), exist_ok=True)
        fig.savefig(save_path, bbox_inches="tight")
    if show:
        plt.show()
    plt.close(fig)
    return fig
