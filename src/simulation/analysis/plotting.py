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
    ax.legend()
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
        ax.legend(loc="upper left")

    if save_path:
        os.makedirs(os.path.dirname(save_path), exist_ok=True)
        fig.savefig(save_path, bbox_inches="tight")
    if show:
        plt.show()
    plt.close(fig)
    return fig
