from simulation.core.genes import Gene, CowardGene, GreenBeardAltruistGene, AltruistGene, GreenBeardGene, SelectiveAltruistGene
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

class Experiment4(Experiment):
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
            (lambda: [GreenBeardAltruistGene()], 0.25),  # 25% GreenBeardAltruistGene
            (lambda: [GreenBeardGene(),CowardGene()], 0.25),  # 25 % GreenBeardGene + CowardGene
            (lambda: [SelectiveAltruistGene()], 0.25),  # 25% SelectiveAltruistGene
            (lambda: [CowardGene()], 0.25),  # All creatures start with the CowardGene
            
        ]
    
    # Four population types:
    # 1. Cowards
    # 2. Selective Altruists (help only those with Green Beard)
    # 3. Green Beard + Coward (have the green beard but also the coward gene)
    # 4. Green Beard Altruists (have the green beard and help others with Green Beard)
