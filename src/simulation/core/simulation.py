"""Core data structures: configuration, experiment contract, and day reports."""

from abc import ABC
from dataclasses import dataclass, field
from typing import Callable, Dict, List, Optional, Tuple


# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------


@dataclass
class SimulationConfig:
    """All tunable parameters for a simulation run.

    Field names from the original codebase (``num_generations``, ``initial_population``,
    ``offspring_min/max``, ``predator_probability``) are kept so that existing
    experiment and configuration files work without modification.  New semantics
    are exposed via ``@property`` aliases documented below.
    """

    # --- World ---
    num_trees: int = 25
    tree_capacity_min: int = 2          # minimum capacity drawn per tree
    tree_capacity_max: int = 6          # maximum capacity drawn per tree

    # --- Time (``num_days`` is a property alias) ---
    num_generations: int = 100

    # --- Initial population sizes ---
    initial_population: int = 80        # herbivores (``initial_herbivores`` alias)
    initial_predators: int = 10

    # --- Reproduction ---
    offspring_min: int = 1              # herbivore (also ``herbivore_offspring_min``)
    offspring_max: int = 2              # herbivore (also ``herbivore_offspring_max``)
    predator_offspring_min: int = 1
    predator_offspring_max: int = 1

    # --- Predation interactions ---
    # ``predator_probability`` is kept for config compatibility but unused in the
    # new agent-based simulator (predators are now explicit creatures).
    predator_probability: float = 0.0
    base_detection_prob: float = 0.3    # base probability each herbivore detects a predator
    altruist_escape_prob: float = 0.5   # probability altruist escapes after warning
    predator_hunt_capacity: int = 1     # max prey a predator catches per tree visit

    # --- Reproducibility ---
    seed: Optional[int] = 42

    # ------------------------------------------------------------------
    # Convenience aliases (read-only properties)
    # ------------------------------------------------------------------

    @property
    def num_days(self) -> int:
        """Alias for ``num_generations``."""
        return self.num_generations

    @property
    def initial_herbivores(self) -> int:
        """Alias for ``initial_population``."""
        return self.initial_population

    @property
    def herbivore_offspring_min(self) -> int:
        return self.offspring_min

    @property
    def herbivore_offspring_max(self) -> int:
        return self.offspring_max


# ---------------------------------------------------------------------------
# Experiment contract
# ---------------------------------------------------------------------------


class Experiment(ABC):
    """Base class for experiments.

    Subclasses must implement ``name``, ``description``, ``config``, and
    ``herbivore_specs``.  ``predator_specs`` defaults to an empty list
    (no explicit predator population).

    The old ``population_specs`` property is kept as an alias for
    ``herbivore_specs`` so that older experiment files continue to work.
    """

    @property
    def name(self) -> str:
        raise NotImplementedError

    @property
    def description(self) -> str:
        raise NotImplementedError

    @property
    def config(self) -> SimulationConfig:
        raise NotImplementedError

    @property
    def herbivore_specs(self) -> List[Tuple[Callable[[], list], float]]:
        """Especificaciones de las poblaciones de herbívoros.

        Debe devolver una lista de tuplas ``(genome_factory, fraction)`` donde:

        - ``genome_factory`` es un callable sin argumentos que devuelve la lista
          de genes de un herbívoro de este subtipo (p. ej. ``lambda: [CowardGene()]``).
        - ``fraction`` es la proporción del total de herbívoros que corresponde
          a este subtipo (entre 0 y 1; la suma de todas las fracciones debe
          ser aproximadamente 1).

        Ejemplo para una población mixta 50/50 cobardes y altruistas::

            return [
                (lambda: [CowardGene()],   0.5),
                (lambda: [AltruistGene()], 0.5),
            ]
        """
        raise NotImplementedError

    @property
    def predator_specs(self) -> List[Tuple[Callable[[], list], float]]:
        """Especificaciones de las poblaciones de depredadores.

        Misma estructura que ``herbivore_specs``: lista de tuplas
        ``(genome_factory, fraction)``.

        Devolver una lista vacía (comportamiento por defecto) equivale a
        no tener depredadores explícitos en el experimento.  En ese caso
        el simulador omite completamente las fases 2 y 3 (asignación de
        depredadores e interacciones depredador–presa).
        """
        return []

    @property
    def population_specs(self) -> List[Tuple[Callable[[], list], float]]:
        """Backward-compatibility alias for ``herbivore_specs``."""
        return self.herbivore_specs


