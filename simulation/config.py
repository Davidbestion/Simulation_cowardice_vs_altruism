"""
simulation/config.py
====================
Configuration dataclasses for the simulation and experiments.

Keep all numeric knobs here so that experiments are fully declarative.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional


@dataclass
class WorldConfig:
    """Physical layout of the world."""

    #: Number of houses (narrative; does not constrain population)
    num_houses: int = 20
    #: Number of trees.  Total food slots = num_trees × 2.
    num_trees: int = 25


@dataclass
class SimConfig:
    """
    Full simulation configuration.

    Attributes
    ----------
    world:
        World layout parameters.
    num_generations:
        How many days (generations) to simulate.
    initial_population:
        Total number of creatures at generation 0.
    predator_probability:
        Probability that a predator appears at any given tree on any day.
    offspring_min / offspring_max:
        Each surviving creature produces a random number of offspring in
        [offspring_min, offspring_max].
    mutation_rate:
        Probability that any gene is lost when copied to an offspring.
        0.0 = perfect inheritance (default).
    seed:
        RNG seed for reproducibility.  None = non-deterministic.
    """

    world: WorldConfig = field(default_factory=WorldConfig)
    num_generations: int = 100
    initial_population: int = 60
    predator_probability: float = 0.30
    offspring_min: int = 1
    offspring_max: int = 2
    mutation_rate: float = 0.0
    seed: Optional[int] = 42
