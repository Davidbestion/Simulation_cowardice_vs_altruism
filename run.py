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
    import argparse
    parser = argparse.ArgumentParser(description="Run simulation")
    parser.add_argument("--plot", action="store_true", help="Generate plots after running")
    parser.add_argument("--show", action="store_true", help="Show plots interactively (implies --plot)")
    args = parser.parse_args()

    e = Experiment1()
    sim = Simulator(e)
    print("Running:", e.name)
    reports = sim.run()
    for r in reports:
        print(f"Gen {r.generation}: start={r.population_start} eaten={r.eaten} starved={r.starved} fed_survived={r.survived} end={r.population_end}")

    if args.show:
        args.plot = True

    if args.plot:
        try:
            from simulation.analysis.plotting import plot_population_stats, plot_gene_frequencies
            outdir = ROOT / "results" / "plots"
            outdir.mkdir(parents=True, exist_ok=True)
            pop_path = outdir / "population.png"
            genes_path = outdir / "gene_distribution.png"
            plot_population_stats(reports, save_path=str(pop_path), show=args.show)
            plot_gene_frequencies(reports, save_path=str(genes_path), show=args.show)
            print("Saved plots to", outdir)
        except Exception as exc:
            print("Plotting skipped (missing dependency or error):", exc)


if __name__ == "__main__":
    main()
