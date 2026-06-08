"""Main simulation engine.

Each day is resolved in five sequential phases:

1. **Herbivore assignment** – each herbivore picks a tree based on its genes;
   capacity is respected (overflow → starvation).
2. **Predator tree selection** – each predator sees only the *visible* herbivores
   (hidden herbivores are excluded) and picks a tree.
3. **Interaction phase** – per tree that has both herbivores and predators:
   a. Detection roll (herbivore camouflage & predator camouflage applied).
   b. Alarm behaviour (coward / altruist / selective-altruist / default).
   c. Hunt phase – each predator hunts from the remaining non-fled herbivores.
4. **Reproduction** – all surviving herbivores and predators produce offspring
   (parents die; see notes on ``offspring_min``/``max``).
5. **Stats collection** – a ``DayReport`` is created and appended.
"""

from collections import Counter
from typing import Dict, List, Tuple
import random

from .simulation import DayReport, Experiment, SimulationConfig, TreeInteractionLog
from .world import World
from .creature import Herbivore, Predator


class Simulator:
    """Motor principal que ejecuta un ``Experiment`` día a día.

    Instanciar el simulador con un experimento y (opcionalmente) una
    configuración alternativa, luego llamar a ``run()`` para obtener la
    lista de ``DayReport`` con los resultados de cada día.
    """

    def __init__(
        self,
        experiment: Experiment,
        config_override: SimulationConfig | None = None,
    ) -> None:
        """
        Args:
            experiment      : Objeto ``Experiment`` que define las poblaciones
                              iniciales y los parámetros de la simulación.
            config_override : Si se proporciona, reemplaza la configuración
                              interna del experimento.  Útil para ejecutar el
                              mismo experimento con distintos parámetros (p. ej.
                              al repetir la simulación con distintas semillas).
        """
        self.experiment = experiment
        self.config: SimulationConfig = (
            config_override if config_override is not None else experiment.config
        )

    # ---------------------------------------------------------------- setup

    def _build_population(
        self,
        specs: List,
        total: int,
        creature_cls,
        offspring_min: int,
        offspring_max: int,
        rng: random.Random,
    ) -> list:
        """Construye la población inicial a partir de una lista de especificaciones.

        Cada especificación define un subtipo de criatura mediante una función
        que genera genomas y una fracción del total de la población.  Las
        fracciones se convierten a números enteros; el último subtipo absorbe
        cualquier diferencia de redondeo para garantizar que la suma sea exactamente
        ``total``.

        Args:
            specs         : Lista de tuplas ``(genome_factory, fraction)`` donde
                            ``genome_factory`` es un callable sin argumentos que
                            devuelve una lista de genes, y ``fraction`` es la
                            proporción del total que tendrá este subtipo (0–1).
            total         : Número total de criaturas a crear.
            creature_cls  : Clase a instanciar (``Herbivore`` o ``Predator``).
            offspring_min : Mínimo de descendientes que producirá cada criatura.
            offspring_max : Máximo de descendientes.
            rng           : Generador de números aleatorios (no se usa aquí
                            actualmente, pero se pasa por consistencia).

        Returns:
            Lista de criaturas del tipo ``creature_cls`` listas para la simulación.
        """
        if not specs or total == 0:
            return []

        counts: List[int] = []
        remaining = total
        for i, (_fn, frac) in enumerate(specs):
            if i == len(specs) - 1:
                count = remaining
            else:
                count = int(round(frac * total))
                remaining -= count
            counts.append(count)

        # Correct any rounding drift
        diff = total - sum(counts)
        if diff:
            counts[0] += diff

        population = []
        for (fn, _), count in zip(specs, counts):
            for _ in range(count):
                genome = fn()
                population.append(
                    creature_cls(
                        genome=genome,
                        min_offspring=offspring_min,
                        max_offspring=offspring_max,
                    )
                )
        return population

    # ---------------------------------------------------------------- phases

    def _assign_herbivores(
        self,
        herbivores: List[Herbivore],
        world: World,
        cfg: SimulationConfig,
        rng: random.Random,
    ) -> Tuple[Dict[int, List[Herbivore]], List[Herbivore]]:
        """Fase 1: cada herbívoro elige y ocupa un árbol.

        Los herbívoros se procesan en orden aleatorio para evitar que el orden
        de la lista favorezca sistemáticamente a ciertos individuos.  Cada uno
        consulta su gen de elección y se asigna al árbol indicado, siempre que
        quede capacidad libre.  Si todos los árboles están llenos antes de que
        un herbívoro pueda asignarse, ese individuo muere de hambre (se añade a
        la lista ``starved``).

        Args:
            herbivores : Población completa de herbívoros al inicio del día.
            world      : El mundo con todos los árboles y sus capacidades.
            cfg        : Parámetros de la simulación.
            rng        : Generador de números aleatorios.

        Returns:
            Una tupla ``(assignments, starved)``:

            - ``assignments`` – Diccionario ``{tree_id: [herbívoros asignados]}``
              con los herbívoros que encontraron sitio en algún árbol.
            - ``starved``     – Lista de herbívoros que no encontraron sitio
              y mueren de hambre ese día (no participan en ninguna fase posterior).
        """
        assignments: Dict[int, List[Herbivore]] = {t.tree_id: [] for t in world.trees}
        # Track remaining capacity per tree
        remaining_cap: Dict[int, int] = {t.tree_id: t.capacity for t in world.trees}
        starved: List[Herbivore] = []

        shuffled = list(herbivores)
        rng.shuffle(shuffled)

        for herb in shuffled:
            # Only offer trees that still have free slots
            available = [t for t in world.trees if remaining_cap[t.tree_id] > 0]
            if not available:
                starved.append(herb)
                continue

            tree_id = herb.choose_tree(available, assignments, cfg, rng)

            # Safety: if the gene returned a full-tree id, fall back to random
            if remaining_cap.get(tree_id, 0) <= 0:
                tree_id = rng.choice(available).tree_id

            assignments[tree_id].append(herb)
            remaining_cap[tree_id] -= 1

        return assignments, starved

    def _assign_predators(
        self,
        predators: List[Predator],
        world: World,
        herb_assignments: Dict[int, List[Herbivore]],
        cfg: SimulationConfig,
        rng: random.Random,
    ) -> Dict[int, List[Predator]]:
        """Fase 2: cada depredador elige a qué árbol ir.

        A diferencia de los herbívoros, los depredadores no tienen límite de
        capacidad: varios depredadores pueden visitar el mismo árbol.  Cada
        depredador construye su propio mapa de presas *visibles* (filtrando los
        herbívoros con ``hidden_from_predator``) y llama a ``choose_tree`` con
        esa información.  Los herbívoros ocultos no cuentan para atraer
        depredadores.

        Args:
            predators        : Población completa de depredadores.
            world            : El mundo con todos los árboles.
            herb_assignments : Resultado de la fase 1: qué herbívoros hay en cada
                               árbol (incluyendo los que tienen
                               ``hidden_from_predator``).
            cfg              : Parámetros de la simulación.
            rng              : Generador de números aleatorios.

        Returns:
            Diccionario ``{tree_id: [depredadores asignados]}`` con los depredadores
            que visitarán cada árbol ese día.
        """
        pred_assignments: Dict[int, List[Predator]] = {t.tree_id: [] for t in world.trees}

        for pred in predators:
            # Build the visible-herbivore map for this specific predator
            visible: Dict[int, List[Herbivore]] = {
                t.tree_id: [
                    h for h in herb_assignments[t.tree_id]
                    if not h.has_trait("hidden_from_predator")
                ]
                for t in world.trees
            }
            tree_id = pred.choose_tree(world.trees, visible, cfg, rng)
            pred_assignments[tree_id].append(pred)

        return pred_assignments

    def _resolve_tree(
        self,
        tree_id: int,
        herbivores: List[Herbivore],
        predators: List[Predator],
        cfg: SimulationConfig,
        rng: random.Random,
    ) -> Tuple[List[Herbivore], int, List[Predator], TreeInteractionLog]:
        """Fase 3: resuelve todas las interacciones en un árbol durante un día.

        Sub-fases internas:

        a) **Detección**: cada herbívoro tira un dado contra ``p_deteccion``
           (reducida por el camuflaje del depredador más sigiloso).  El primer
           herbívoro en superar el umbral es el "detector" y activa su
           comportamiento de alarma.  Si nadie detecta al depredador, se pasa
           directamente a la caza.

        b) **Alarma**: el detector ejecuta ``handle_predator()``, que determina
           quiénes huyen (``fled``) y quiénes son devorados directamente
           (``directly_eaten``) según el gen de comportamiento del detector.

        c) **Caza**: los depredadores atacan en orden aleatorio sobre los
           herbívoros restantes (los que no huyeron ni fueron devorados
           directamente).  Las presas capturadas se retiran del pool antes
           de que el siguiente depredador ataque.

        Args:
            tree_id     : Identificador del árbol que se está resolviendo.
            herbivores  : Herbívoros asignados a este árbol en la fase 1.
            predators   : Depredadores que eligieron este árbol en la fase 2.
            cfg         : Parámetros de la simulación.
            rng         : Generador de números aleatorios.

        Returns:
            Una tupla ``(survivors, total_eaten, log)``:

            - ``survivors``   – Herbívoros que sobrevivieron el día en este árbol
              (los que huyeron + los que resistieron la caza).
            - ``total_eaten`` – Número total de herbívoros devorados en este árbol
              (directamente en la alarma + capturados en la caza).
            - ``log``         – Objeto ``TreeInteractionLog`` con estadísticas
              detalladas de lo ocurrido en este árbol para el informe del día.
        """
        if not predators:
            log = TreeInteractionLog(
                tree_id=tree_id,
                herbivores_present=len(herbivores),
                predators_present=0,
                predator_detected=False,
                detector_gene="none",
                fled=0,
                directly_eaten=0,
                hunted=0,
                survived=len(herbivores),
            )
            return list(herbivores), 0, [], log

        # Detection probability: use the camouflage of the most-camouflaged predator
        # (best-camo predator is hardest to spot; one stealthy predator still provides
        # some cover even if others are visible — simplified model).
        max_camouflage = max(
            (p.get_trait_value("camouflage_factor", 0.0) for p in predators),
            default=0.0,
        )
        det_prob = cfg.base_detection_prob * (1.0 - max_camouflage)

        # Each herbivore independently tries to detect a predator
        herb_pool = list(herbivores)
        rng.shuffle(herb_pool)

        detector = None
        for h in herb_pool:
            if rng.random() < det_prob:
                detector = h
                break

        fled: List[Herbivore] = []
        directly_eaten: List[Herbivore] = []
        detector_gene_name = "none"

        if detector is not None:
            # Identify the gene that drives the response (for logging)
            detector_gene_name = next(
                (
                    getattr(g, "name", type(g).__name__)
                    for g in detector.genome
                    if hasattr(g, "predator_behavior")
                ),
                "default",
            )
            fled, directly_eaten = detector.handle_predator(herb_pool, cfg, rng)

        # Remaining herbivores face the hunt
        escaped_ids = {id(h) for h in fled}
        eaten_ids = {id(h) for h in directly_eaten}
        remaining = [
            h for h in herb_pool
            if id(h) not in escaped_ids and id(h) not in eaten_ids
        ]

        # Each predator hunts in random order; the prey pool shrinks after each kill.
        # Only predators that catch ≥1 prey are "fed" and will survive to reproduce.
        fed_predators: List[Predator] = []
        total_hunted: List[Herbivore] = []
        rng.shuffle(predators)
        for pred in predators:
            if not remaining:
                break  # prey exhausted; remaining predators starve
            caught, remaining = pred.hunt(remaining, cfg, rng)
            total_hunted.extend(caught)
            if caught:
                fed_predators.append(pred)

        survivors = fled + remaining  # fled are safe; remaining survived the hunt
        total_eaten_count = len(directly_eaten) + len(total_hunted)

        log = TreeInteractionLog(
            tree_id=tree_id,
            herbivores_present=len(herbivores),
            predators_present=len(predators),
            predator_detected=detector is not None,
            detector_gene=detector_gene_name,
            fled=len(fled),
            directly_eaten=len(directly_eaten),
            hunted=len(total_hunted),
            survived=len(survivors),
        )
        return survivors, total_eaten_count, fed_predators, log

    # ---------------------------------------------------------------- main loop

    def run(self) -> List[DayReport]:
        """Ejecuta la simulación completa y devuelve los informes de cada día.

        El flujo general es:

        1. Crear el mundo una sola vez con capacidades aleatorias de árboles.
        2. Construir las poblaciones iniciales de herbívoros y depredadores.
        3. Para cada día (hasta ``cfg.num_generations`` o hasta que los
           herbívoros se extingan):

           a. Asignar herbívoros a árboles (``_assign_herbivores``).
           b. Asignar depredadores a árboles (``_assign_predators``).
           c. Resolver cada árbol (``_resolve_tree``).
           d. Reproducir todos los supervivientes (herbívoros y depredadores);
              los progenitores mueren.
           e. Crear el ``DayReport`` con todas las estadísticas del día.

        Returns:
            Lista de ``DayReport``, uno por día simulado.  Si la población de
            herbívoros llega a cero, la lista puede ser más corta que
            ``cfg.num_generations``.
        """
        cfg = self.config
        rng = random.Random(cfg.seed)

        # --- Build world (fixed for entire simulation) ---
        world = World.create(
            num_trees=cfg.num_trees,
            capacity_min=cfg.tree_capacity_min,
            capacity_max=cfg.tree_capacity_max,
            rng=rng,
        )

        # --- Initialise populations ---
        herbivores: List[Herbivore] = self._build_population(
            specs=self.experiment.herbivore_specs,
            total=cfg.initial_herbivores,
            creature_cls=Herbivore,
            offspring_min=cfg.herbivore_offspring_min,
            offspring_max=cfg.herbivore_offspring_max,
            rng=rng,
        )
        predators: List[Predator] = self._build_population(
            specs=self.experiment.predator_specs,
            total=cfg.initial_predators,
            creature_cls=Predator,
            offspring_min=cfg.predator_offspring_min,
            offspring_max=cfg.predator_offspring_max,
            rng=rng,
        )

        reports: List[DayReport] = []

        for day in range(1, cfg.num_generations + 1):
            herb_count_start = len(herbivores)
            pred_count_start = len(predators)

            # Phase 1 – herbivore tree assignment
            herb_assignments, starved = self._assign_herbivores(herbivores, world, cfg, rng)

            # Phase 2 – predator tree selection (only if predators exist)
            if predators:
                pred_assignments = self._assign_predators(predators, world, herb_assignments, cfg, rng)
            else:
                pred_assignments = {t.tree_id: [] for t in world.trees}

            # Phase 3 – per-tree interactions
            herb_survivors: List[Herbivore] = []
            pred_survivors: List[Predator] = []   # predators that caught ≥1 prey
            total_eaten = 0
            tree_logs: List[TreeInteractionLog] = []

            for tree in world.trees:
                tree_herbs = herb_assignments[tree.tree_id]
                tree_preds = pred_assignments[tree.tree_id]
                if not tree_herbs:
                    continue  # predators at empty trees catch nothing and starve
                survivors, eaten, fed_preds, log = self._resolve_tree(
                    tree.tree_id, tree_herbs, tree_preds, cfg, rng
                )
                herb_survivors.extend(survivors)
                pred_survivors.extend(fed_preds)
                total_eaten += eaten
                tree_logs.append(log)

            # Phase 4 – reproduction (parents die; offspring carry the same genome)
            new_herbivores: List[Herbivore] = []
            for h in herb_survivors:
                new_herbivores.extend(h.reproduce(rng))

            new_predators: List[Predator] = []
            for p in pred_survivors:   # only predators that caught prey reproduce
                new_predators.extend(p.reproduce(rng))

            herbivores = new_herbivores
            predators = new_predators

            # Phase 5 – stats
            herb_counter: Counter = Counter()
            for h in herbivores:
                if h.genome:
                    for g in h.genome:
                        herb_counter[getattr(g, "name", type(g).__name__)] += 1
                else:
                    herb_counter["none"] += 1
            herb_total = sum(herb_counter.values()) or 1
            herb_freqs = {k: v / herb_total for k, v in herb_counter.items()}

            pred_counter: Counter = Counter()
            for p in predators:
                if p.genome:
                    for g in p.genome:
                        pred_counter[getattr(g, "name", type(g).__name__)] += 1
                else:
                    pred_counter["none"] += 1
            pred_total = sum(pred_counter.values()) or 1
            pred_freqs = {k: v / pred_total for k, v in pred_counter.items()}

            report = DayReport(
                generation=day,
                population_start=herb_count_start,
                starved=len(starved),
                eaten=total_eaten,
                survived=len(herb_survivors),
                population_end=len(herbivores),
                gene_frequencies=herb_freqs,
                predator_count_start=pred_count_start,
                predator_count_end=len(predators),
                predator_gene_frequencies=pred_freqs,
                tree_interactions=tree_logs,
            )
            reports.append(report)

            if len(herbivores) == 0:
                break

        return reports
