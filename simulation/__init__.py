"""
Paquete simulation: simulación evolutiva de cobardía vs. altruismo.

Estructura:
    models.py       → Trait, BeardColor, Creature, DayStats
    strategies.py   → PredatorEncounterStrategy y subclases por experimento
    engine.py       → SimulationConfig, PopulationFactory, Simulation
    analysis.py     → run_multiple_simulations, extract_series
    visualization.py → COLORS y todas las funciones de graficación

Uso típico en el notebook:
    from simulation import *
"""

from .models import Trait, BeardColor, Creature, DayStats
from .strategies import (
    PredatorEncounterStrategy,
    BaseEncounterStrategy,
    Experiment1Strategy,
    Experiment2Strategy,
    Experiment3Strategy,
)
from .engine import SimulationConfig, PopulationFactory, Simulation
from .analysis import run_multiple_simulations, extract_series
from .visualization import (
    COLORS,
    plot_population_evolution,
    plot_altruist_fraction,
    compare_escape_probabilities,
    compare_initial_ratios,
    plot_exp3_composition_bars,
)

__all__ = [
    # Modelos
    "Trait", "BeardColor", "Creature", "DayStats",
    # Estrategias
    "PredatorEncounterStrategy", "BaseEncounterStrategy",
    "Experiment1Strategy", "Experiment2Strategy", "Experiment3Strategy",
    # Motor
    "SimulationConfig", "PopulationFactory", "Simulation",
    # Análisis
    "run_multiple_simulations", "extract_series",
    # Visualización
    "COLORS",
    "plot_population_evolution", "plot_altruist_fraction",
    "compare_escape_probabilities", "compare_initial_ratios",
    "plot_exp3_composition_bars",
]
