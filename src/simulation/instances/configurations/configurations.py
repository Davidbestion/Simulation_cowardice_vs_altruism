"""Configuraciones de referencia compartidas.

Las configuraciones específicas de cada experimento viven en sus respectivos
archivos ``experiments/experiment_N.py``.  Este módulo expone únicamente la
configuración por defecto usada como punto de partida en experimentos ad-hoc.
"""
from simulation.core.simulation import SimulationConfig

default_config = SimulationConfig(
    num_trees=25,
    tree_capacity_min=2,
    tree_capacity_max=6,
    num_generations=200,
    initial_population=80,
    initial_predators=8,
    offspring_min=1,
    offspring_max=2,
    predator_offspring_min=1,
    predator_offspring_max=2,
    base_detection_prob=0.30,
    altruist_escape_prob=0.50,
    predator_hunt_capacity=1,
    seed=42,
)

__all__ = ["default_config"]
