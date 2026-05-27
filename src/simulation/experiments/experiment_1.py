from ..core.genes import Gene, CowardGene, GreenBeardAltruistGene
from ..core.creature import Creature
from ..core.simulation import Experiment, SimulationConfig
from ..core.world import World

configuration = SimulationConfig(
    num_generations=100,
    initial_population=80,
    predator_probability=0.30,
    offspring_min=1,
    offspring_max=2,
    seed=42,
)

class Experiment1(Experiment):
    """Pure cowardice

    In this experiment, we start with a population of creatures that all have the CowardGene.
    """

    @property
    def name(self) -> str:
        return "Experiment 1: Pure Cowardice"

    @property
    def description(self) -> str:
        return (
            "All creatures carry the CowardGene, which allows them to escape predators with a certain probability.\n"
            "This experiment serves as a baseline for the effectiveness of cowardice as a defense mechanism against predation."
        )

    @property
    def config(self) -> SimulationConfig:
        return configuration

    @property
    def population_specs(self) -> list[tuple[callable, float]]:
        return [
            (lambda: [CowardGene()], 1.0),  # All creatures start with the CowardGene
        ]
