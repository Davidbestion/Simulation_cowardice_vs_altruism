"""Experimento 8 — Agrupamiento social con barba verde vs depredadores camuflados.

Herbívoros: 50 % CowardGene / 50 % SocialGreenBeardAltruistGene.
Depredadores: 50 % plain / 50 % CamouflagePredatorGene.
tree_capacity_max=10 (árboles de mayor capacidad para permitir agrupamiento).
5 niveles de detección, 30 corridas c/u.
"""
from simulation.core import (
    SimulationConfig, CowardGene, CamouflagePredatorGene,
    SocialGreenBeardAltruistGene,
)
from simulation.analysis.runner import SimpleExperiment, RandomPredatorGene

_herbivore_specs = [
    (lambda: [CowardGene()],                   0.50),
    (lambda: [SocialGreenBeardAltruistGene()], 0.50),
]


def _make(base_detection_prob: float) -> SimpleExperiment:
    return SimpleExperiment(
        name=f"Exp 8 — Barba verde social vs camuflaje predador (detección={base_detection_prob})",
        description=(
            f"50% CowardGene / 50% SocialGreenBeardAltruistGene contra "
            f"50% plain / 50% CamouflagePredatorGene. "
            f"tree_capacity_max=10, base_detection_prob={base_detection_prob}."
        ),
        config=SimulationConfig(
            num_trees=25, tree_capacity_min=2, tree_capacity_max=10,
            num_generations=300, initial_population=80, initial_predators=8,
            offspring_min=1, offspring_max=2,
            predator_offspring_min=1, predator_offspring_max=2,
            base_detection_prob=base_detection_prob, altruist_escape_prob=0.50,
            predator_hunt_capacity=1, seed=0,
        ),
        herbivore_specs=_herbivore_specs,
        predator_specs=[
            (lambda: [RandomPredatorGene()],    0.50),
            (lambda: [CamouflagePredatorGene()], 0.50),
        ],
    )


exp8_det010 = _make(0.10)
exp8_det030 = _make(0.30)
exp8_det050 = _make(0.50)
exp8_det070 = _make(0.70)
exp8_det090 = _make(0.90)
