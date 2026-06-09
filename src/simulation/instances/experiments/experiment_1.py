"""Experimento 1 — Cobardía pura (línea base).

Población homogénea de CowardGene.  Establece la dinámica de referencia
bajo depredación aleatoria (RandomPredatorGene).
"""
from simulation.core import SimulationConfig, CowardGene
from simulation.analysis.runner import SimpleExperiment, RandomPredatorGene

_config = SimulationConfig(
    num_trees=25,
    tree_capacity_min=2,
    tree_capacity_max=2,
    num_generations=100,
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

exp1 = SimpleExperiment(
    name="Experimento 1 — Cobardía pura",
    description=(
        "Población de referencia compuesta íntegramente por individuos portadores de CowardGene. "
        "Establece la dinámica de equilibrio bajo una estrategia individualista sin cooperación."
    ),
    config=_config,
    herbivore_specs=[(lambda: [CowardGene()], 1.0)],
    predator_specs=[(lambda: [RandomPredatorGene()], 1.0)],
)
