from dataclasses import dataclass, field
from typing import List


@dataclass
class Tree:
    """A foraging site.  At most ``max_capacity`` creatures can eat here each day."""

    tree_id: int
    max_capacity: int = 2
    has_predator: bool = False

    def __repr__(self) -> str:
        return f"Tree({self.tree_id})"

@dataclass
class World:
    """
    The complete environment: a collection of Trees.
    """

    num_trees: int

    trees: List[Tree] = field(init=True)

    def total_tree_capacity(self) -> int:
        return sum(tree.max_capacity for tree in self.trees)
