from abc import ABC
from dataclasses import dataclass, field
from typing import Callable, List, Tuple, Dict, Optional


@dataclass
class SimulationConfig:
    """Configuration parameters for the simulation."""
    num_trees: int = 25
    num_generations: int = 100
    initial_population: int = 80
    predator_probability: float = 0.30
    offspring_min: int = 1
    offspring_max: int = 2
    seed: Optional[int] = 42
    # Probability that an altruist who warns will escape unscathed
    altruist_escape_prob: float = 0.5


class Experiment(ABC):
    """Base class for experiments. Subclasses must implement the abstract properties below."""

    @property
    def name(self) -> str:
        raise NotImplementedError

    @property
    def description(self) -> str:
        raise NotImplementedError

    @property
    def config(self) -> SimulationConfig:
        raise NotImplementedError

    @property
    def population_specs(self) -> List[Tuple[Callable[[], list], float]]:
        """Return a list of tuples, where each tuple contains a function 
        that generates a genome and the fraction of the initial population 
        that should have that genome."""
        raise NotImplementedError


@dataclass
class GenerationReport:
    generation: int
    population_start: int
    starved: int
    eaten: int
    survived: int
    population_end: int
    gene_frequencies: Dict[str, float] = field(default_factory=dict)
