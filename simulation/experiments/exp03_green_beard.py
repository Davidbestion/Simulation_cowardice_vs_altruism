"""
Experiment 03 – Green Beard Altruism (coupled genes)
======================================================
Extension of Exp02: altruists now carry a **visible green beard** AND
they only warn companions that also have a green beard.

In this experiment the beard and the altruism behaviour are **inseparable**:
a creature either has both (green-beard altruist) or neither.

Genotypes
---------
* **GreenBeard + SelectiveAltruist** – has the badge and the behaviour;
  warns only fellow badge-bearers.
* **Coward**   – flees silently, no badge.
* **Neutral**  – no badge, no behaviour; gets eaten.

Questions
---------
* Does selective kin recognition give altruists a stronger advantage than
  indiscriminate altruism (Exp02)?
* Does the green-beard cluster become self-sustaining?

Note: in this experiment the two genes are always inherited together,
so there are no cheaters (badge without altruism).  See Exp04 for that.
"""

from simulation.config import SimConfig, WorldConfig
from simulation.experiments.base import Experiment, PopulationSpec
from simulation.genes.coward import CowardGene
from simulation.genes.green_beard import GreenBeardGene
from simulation.genes.selective_altruist import SelectiveAltruistGene

_ESCAPE_PROB = 0.5


class GreenBeardExperiment(Experiment):

    @property
    def name(self) -> str:
        return "Exp03 – Green Beard Altruism (coupled genes)"

    @property
    def description(self) -> str:
        return (
            "Altruists carry a green beard AND warn only other green-beards.\n"
            "Beard and altruism are inseparable (no cheaters possible).\n"
            "Competing with cowards and neutrals."
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
            # Green-beard altruist: badge + selective behaviour (coupled)
            (
                lambda: [
                    GreenBeardGene(),
                    SelectiveAltruistGene(escape_probability=_ESCAPE_PROB),
                ],
                1 / 3,
            ),
            (lambda: [CowardGene()], 1 / 3),
            (lambda: [], 1 / 3),  # Neutral
        ]
