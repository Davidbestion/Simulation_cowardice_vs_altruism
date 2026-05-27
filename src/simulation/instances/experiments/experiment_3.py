from simulation.core.genes import Gene, CowardGene, GreenBeardAltruistGene
from simulation.core.creature import Creature
from simulation.core.simulation import Experiment, SimulationConfig
from simulation.core.world import World

configuration = SimulationConfig(
    num_generations=100,
    initial_population=80,
    predator_probability=0.30,
    offspring_min=1,
    offspring_max=2,
    seed=42,
)

class Experiment3(Experiment):
    """Pure cowardice vs selective altruism

    In this experiment, we start with a population of creatures that have either the CowardGene or the GreenBeardAltruistGene.
    """

    @property
    def name(self) -> str:
        return "Experiment 3: Pure Cowardice vs Selective Altruism"

    @property
    def description(self) -> str:
        return (
            "All creatures carry either the CowardGene or the GreenBeardAltruistGene.\n"
            "This experiment serves as a baseline for the effectiveness of cowardice and selective altruism as defense mechanisms against predation."
        )

    @property
    def config(self) -> SimulationConfig:
        return configuration

    @property
    def population_specs(self) -> list[tuple[callable, float]]:
        return [
            (lambda: [CowardGene()], 0.5),  # 50% CowardGene
            (lambda: [GreenBeardAltruistGene()], 0.5),  # 50% GreenBeardAltruistGene
        ]
