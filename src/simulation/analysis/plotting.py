"""Plotting utilities for simulation reports.

Funciones disponibles:

Corrida única
- ``plot_gene_distribution_single(reports, title="", show=True)``
- ``plot_population_single(reports, title="", show=True)``
- ``plot_gene_frequencies(reports, save_path=None, show=False, relative=True)``
- ``plot_population_stats(reports, save_path=None, show=False)``
- ``plot_predator_population_stats(reports, save_path=None, show=False)``

Múltiples corridas (agregadas)
- ``plot_aggregated_population_stats(all_reports, title="", save_path=None, show=False)``
- ``plot_aggregated_predator_population_stats(all_reports, save_path=None, show=False)``
- ``plot_aggregated_gene_frequencies_final(all_reports, save_path=None, show=False)``
- ``plot_aggregated_gene_evolution(all_reports, save_path=None, show=False)``
- ``plot_aggregated_gene_distribution(all_reports, title="", save_path=None, show=False)``
- ``plot_predator_gene_frequencies(reports, save_path=None, show=False)``
- ``plot_aggregated_predator_gene_evolution(all_reports, title="", save_path=None, show=False)``

Todos los módulos importan ``matplotlib`` de forma local para que el módulo
pueda importarse aunque ``matplotlib`` no esté instalado.
"""
from __future__ import annotations

from typing import List, Optional
import os
import statistics


def plot_gene_distribution_single(
    reports: List,
    title: str = "",
    show: bool = True,
    save_path: Optional[str] = None,
):
    """Gráfico apilado de frecuencias génicas para una corrida individual.

    Args:
        reports   : Lista de ``DayReport`` de una sola corrida.
        title     : Título del gráfico; si está vacío se usa uno genérico.
        show      : Si es ``True``, llama a ``plt.show()`` al finalizar.
        save_path : Ruta opcional para guardar la figura en disco.
    """
    try:
        import matplotlib.pyplot as plt
    except Exception as exc:
        raise ImportError("matplotlib is required for plotting") from exc

    if not reports:
        raise ValueError("No reports provided")

    gens = [r.generation for r in reports]
    gene_set: set = set()
    for r in reports:
        gene_set.update(r.gene_frequencies.keys())
    genes = sorted(gene_set)

    data = [[r.gene_frequencies.get(g, 0.0) for r in reports] for g in genes]

    fig, ax = plt.subplots(figsize=(10, 5))
    if data:
        ax.stackplot(gens, *data, labels=genes)
    ax.set_xlabel("Generación")
    ax.set_ylabel("Frecuencia relativa")
    ax.set_title(title or "Distribución génica por generación")
    if genes:
        ax.legend(loc="upper right", fontsize=8)
    ax.grid(True, alpha=0.3)

    if save_path:
        import os
        os.makedirs(os.path.dirname(save_path), exist_ok=True)
        fig.savefig(save_path, bbox_inches="tight")
    if show:
        plt.show()
    plt.close(fig)
    return fig


def plot_population_single(
    reports: List,
    title: str = "",
    show: bool = True,
    save_path: Optional[str] = None,
):
    """Gráfico de dinámica poblacional para una corrida individual.

    Muestra población final, individuos comidos y muertos por inanición
    a lo largo de las generaciones.

    Args:
        reports   : Lista de ``DayReport`` de una sola corrida.
        title     : Título del gráfico; si está vacío se usa uno genérico.
        show      : Si es ``True``, llama a ``plt.show()`` al finalizar.
        save_path : Ruta opcional para guardar la figura en disco.
    """
    try:
        import matplotlib.pyplot as plt
    except Exception as exc:
        raise ImportError("matplotlib is required for plotting") from exc

    if not reports:
        raise ValueError("No reports provided")

    gens = [r.generation for r in reports]

    fig, ax = plt.subplots(figsize=(10, 5))
    ax.plot(gens, [r.population_end for r in reports], label="Población (fin de generación)")
    ax.plot(gens, [r.eaten for r in reports], label="Comidos", linestyle="--")
    ax.plot(gens, [r.starved for r in reports], label="Muertos por inanición", linestyle=":")
    ax.set_xlabel("Generación")
    ax.set_ylabel("Individuos")
    ax.set_title(title or "Dinámica poblacional")
    ax.legend(loc="upper right", fontsize=8)
    ax.grid(True, alpha=0.3)

    if save_path:
        import os
        os.makedirs(os.path.dirname(save_path), exist_ok=True)
        fig.savefig(save_path, bbox_inches="tight")
    if show:
        plt.show()
    plt.close(fig)
    return fig


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


