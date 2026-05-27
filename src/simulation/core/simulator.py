from collections import Counter
from typing import List
import random

from .simulation import GenerationReport, SimulationConfig, Experiment
from .world import World, Tree
from .creature import Creature


class Simulator:
    """Runs an Experiment day-by-day and collects GenerationReport objects."""

    def __init__(self, experiment: Experiment):
        self.experiment = experiment
        self.config: SimulationConfig = experiment.config

    def _initialize_population(self) -> List[Creature]:
        cfg = self.config
        specs = self.experiment.population_specs
        initial = cfg.initial_population

        # Compute integer counts for each spec; ensure total equals initial
        counts = []
        remaining = initial
        for i, (_fn, frac) in enumerate(specs):
            if i == len(specs) - 1:
                count = remaining
            else:
                count = int(round(frac * initial))
                remaining -= count
            counts.append(count)
        # adjust rounding if necessary
        if sum(counts) != initial:
            diff = initial - sum(counts)
            counts[0] += diff

        population: List[Creature] = []
        for (fn, _), count in zip(specs, counts):
            for _ in range(count):
                genome = fn()
                c = Creature(genome=genome, min_offspring=cfg.offspring_min, max_offspring=cfg.offspring_max)
                population.append(c)

        return population

    def run(self) -> List[GenerationReport]:
        cfg = self.config
        if cfg.seed is not None:
            random.seed(cfg.seed)

        population = self._initialize_population()
        reports: List[GenerationReport] = []
        for gen in range(1, cfg.num_generations + 1):
            population_start = len(population)

            # Create world and trees
            trees = [Tree(tree_id=i) for i in range(cfg.num_trees)]
            world = World(num_trees=cfg.num_trees, trees=trees)

            # Determine total feeding capacity
            total_capacity = sum(t.max_capacity for t in trees)

            # Prepare assignments: either fill trees to capacity (if overpopulated)
            assignments = {t.tree_id: [] for t in trees}
            starved = 0
            eaten = 0

            if population_start > total_capacity:
                # Some creatures die by hunger immediately
                starved = population_start - total_capacity
                shuffled = population.copy()
                random.shuffle(shuffled)
                survivors_for_assignment = shuffled[:total_capacity]
                idx = 0
                for t in trees:
                    cap = t.max_capacity
                    assignments[t.tree_id] = survivors_for_assignment[idx : idx + cap]
                    idx += cap
            else:
                # Place each creature into a random available slot (no one starves by hunger)
                slots = []
                for t in trees:
                    slots.extend([t.tree_id] * t.max_capacity)
                chosen = random.sample(slots, k=population_start)
                shuffled = population.copy()
                random.shuffle(shuffled)
                for creature, pos in zip(shuffled, chosen):
                    assignments[pos].append(creature)

            # Resolve predators and who survives per tree
            survivors: List[Creature] = []

            for t in trees:
                assigned = assignments[t.tree_id]
                if not assigned:
                    continue
                t.has_predator = random.random() < cfg.predator_probability

                if not t.has_predator:
                    # No predator: everyone assigned survives
                    survivors.extend(assigned)
                    continue

                # Predator present
                if len(assigned) == 1:
                    # Single occupant dies
                    eaten += 1
                    continue

                # Choose a random detector among the occupants
                detector = random.choice(assigned)
                survivor_list, eaten_count = detector.handle_predator(assigned, cfg)
                # Add survivors and eaten counts
                survivors.extend(survivor_list)
                eaten += eaten_count

            # Reproduction: survivors reproduce (1..N offspring) and then die
            new_population: List[Creature] = []
            for c in survivors:
                descendants = c.reproduce()
                new_population.extend(descendants)
                # Note: parents die after reproduction, so we don't add them to new_population
                # (If we wanted parents to survive, we'd add `new_population.append(c)` here as well.)
                
                
                # num_offspring = random.randint(cfg.offspring_min, cfg.offspring_max)
                # for _ in range(num_offspring):
                #     child = Creature(genome=[*c.genome], min_offspring=cfg.offspring_min, max_offspring=cfg.offspring_max)
                #     new_population.append(child)

            population = new_population

            # Compute gene frequencies on the new population
            counter = Counter()
            for c in population:
                for g in c.genome:
                    key = getattr(g, "name", type(g).__name__)
                    counter[key] += 1
            total = sum(counter.values()) or 1
            freqs = {k: v / total for k, v in counter.items()}

            report = GenerationReport(
                generation=gen,
                population_start=population_start,
                starved=starved,
                eaten=eaten,
                survived=len(survivors),
                population_end=len(population),
                gene_frequencies=freqs,
            )
            reports.append(report)

            if len(population) == 0:
                break

        return reports
    
