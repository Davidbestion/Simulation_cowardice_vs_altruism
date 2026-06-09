"""Experimento 9 — Social vs Solitario · Emboscador camuflado vs Cazador cauteloso.

Herbívoros: 50 % SolitaryCowardGene / 50 % SocialGreenBeardAltruistGene.
Depredadores: 50 % AmbushCamoGene / 50 % CautiousPredatorGene.
tree_capacity_min=1, tree_capacity_max=10 (alta variabilidad de árbol).
5 niveles de detección, 30 corridas c/u.
"""
from simulation.core import (
    SimulationConfig, SolitaryCowardGene, SocialGreenBeardAltruistGene,
    AmbushCamoGene, CautiousPredatorGene,
)
from simulation.analysis.runner import SimpleExperiment

_herbivore_specs = [
    (lambda: [SolitaryCowardGene()],           0.50),
    (lambda: [SocialGreenBeardAltruistGene()], 0.50),
]
_predator_specs = [
    (lambda: [AmbushCamoGene()],        0.50),
    (lambda: [CautiousPredatorGene()],  0.50),
]


def _make(base_detection_prob: float) -> SimpleExperiment:
    return SimpleExperiment(
        name=f"Exp 9 — Social/Solitario vs Emboscador-Camo/Cauteloso (detección={base_detection_prob})",
        description=(
            f"50% SolitaryCowardGene / 50% SocialGreenBeardAltruistGene contra "
            f"50% AmbushCamoGene / 50% CautiousPredatorGene. "
            f"tree_capacity_max=10, base_detection_prob={base_detection_prob}."
        ),
        config=SimulationConfig(
            num_trees=25, tree_capacity_min=1, tree_capacity_max=10,
            num_generations=300, initial_population=80, initial_predators=8,
            offspring_min=1, offspring_max=2,
            predator_offspring_min=1, predator_offspring_max=2,
            base_detection_prob=base_detection_prob, altruist_escape_prob=0.50,
            predator_hunt_capacity=1, seed=0,
        ),
        herbivore_specs=_herbivore_specs,
        predator_specs=_predator_specs,
    )


exp9_det010 = _make(0.10)
exp9_det030 = _make(0.30)
exp9_det050 = _make(0.50)
exp9_det070 = _make(0.70)
exp9_det090 = _make(0.90)
