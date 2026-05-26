"""
simulation/genes/selective_altruist.py
=======================================
SelectiveAltruistGene: warn ONLY companions that share a specific trait.

Behaviour
---------
* The creature inspects its companions for the presence of ``recognition_trait``
  (default: ``'green_beard'``).
* If any companion carries that trait, the creature issues a WARN_SIMILAR
  decision; those companions escape safely; the actor gets an escape attempt.
* If NO companion carries the trait, the gene returns None → the creature
  falls back to the default (STAY → eaten).  It does NOT help those it cannot
  recognise as kin.

This does NOT automatically give the actor the recognition trait.
Combine with GreenBeardGene if the actor should also carry the badge.

Experiment scenarios
--------------------
Exp 03 – coupled genes:
    ``[GreenBeardGene(), SelectiveAltruistGene()]``
    Actor has the badge AND the selective behaviour.
    Other badge-bearers save each other; non-badge creatures are ignored.

Exp 04 – separated genes:
    Badge-bearers without altruism (cheaters), altruists without badge, etc.
    Cheaters exploit altruists who warn them without reciprocating.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, List, Optional

from simulation.core.gene import Gene, PredatorAction, PredatorDecision

if TYPE_CHECKING:
    from simulation.core.creature import Creature


class SelectiveAltruistGene(Gene):
    """
    Altruist that only warns companions bearing a specific physical trait.

    Parameters
    ----------
    escape_probability:
        Probability [0, 1] that the altruist escapes after warning.
    recognition_trait:
        The trait key to look for in companions (default: ``'green_beard'``).
    """

    PRIORITY = 10  # Same as AltruistGene; only one should be in a genome at once

    def __init__(
        self,
        escape_probability: float = 0.5,
        recognition_trait: str = "green_beard",
    ) -> None:
        self.escape_probability = escape_probability
        self.recognition_trait = recognition_trait

    @property
    def name(self) -> str:
        return "selective_altruist"

    def decide_predator_action(
        self,
        actor: "Creature",
        companions: List["Creature"],
    ) -> Optional[PredatorDecision]:
        # If there are no companions, do nothing. The engine treats singletons
        # specially (they are eaten if a predator is present).
        if not companions:
            return None

        # If at least one companion carries the recognition trait, warn
        # those companions. Otherwise, if companions exist but none are
        # worthy, flee silently (the altruist saves itself when it cannot
        # help anyone).
        worthy = [c for c in companions if c.has_trait(self.recognition_trait)]
        if worthy:
            return PredatorDecision(
                action=PredatorAction.WARN_SIMILAR,
                escape_probability=self.escape_probability,
                similarity_trait=self.recognition_trait,
            )
        # Companions exist but none are worthy: flee silently.
        return PredatorDecision(action=PredatorAction.FLEE_SILENT)

    def __repr__(self) -> str:
        return (
            f"SelectiveAltruistGene("
            f"escape_prob={self.escape_probability}, "
            f"trait='{self.recognition_trait}')"
        )
