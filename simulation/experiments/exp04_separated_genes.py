"""
Experiment 04 – Separated Beard and Altruism Genes
=====================================================
The green beard trait and the selective altruism behaviour are now
**independent genes** that can appear in any combination.

This enables **cheaters** (free-riders): creatures that carry the green
beard (so they look like cooperators and get warned) but do NOT carry the
altruism gene (so they never warn anyone back).

Genotypes in initial population
---------------------------------
* **GreenBeard + SelectiveAltruist** (25 %) – true cooperator:
  has badge, warns badge-bearers.
* **GreenBeard only**                (25 %) – cheater / free-rider:
  has badge, gets warned, never warns back.
* **SelectiveAltruist only**         (15 %) – unrecognised altruist:
  warns badge-bearers, but has no badge itself (not saved in return unless
  its companion is a general altruist).
* **Coward**                         (20 %) – flees silently.
* **Neutral**                        (15 %) – no special behaviour.

Questions
---------
* Do cheaters destabilise the cooperative group?
* Can genuine cooperators survive long-term when cheaters exploit them?
* What is the equilibrium frequency of each genotype?

This experiment directly models the classic *green-beard problem* in
evolutionary biology (Dawkins, 1976; Hamilton, 1964).
"""

from simulation.config import SimConfig, WorldConfig
from simulation.experiments.base import Experiment, PopulationSpec
from simulation.genes.coward import CowardGene
from simulation.genes.green_beard import GreenBeardGene
from simulation.genes.selective_altruist import SelectiveAltruistGene

_ESCAPE_PROB = 0.5


class SeparatedGenesExperiment(Experiment):

    @property
    def name(self) -> str:
        return "Exp04 – Separated Beard and Altruism Genes"

    @property
    def description(self) -> str:
        return (
            "Green beard (trait) and selective altruism (behaviour) are\n"
            "independent genes. Cheaters (beard, no altruism) can exploit\n"
            "true cooperators (beard + altruism)."
        )

    @property
    def config(self) -> SimConfig:
        return SimConfig(
            world=WorldConfig(num_houses=80, num_trees=80),
            num_generations=150,
            initial_population=80,
            predator_probability=0.30,
            offspring_min=1,
            offspring_max=2,
            seed=42,
        )

    @property
    def population_specs(self) -> PopulationSpec:
        return [
            # True cooperators: badge + selective altruism
            (
                lambda: [
                    GreenBeardGene(),
                    SelectiveAltruistGene(escape_probability=_ESCAPE_PROB),
                ],
                0.25,
            ),
            # Cheaters: badge only, no altruism (free-riders)
            (lambda: [GreenBeardGene()], 0.25),
            # Unrecognised altruists: altruism without badge
            (
                lambda: [SelectiveAltruistGene(escape_probability=_ESCAPE_PROB)],
                0.15,
            ),
            # Cowards
            (lambda: [CowardGene()], 0.20),
            # Neutrals
            (lambda: [], 0.15),
        ]
