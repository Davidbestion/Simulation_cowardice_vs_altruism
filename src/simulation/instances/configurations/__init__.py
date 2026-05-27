"""Package for simulation configuration variants.

Exposes the named `SimulationConfig` instances defined in
`configurations.py` at the package level for convenience.
"""
from .configurations import *

__all__ = [
    "default_config",
    "high_predation",
    "low_predation",
    "many_trees",
    "few_trees",
    "high_fecundity",
]
