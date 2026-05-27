import random
import uuid
from typing import List, Dict, Any, Tuple


class Creature:
    """A single creature in the simulation."""

    def __init__(self, genome: list, min_offspring: int = 1, max_offspring: int = 2) -> None:
        self.genome = genome
        self.physical_traits = self.get_physical_traits()
        self.behavioral_traits = self.get_behavioral_traits()
        self.creature_id = uuid.uuid4().hex[:6]
        self.min_offspring = min_offspring
        self.max_offspring = max_offspring

    def has_trait(self, trait: str) -> bool:
        """Return True if the creature's traits dict has a truthy value for *trait*."""
        return bool(self.physical_traits.get(trait, False)) or bool(self.behavioral_traits.get(trait, False))

    def has_gene(self, gene_type: type) -> bool:
        """Return True if the genome contains at least one instance of *gene_type*."""
        return any(isinstance(g, gene_type) for g in self.genome)

    def get_physical_traits(self) -> dict:
        """Return a dict of the creature's physical traits."""
        traits = {}
        for gene in self.genome:
            traits.update(gene.apply_physical_traits(self))
        return traits

    def get_behavioral_traits(self) -> dict:
        """Return a dict of the creature's behavioral traits."""
        traits = {}
        for gene in self.genome:
            traits.update(gene.apply_behavioral_traits(self))
        return traits

    def handle_predator(self, assigned: List["Creature"], cfg: Any) -> Tuple[List["Creature"], int]:
        """Decide action when this creature detects a predator.

        Returns a tuple `(survivors, eaten_count)` where `survivors` is a list
        of creatures that escape (subset of `assigned`) and `eaten_count` is the
        number of creatures eaten by the predator as a result of this event.
        """
        # Ensure the assigned list includes self
        if self not in assigned:
            assigned = [self] + assigned

        # Find genes that implement predator_behavior and pick the highest priority
        behavior_genes = [g for g in self.genome if hasattr(g, "predator_behavior")]
        if behavior_genes:
            behavior_genes.sort(key=lambda g: getattr(g, "PRIORITY", 0), reverse=True)
            for g in behavior_genes:
                result = g.predator_behavior(self, assigned, cfg)
                if result is not None:
                    return result

        # Default: no special behavior -> all die
        return [], len(assigned)

    def reproduce(self) -> List["Creature"]:
        """Return a list of offspring creatures with the same genome."""
        num_offspring = random.randint(self.min_offspring, self.max_offspring)
        return [Creature(self.genome, self.min_offspring, self.max_offspring) for _ in range(num_offspring)]
