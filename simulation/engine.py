"""
Motor de la simulación: configuración, fábrica de poblaciones y ciclo diario.

Módulo principal de ejecución. Contiene:
- SimulationConfig  → parámetros ajustables de una simulación.
- PopulationFactory → crea la población inicial para cada experimento.
- Simulation        → motor del ciclo diario de la simulación.
"""

import random
from dataclasses import dataclass, replace
from typing import List, Optional, Tuple

from .models import Creature, Trait, BeardColor, DayStats
from .strategies import PredatorEncounterStrategy


@dataclass
class SimulationConfig:
    """
    Parámetros de configuración de una simulación.

    Centralizar la configuración en un dataclass desacopla los parámetros
    de la lógica de simulación (Principio de Inversión de Dependencias).

    Attributes:
        num_trees:                Número total de árboles en el entorno.
        num_predator_trees:       Árboles que contienen un depredador por día.
                                  Se redistribuyen aleatoriamente cada día.
        initial_population:       Tamaño inicial de la población.
        num_days:                 Duración de la simulación en días.
        escape_probability:       Prob. (0-1) de que el altruista escape al
                                  depredador tras avisar a su compañera.
        offspring_range:          (min, max) hijos adicionales por criatura
                                  sobreviviente. Los hijos heredan todos los rasgos.
        max_population:           Capacidad de carga del entorno.
                                  None = sin límite (puede crecer indefinidamente).
        num_runs:                 Repeticiones de la simulación para obtener
                                  estadísticas robustas (media ± std).
        initial_altruist_ratio:   Fracción inicial de altruistas (0-1).
        initial_green_beard_ratio: Fracción inicial con barba verde (0-1).
                                  Solo relevante para el Experimento 3.
        random_seed:              Semilla base para reproducibilidad.
                                  None = completamente aleatorio.
    """
    num_trees:                int            = 50
    num_predator_trees:       int            = 10
    initial_population:       int            = 100
    num_days:                 int            = 200
    escape_probability:       float          = 0.5
    offspring_range:          Tuple[int,int] = (1, 2)
    max_population:           Optional[int]  = 2000
    num_runs:                 int            = 15
    initial_altruist_ratio:   float          = 0.5
    initial_green_beard_ratio: float         = 0.5
    random_seed:              Optional[int]  = 42

    def __post_init__(self) -> None:
        """Valida la consistencia de los parámetros al construir el objeto."""
        if not 0.0 <= self.initial_altruist_ratio <= 1.0:
            raise ValueError("initial_altruist_ratio debe estar entre 0 y 1.")
        if not 0.0 <= self.escape_probability <= 1.0:
            raise ValueError("escape_probability debe estar entre 0 y 1.")
        if not 0.0 <= self.initial_green_beard_ratio <= 1.0:
            raise ValueError("initial_green_beard_ratio debe estar entre 0 y 1.")
        if self.num_predator_trees > self.num_trees:
            raise ValueError("num_predator_trees no puede superar num_trees.")
        if self.offspring_range[0] > self.offspring_range[1]:
            raise ValueError("offspring_range[0] debe ser <= offspring_range[1].")

    def with_changes(self, **kwargs) -> "SimulationConfig":
        """
        Retorna una copia de la configuración con los campos indicados modificados.

        Conveniente para crear variantes de una configuración base sin
        repetir todos los parámetros.

        Args:
            **kwargs: Campos a modificar (deben ser atributos válidos de SimulationConfig).

        Returns:
            Nueva instancia de SimulationConfig con los cambios aplicados.

        Example:
            cfg_50 = cfg_base.with_changes(escape_probability=0.5)
            cfg_70 = cfg_base.with_changes(escape_probability=0.7)
        """
        return replace(self, **kwargs)


