"""
simulation/experiments/base.py
================================
Experiment abstract base class + ExperimentResult.

How to create a new experiment
-------------------------------
1. Subclass ``Experiment``.
2. Override ``name``, ``description``, ``config``, and ``population_specs``.
3. ``population_specs`` is a list of ``(genome_factory, fraction)`` pairs.
   Each factory is a zero-argument callable that returns a list of Gene
   instances.  Fractions should sum to ≈ 1.0.

Example::

    class MyExperiment(Experiment):
        @property
        def name(self): return "My experiment"

        @property
        def description(self): return "Testing X vs Y"

        @property
        def config(self): return SimConfig(num_generations=50)

        @property
        def population_specs(self):
            return [
                (lambda: [AltruistGene()], 0.5),
                (lambda: [],               0.5),
            ]
"""

from __future__ import annotations

import random
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Callable, Dict, List, Tuple

from simulation.config import SimConfig
from simulation.core.creature import Creature
from simulation.core.engine import GenerationReport, SimulationEngine
from simulation.core.gene import Gene
from simulation.core.world import World


# ---------------------------------------------------------------------------
# Result container
# ---------------------------------------------------------------------------

@dataclass
class ExperimentResult:
    """All data produced by a completed experiment."""

    name: str
    config: SimConfig
    reports: List[GenerationReport] = field(default_factory=list)

    def gene_frequency_history(self) -> Dict[str, List[float]]:
        """
        Return a dict mapping gene_name → list of per-generation frequencies.
        Generations where a gene is absent are recorded as 0.0.
        """
        all_genes: set = set()
        for r in self.reports:
            all_genes.update(r.gene_frequencies.keys())

        history: Dict[str, List[float]] = {g: [] for g in sorted(all_genes)}
        for r in self.reports:
            for g in sorted(all_genes):
                history[g].append(r.gene_frequencies.get(g, 0.0))
        return history

    def population_history(self) -> List[int]:
        """Return population size at the end of each generation."""
        return [r.population_end for r in self.reports]

    @property
    def final_report(self) -> GenerationReport | None:
        return self.reports[-1] if self.reports else None


# ---------------------------------------------------------------------------
# Type alias for population specification
# ---------------------------------------------------------------------------

#: List of (genome_factory, fraction) pairs.
PopulationSpec = List[Tuple[Callable[[], List[Gene]], float]]


# ---------------------------------------------------------------------------
# Abstract Experiment
# ---------------------------------------------------------------------------

class Experiment(ABC):
    """
    Abstract base class for all simulation experiments.

    Subclasses are fully declarative: they only need to describe WHAT
    to simulate.  The ``run`` method handles all mechanics.
    """

    @property
    @abstractmethod
    def name(self) -> str:
        """Short human-readable name for this experiment."""

    @property
    @abstractmethod
    def description(self) -> str:
        """Multi-line description of what this experiment tests."""

    @property
    @abstractmethod
    def config(self) -> SimConfig:
        """Simulation parameters for this experiment."""

    @property
    @abstractmethod
    def population_specs(self) -> PopulationSpec:
        """
        Describe the initial population as a list of (factory, fraction) pairs.

        Each factory is called once per creature and must return a fresh
        list of Gene instances.  Fractions should sum to ≈ 1.0.
        """

    # ------------------------------------------------------------------
    # Population construction
    # ------------------------------------------------------------------

    def build_initial_population(self) -> List[Creature]:
        """
        Build the starting population according to ``population_specs``.

        Handles rounding: the last group absorbs any leftover creatures
        so that the total is always exactly ``config.initial_population``.
        """
        cfg = self.config
        rng = random.Random(cfg.seed)
        total = cfg.initial_population
        specs = self.population_specs

        creatures: List[Creature] = []
        remaining = total

        for i, (factory, fraction) in enumerate(specs):
            if i == len(specs) - 1:
                count = max(0, remaining)
            else:
                count = round(total * fraction)
                remaining -= count
            for _ in range(count):
                creatures.append(Creature(genome=factory()))

        rng.shuffle(creatures)
        return creatures

    # ------------------------------------------------------------------
    # Main run loop
    # ------------------------------------------------------------------

    def run(self, verbose: bool = True) -> ExperimentResult:
        """
        Execute the experiment and return an ExperimentResult.

        Parameters
        ----------
        verbose:
            Print per-generation progress to stdout.
        """
        cfg = self.config
        world = World(
            num_houses=cfg.world.num_houses,
            num_trees=cfg.world.num_trees,
        )
        rng = random.Random(cfg.seed)

        engine = SimulationEngine(
            world=world,
            predator_probability=cfg.predator_probability,
            offspring_range=(cfg.offspring_min, cfg.offspring_max),
            mutation_rate=cfg.mutation_rate,
            rng=rng,
        )

        creatures = self.build_initial_population()
        result = ExperimentResult(name=self.name, config=cfg)

        if verbose:
            _print_header(self, world)

        for gen in range(cfg.num_generations):
            if not creatures:
                if verbose:
                    print(f"  Gen {gen:3d}: EXTINCTION – simulation stopped.")
                break

            creatures, report = engine.run_generation(creatures, gen)
            result.reports.append(report)

            if verbose and (gen % 10 == 0 or gen < 5):
                _print_generation(report)

        if verbose and result.reports:
            _print_final(result)

        return result


# ---------------------------------------------------------------------------
# Verbose output helpers (private)
# ---------------------------------------------------------------------------

def _print_header(exp: Experiment, world: World) -> None:
    width = 62
    print(f"\n{'=' * width}")
    print(f"  {exp.name}")
    for line in exp.description.splitlines():
        print(f"  {line}")
    print(f"{'=' * width}")
    cfg = exp.config
    pop = cfg.initial_population
    slots = world.total_tree_capacity()
    print(
        f"  Population: {pop}  |  Trees: {cfg.world.num_trees}"
        f" ({slots} slots)  |  Predator prob: {cfg.predator_probability:.0%}"
        f"  |  Gens: {cfg.num_generations}"
    )
    print()


def _print_generation(r: GenerationReport) -> None:
    freq_parts = ", ".join(
        f"{g}={f:.0%}" for g, f in sorted(r.gene_frequencies.items())
    )
    genes_str = f"[{freq_parts}]" if freq_parts else "[no genes]"
    print(
        f"  Gen {r.generation:3d}: "
        f"pop={r.population_end:5d} "
        f"| survived={r.survived:4d} "
        f"| eaten={r.eaten:4d} "
        f"| starved={r.starved:4d} "
        f"| {genes_str}"
    )


def _print_final(result: ExperimentResult) -> None:
    fr = result.final_report
    print(f"\n  --- Final state (gen {fr.generation}) ---")
    print(f"  Population: {fr.population_end}")
    for g, f in sorted(fr.gene_frequencies.items()):
        bar = "█" * int(f * 30)
        print(f"  {g:25s}: {f:5.1%}  {bar}")
    print()
