"""Utilidades de ejecución y definición de experimentos para notebooks y scripts.

Proporciona:
- ``RandomPredatorGene`` — gen de depredador con selección aleatoria de árbol.
- ``SimpleExperiment``   — implementación concreta de ``Experiment`` parametrizable.
- ``run_multiple``       — ejecuta un experimento N veces con semillas distintas.
"""
from __future__ import annotations

from dataclasses import replace as dc_replace
from typing import Callable, List, Optional, Tuple

from ..core.genes import Gene
from ..core.simulation import Experiment, SimulationConfig
from ..core.simulator import Simulator


class RandomPredatorGene(Gene):
    """Depredador con selección de árbol completamente aleatoria.

    A diferencia del comportamiento por defecto del depredador —que elige el árbol
    con más presas visibles—, este gen provoca que el depredador elija árbol al
    azar en cada generación.  Es el equivalente funcional del modelo de depredación
    estocástica del estudio original: la presión de depredación no está dirigida
    hacia los grupos más numerosos.
    """

    name = "random_predator"
    PRIORITY = 100

    def predator_choose_tree(self, predator, trees, visible_herbivores, cfg, rng):
        if not trees:
            return None
        return rng.choice(trees).tree_id


class SimpleExperiment(Experiment):
    """Implementación concreta de ``Experiment`` para uso en notebooks y scripts.

    Permite definir experimentos de forma declarativa especificando nombre,
    descripción, configuración y poblaciones directamente en el constructor,
    sin necesidad de crear una subclase dedicada para cada escenario.
    """

    def __init__(
        self,
        name: str,
        description: str,
        config: SimulationConfig,
        herbivore_specs: List[Tuple[Callable[[], list], float]],
        predator_specs: Optional[List[Tuple[Callable[[], list], float]]] = None,
    ) -> None:
        """
        Args:
            name            : Identificador del experimento.
            description     : Descripción breve de la hipótesis o condición experimental.
            config          : Parámetros de la simulación (``SimulationConfig``).
            herbivore_specs : Lista de tuplas ``(genome_factory, fracción)`` para herbívoros.
                              ``genome_factory`` es un callable sin argumentos que devuelve
                              la lista de genes del subtipo.
            predator_specs  : Lista de tuplas ``(genome_factory, fracción)`` para depredadores.
                              Si es ``None``, se usa un único tipo de depredador con
                              ``RandomPredatorGene`` (100 % de la población).
        """
        self._name = name
        self._description = description
        self._config = config
        self._herbivore_specs = list(herbivore_specs)
        if predator_specs is not None:
            self._predator_specs = list(predator_specs)
        else:
            self._predator_specs = [(lambda: [RandomPredatorGene()], 1.0)]

    @property
    def name(self) -> str:
        return self._name

    @property
    def description(self) -> str:
        return self._description

    @property
    def config(self) -> SimulationConfig:
        return self._config

    @property
    def herbivore_specs(self) -> List[Tuple[Callable[[], list], float]]:
        return self._herbivore_specs

    @property
    def predator_specs(self) -> List[Tuple[Callable[[], list], float]]:
        return self._predator_specs


def run_multiple(
    experiment: Experiment,
    config: SimulationConfig,
    n_runs: int,
    base_seed: int = 0,
) -> List[list]:
    """Ejecuta el experimento ``n_runs`` veces con semillas distintas y consecutivas.

    Args:
        experiment : Objeto ``Experiment`` a ejecutar.
        config     : Configuración base; el campo ``seed`` se sustituye por
                     ``base_seed + i`` en la corrida ``i`` (0-indexed).
        n_runs     : Número de corridas independientes.
        base_seed  : Semilla de la primera corrida.  Las siguientes usan
                     ``base_seed + 1``, ``base_seed + 2``, etc.

    Returns:
        Lista de ``n_runs`` listas de ``DayReport``, una por corrida.
    """
    all_reports = []
    for run_idx in range(n_runs):
        run_cfg = dc_replace(config, seed=base_seed + run_idx)
        sim = Simulator(experiment, config_override=run_cfg)
        all_reports.append(sim.run())
    return all_reports
