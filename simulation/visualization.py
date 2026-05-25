"""
Funciones de visualización y comparación paramétrica.

Todas las funciones de graficación se centralizan aquí para mantener
el notebook libre de código de presentación (Principio de Responsabilidad Única).

Paleta de colores COLORS exportada para uso en el notebook si se necesita.
"""

from typing import Callable, List, Tuple

import numpy as np
import matplotlib.pyplot as plt

from .models import DayStats
from .engine import SimulationConfig
from .analysis import run_multiple_simulations, extract_series


# ---------------------------------------------------------------------------
# Paleta de colores por tipo de criatura
# ---------------------------------------------------------------------------
COLORS: dict = {
    "altruist":          "#2ecc71",   # Verde
    "coward":            "#e74c3c",   # Rojo
    "total":             "#2c3e50",   # Azul oscuro
    "altruist_green":    "#1abc9c",   # Verde agua
    "altruist_no_green": "#3498db",   # Azul
    "coward_green":      "#e67e22",   # Naranja
    "coward_no_green":   "#9b59b6",   # Violeta
    "deaths":            "#c0392b",   # Rojo oscuro
    "births":            "#27ae60",   # Verde
}


# ---------------------------------------------------------------------------
# Auxiliar interno
# ---------------------------------------------------------------------------
def _plot_band(ax, days: np.ndarray, matrix: np.ndarray, color: str, label: str) -> None:
    """
    Traza la media ± 1 desviación estándar de una serie de tiempo.

    Args:
        ax:     Eje de matplotlib donde dibujar.
        days:   Array 1-D con los días (eje X).
        matrix: Array (num_runs × num_days) con los valores por ejecución.
        color:  Color de la línea y la banda.
        label:  Etiqueta para la leyenda.
    """
    mean = matrix.mean(axis=0)
    std  = matrix.std(axis=0)
    ax.plot(days, mean, color=color, linewidth=2, label=label)
    ax.fill_between(days, np.maximum(0, mean - std), mean + std, alpha=0.25, color=color)


# ---------------------------------------------------------------------------
# Funciones principales de graficación
# ---------------------------------------------------------------------------
def plot_population_evolution(
    all_runs:   List[List[DayStats]],
    config:     SimulationConfig,
    title:      str = "Evolución de la Población",
    show_types: str = "exp1",
) -> None:
    """
    Grafica la evolución de la población a lo largo del tiempo.

    Panel izquierdo: población total (media ± std).
    Panel derecho:   composición de la población (según el experimento).

    Args:
        all_runs:   Resultados de run_multiple_simulations.
        config:     Configuración usada (necesita num_days).
        title:      Título del gráfico.
        show_types: "exp1" o "exp2" → altruistas vs. cobardes.
                    "exp3" → los cuatro fenotipos.
    """
    num_days = config.num_days
    days     = np.arange(1, num_days + 1)
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 6))
    fig.suptitle(title, fontsize=15, fontweight="bold")

    _plot_band(ax1, days, extract_series(all_runs, "total_population", num_days),
               COLORS["total"], "Total")
    ax1.set_xlabel("Día"); ax1.set_ylabel("Cantidad de criaturas")
    ax1.set_title("Población Total"); ax1.legend()

    if show_types in ("exp1", "exp2"):
        _plot_band(ax2, days, extract_series(all_runs, "altruist_count", num_days),
                   COLORS["altruist"], "Altruistas")
        _plot_band(ax2, days, extract_series(all_runs, "coward_count",   num_days),
                   COLORS["coward"],   "Cobardes")
    else:  # exp3
        for attr, label, color in [
            ("altruist_green_count",    "Altruista + Barba Verde", COLORS["altruist_green"]),
            ("altruist_no_green_count", "Altruista + Sin Barba",   COLORS["altruist_no_green"]),
            ("coward_green_count",      "Cobarde + Barba Verde",   COLORS["coward_green"]),
            ("coward_no_green_count",   "Cobarde + Sin Barba",     COLORS["coward_no_green"]),
        ]:
            _plot_band(ax2, days, extract_series(all_runs, attr, num_days), color, label)

    ax2.set_xlabel("Día"); ax2.set_ylabel("Cantidad de criaturas")
    ax2.set_title("Composición de la Población"); ax2.legend()
    plt.tight_layout(); plt.show()


