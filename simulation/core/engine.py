"""
simulation/core/engine.py
=========================
SimulationEngine: runs the daily cycle.

Daily cycle (one generation)
-----------------------------
1. Assign creatures randomly to trees (max 2 per tree).
   Creatures that cannot be assigned starve and die.
2. For each tree, roll for predator presence.
   If a predator appears, resolve the encounter using gene-driven decisions
   (see _resolve_tree).
3. Surviving creatures reproduce (1-2 offspring each) then die.
4. The new generation starts the next day.

Predator encounter resolution
------------------------------
Only ONE creature per tree randomly detects the predator and acts.
The companion (if any) is a passive bystander — its own genes do NOT
trigger independently.

  Detector is COWARD  (FLEE_SILENT): detector flees; companion is eaten.
  Detector is ALTRUIST (WARN_*):     warned companions escape safely (100 %);
                                     detector attempts escape with
                                     escape_probability; unwarned companions
                                     (wrong trait for WARN_SIMILAR) are eaten.
  Detector is NEUTRAL (STAY):        detector stays; all companions are eaten.
"""

from __future__ import annotations

import random
from collections import defaultdict
from dataclasses import dataclass, field
from typing import Dict, List, Set, Tuple, TYPE_CHECKING

if TYPE_CHECKING:
    from .creature import Creature
    from .world import World

from .gene import PredatorAction


# ---------------------------------------------------------------------------
# Report dataclass
# ---------------------------------------------------------------------------

@dataclass
class GenerationReport:
    """Statistics produced after each generation."""

    generation: int
    population_start: int
    starved: int
    eaten: int
    survived: int
    population_end: int
    #: gene_name → fraction of the new generation that carries it
    gene_frequencies: Dict[str, float] = field(default_factory=dict)


# ---------------------------------------------------------------------------
# Engine
# ---------------------------------------------------------------------------

