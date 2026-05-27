#!/usr/bin/env python3
"""Simple runner to verify package imports and print experiment metadata."""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
# Ensure 'src' is on sys.path
sys.path.insert(0, str(ROOT / "src"))

from simulation.instances.loader import discover_experiments, discover_configurations
from simulation.core.simulator import Simulator
from simulation.core.simulation import SimulationConfig


def main() -> None:
    import argparse
    parser = argparse.ArgumentParser(description="Run simulation")
    parser.add_argument("--plot", action="store_true", help="Generate plots after running")
    parser.add_argument("--show", action="store_true", help="Show plots interactively (implies --plot)")
    parser.add_argument("--list-experiments", action="store_true", help="List discovered experiments")
    parser.add_argument("--list-configs", action="store_true", help="List discovered configurations")
    parser.add_argument("--experiment", "-e", help="Experiment name to run (use --list-experiments)")
    parser.add_argument("--config", "-c", help="Configuration name to use (use --list-configs)")
    parser.add_argument("--run-all", action="store_true", help="Run all experiments with all discovered configurations")
    args = parser.parse_args()

    exps = discover_experiments()
    configs = discover_configurations()

    if args.list_experiments:
        if not exps:
            print("No experiments discovered")
        for name, obj in exps.items():
            print(name, "->", getattr(obj, "__module__", ""))
        return

    if args.list_configs:
        if not configs:
            print("No configurations discovered")
        for name, cfg in configs.items():
            print(name, cfg)
        return

    runs = []  # list of tuples (exp_obj_or_class, config_obj_or_None, label)

    if args.run_all:
        # Run every experiment with every discovered config (or its default if none)
        for ename, exp in exps.items():
            for cname, cfg in (configs.items() or [(None, None)]):
                runs.append((exp, cfg, f"{ename}__{cname}"))
    else:
        # single experiment selection (or default to first discovered)
        if args.experiment:
            if args.experiment not in exps:
                print(f"Experiment '{args.experiment}' not found. Use --list-experiments to see available names.")
                return
            exp = exps[args.experiment]
        else:
            if not exps:
                print("No experiments discovered to run")
                return
            # pick first discovered
            first_name = next(iter(exps))
            exp = exps[first_name]

        if args.config:
            if args.config not in configs:
                print(f"Configuration '{args.config}' not found. Use --list-configs to see available names.")
                return
            cfg = configs[args.config]
            runs.append((exp, cfg, f"{getattr(exp,'__name__',str(exp))}__{args.config}"))
        else:
            # run with experiment's own config if available, else with no override or first discovered config
            if isinstance(exp, type):
                exp_inst = exp()
            else:
                exp_inst = exp

            if configs:
                # run using first discovered configuration in addition to experiment default
                first_cfg_name, first_cfg = next(iter(configs.items()))
                runs.append((exp, first_cfg, f"{getattr(exp,'__name__',str(exp))}__{first_cfg_name}"))
            else:
                runs.append((exp, None, f"{getattr(exp,'__name__',str(exp))}"))

    # Execute runs
    for exp, cfg, label in runs:
        # instantiate experiment if class
        if isinstance(exp, type):
            e = exp()
        else:
            e = exp

        # apply config override if provided
        if cfg is not None:
            try:
                # override instance attribute (shadows property)
                e.config = cfg
            except Exception:
                pass

        print("Running:", getattr(e, "name", repr(e)))
        sim = Simulator(e)
        reports = sim.run()
        for r in reports:
            print(f"Gen {r.generation}: start={r.population_start} eaten={r.eaten} starved={r.starved} fed_survived={r.survived} end={r.population_end}")

        # Plotting per-run
        if args.plot:
            try:
                from simulation.analysis.plotting import plot_population_stats, plot_gene_frequencies
                outdir = ROOT / "results" / "plots"
                outdir.mkdir(parents=True, exist_ok=True)
                safe_label = label.replace(None, "default")
                pop_path = outdir / f"population_{safe_label}.png"
                genes_path = outdir / f"gene_distribution_{safe_label}.png"
                plot_population_stats(reports, save_path=str(pop_path), show=args.show)
                plot_gene_frequencies(reports, save_path=str(genes_path), show=args.show)
                print("Saved plots to", outdir)
            except Exception as exc:
                print("Plotting skipped (missing dependency or error):", exc)

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