def plot_altruist_fraction(
    all_runs: List[List[DayStats]],
    config:   SimulationConfig,
    title:    str = "Fracción de Altruistas a lo largo del tiempo",
) -> None:
    """
    Grafica la fracción de altruistas en la población a lo largo del tiempo.

    Muestra también la línea de ratio inicial (referencia) y el 50%.

    Args:
        all_runs: Resultados de run_multiple_simulations.
        config:   Configuración usada.
        title:    Título del gráfico.
    """
    num_days = config.num_days
    days     = np.arange(1, num_days + 1)
    alt_m    = extract_series(all_runs, "altruist_count",   num_days)
    total_m  = extract_series(all_runs, "total_population", num_days)
    with np.errstate(divide="ignore", invalid="ignore"):
        frac_m = np.where(total_m > 0, alt_m / total_m, np.nan)
    mean_f = np.nanmean(frac_m, axis=0)
    std_f  = np.nanstd(frac_m,  axis=0)

    fig, ax = plt.subplots(figsize=(10, 5))
    ax.plot(days, mean_f, color=COLORS["altruist"], linewidth=2, label="Fracción altruistas")
    ax.fill_between(days, np.clip(mean_f - std_f, 0, 1),
                    np.clip(mean_f + std_f, 0, 1), alpha=0.3, color=COLORS["altruist"])
    ax.axhline(0.5, color="gray",  linestyle="--", linewidth=1, label="50%")
    ax.axhline(config.initial_altruist_ratio, color="black", linestyle=":", linewidth=1,
               label=f"Ratio inicial ({config.initial_altruist_ratio:.0%})")
    ax.set_xlabel("Día"); ax.set_ylabel("Fracción de altruistas")
    ax.set_ylim(0, 1); ax.set_title(title, fontweight="bold"); ax.legend()
    plt.tight_layout(); plt.show()


def compare_escape_probabilities(
    escape_probs:          List[float],
    config_base:           SimulationConfig,
    strategy_class,
    population_factory_fn: Callable,
    title: str = "Efecto de la Probabilidad de Escape",
) -> None:
    """
    Compara la fracción final de altruistas para distintas probabilidades de escape.

    Para cada valor de escape_probability corre config_base.num_runs simulaciones
    y muestra la fracción media ± std de altruistas al final del último día.

    Args:
        escape_probs:          Lista de probabilidades a comparar (0-1).
        config_base:           Configuración base (escape_probability se sobreescribe).
        strategy_class:        Clase de estrategia a instanciar.
        population_factory_fn: Callable(config) -> List[Creature].
        title:                 Título del gráfico.
    """
    means, stds = [], []
    for ep in escape_probs:
        cfg  = config_base.with_changes(escape_probability=ep)
        runs = run_multiple_simulations(cfg, strategy_class(), population_factory_fn)
        fracs = [r[-1].altruist_count / r[-1].total_population
                 for r in runs if r and r[-1].total_population > 0]
        means.append(float(np.mean(fracs))); stds.append(float(np.std(fracs)))

    fig, ax = plt.subplots(figsize=(10, 5))
    ax.errorbar(escape_probs, means, yerr=stds, fmt="o-", color=COLORS["altruist"],
                capsize=6, linewidth=2, markersize=8, label="Fracción final altruistas")
    ax.axhline(0.5, color="gray", linestyle="--", linewidth=1, label="50%")
    ax.axhline(config_base.initial_altruist_ratio, color="black", linestyle=":", linewidth=1,
               label=f"Ratio inicial ({config_base.initial_altruist_ratio:.0%})")
    ax.set_xlabel("Probabilidad de Escape"); ax.set_ylabel("Fracción Final Altruistas")
    ax.set_ylim(0, 1); ax.set_title(title, fontweight="bold"); ax.legend()
    plt.tight_layout(); plt.show()