@dataclass
class SimulationEngine:
    """
    Runs the daily simulation cycle.

    Parameters
    ----------
    world:
        The World instance (provides the tree list).
    predator_probability:
        Probability [0, 1] that a predator appears at any given tree on
        any given day.
    offspring_range:
        (min, max) number of offspring each surviving creature produces.
    mutation_rate:
        Probability [0, 1] that any individual gene is lost when copied
        to an offspring.  0.0 = perfect inheritance.
    rng:
        Random number generator.  Providing a seeded instance makes runs
        reproducible.
    """

    world: "World"
    predator_probability: float = 0.3
    offspring_range: Tuple[int, int] = (1, 2)
    mutation_rate: float = 0.0
    rng: random.Random = field(default_factory=random.Random)

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def run_generation(
        self,
        creatures: List["Creature"],
        generation: int,
    ) -> Tuple[List["Creature"], GenerationReport]:
        """
        Execute one full day/generation cycle.

        Returns
        -------
        (next_generation, report)
        """
        population_start = len(creatures)

        # 1. Assign creatures to trees --------------------------------
        tree_assignments = self._assign_to_trees(creatures)
        assigned_ids: Set[int] = {
            id(c)
            for group in tree_assignments.values()
            for c in group
        }
        starved_count = sum(1 for c in creatures if id(c) not in assigned_ids)

        # 2. Resolve each tree ----------------------------------------
        survivors: List["Creature"] = []
        for _tree_id, group in tree_assignments.items():
            has_predator = self.rng.random() < self.predator_probability
            survivors.extend(self._resolve_tree(group, has_predator))

        eaten_count = population_start - starved_count - len(survivors)

        # 3. Survivors reproduce; they then die -----------------------
        next_generation: List["Creature"] = []
        for creature in survivors:
            num_offspring = self.rng.randint(*self.offspring_range)
            next_generation.extend(
                creature.reproduce(num_offspring, self.mutation_rate)
            )

        report = GenerationReport(
            generation=generation,
            population_start=population_start,
            starved=starved_count,
            eaten=eaten_count,
            survived=len(survivors),
            population_end=len(next_generation),
            gene_frequencies=self._gene_frequencies(next_generation),
        )
        return next_generation, report

    # ------------------------------------------------------------------
    # Tree assignment
    # ------------------------------------------------------------------

    def _assign_to_trees(
        self, creatures: List["Creature"]
    ) -> Dict[int, List["Creature"]]:
        """
        Randomly assign creatures to available tree slots.

        Builds a flat list of (tree_id, slot_index) for every available
        slot across all trees, shuffles it, then pairs each slot with a
        creature.  Creatures with no matching slot starve.
        """
        # Flat list of all available slots
        slots: List[int] = []  # each entry is the tree_id for that slot
        for tree in self.world.trees:
            slots.extend([tree.tree_id] * tree.max_capacity)
        self.rng.shuffle(slots)

        shuffled_creatures = list(creatures)
        self.rng.shuffle(shuffled_creatures)

        assignments: Dict[int, List["Creature"]] = defaultdict(list)
        for creature, tree_id in zip(shuffled_creatures, slots):
            assignments[tree_id].append(creature)

        return dict(assignments)

    # ------------------------------------------------------------------
    # Predator encounter
    # ------------------------------------------------------------------

    def _resolve_tree(
        self,
        group: List["Creature"],
        has_predator: bool,
    ) -> List["Creature"]:
        """
        Determine which creatures survive at this tree.

        If there is no predator everyone feeds and survives.

        If there is a predator, ONE creature is chosen at random to be the
        detector — the only one that notices the predator and reacts.
        Companions are passive: they only escape if the detector warns them.

        * FLEE_SILENT: detector flees silently; companions are eaten.
        * WARN_ALL / WARN_SIMILAR: warned companions escape safely (100 %);
          detector attempts escape with escape_probability; unwarned
          companions (e.g. wrong trait for WARN_SIMILAR) are eaten.
        * STAY (default): detector stays; all companions are eaten.
        """
        if not has_predator:
            return list(group)
        if not group:
            return []

        # If a predator is present and there's only one creature at the
        # tree, the predator eats it (singletons do not flee).
        if len(group) == 1:
            return []

        # Randomly choose which creature detects the predator
        detector = self.rng.choice(group)
        companions = [c for c in group if c is not detector]
        decision = detector.decide_predator_action(companions)

        survivors: Set[int] = set()

        if decision.action == PredatorAction.FLEE_SILENT:
            # Coward: detector escapes; companions face the predator alone
            survivors.add(id(detector))

        elif decision.action in (PredatorAction.WARN_ALL, PredatorAction.WARN_SIMILAR):
            # Altruist: warned companions escape safely; detector rolls for escape
            targets = self._get_warn_targets(detector, companions, decision)
            for target in targets:
                survivors.add(id(target))
            if self.rng.random() < decision.escape_probability:
                survivors.add(id(detector))

        # STAY (default): nobody survives the encounter

        id_to_creature = {id(c): c for c in group}
        return [id_to_creature[cid] for cid in survivors if cid in id_to_creature]

    def _get_warn_targets(
        self,
        warner: "Creature",
        companions: List["Creature"],
        decision,
    ) -> List["Creature"]:
        """Return the list of companions that *warner* chooses to alert."""
        if decision.action == PredatorAction.WARN_ALL:
            return companions
        if decision.action == PredatorAction.WARN_SIMILAR:
            trait = decision.similarity_trait
            if trait is None:
                return []
            return [c for c in companions if c.has_trait(trait)]
        return []

    # ------------------------------------------------------------------
    # Statistics helpers
    # ------------------------------------------------------------------

    def _gene_frequencies(
        self, creatures: List["Creature"]
    ) -> Dict[str, float]:
        """Return a dict mapping gene name → fraction of population carrying it."""
        if not creatures:
            return {}
        counts: Dict[str, int] = defaultdict(int)
        for creature in creatures:
            for gene in creature.genome:
                counts[gene.name] += 1
        n = len(creatures)
        return {name: count / n for name, count in counts.items()}
