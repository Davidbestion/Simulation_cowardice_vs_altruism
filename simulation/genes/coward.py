"""
simulation/genes/coward.py
==========================
CowardGene: flee immediately and silently when a predator appears.

Behaviour
---------
* The coward always escapes (100 % survival when predator present).
* It does NOT warn any companion; companions are left to face the predator.
* Priority is lower than AltruistGene so that if a creature somehow
  carries both genes, the altruist behaviour takes precedence.

Evolutionary insight
--------------------
Cowards have a short-term individual advantage: they always survive a
predator encounter.  However, they provide no benefit to companions and
may eventually lose ground if altruistic clusters outperform them.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, List, Optional

from simulation.core.gene import Gene, PredatorAction, PredatorDecision

if TYPE_CHECKING:
    from simulation.core.creature import Creature


class CowardGene(Gene):
    """Coward: always flees silently when a predator is present."""

    PRIORITY = 5  # Below AltruistGene (10)

    @property
    def name(self) -> str:
        return "coward"

    def decide_predator_action(
        self,
        actor: "Creature",
        companions: List["Creature"],
    ) -> Optional[PredatorDecision]:
        # Always flee, regardless of companions
        return PredatorDecision(action=PredatorAction.FLEE_SILENT)

    def __repr__(self) -> str:
        return "CowardGene()"
