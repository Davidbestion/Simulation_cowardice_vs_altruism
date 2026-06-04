"""Core simulation package exports."""
from .creature import Creature, Herbivore, Predator
from .genes import (
    Gene,
    CowardGene,
    AltruistGene,
    SelectiveAltruistGene,
    GreenBeardGene,
    SocialGene,
    SolitaryGene,
    HiddenHerbivoreGene,
    CamouflageGene,
    AmbushGene,
    CautiousPredatorGene,
    GreedyHunterGene,
    # Backward-compat aliases
    GreenBeardAltruistGene,
    NoPhysicalGene,
)
from .simulation import SimulationConfig, Experiment, DayReport, GenerationReport, TreeInteractionLog
from .world import World, Tree

__all__ = [
    # Creatures
    "Creature",
    "Herbivore",
    "Predator",
    # Genes – herbivore
    "Gene",
    "CowardGene",
    "AltruistGene",
    "SelectiveAltruistGene",
    "GreenBeardGene",
    "SocialGene",
    "SolitaryGene",
    "HiddenHerbivoreGene",
    # Genes – predator
    "CamouflageGene",
    "AmbushGene",
    "CautiousPredatorGene",
    "GreedyHunterGene",
    # Aliases
    "GreenBeardAltruistGene",
    "NoPhysicalGene",
    # Simulation contracts
    "SimulationConfig",
    "Experiment",
    "DayReport",
    "GenerationReport",
    "TreeInteractionLog",
    # World
    "World",
    "Tree",
]
