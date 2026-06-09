"""Experimento 2 — Cobardía vs Altruismo puro.

Tres condiciones:
  2A — p_escape=0.50, corrida única (seed=42)
  2B — p_escape=0.90, corrida única (seed=42)
  2C — p_escape=0.90, validación estadística 30 corridas (seed base=0)
"""
from simulation.core import SimulationConfig, CowardGene, AltruistGene
from simulation.analysis.runner import SimpleExperiment, RandomPredatorGene

_herbivore_specs = [
    (lambda: [CowardGene()],   0.50),
    (lambda: [AltruistGene()], 0.50),
]
_predator_specs = [(lambda: [RandomPredatorGene()], 1.0)]

exp2a = SimpleExperiment(
    name="Experimento 2A — Cobardía vs Altruismo (p_escape=0.50)",
    description="50 % CowardGene / 50 % AltruistGene; probabilidad de escape del altruista = 0.50.",
    config=SimulationConfig(
        num_trees=25, tree_capacity_min=2, tree_capacity_max=2,
        num_generations=100, initial_population=80, initial_predators=8,
        offspring_min=1, offspring_max=2,
        predator_offspring_min=1, predator_offspring_max=2,
        base_detection_prob=0.30, altruist_escape_prob=0.50,
        predator_hunt_capacity=1, seed=42,
    ),
    herbivore_specs=_herbivore_specs,
    predator_specs=_predator_specs,
)

exp2b = SimpleExperiment(
    name="Experimento 2B — Cobardía vs Altruismo (p_escape=0.90)",
    description="50 % CowardGene / 50 % AltruistGene; probabilidad de escape del altruista = 0.90.",
    config=SimulationConfig(
        num_trees=25, tree_capacity_min=2, tree_capacity_max=2,
        num_generations=200, initial_population=80, initial_predators=8,
        offspring_min=1, offspring_max=2,
        predator_offspring_min=1, predator_offspring_max=2,
        base_detection_prob=0.30, altruist_escape_prob=0.90,
        predator_hunt_capacity=1, seed=42,
    ),
    herbivore_specs=_herbivore_specs,
    predator_specs=_predator_specs,
)

exp2c = SimpleExperiment(
    name="Experimento 2C — Cobardía vs Altruismo (p_escape=0.90, 30 corridas)",
    description="Validación estadística de 2B: 30 corridas con semillas distintas (base_seed=0).",
    config=SimulationConfig(
        num_trees=25, tree_capacity_min=2, tree_capacity_max=2,
        num_generations=200, initial_population=80, initial_predators=8,
        offspring_min=1, offspring_max=2,
        predator_offspring_min=1, predator_offspring_max=2,
        base_detection_prob=0.30, altruist_escape_prob=0.90,
        predator_hunt_capacity=1, seed=0,
    ),
    herbivore_specs=_herbivore_specs,
    predator_specs=_predator_specs,
)
