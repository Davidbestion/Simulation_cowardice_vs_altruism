"""Módulo de análisis y visualización para los resultados de la simulación."""
from .plotting import (
    plot_gene_distribution_single,
    plot_population_single,
    plot_gene_frequencies,
    plot_population_stats,
    plot_predator_population_stats,
    plot_aggregated_population_stats,
    plot_aggregated_predator_population_stats,
    plot_aggregated_gene_frequencies_final,
    plot_aggregated_gene_evolution,
    plot_aggregated_gene_distribution,
    plot_predator_gene_frequencies,
    plot_aggregated_predator_gene_evolution,
)
from .runner import RandomPredatorGene, SimpleExperiment, run_multiple

__all__ = [
    # Visualización — corrida única
    "plot_gene_distribution_single",
    "plot_population_single",
    # Visualización — corrida única (API extendida)
    "plot_gene_frequencies",
    "plot_population_stats",
    "plot_predator_population_stats",
    # Visualización — agregada (múltiples corridas)
    "plot_aggregated_population_stats",
    "plot_aggregated_predator_population_stats",
    "plot_aggregated_gene_frequencies_final",
    "plot_aggregated_gene_evolution",
    "plot_aggregated_gene_distribution",
    "plot_predator_gene_frequencies",
    "plot_aggregated_predator_gene_evolution",
    # Ejecución
    "RandomPredatorGene",
    "SimpleExperiment",
    "run_multiple",
]
