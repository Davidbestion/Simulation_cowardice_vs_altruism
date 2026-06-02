from abc import ABC

from typing import Dict, List, Any, Optional, Tuple
import random

from .creature import Creature

class Gene(ABC):
    """A single gene in the simulation."""

    name: str = "gene"
    # Priority used to pick which gene's behavior applies when multiple genes present.
    PRIORITY: int = 0

    def apply_physical_traits(self, creature: Creature) -> Dict[str, bool]:
        return {}

    def predator_behavior(self, notifier: Creature, assigned: List[Creature], cfg: Any) -> Optional[Tuple[List[Creature], int]]:
        """Return (survivors, eaten_count) when `notifier` acts under predator.

        Return None if this gene does not define a predator behavior.
        """
        return None


class CowardGene(Gene):
    """A gene that gives the creature cowardly behavior."""

    name: str = "coward"
    PRIORITY: int = 10

    def predator_behavior(self, notifier: Creature, assigned: List[Creature], cfg: Any):
        # Coward flees, others die
        survivors = [notifier]
        eaten = max(0, len(assigned) - 1)
        return survivors, eaten


class AltruistGene(Gene):
    """A gene that gives the creature altruistic behavior."""

    name: str = "altruist"
    PRIORITY: int = 20

    def predator_behavior(self, notifier: Creature, assigned: List[Creature], cfg: Any):
        # Notifier warns everyone else -> they all escape 100%.
        others = [c for c in assigned if c is not notifier]
        survivors = list(others)
        # Notifier escapes with configured probability
        if random.random() < getattr(cfg, "altruist_escape_prob", 0.5):
            survivors.append(notifier)
            eaten = 0
        else:
            eaten = 1
        return survivors, eaten

class SelectiveAltruistGene(Gene):
    """A gene that gives the creature altruistic behavior only towards green-bearded individuals."""

    name: str = "selective_altruist"
    PRIORITY: int = 25

    def predator_behavior(self, notifier: Creature, assigned: List[Creature], cfg: Any):
        # Notifier warns only creatures with green_beard
        green_targets = [c for c in assigned if c.has_trait("green_beard") and c is not notifier]
        if green_targets:
            survivors = list(green_targets)
            # Notifier escapes probabilistically
            if random.random() < getattr(cfg, "altruist_escape_prob", 0.5):
                survivors.append(notifier)
                eaten = len([c for c in assigned if c not in survivors])
            else:
                # notifier eaten, others non-green eaten
                eaten = 1 + len([c for c in assigned if c not in survivors and c is not notifier])
            return survivors, eaten
        else:
            # No green targets: notifier flees, others die
            survivors = [notifier]
            eaten = max(0, len(assigned) - 1)
            return survivors, eaten

class NoPhysicalGene(Gene):
    """A gene that has no physical effect."""

    name: str = "no_physical"
    PRIORITY: int = 0

    def apply_physical_traits(self, creature: Creature) -> Dict[str, bool]:
        return {}


class GreenBeardGene(Gene):
    """A gene that gives the creature a green beard trait."""

    name: str = "green_beard"
    PRIORITY: int = 5

    def apply_physical_traits(self, creature: Creature) -> Dict[str, bool]:
        return {"green_beard": True}


class GreenBeardAltruistGene(Gene):
    """A gene that gives the creature both a green beard and altruistic behavior."""

    name: str = "green_beard_altruist"
    PRIORITY: int = 30

    def apply_physical_traits(self, creature: Creature) -> Dict[str, bool]:
        return {"green_beard": True}

    def predator_behavior(self, notifier: Creature, assigned: List[Creature], cfg: Any):
        # Notifier warns only creatures with green_beard
        green_targets = [c for c in assigned if c.has_trait("green_beard") and c is not notifier]
        if green_targets:
            survivors = list(green_targets)
            # Notifier escapes probabilistically
            if random.random() < getattr(cfg, "altruist_escape_prob", 0.5):
                survivors.append(notifier)
                eaten = len([c for c in assigned if c not in survivors])
            else:
                # notifier eaten, others non-green eaten
                eaten = 1 + len([c for c in assigned if c not in survivors and c is not notifier])
            return survivors, eaten
        else:
            # No green targets: notifier flees, others die
            survivors = [notifier]
            eaten = max(0, len(assigned) - 1)
            return survivors, eaten
