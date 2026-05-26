"""
simulation/core/world.py
========================
World, House, and Tree – the physical environment of the simulation.

Rules:
* Every creature lives in a House.
* Every day all creatures leave their house and go to a Tree to eat.
* Each Tree can feed at most ``max_capacity`` creatures per day (default 2).
* A Tree may have a predator on any given day (probability set in the engine).
* Houses have no hard capacity limit; they are mainly narrative containers.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import List


@dataclass
class Tree:
    """A foraging site.  At most ``max_capacity`` creatures can eat here each day."""

    tree_id: int
    max_capacity: int = 2

    def __repr__(self) -> str:
        return f"Tree({self.tree_id})"


@dataclass
class House:
    """Where creatures sleep and reproduce between days."""

    house_id: int

    def __repr__(self) -> str:
        return f"House({self.house_id})"


@dataclass
class World:
    """
    The complete environment: a collection of Houses and Trees.

    Parameters
    ----------
    num_houses:
        Number of houses in the world.
    num_trees:
        Number of trees available for foraging.
    """

    num_houses: int
    num_trees: int

    houses: List[House] = field(init=False)
    trees: List[Tree] = field(init=False)

    def __post_init__(self) -> None:
        self.houses = [House(i) for i in range(self.num_houses)]
        self.trees = [Tree(i) for i in range(self.num_trees)]

    def total_tree_capacity(self) -> int:
        """Maximum number of creatures that can eat on a single day."""
        return sum(t.max_capacity for t in self.trees)
