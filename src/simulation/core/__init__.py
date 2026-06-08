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
    CamouflageHerbivoreGene,
    CamouflagePredatorGene,
    AmbushGene,
    CautiousPredatorGene,
    GreedyHunterGene,
    SocialGreenBeardAltruistGene,
    SolitaryCowardGene,
    AmbushCamoGene,
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
    "CamouflageHerbivoreGene",
    # Genes – predator
    "CamouflagePredatorGene",
    "AmbushGene",
    "CautiousPredatorGene",
    "GreedyHunterGene",
    # Composite genes
    "SocialGreenBeardAltruistGene",
    "SolitaryCowardGene",
    "AmbushCamoGene",
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
