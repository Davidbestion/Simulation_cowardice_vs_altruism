"""Experimento 4 — Cuatro estrategias desacopladas.

Compite cobardía pura, impostor (GreenBeard + CowardGene), altruismo selectivo
sin señal y altruismo con señal integrada (GreenBeardAltruistGene).
30 corridas, 400 generaciones.
"""
from simulation.core import (
    SimulationConfig, CowardGene, GreenBeardGene,
    SelectiveAltruistGene, GreenBeardAltruistGene,
)
from simulation.analysis.runner import SimpleExperiment, RandomPredatorGene

exp4 = SimpleExperiment(
    name="Experimento 4 — Cuatro estrategias desacopladas",
    description=(
        "Competencia entre cobardía pura, señalización sin cooperación (impostor), "
        "altruismo selectivo sin señal y altruismo con señal integrada."
    ),
    config=SimulationConfig(
        num_trees=25, tree_capacity_min=2, tree_capacity_max=2,
        num_generations=400, initial_population=80, initial_predators=8,
        offspring_min=1, offspring_max=2,
        predator_offspring_min=1, predator_offspring_max=2,
        base_detection_prob=0.30, altruist_escape_prob=0.50,
        predator_hunt_capacity=1, seed=0,
    ),
    herbivore_specs=[
        (lambda: [CowardGene()],                          0.25),
        (lambda: [GreenBeardGene(), CowardGene()],         0.25),
        (lambda: [SelectiveAltruistGene()],                0.25),
        (lambda: [GreenBeardAltruistGene()],               0.25),
    ],
    predator_specs=[(lambda: [RandomPredatorGene()], 1.0)],
)
