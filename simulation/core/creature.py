"""
simulation/core/creature.py
===========================
Creature: the basic unit of the simulation.

A creature holds:
* genome  – ordered list of Gene instances
* traits  – dict of physical characteristics set by genes at birth
* creature_id – short unique hex string for debugging

Behaviour is entirely delegated to genes; the creature itself is just a
container that knows how to ask its genes for decisions.
"""

from __future__ import annotations

import copy
import uuid
from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Any, Dict, List, Optional, Type

if TYPE_CHECKING:
    from .gene import Gene, PredatorDecision


@dataclass
class Creature:
    """
    A single creature in the simulation.

    Parameters
    ----------
    genome:
        List of Gene instances.  The order does not matter; the creature
        sorts them by PRIORITY internally.
    """

    genome: List["Gene"]
    traits: Dict[str, Any] = field(default_factory=dict, init=False)
    creature_id: str = field(
        default_factory=lambda: uuid.uuid4().hex[:6], init=False
    )

    def __post_init__(self) -> None:
        # Apply genes from lowest to highest priority so that a
        # higher-priority gene can override traits set by a lower one.
        for gene in sorted(self.genome, key=lambda g: g.PRIORITY):
            gene.apply_traits(self)

    # ------------------------------------------------------------------
    # Trait / gene inspection
    # ------------------------------------------------------------------

    def has_trait(self, trait: str) -> bool:
        """Return True if the creature's traits dict has a truthy value for *trait*."""
        return bool(self.traits.get(trait, False))

    def has_gene(self, gene_type: Type["Gene"]) -> bool:
        """Return True if the genome contains at least one instance of *gene_type*."""
        return any(isinstance(g, gene_type) for g in self.genome)

    def get_gene(self, gene_type: Type["Gene"]) -> Optional["Gene"]:
        """Return the first gene of *gene_type* found in the genome, or None."""
        for g in self.genome:
            if isinstance(g, gene_type):
                return g
        return None

    # ------------------------------------------------------------------
    # Behaviour
    # ------------------------------------------------------------------

    def decide_predator_action(
        self, companions: List["Creature"]
    ) -> "PredatorDecision":
        """
        Ask the genome what to do when a predator is present.

        Genes are consulted from highest PRIORITY to lowest.  The first
        gene that returns a non-None decision wins.  If no gene responds,
        the default is STAY (get eaten).
        """
        from .gene import PredatorDecision, PredatorAction

        for gene in sorted(self.genome, key=lambda g: g.PRIORITY, reverse=True):
            decision = gene.decide_predator_action(self, companions)
            if decision is not None:
                return decision
        return PredatorDecision(action=PredatorAction.STAY)

    # ------------------------------------------------------------------
    # Reproduction
    # ------------------------------------------------------------------

    def reproduce(
        self, num_offspring: int, mutation_rate: float = 0.0
    ) -> List["Creature"]:
        """
        Produce *num_offspring* children.

        Each child inherits a deep copy of the parent's genome.
        If *mutation_rate* > 0, each gene has that probability of being
        dropped (lost) in each offspring independently.

        Note: the parent dies after reproducing (handled by the engine).
        """
        import random

        offspring: List[Creature] = []
        for _ in range(num_offspring):
            if mutation_rate > 0.0:
                new_genome = [
                    copy.deepcopy(g)
                    for g in self.genome
                    if random.random() > mutation_rate
                ]
            else:
                new_genome = copy.deepcopy(self.genome)
            offspring.append(Creature(genome=new_genome))
        return offspring

    # ------------------------------------------------------------------
    # Representation
    # ------------------------------------------------------------------

    def __repr__(self) -> str:
        gene_names = [g.name for g in self.genome] or ["(none)"]
        traits_str = ", ".join(f"{k}={v}" for k, v in self.traits.items()) or ""
        return (
            f"Creature({self.creature_id}"
            f", genes={gene_names}"
            + (f", traits={{{traits_str}}}" if traits_str else "")
            + ")"
        )