def plot_predator_population_stats(reports: List, save_path: Optional[str] = None, show: bool = False):
    try:
        import matplotlib.pyplot as plt
    except Exception as exc:
        raise ImportError("matplotlib is required for plotting") from exc

    gens = [r.generation for r in reports]
    population = [getattr(r, "predator_count_end", 0) for r in reports]
    population_start = [getattr(r, "predator_count_start", 0) for r in reports]

    fig, ax = plt.subplots(figsize=(10, 6))
    ax.plot(gens, population_start, label="Predators (start)", marker="o")
    ax.plot(gens, population, label="Predators (end)", marker="x")
    ax.set_xlabel("Generation")
    ax.set_ylabel("Count")
    ax.set_title("Predator population outcomes per generation")
    ax.legend(loc="upper right")
    ax.grid(True)

    if save_path:
        os.makedirs(os.path.dirname(save_path), exist_ok=True)
        fig.savefig(save_path, bbox_inches="tight")
    if show:
        plt.show()
    plt.close(fig)
    return fig


def plot_aggregated_population_stats(all_reports: List[List], title: str = "", save_path: Optional[str] = None, show: bool = False, plot_individual: bool = True):
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
    ax.set_title(title or "Aggregated population across runs")
    ax.legend(loc="upper right")
    ax.grid(True)

    if save_path:
        os.makedirs(os.path.dirname(save_path), exist_ok=True)
        fig.savefig(save_path, bbox_inches="tight")
    if show:
        plt.show()
    plt.close(fig)
    return fig


def plot_aggregated_predator_population_stats(all_reports: List[List], save_path: Optional[str] = None, show: bool = False, plot_individual: bool = True):
    try:
        import matplotlib.pyplot as plt
    except Exception as exc:
        raise ImportError("matplotlib is required for plotting") from exc

    if not all_reports:
        raise ValueError("No reports provided for aggregation")

    max_gens = max((len(r) for r in all_reports), default=0)
    if max_gens == 0:
        raise ValueError("No generation data found in reports")

    padded = []
    for reports in all_reports:
        series = [getattr(rep, "predator_count_end", 0) for rep in reports]
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
    if plot_individual:
        for run in padded:
            ax.plot(gens, run, color="gray", alpha=0.15, linewidth=0.8, zorder=1)

    lower = [m - s for m, s in zip(means, stds)]
    upper = [m + s for m, s in zip(means, stds)]
    ax.fill_between(gens, lower, upper, color="blue", alpha=0.18, label="±1 std", zorder=2)
    ax.plot(gens, lower, color="blue", alpha=0.6, linewidth=0.8, linestyle="--", zorder=3)
    ax.plot(gens, upper, color="blue", alpha=0.6, linewidth=0.8, linestyle="--", zorder=3)
    ax.plot(gens, means, color="blue", lw=2, marker="o", markersize=4, label="Mean predator population (end)", zorder=4)
    ax.set_xlabel("Generation")
    ax.set_ylabel("Predator population (end)")
    ax.set_title("Aggregated predator population across runs")
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


