"""
Experiment 02 – Altruism vs Cowardice
=======================================
Three genotypes compete in the same population:

* **Altruist** – warns all companions when a predator appears.
  Companion escapes safely; altruist has a 50 % chance of escaping.
* **Coward**   – flees silently without warning anyone.
  Always survives; companion is left to face the predator alone.
* **Neutral**  – no special gene; gets eaten when a predator is present.

Questions
---------
* Which strategy dominates in the long run?
* Does altruism survive despite the short-term cost?
* How does predator probability affect the balance?

Note: in this experiment companions are warned indiscriminately (no
recognition mechanism).  See Exp03 for kin-selective altruism.
"""

from simulation.config import SimConfig, WorldConfig
from simulation.experiments.base import Experiment, PopulationSpec
from simulation.genes.altruist import AltruistGene
from simulation.genes.coward import CowardGene

_ESCAPE_PROB = 0.5


class AltruismCowardiceExperiment(Experiment):

    @property
    def name(self) -> str:
        return "Exp02 – Altruism vs Cowardice"

    @property
    def description(self) -> str:
        return (
            "Three genotypes: altruist (warns all, 50% escape),\n"
            "coward (flees silently, always survives),\n"
            "and neutral (gets eaten). Equal starting proportions."
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
            (lambda: [AltruistGene(escape_probability=_ESCAPE_PROB)], 1 / 3),
            (lambda: [CowardGene()], 1 / 3),
            (lambda: [], 1 / 3),  # Neutral
        ]
