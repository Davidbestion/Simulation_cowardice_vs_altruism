"""
Utilidades de análisis: ejecución múltiple y extracción de series temporales.
"""

import random
from typing import Callable, List

import numpy as np

from .models import DayStats
from .engine import SimulationConfig, Simulation
from .strategies import PredatorEncounterStrategy


def run_multiple_simulations(
    config:                SimulationConfig,
    strategy:              PredatorEncounterStrategy,
    population_factory_fn: Callable,
) -> List[List[DayStats]]:
    """
    Ejecuta la simulación num_runs veces con semillas distintas.

    Cada ejecución usa una semilla diferente (pero derivada de random_seed)
    para garantizar variabilidad entre ejecuciones y reproducibilidad global.

    Args:
        config:                Configuración de la simulación.
        strategy:              Estrategia de encuentro a utilizar.
        population_factory_fn: Callable(config) -> List[Creature] que crea
                               la población inicial para cada ejecución.

    Returns:
        Lista de listas de DayStats (una lista por ejecución).
        Cada lista interna tiene entre 1 y config.num_days elementos;
        puede ser más corta si la población se extingue antes.
    """
    all_runs: List[List[DayStats]] = []
    for run_idx in range(config.num_runs):
        if config.random_seed is not None:
            random.seed(config.random_seed + run_idx)
        population = population_factory_fn(config)
        sim        = Simulation(config, strategy, population)
        all_runs.append(sim.run())
    return all_runs


def extract_series(
    all_runs:  List[List[DayStats]],
    attribute: str,
    num_days:  int,
) -> np.ndarray:
    """
    Extrae una serie de tiempo de un atributo de DayStats.

    Args:
        all_runs:  Resultados de múltiples ejecuciones.
        attribute: Nombre del atributo de DayStats a extraer
                   (e.g., 'total_population', 'altruist_count').
        num_days:  Número de días total de la simulación.

    Returns:
        Array numpy de forma (num_runs, num_days).
        Si una ejecución termina antes por extinción, las posiciones
        restantes se rellenan con 0.
    """
    matrix = np.zeros((len(all_runs), num_days))
    for r, run in enumerate(all_runs):
        for d, stats in enumerate(run):
            if d < num_days:
                matrix[r, d] = getattr(stats, attribute)
    return matrix
