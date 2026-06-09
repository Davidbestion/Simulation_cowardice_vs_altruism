"""Experimento 3 — Altruismo selectivo con señal de barba verde.

Barrido 2 fracciones × 3 valores de p_escape → 6 condiciones, 30 corridas c/u.
"""
from simulation.core import SimulationConfig, CowardGene, GreenBeardAltruistGene
from simulation.analysis.runner import SimpleExperiment, RandomPredatorGene

_predator_specs = [(lambda: [RandomPredatorGene()], 1.0)]


def _make(frac_altruist: float, p_escape: float) -> SimpleExperiment:
    frac_coward = 1.0 - frac_altruist
    label = f"{frac_altruist:.0%}"
    return SimpleExperiment(
        name=f"Exp 3 — GreenBeardAltruist vs Coward ({label} inicial, p_escape={p_escape})",
        description=(
            f"Fracción inicial de GreenBeardAltruistGene = {label}, "
            f"altruist_escape_prob = {p_escape}."
        ),
        config=SimulationConfig(
            num_trees=25, tree_capacity_min=2, tree_capacity_max=2,
            num_generations=200, initial_population=80, initial_predators=8,
            offspring_min=1, offspring_max=2,
            predator_offspring_min=1, predator_offspring_max=2,
            base_detection_prob=0.30, altruist_escape_prob=p_escape,
            predator_hunt_capacity=1, seed=0,
        ),
        herbivore_specs=[
            (lambda: [GreenBeardAltruistGene()], frac_altruist),
            (lambda: [CowardGene()],             frac_coward),
        ],
        predator_specs=_predator_specs,
    )


exp3_50_010 = _make(0.50, 0.10)
exp3_50_050 = _make(0.50, 0.50)
exp3_50_090 = _make(0.50, 0.90)
exp3_10_010 = _make(0.10, 0.10)
exp3_10_050 = _make(0.10, 0.50)
exp3_10_090 = _make(0.10, 0.90)