def plot_aggregated_gene_distribution(all_reports: List[List], title: str = "", save_path: Optional[str] = None, show: bool = False, relative: bool = True, plot_individual: bool = True):
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
        # Only average over runs where herbivores are still alive at this generation
        alive_freqs = []
        for reports in all_reports:
            if gen_idx < len(reports):
                freqs = reports[gen_idx].gene_frequencies
                if freqs:
                    alive_freqs.append(freqs)
        for g in genes:
            if alive_freqs:
                mean_series[g].append(statistics.mean(f.get(g, 0.0) for f in alive_freqs))
            else:
                mean_series[g].append(0.0)

    gens = list(range(1, max_gens + 1))

    # Prepare data for stackplot in the same gene order as `genes`
    data = [mean_series[g] for g in genes]

    fig, ax = plt.subplots(figsize=(10, 6))
    if data:
        ax.stackplot(gens, *data, labels=genes)

    # Overlay individual run boundary lines, stopping at extinction
    if plot_individual:
        extinction_label_used = False
        for reports in all_reports:
            last_alive = -1
            for gen_idx in range(len(reports)):
                if reports[gen_idx].gene_frequencies:
                    last_alive = gen_idx
            if last_alive < 0:
                continue
            went_extinct = last_alive < max_gens - 1
            n = last_alive + 1
            if len(genes) >= 2:
                cumsum = [0.0] * n
                for g in genes[:-1]:
                    for gen_idx in range(n):
                        freqs = reports[gen_idx].gene_frequencies if gen_idx < len(reports) else {}
                        cumsum[gen_idx] += freqs.get(g, 0.0)
                    ax.plot(
                        gens[:n], list(cumsum),
                        color="black", alpha=0.25, linewidth=0.8, zorder=3,
                    )
            if went_extinct:
                label = "Extinción" if not extinction_label_used else None
                ax.plot(
                    gens[last_alive], 1.0,
                    marker="x", color="red", alpha=0.5, markersize=5,
                    markeredgewidth=1.2, zorder=5, label=label,
                )
                extinction_label_used = True

    ax.set_xlabel("Generation")
    ax.set_ylabel("Relative frequency" if relative else "Counts")
    ax.set_title(title or "Aggregated gene distribution per generation (mean across runs)")
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


def plot_predator_gene_frequencies(reports: List, save_path: Optional[str] = None, show: bool = False, relative: bool = True):
    try:
        import matplotlib.pyplot as plt
    except Exception as exc:
        raise ImportError("matplotlib is required for plotting") from exc

    if not reports:
        raise ValueError("No reports provided")

    gens = [r.generation for r in reports]
    gene_set = set()
    for r in reports:
        gene_set.update(getattr(r, "predator_gene_frequencies", {}).keys())
    genes = sorted(gene_set)

    if relative:
        data = [[getattr(r, "predator_gene_frequencies", {}).get(g, 0.0) for r in reports] for g in genes]
        ylabel = "Relative frequency"
        title = "Predator gene distribution per generation (relative)"
    else:
        data = [[int(round(getattr(r, "predator_gene_frequencies", {}).get(g, 0.0) * getattr(r, "predator_count_end", 0))) for r in reports] for g in genes]
        ylabel = "Counts"
        title = "Predator gene distribution per generation (counts)"

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