def compare_initial_ratios(
    ratios:                List[float],
    config_base:           SimulationConfig,
    strategy_class,
    population_factory_fn: Callable,
    title: str = "Efecto del Ratio Inicial de Altruistas",
) -> None:
    """
    Compara el resultado final para distintas distribuciones iniciales.

    Panel izquierdo: fracción final de altruistas vs. ratio inicial.
    Panel derecho:   población final total vs. ratio inicial.

    Args:
        ratios:                Lista de ratios iniciales (0-1) a comparar.
        config_base:           Configuración base.
        strategy_class:        Clase de estrategia a instanciar.
        population_factory_fn: Callable(config) -> List[Creature].
        title:                 Título del gráfico.
    """
    means_frac, stds_frac, means_pop, stds_pop = [], [], [], []
    for ratio in ratios:
        cfg  = config_base.with_changes(initial_altruist_ratio=ratio)
        runs = run_multiple_simulations(cfg, strategy_class(), population_factory_fn)
        fracs = [r[-1].altruist_count / r[-1].total_population
                 for r in runs if r and r[-1].total_population > 0]
        pops  = [r[-1].total_population for r in runs if r]
        means_frac.append(float(np.mean(fracs))); stds_frac.append(float(np.std(fracs)))
        means_pop.append(float(np.mean(pops)));   stds_pop.append(float(np.std(pops)))

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 5))
    fig.suptitle(title, fontsize=14, fontweight="bold")
    ax1.errorbar(ratios, means_frac, yerr=stds_frac, fmt="o-", color=COLORS["altruist"],
                 capsize=5, linewidth=2, markersize=8)
    ax1.plot(ratios, ratios, "k--", linewidth=1, label="Sin cambio")
    ax1.set_xlabel("Ratio Inicial"); ax1.set_ylabel("Fracción Final Altruistas")
    ax1.set_xlim(0, 1); ax1.set_ylim(0, 1)
    ax1.set_title("Fracción Final vs. Ratio Inicial"); ax1.legend()
    ax2.errorbar(ratios, means_pop, yerr=stds_pop, fmt="o-", color=COLORS["total"],
                 capsize=5, linewidth=2, markersize=8)
    ax2.set_xlabel("Ratio Inicial"); ax2.set_ylabel("Población Final")
    ax2.set_title("Población Final vs. Ratio Inicial")
    plt.tight_layout(); plt.show()


def plot_exp3_composition_bars(
    configs_and_runs: List[Tuple[str, List[List[DayStats]]]],
    title: str = "Composición Final de la Población — Experimento 3",
) -> None:
    """
    Gráfico de barras apiladas: composición final para distintas configuraciones.

    Args:
        configs_and_runs: Lista de tuplas (etiqueta, all_runs) por configuración.
        title:            Título del gráfico.
    """
    phenotypes = [
        ("altruist_green_count",    "Altruista + Barba Verde", COLORS["altruist_green"]),
        ("altruist_no_green_count", "Altruista + Sin Barba",   COLORS["altruist_no_green"]),
        ("coward_green_count",      "Cobarde + Barba Verde",   COLORS["coward_green"]),
        ("coward_no_green_count",   "Cobarde + Sin Barba",     COLORS["coward_no_green"]),
    ]
    labels = [lbl for lbl, _ in configs_and_runs]
    x      = np.arange(len(labels))
    bottom = np.zeros(len(labels))
    fig, ax = plt.subplots(figsize=(max(10, len(labels) * 2), 6))
    for attr, label, color in phenotypes:
        vals = []
        for _, runs in configs_and_runs:
            fracs = [getattr(r[-1], attr) / r[-1].total_population
                     for r in runs if r and r[-1].total_population > 0]
            vals.append(float(np.mean(fracs)) if fracs else 0.0)
        ax.bar(x, vals, bottom=bottom, label=label, color=color,
               edgecolor="white", linewidth=0.5)
        bottom += np.array(vals)
    ax.set_xticks(x); ax.set_xticklabels(labels, rotation=20, ha="right")
    ax.set_ylabel("Fracción de la Población Final"); ax.set_ylim(0, 1)
    ax.set_title(title, fontweight="bold"); ax.legend(loc="upper right")
    plt.tight_layout(); plt.show()
