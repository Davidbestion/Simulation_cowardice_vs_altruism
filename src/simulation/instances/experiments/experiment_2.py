from simulation.core.genes import AltruistGene, CowardGene
from simulation.core.simulation import Experiment, SimulationConfig

configuration = SimulationConfig(
    num_generations=100,
    initial_population=80,
    predator_probability=0.30,
    offspring_min=1,
    offspring_max=2,
    seed=42,
)

class Experiment2(Experiment):
    """Pure cowardice vs pure altruism

    In this experiment, we start with a population of creatures that have either the CowardGene or the AltruistGene.
    """

    @property
    def name(self) -> str:
        return "Experiment 2: Pure Cowardice vs Pure Altruism"

    @property
    def description(self) -> str:
        return (
            "All creatures carry either the CowardGene or the AltruistGene.\n"
            "This experiment serves as a baseline for the effectiveness of cowardice and altruism as defense mechanisms against predation."
        )

    @property
    def config(self) -> SimulationConfig:
        return configuration

    @property
    def herbivore_specs(self) -> list[tuple[callable, float]]:
        return [
            (lambda: [CowardGene()], 0.5),  # 50% CowardGene
            (lambda: [AltruistGene()], 0.5),  # 50% AltruistGene
        ]