class PopulationFactory:
    """
    Crea la población inicial para cada experimento.

    Principio de Responsabilidad Única: esta clase solo construye listas
    de criaturas según la configuración; no sabe nada sobre la dinámica
    ni el ciclo de la simulación.

    Métodos estáticos disponibles:
        create_exp1_population → Experimento 1 (sin barba verde)
        create_exp2_population → Experimento 2 (barba verde ↔ altruismo)
        create_exp3_population → Experimento 3 (4 fenotipos independientes)
    """

    @staticmethod
    def create_exp1_population(config: SimulationConfig) -> List[Creature]:
        """
        Población para el Experimento 1: sin barba verde.

        Todas las criaturas carecen de barba verde. La única distinción
        es el rasgo de comportamiento (altruista o cobarde).

        Args:
            config: Configuración con initial_population e initial_altruist_ratio.

        Returns:
            Lista mezclada de criaturas, todas sin barba verde.
        """
        n           = config.initial_population
        n_altruists = int(n * config.initial_altruist_ratio)
        n_cowards   = n - n_altruists
        creatures = (
            [Creature(trait=Trait.ALTRUIST, beard=BeardColor.NONE)] * n_altruists +
            [Creature(trait=Trait.COWARD,   beard=BeardColor.NONE)] * n_cowards
        )
        random.shuffle(creatures)
        return creatures

    @staticmethod
    def create_exp2_population(config: SimulationConfig) -> List[Creature]:
        """
        Población para el Experimento 2: barba verde ↔ altruismo.

        Todos los altruistas tienen barba verde y ningún cobarde la tiene.
        Los genes de barba y altruismo están perfectamente correlacionados.

        Args:
            config: Configuración con initial_population e initial_altruist_ratio.

        Returns:
            Lista mezclada donde altruista=barba_verde y cobarde=sin_barba.
        """
        n           = config.initial_population
        n_altruists = int(n * config.initial_altruist_ratio)
        n_cowards   = n - n_altruists
        creatures = (
            [Creature(trait=Trait.ALTRUIST, beard=BeardColor.GREEN)] * n_altruists +
            [Creature(trait=Trait.COWARD,   beard=BeardColor.NONE)]  * n_cowards
        )
        random.shuffle(creatures)
        return creatures

    @staticmethod
    def create_exp3_population(config: SimulationConfig) -> List[Creature]:
        """
        Población para el Experimento 3: 4 fenotipos con genes independientes.

        Los genes de altruismo (ar) y barba verde (gr) son independientes,
        generando los siguientes 4 fenotipos:

            Altruista + Barba Verde  → proporción: ar  × gr
            Altruista + Sin Barba   → proporción: ar  × (1 - gr)
            Cobarde   + Barba Verde  → proporción: (1-ar) × gr
            Cobarde   + Sin Barba    → proporción: (1-ar) × (1-gr)

        Args:
            config: Configuración con initial_population, initial_altruist_ratio
                    e initial_green_beard_ratio.

        Returns:
            Lista mezclada de criaturas con los 4 fenotipos.
        """
        n  = config.initial_population
        ar = config.initial_altruist_ratio
        gr = config.initial_green_beard_ratio
        n_ag = int(n * ar       * gr)        # Altruista + Barba Verde
        n_an = int(n * ar       * (1 - gr))  # Altruista + Sin Barba
        n_cg = int(n * (1 - ar) * gr)        # Cobarde   + Barba Verde
        n_cn = n - n_ag - n_an - n_cg        # Cobarde   + Sin Barba (resto)
        creatures = (
            [Creature(trait=Trait.ALTRUIST, beard=BeardColor.GREEN)] * n_ag +
            [Creature(trait=Trait.ALTRUIST, beard=BeardColor.NONE)]  * n_an +
            [Creature(trait=Trait.COWARD,   beard=BeardColor.GREEN)] * n_cg +
            [Creature(trait=Trait.COWARD,   beard=BeardColor.NONE)]  * n_cn
        )
        random.shuffle(creatures)
        return creatures


