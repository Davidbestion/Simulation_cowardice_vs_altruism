"""
Experiment 01 – Baseline (no genes)
=====================================
All creatures are genetically identical with no special behaviours.
When a predator appears, every creature present is eaten.

Purpose
-------
Establish the baseline population dynamics: how stable is the population
under pure predation and starvation pressure when no defence mechanisms exist?
"""

from simulation.config import SimConfig, WorldConfig
from simulation.experiments.base import Experiment, PopulationSpec


class BaselineExperiment(Experiment):

    @property
    def name(self) -> str:
        return "Exp01 – Baseline (no genes)"

    @property
    def description(self) -> str:
        return (
            "No special genes. All creatures are identical.\n"
            "Predators eat all creatures at the tree. No escape possible."
        )

    @property
    def config(self) -> SimConfig:
        return SimConfig(
            world=WorldConfig(num_houses=80, num_trees=80),
            num_generations=100,
            initial_population=80,
            predator_probability=0.30,
            offspring_min=1,
            offspring_max=2,
            seed=42,
        )

    @property
    def population_specs(self) -> PopulationSpec:
        return [
            (lambda: [], 1.0),  # All creatures carry no genes
        ]