def plot_aggregated_predator_gene_evolution(all_reports: List[List], title: str = "", save_path: Optional[str] = None, show: bool = False, plot_individual: bool = True):
    try:
        import matplotlib.pyplot as plt
    except Exception as exc:
        raise ImportError("matplotlib is required for plotting") from exc

    if not all_reports:
        raise ValueError("No reports provided for aggregation")

    max_gens = max((len(r) for r in all_reports), default=0)
    if max_gens == 0:
        raise ValueError("No generation data found in reports")

    gene_set = set()
    for reports in all_reports:
        for rep in reports:
            gene_set.update(getattr(rep, "predator_gene_frequencies", {}).keys())
    genes = sorted(gene_set)

    mean_series = {g: [] for g in genes}
    for gen_idx in range(max_gens):
        # Collect only runs where predators are still alive at this generation
        alive_freqs = []
        for reports in all_reports:
            if gen_idx < len(reports):
                freqs = getattr(reports[gen_idx], "predator_gene_frequencies", {})
                if freqs:
                    alive_freqs.append(freqs)
        for g in genes:
            if alive_freqs:
                mean_series[g].append(statistics.mean(f.get(g, 0.0) for f in alive_freqs))
            else:
                mean_series[g].append(0.0)

    gens = list(range(1, max_gens + 1))
    data = [mean_series[g] for g in genes]

    fig, ax = plt.subplots(figsize=(10, 6))
    if data:
        ax.stackplot(gens, *data, labels=genes)

    if plot_individual:
        extinction_label_used = False
        for reports in all_reports:
            last_alive = -1
            for gen_idx in range(len(reports)):
                if getattr(reports[gen_idx], "predator_gene_frequencies", {}):
                    last_alive = gen_idx
            if last_alive < 0:
                continue
            went_extinct = last_alive < max_gens - 1
            n = last_alive + 1
            if len(genes) >= 2:
                cumsum = [0.0] * n
                for g in genes[:-1]:
                    for gen_idx in range(n):
                        freqs = getattr(reports[gen_idx], "predator_gene_frequencies", {}) if gen_idx < len(reports) else {}
                        cumsum[gen_idx] += freqs.get(g, 0.0)
                    ax.plot(
                        gens[:n], list(cumsum),
                        color="black", alpha=0.25, linewidth=0.8, zorder=3,
                    )
            if went_extinct:
                label = "Extinción" if not extinction_label_used else None
                ax.plot(
                    gens[last_alive], 1.0,
                    marker="x", color="red", alpha=0.5, markersize=5,
                    markeredgewidth=1.2, zorder=5, label=label,
                )
                extinction_label_used = True

    ax.set_xlabel("Generation")
    ax.set_ylabel("Relative frequency")
    ax.set_title(title or "Predator gene frequency evolution (aggregated)")
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


def plot_aggregated_coevolution(
    all_reports: List[List],
    title: str = "",
    save_path: Optional[str] = None,
    show: bool = False,
):
    """Evolución temporal de herbívoros y depredadores en el mismo gráfico (eje dual).

    El eje izquierdo (verde) muestra la población de herbívoros; el derecho (rojo)
    la de depredadores. Se superponen las corridas individuales (muy tenues), la
    banda ±1 std y la media para cada especie.
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

    gens = list(range(1, max_gens + 1))

    herb_padded, pred_padded = [], []
    for reports in all_reports:
        h = [rep.population_end for rep in reports]
        p = [getattr(rep, "predator_count_end", 0) for rep in reports]
        if len(h) < max_gens:
            h = h + [0] * (max_gens - len(h))
            p = p + [0] * (max_gens - len(p))
        herb_padded.append(h)
        pred_padded.append(p)

    def _mean_std(padded):
        means, stds = [], []
        for i in range(max_gens):
            vals = [run[i] for run in padded]
            means.append(statistics.mean(vals))
            stds.append(statistics.stdev(vals) if len(vals) > 1 else 0.0)
        return means, stds

    herb_means, herb_stds = _mean_std(herb_padded)
    pred_means, pred_stds = _mean_std(pred_padded)

    herb_color = "#2ca02c"
    pred_color = "#d62728"

    fig, ax = plt.subplots(figsize=(10, 6))

    for run in herb_padded:
        ax.plot(gens, run, color=herb_color, alpha=0.08, linewidth=0.7, zorder=1)
    for run in pred_padded:
        ax.plot(gens, run, color=pred_color, alpha=0.08, linewidth=0.7, zorder=1)

    ax.fill_between(
        gens,
        [m - s for m, s in zip(herb_means, herb_stds)],
        [m + s for m, s in zip(herb_means, herb_stds)],
        color=herb_color, alpha=0.15, zorder=2,
    )
    ax.fill_between(
        gens,
        [max(0, m - s) for m, s in zip(pred_means, pred_stds)],
        [m + s for m, s in zip(pred_means, pred_stds)],
        color=pred_color, alpha=0.15, zorder=2,
    )

    ax.plot(gens, herb_means, color=herb_color, lw=2, label="Herbívoros (media)", zorder=3)
    ax.plot(gens, pred_means, color=pred_color, lw=2, label="Depredadores (media)", zorder=3)

    ax.set_xlabel("Generation")
    ax.set_ylabel("Individuos")
    ax.set_title(title or "Coevolución poblacional (herbívoros y depredadores)")
    ax.legend(loc="upper right")
    ax.grid(True, alpha=0.3)

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
