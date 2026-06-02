"""Dynamic discovery utilities for experiment instances and configurations.

This module discovers Python modules under the `simulation.instances`
subpackages `experiments` and `configurations` and returns mappings of
available experiment classes/instances and `SimulationConfig` objects.

Usage:
    from simulation.instances.loader import discover_experiments, discover_configurations

    exps = discover_experiments()
    configs = discover_configurations()

Keys are simple names (class name for experiment classes, variable name for
config objects). Values are the class or instance objects.
"""
from __future__ import annotations

import importlib
import inspect
import pkgutil
import sys
from typing import Dict, Any

from simulation.core.simulation import Experiment, SimulationConfig


def _iter_submodules(package_name: str):
    try:
        pkg = importlib.import_module(package_name)
    except Exception:
        return
    if not hasattr(pkg, "__path__"):
        return
    for finder, name, ispkg in pkgutil.iter_modules(pkg.__path__):
        yield f"{package_name}.{name}"


def discover_experiments(package_name: str = "simulation.instances.experiments") -> Dict[str, Any]:
    """Return a mapping of experiment name -> class or instance found under package.

    The function imports each module under `package_name` and looks for:
    - classes that subclass `Experiment` (excluding the base class)
    - module-level instances that are instances of `Experiment`

    The mapping key is the class name for classes, or the variable name for
    instances.
    """
    experiments: Dict[str, Any] = {}
    for full in _iter_submodules(package_name):
        try:
            m = importlib.import_module(full)
        except Exception as exc:
            print(f"warning: failed to import {full}: {exc}", file=sys.stderr)
            continue

        for name, obj in inspect.getmembers(m, inspect.isclass):
            try:
                if issubclass(obj, Experiment) and obj is not Experiment:
                    experiments[name] = obj
            except Exception:
                continue

        for name, obj in inspect.getmembers(m):
            if isinstance(obj, Experiment):
                experiments[name] = obj

    return experiments


def discover_configurations(package_name: str = "simulation.instances.configurations") -> Dict[str, SimulationConfig]:
    """Return a mapping of configuration variable name -> SimulationConfig instance.

    The function imports each module under `package_name` and returns any
    module-level objects that are instances of `SimulationConfig`.
    """
    configs: Dict[str, SimulationConfig] = {}
    for full in _iter_submodules(package_name):
        try:
            m = importlib.import_module(full)
        except Exception as exc:
            print(f"warning: failed to import {full}: {exc}", file=sys.stderr)
            continue

        for name, obj in inspect.getmembers(m):
            if isinstance(obj, SimulationConfig):
                configs[name] = obj

    return configs


def discover_all() -> Dict[str, Dict[str, Any]]:
    return {
        "experiments": discover_experiments(),
        "configurations": discover_configurations(),
    }
