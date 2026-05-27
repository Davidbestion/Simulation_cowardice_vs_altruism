#!/usr/bin/env python3
"""Simple runner to verify package imports and print experiment metadata."""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
# Ensure 'src' is on sys.path
sys.path.insert(0, str(ROOT / "src"))

from simulation.experiments.experiment_1 import Experiment1
from simulation.core.simulator import Simulator


def main() -> None:
    e = Experiment1()
    sim = Simulator(e)
    print("Running:", e.name)
    reports = sim.run()
    for r in reports:
        print(f"Gen {r.generation}: start={r.population_start} eaten={r.eaten} starved={r.starved} fed_survived={r.survived} end={r.population_end}")


if __name__ == "__main__":
    main()