# ---------------------------------------------------------------------------
# Per-tree interaction log
# ---------------------------------------------------------------------------


@dataclass
class TreeInteractionLog:
    """Registro de todo lo ocurrido en un árbol concreto durante un día.

    Una instancia se crea por cada árbol que tenía al menos un herbívoro
    asignado, y se adjunta al ``DayReport`` del día correspondiente.

    Atributos:
        tree_id            : Identificador del árbol.
        herbivores_present : Herbívoros asignados al árbol al inicio del día
                             (antes de cualquier interacción).
        predators_present  : Depredadores que eligieron este árbol.
        predator_detected  : ``True`` si al menos un herbívoro detectó al
                             depredador y activó un comportamiento de alarma.
        detector_gene      : Nombre del gen de comportamiento del herbívoro
                             detector (p. ej. ``"coward"``, ``"altruist"``),
                             o ``"none"`` si nadie detectó al depredador.
        fled               : Herbívoros que escaparon durante la fase de alarma
                             (antes de la caza).
        directly_eaten     : Herbívoros devorados directamente por el
                             comportamiento de alarma (p. ej. el altruista
                             que se sacrifica).
        hunted             : Herbívoros capturados durante la fase de caza
                             normal (los que no huyeron).
        survived           : Herbívoros que sobrevivieron el día en este árbol
                             (``herbivores_present - directly_eaten - hunted``).
    """

    tree_id: int
    herbivores_present: int
    predators_present: int
    predator_detected: bool
    detector_gene: str
    fled: int
    directly_eaten: int
    hunted: int
    survived: int


# ---------------------------------------------------------------------------
# Day (generation) report
# ---------------------------------------------------------------------------


@dataclass
class DayReport:
    """Estadísticas de un día completo de la simulación.

    Se crea uno por día y se adjunta a la lista que devuelve ``Simulator.run()``.
    Los nombres de los campos principales (``generation``, ``population_start``,
    ``eaten``, ``starved``, ``gene_frequencies``) se mantienen idénticos a los
    de la versión anterior para que el código de graficado siga funcionando sin
    cambios.

    Atributos:
        generation              : Número de día (base 1).
        population_start        : Herbívoros al inicio del día (antes de hambre
                                  y depredación).
        starved                 : Herbívoros que murieron de hambre (no encontraron
                                  sitio en ningún árbol).
        eaten                   : Herbívoros devorados en total (directamente en
                                  la alarma + cazados en la fase de caza).
        survived                : Herbívoros vivos al final del día, antes de
                                  reproducirse.
        population_end          : Herbívoros al inicio del día siguiente, tras la
                                  reproducción de los supervivientes.
        gene_frequencies        : Diccionario ``{nombre_gen: frecuencia}`` calculado
                                  sobre la nueva población de herbívoros (valores
                                  entre 0 y 1).
        predator_count_start    : Depredadores al inicio del día.
        predator_count_end      : Depredadores al inicio del día siguiente
                                  (tras su reproducción).
        predator_gene_frequencies: Frecuencias de genes en la población de
                                   depredadores al final del día.
        tree_interactions       : Lista de ``TreeInteractionLog``, uno por cada
                                  árbol con al menos un herbívoro ese día.  Permite
                                  reconstruir exactamente qué ocurrió en cada sitio.
    """

    # Core fields (used by plotting)
    generation: int                     # day number, 1-indexed
    population_start: int               # herbivore count at start of day
    starved: int                        # herbivores that found no tree slot
    eaten: int                          # total herbivores eaten (direct + hunted)
    survived: int                       # herbivores alive after interactions (before repro)
    population_end: int                 # herbivore count after reproduction
    gene_frequencies: Dict[str, float] = field(default_factory=dict)

    # New fields
    predator_count_start: int = 0
    predator_count_end: int = 0
    predator_gene_frequencies: Dict[str, float] = field(default_factory=dict)
    tree_interactions: List[TreeInteractionLog] = field(default_factory=list)

    @property
    def day(self) -> int:
        """Alias for ``generation``."""
        return self.generation


# Backward-compatibility alias
GenerationReport = DayReport
