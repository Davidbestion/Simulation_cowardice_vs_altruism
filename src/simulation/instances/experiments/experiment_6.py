"""Experimento 6 — Camuflaje en depredadores.

Fondo de herbívoros: 100 % CowardGene.
Barrido 2 fracciones × 3 niveles de detección → 6 condiciones, 30 corridas c/u.
"""
from simulation.core import SimulationConfig, CowardGene, CamouflagePredatorGene
from simulation.analysis.runner import SimpleExperiment, RandomPredatorGene

_herbivore_specs = [(lambda: [CowardGene()], 1.0)]


def _make(frac_camo: float, base_detection_prob: float) -> SimpleExperiment:
    frac_plain = 1.0 - frac_camo
    return SimpleExperiment(
        name=(
            f"Exp 6 — Camuflaje depredadores ({frac_camo:.0%} inicial, "
            f"detección={base_detection_prob})"
        ),
        description=(
            f"Fracción inicial de CamouflagePredatorGene = {frac_camo:.0%}, "
            f"base_detection_prob = {base_detection_prob}."
        ),
        config=SimulationConfig(
            num_trees=25, tree_capacity_min=2, tree_capacity_max=2,
            num_generations=200, initial_population=80, initial_predators=8,
            offspring_min=1, offspring_max=2,
            predator_offspring_min=1, predator_offspring_max=2,
            base_detection_prob=base_detection_prob, altruist_escape_prob=0.50,
            predator_hunt_capacity=1, seed=0,
        ),
        herbivore_specs=_herbivore_specs,
        predator_specs=[
            (lambda: [RandomPredatorGene()],    frac_plain),
            (lambda: [CamouflagePredatorGene()], frac_camo),
        ],
    )


exp6_50_010 = _make(0.50, 0.10)
exp6_50_030 = _make(0.50, 0.30)
exp6_50_050 = _make(0.50, 0.50)
exp6_10_010 = _make(0.10, 0.10)
exp6_10_030 = _make(0.10, 0.30)
exp6_10_050 = _make(0.10, 0.50)
