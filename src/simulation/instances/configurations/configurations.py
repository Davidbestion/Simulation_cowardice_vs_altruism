
from simulation.core.simulation import SimulationConfig

# Centralized simulation configurations.
# ``num_generations``, ``initial_population``, ``offspring_min/max``, and
# ``predator_probability`` keep their old names for backward compatibility.
# New fields (``tree_capacity_min/max``, ``initial_predators``, etc.) can be
# added to any config as needed.

default_config = SimulationConfig(
    num_trees=25,
    tree_capacity_min=2,
    tree_capacity_max=6,
    num_generations=200,
    initial_population=80,
    initial_predators=10,
    offspring_min=1,
    offspring_max=2,
    base_detection_prob=0.3,
    altruist_escape_prob=0.5,
    predator_hunt_capacity=1,
    seed=42,
)

high_escape_prob = SimulationConfig(
    num_trees=25,
    tree_capacity_min=2,
    tree_capacity_max=6,
    num_generations=200,
    initial_population=80,
    initial_predators=10,
    offspring_min=1,
    offspring_max=2,
    base_detection_prob=0.3,
    altruist_escape_prob=0.9,
    predator_hunt_capacity=1,
    seed=42,
)

low_escape_prob = SimulationConfig(
    num_trees=25,
    tree_capacity_min=2,
    tree_capacity_max=6,
    num_generations=200,
    initial_population=80,
    initial_predators=10,
    offspring_min=1,
    offspring_max=2,
    base_detection_prob=0.3,
    altruist_escape_prob=0.1,
    predator_hunt_capacity=1,
    seed=42,
)

# high_predation = SimulationConfig(
# 	num_trees=25,
# 	num_generations=100,
# 	initial_population=80,
# 	predator_probability=0.60,
# 	offspring_min=1,
# 	offspring_max=2,
# 	seed=100,
# 	altruist_escape_prob=0.5,
# )

# low_predation = SimulationConfig(
# 	num_trees=25,
# 	num_generations=100,
# 	initial_population=80,
# 	predator_probability=0.10,
# 	offspring_min=1,
# 	offspring_max=2,
# 	seed=101,
# 	altruist_escape_prob=0.5,
# )

# many_trees = SimulationConfig(
# 	num_trees=50,
# 	num_generations=100,
# 	initial_population=200,
# 	predator_probability=0.30,
# 	offspring_min=1,
# 	offspring_max=2,
# 	seed=202,
# 	altruist_escape_prob=0.5,
# )

# few_trees = SimulationConfig(
# 	num_trees=10,
# 	num_generations=100,
# 	initial_population=40,
# 	predator_probability=0.30,
# 	offspring_min=1,
# 	offspring_max=2,
# 	seed=303,
# 	altruist_escape_prob=0.5,
# )

# high_fecundity = SimulationConfig(
# 	num_trees=25,
# 	num_generations=100,
# 	initial_population=80,
# 	predator_probability=0.30,
# 	offspring_min=2,
# 	offspring_max=4,
# 	seed=404,
# 	altruist_escape_prob=0.5,
# )

__all__ = [
	"default_config",
 	"high_escape_prob",
	# "high_predation",
	# "low_predation",
	# "many_trees",
	# "few_trees",
	# "high_fecundity",
]


