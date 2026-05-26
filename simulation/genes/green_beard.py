"""
simulation/genes/green_beard.py
================================
GreenBeardGene: a purely physical/visual marker.

This gene gives the creature a distinctive green beard that other creatures
with the right recognition ability (e.g. SelectiveAltruistGene) can detect.

It has NO behavioural effect on its own.  Its only purpose is to set
``creature.traits['green_beard'] = True``.

By keeping the trait gene separate from the behavioural gene we can model
the classic *green beard problem*:
* Creatures can have the badge without the behaviour (cheaters / free-riders).
* Creatures can have the behaviour without the badge (unrecognised altruists).

See also
--------
* simulation/genes/selective_altruist.py  – the gene that reads this trait.
* experiments/exp03_green_beard.py        – trait and behaviour coupled.
* experiments/exp04_separated_genes.py   – trait and behaviour decoupled.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from simulation.core.gene import Gene

if TYPE_CHECKING:
    from simulation.core.creature import Creature


class GreenBeardGene(Gene):
    """Sets ``green_beard = True`` on the creature's trait dict at birth."""

    PRIORITY = 1  # Low priority; purely physical, no override needed

    @property
    def name(self) -> str:
        return "green_beard"

    def apply_traits(self, creature: "Creature") -> None:
        creature.traits["green_beard"] = True

    def __repr__(self) -> str:
        return "GreenBeardGene()"
