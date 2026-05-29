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
from dataclasses import replace as dc_replace


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
    parser.add_argument("--repeats", "-r", type=int, default=1, help="Number of times to repeat each selected run")
    parser.add_argument("--aggregate", action="store_true", help="Create aggregated plots across repeats")
    parser.add_argument("--deterministic", action="store_true", help="When repeating, use deterministic seeds (base seed + run index). By default repeats are non-deterministic to produce varied outcomes.")
    args = parser.parse_args()

    if args.show:
        args.plot = True

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

    # Execute runs (support repeats and aggregated plotting)
    for exp, cfg, label in runs:
        safe_label = str(label).replace("None", "default")
        outdir = ROOT / "results" / "plots"
        outdir.mkdir(parents=True, exist_ok=True)

        all_reports = []
        exp_cls = exp if isinstance(exp, type) else type(exp)
        for i in range(max(1, args.repeats)):
            # instantiate fresh experiment for each repetition
            e_run = exp_cls()

            # determine base configuration and apply per-run seed if requested
            base_cfg = cfg if cfg is not None else getattr(e_run, "config", None)
            if base_cfg is not None:
                if args.repeats > 1:
                    # Default: make repeated runs vary. If the user requests deterministic
                    # repetition, generate seeds as base + index; otherwise leave seed None
                    # so the system RNG produces different runs.
                    if args.deterministic:
                        run_seed = base_cfg.seed + i if base_cfg.seed is not None else None
                        run_cfg = dc_replace(base_cfg, seed=run_seed)
                    else:
                        # If base_cfg has a seed, replace it with None to use system randomness.
                        run_cfg = dc_replace(base_cfg, seed=None) if base_cfg.seed is not None else base_cfg
                else:
                    run_cfg = base_cfg
                # override instance attribute (shadows property)
                try:
                    e_run.config = run_cfg
                except Exception:
                    pass

            print(f"Running: {getattr(e_run, 'name', repr(e_run))} (run {i+1}/{max(1, args.repeats)})")
            sim = Simulator(e_run, config_override=run_cfg if 'run_cfg' in locals() else None)
            reports = sim.run()
            all_reports.append(reports)
            for r in reports:
                print(f"Gen {r.generation}: start={r.population_start} eaten={r.eaten} starved={r.starved} fed_survived={r.survived} end={r.population_end}")

            # Per-run plotting
            if args.plot:
                try:
                    from simulation.analysis.plotting import plot_population_stats, plot_gene_frequencies
                    pop_path = outdir / f"population_{safe_label}_run{i+1}.png"
                    genes_path = outdir / f"gene_distribution_{safe_label}_run{i+1}.png"
                    plot_population_stats(reports, save_path=str(pop_path), show=args.show)
                    plot_gene_frequencies(reports, save_path=str(genes_path), show=args.show)
                    print("Saved plots to", outdir)
                except Exception as exc:
                    print("Plotting skipped (missing dependency or error):", exc)

        # Aggregated plotting across repeats
        if args.repeats > 1 and args.aggregate:
            try:
                from simulation.analysis.plotting import (
                    plot_aggregated_population_stats,
                    plot_aggregated_gene_frequencies_final,
                    plot_aggregated_gene_distribution,
                )
                pop_agg_path = outdir / f"population_agg_{safe_label}.png"
                genes_agg_path = outdir / f"gene_distribution_agg_{safe_label}.png"
                gene_evo_path = outdir / f"gene_evolution_agg_{safe_label}.png"
                plot_aggregated_population_stats(all_reports, save_path=str(pop_agg_path), show=args.show)
                plot_aggregated_gene_frequencies_final(all_reports, save_path=str(genes_agg_path), show=args.show)
                plot_aggregated_gene_distribution(all_reports, save_path=str(gene_evo_path), show=args.show)
                print("Saved aggregated plots to", outdir)
            except Exception as exc:
                print("Aggregated plotting skipped (missing dependency or error):", exc)

    # done


if __name__ == "__main__":
    main()
