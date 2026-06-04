from simulation.core.genes import CowardGene, GreenBeardAltruistGene, GreenBeardGene, SelectiveAltruistGene
from simulation.core.simulation import Experiment, SimulationConfig

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
    def herbivore_specs(self) -> list[tuple[callable, float]]:
        return [
            (lambda: [GreenBeardAltruistGene()], 0.25),
            (lambda: [GreenBeardGene(), CowardGene()], 0.25),
            (lambda: [SelectiveAltruistGene()], 0.25),
            (lambda: [CowardGene()], 0.25),
        ]
    
    # Four population types:
    # 1. Cowards
    # 2. Selective Altruists (help only those with Green Beard)
    # 3. Green Beard + Coward (have the green beard but also the coward gene)
    # 4. Green Beard Altruists (have the green beard and help others with Green Beard)
