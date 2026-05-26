"""
main.py – entry point for the Cowardice vs Altruism simulation
===============================================================

Usage examples
--------------
Run all experiments (text output only):
    python main.py

Run a single experiment:
    python main.py --exp 2

Show interactive plots:
    python main.py --plot

Save plots to a file:
    python main.py --save-plot results/plots.png

Suppress per-generation output:
    python main.py --no-verbose

Combine flags:
    python main.py --exp 3 --plot --save-plot results/exp03.png
"""

import argparse
import sys
from pathlib import Path

# Ensure the project root is on sys.path so "simulation" is importable
# whether the script is run from the repo root or another directory.
sys.path.insert(0, str(Path(__file__).resolve().parent))

from simulation.experiments.exp01_baseline import BaselineExperiment
from simulation.experiments.exp02_altruism_cowardice import AltruismCowardiceExperiment
from simulation.experiments.exp03_green_beard import GreenBeardExperiment
from simulation.experiments.exp04_separated_genes import SeparatedGenesExperiment
from simulation.analysis.reporter import plot_results, print_summary

EXPERIMENTS = {
    1: BaselineExperiment,
    2: AltruismCowardiceExperiment,
    3: GreenBeardExperiment,
    4: SeparatedGenesExperiment,
}


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        description="Cowardice vs Altruism – evolutionary simulation",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    p.add_argument(
        "--exp",
        type=int,
        choices=list(EXPERIMENTS),
        default=None,
        metavar="{1,2,3,4}",
        help="Experiment number to run (default: all).",
    )
    p.add_argument(
        "--plot",
        action="store_true",
        default=False,
        help="Display interactive matplotlib plots.",
    )
    p.add_argument(
        "--save-plot",
        type=str,
        default=None,
        metavar="PATH",
        help="Save plots to PATH (e.g. results/plots.png).",
    )
    p.add_argument(
        "--no-verbose",
        action="store_true",
        default=False,
        help="Suppress per-generation progress output.",
    )
    return p


def main() -> None:
    args = build_parser().parse_args()
    verbose = not args.no_verbose

    experiment_classes = (
        [EXPERIMENTS[args.exp]] if args.exp is not None else list(EXPERIMENTS.values())
    )

    results = []
    for cls in experiment_classes:
        experiment = cls()
        result = experiment.run(verbose=verbose)
        print_summary(result)
        results.append(result)

    if args.plot or args.save_plot:
        plot_results(results, save_path=args.save_plot, show=args.plot)


if __name__ == "__main__":
    main()
