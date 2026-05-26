"""
simulation/core/gene.py
=======================
Base class for all genes and the data types used to represent
predator-encounter decisions.

Design principles
-----------------
* A Gene is a behaviour/trait modifier.  It can do two things:
  1. Set physical traits on a Creature when the creature is born
     (``apply_traits``).
  2. Return a ``PredatorDecision`` when the creature faces a predator
     (``decide_predator_action``).

* When a creature has several genes that would both respond to the same
  situation the gene with the **highest PRIORITY** wins.  Returning
  ``None`` from ``decide_predator_action`` means "I have nothing to say
  here; let a lower-priority gene (or the default) decide."

* Default behaviour when no gene responds: ``PredatorAction.STAY``
  (the creature faces the predator and gets eaten).
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from enum import Enum, auto
from typing import TYPE_CHECKING, List, Optional

if TYPE_CHECKING:
    from .creature import Creature


# ---------------------------------------------------------------------------
# Predator action vocabulary
# ---------------------------------------------------------------------------

class PredatorAction(Enum):
    """The possible decisions a creature can make when a predator appears."""
    STAY = auto()           # Do nothing → get eaten
    FLEE_SILENT = auto()    # Flee immediately without warning anyone (coward)
    WARN_ALL = auto()       # Warn every companion; they escape safely; actor gets escape chance
    WARN_SIMILAR = auto()   # Warn only companions that share a specific physical trait


@dataclass
class PredatorDecision:
    """
    The decision returned by a gene for a predator encounter.

    Attributes
    ----------
    action:
        What the creature will do.
    escape_probability:
        Relevant only for WARN_* actions.  After warning companions the
        actor attempts to escape with this probability.
    similarity_trait:
        Relevant only for WARN_SIMILAR.  Only companions whose
        ``traits[similarity_trait]`` is truthy receive the warning.
    """
    action: PredatorAction
    escape_probability: float = 0.0
    similarity_trait: Optional[str] = None


# ---------------------------------------------------------------------------
# Abstract Gene base class
# ---------------------------------------------------------------------------

class Gene(ABC):
    """
    Abstract base class for every gene in the simulation.

    Subclasses must implement:
    * ``name``  – unique string identifier used in statistics output.

    Subclasses may override:
    * ``apply_traits``               – modify creature's physical traits at birth.
    * ``decide_predator_action``     – return a PredatorDecision when a predator
                                       is encountered, or None to defer.
    """

    #: Higher PRIORITY genes override lower ones when both would respond
    #: to the same situation.
    PRIORITY: int = 0

    @property
    @abstractmethod
    def name(self) -> str:
        """Unique, human-readable identifier for this gene type."""

    def apply_traits(self, creature: "Creature") -> None:
        """
        Called once when the creature is instantiated.
        Modify ``creature.traits`` to set physical characteristics.

        Example::

            def apply_traits(self, creature):
                creature.traits['green_beard'] = True
        """

    def decide_predator_action(
        self,
        actor: "Creature",
        companions: List["Creature"],
    ) -> Optional[PredatorDecision]:
        """
        Return a ``PredatorDecision`` if this gene drives a specific
        predator response, or ``None`` to defer to lower-priority genes.

        Parameters
        ----------
        actor:
            The creature that owns this gene.
        companions:
            The other creatures present at the same tree.
        """
        return None

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}()"