class Simulation:
    """
    Motor central de la simulación evolutiva.

    Gestiona el ciclo diario completo: asignación de criaturas a árboles,
    resolución de encuentros con depredadores, reproducción y registro
    de estadísticas.

    Ciclo diario:
        1. Mezclar aleatoriamente la población.
        2. Agrupar criaturas en parejas (o individualmente si el total es
           impar) y asignar cada grupo a un árbol elegido al azar.
        3. Árbol SIN depredador → todas las criaturas del grupo sobreviven.
        4. Árbol CON depredador → se aplica la PredatorEncounterStrategy.
        5. Cada sobreviviente produce 1..N hijos adicionales que heredan
           todos sus rasgos (reproducción asexual sin mutación).
        6. Si la población supera max_population → muestreo aleatorio.
        7. Registrar estadísticas del día.

    Attributes:
        config:    Configuración de la simulación.
        strategy:  Estrategia de encuentro con depredadores (inyectada).
        creatures: Población actual de criaturas.
        history:   Historial de DayStats (un elemento por día simulado).

    Notes:
        Principio de Inversión de Dependencias: Simulation depende de la
        interfaz abstracta PredatorEncounterStrategy, no de ninguna
        implementación concreta. Esto permite intercambiar la estrategia
        sin tocar esta clase.
    """

    def __init__(
        self,
        config:             SimulationConfig,
        strategy:           PredatorEncounterStrategy,
        initial_population: List[Creature],
    ) -> None:
        """
        Inicializa el motor de simulación.

        Args:
            config:             Configuración de la simulación.
            strategy:           Estrategia de encuentro (inyección de dependencia).
            initial_population: Población inicial (se copia internamente para
                                evitar efectos secundarios en el llamador).
        """
        self.config    = config
        self.strategy  = strategy
        self.creatures = list(initial_population)
        self.history:  List[DayStats] = []

    # ---- Métodos privados ----------------------------------------

    def _assign_to_trees(self) -> Tuple[List[Tuple[bool, List[Creature]]], int]:
        """
        Mezcla la población, llena los árboles y devuelve las criaturas
        que no encontraron árbol libre (mueren de hambre).

        Cada árbol admite EXACTAMENTE 2 criaturas por día. Si hay más
        criaturas que `num_trees × 2`, el exceso no puede alimentarse
        ni reproducirse (muere). Este límite es la capacidad de carga
        natural del entorno; no hace falta un cap artificial.

        Returns:
            Tupla (assignments, starved) donde:
            - assignments: lista de (tiene_depredador, [criaturas_en_el_árbol])
            - starved:     número de criaturas que no encontraron árbol
        """
        total_capacity = self.config.num_trees * 2
        shuffled = list(self.creatures)
        random.shuffle(shuffled)

        assigned = shuffled[:total_capacity]          # caben en árboles
        starved  = len(shuffled) - len(assigned)      # sin árbol → mueren

        predator_set = set(
            random.sample(
                range(self.config.num_trees),
                min(self.config.num_predator_trees, self.config.num_trees),
            )
        )
        assignments: List[Tuple[bool, List[Creature]]] = []
        for i in range(0, len(assigned), 2):
            group    = assigned[i : i + 2]
            tree_idx = i // 2          # par 0 → árbol 0, par 1 → árbol 1, ...
            assignments.append((tree_idx in predator_set, group))
        return assignments, starved

    def _reproduce(
        self,
        survivors: List[Creature],
    ) -> Tuple[List[Creature], int]:
        """
        Genera la nueva generación a partir de los sobrevivientes.

        Cada criatura sobreviviente llama a reproduce() (1 o 2 hijos idénticos)
        y luego MUERE: la nueva generación está formada ÚNICAMENTE por los hijos.
        El progenitor no se incluye en la siguiente ronda.

        Ciclo real: criatura sale → posible muerte por depredador → las que
        sobreviven regresan a casa, dejan 1 o 2 hijos y desaparecen.

        Args:
            survivors: Criaturas que sobrevivieron el encuentro con depredadores.

        Returns:
            Tupla (nueva_población, nacimientos).
        """
        offspring: List[Creature] = []
        for creature in survivors:
            offspring.extend(creature.reproduce())  # padre muere; quedan 1 o 2 hijos
        births = len(offspring)
        if self.config.max_population and births > self.config.max_population:
            random.shuffle(offspring)
            offspring = offspring[: self.config.max_population]
        return offspring, births

    def _collect_stats(self, day: int, deaths: int, births: int) -> DayStats:
        """
        Recolecta estadísticas de la población actual al final del día.

        Args:
            day:    Número del día actual (1-indexado).
            deaths: Muertes ocurridas durante el día.
            births: Nacimientos ocurridos durante el día.

        Returns:
            DayStats con todos los conteos de tipos de criaturas.
        """
        ag = sum(1 for c in self.creatures
                 if c.trait == Trait.ALTRUIST and c.beard == BeardColor.GREEN)
        an = sum(1 for c in self.creatures
                 if c.trait == Trait.ALTRUIST and c.beard == BeardColor.NONE)
        cg = sum(1 for c in self.creatures
                 if c.trait == Trait.COWARD   and c.beard == BeardColor.GREEN)
        cn = sum(1 for c in self.creatures
                 if c.trait == Trait.COWARD   and c.beard == BeardColor.NONE)
        return DayStats(
            day                     = day,
            total_population        = len(self.creatures),
            altruist_count          = ag + an,
            coward_count            = cg + cn,
            green_beard_count       = ag + cg,
            altruist_green_count    = ag,
            altruist_no_green_count = an,
            coward_green_count      = cg,
            coward_no_green_count   = cn,
            deaths                  = deaths,
            births                  = births,
        )

    # ---- Métodos públicos ----------------------------------------

    def run_day(self) -> DayStats:
        """
        Ejecuta un día completo de la simulación.

        Ciclo:
          1. Criaturas salen a buscar árbol (capacidad: 2 por árbol).
          2. Las que no encuentran árbol mueren de hambre.
          3. Depredadores cazan en sus árboles asignados.
          4. Sobrevivientes regresan, dejan 1-2 hijos y mueren.

        Returns:
            DayStats con las estadísticas del día recién simulado.
        """
        day_number               = len(self.history) + 1
        assignments, starved     = self._assign_to_trees()
        survivors: List[Creature] = []
        predator_deaths: int      = 0
        for has_predator, group in assignments:
            if not has_predator:
                survivors.extend(group)
            else:
                escaped = self.strategy.handle_encounter(
                    group, self.config.escape_probability
                )
                survivors.extend(escaped)
                predator_deaths += len(group) - len(escaped)
        self.creatures, births = self._reproduce(survivors)
        total_deaths = predator_deaths + starved
        stats = self._collect_stats(day_number, total_deaths, births)
        self.history.append(stats)
        return stats

    def run(self) -> List[DayStats]:
        """
        Ejecuta la simulación completa durante config.num_days días.

        La simulación se detiene anticipadamente si la población
        se extingue completamente.

        Returns:
            Lista de DayStats con el historial completo de la simulación.
        """
        for _ in range(self.config.num_days):
            self.run_day()
            if not self.creatures:
                break  # Extinción: no tiene sentido continuar
        return self.history
