"""
simulation/genes/altruist.py
============================
AltruistGene: warn ALL companions when a predator appears.

Behaviour
---------
* Companion(s) at the same tree escape safely (100 %).
* The altruist itself then has ``escape_probability`` chance of surviving.
* If alone (no companions), the altruist has no one to warn and falls back
  to the default behaviour (STAY → eaten).

Note on interactions
--------------------
If two altruists share a tree they each warn the other simultaneously.
Both end up in the "warned" set → both escape safely.  This mutual benefit
is an emergent property of the engine's resolution algorithm.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, List, Optional

from simulation.core.gene import Gene, PredatorAction, PredatorDecision

if TYPE_CHECKING:
    from simulation.core.creature import Creature


class AltruistGene(Gene):
    """
    Altruist: sacrifices a chance of escape to save all companions.

    Parameters
    ----------
    escape_probability:
        Probability [0, 1] that the altruist successfully escapes after
        issuing the warning.  Default 0.5 (50 %).
    """

    PRIORITY = 10  # Overrides coward if a creature somehow has both

    def __init__(self, escape_probability: float = 0.5) -> None:
        self.escape_probability = escape_probability

    @property
    def name(self) -> str:
        return "altruist"

    def decide_predator_action(
        self,
        actor: "Creature",
        companions: List["Creature"],
    ) -> Optional[PredatorDecision]:
        if companions:
            return PredatorDecision(
                action=PredatorAction.WARN_ALL,
                escape_probability=self.escape_probability,
            )
        # Alone – nothing to warn; defer to default (STAY)
        return None

    def __repr__(self) -> str:
        return f"AltruistGene(escape_prob={self.escape_probability})"
