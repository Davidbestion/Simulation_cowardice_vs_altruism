import random
import uuid
from typing import Any, Dict, List, Tuple


class Creature:
    """Clase base para todas las criaturas de la simulación.

    Una criatura es un agente definido por su genoma: una lista de genes
    que determinan tanto sus características físicas (rasgos observables)
    como su comportamiento en distintas situaciones (elección de árbol,
    respuesta ante depredadores, estrategia de caza, etc.).

    No hay mutación ni cruce genético: los descendientes heredan exactamente
    el mismo genoma que su progenitor.
    """

    creature_type: str = "creature"

    def __init__(self, genome: List[Any], min_offspring: int = 1, max_offspring: int = 2) -> None:
        """
        Args:
            genome        : Lista de objetos ``Gene`` que definen a la criatura.
                            El orden no importa; lo que importa es la presencia
                            y la prioridad (``PRIORITY``) de cada gen.
            min_offspring : Mínimo de descendientes que produce esta criatura
                            al reproducirse al final del día.
            max_offspring : Máximo de descendientes.  El número real se sortea
                            uniformemente en ``[min_offspring, max_offspring]``.
        """
        self.genome: List[Any] = list(genome)
        self.physical_traits: Dict[str, Any] = self._compute_physical_traits()
        self.creature_id: str = uuid.uuid4().hex[:6]
        self.min_offspring: int = min_offspring
        self.max_offspring: int = max_offspring

    # ------------------------------------------------------------------ traits

    def _compute_physical_traits(self) -> Dict[str, Any]:
        """Acumula los rasgos físicos aportados por todos los genes del genoma.

        Itera sobre cada gen y llama a ``apply_physical_traits``; los resultados
        se fusionan en un único diccionario.  Si dos genes devuelven la misma
        clave, el gen que aparece más tarde en la lista sobreescribe al anterior.

        Returns:
            Diccionario ``{nombre_del_rasgo: valor}`` con todos los rasgos físicos
            de la criatura (p. ej. ``{"green_beard": True, "hunt_evasion": 0.4}``).
        """
        traits: dict = {}
        for gene in self.genome:
            traits.update(gene.apply_physical_traits(self))
        return traits

    def has_trait(self, trait: str) -> bool:
        """Indica si la criatura posee un rasgo físico con valor verdadero.

        Args:
            trait : Nombre del rasgo a consultar (p. ej. ``"green_beard"``).

        Returns:
            ``True`` si el rasgo existe en el diccionario de rasgos físicos
            y su valor es truthy; ``False`` en caso contrario.
        """
        return bool(self.physical_traits.get(trait, False))

    def has_gene(self, gene_type: type) -> bool:
        """Indica si el genoma contiene al menos una instancia de un tipo de gen.

        Útil para comprobar desde fuera si una criatura "tiene" un comportamiento
        específico sin acceder directamente a su lista de genes.

        Args:
            gene_type : Clase del gen a buscar (p. ej. ``CowardGene``).

        Returns:
            ``True`` si al menos uno de los genes del genoma es una instancia
            de ``gene_type``.
        """
        return any(isinstance(g, gene_type) for g in self.genome)

    def get_trait_value(self, trait: str, default: float = 0.0) -> float:
        """Devuelve el valor numérico de un rasgo físico.

        A diferencia de ``has_trait`` (que sólo dice si existe), este método
        es útil cuando el rasgo almacena una probabilidad o un factor numérico
        (p. ej. ``hunt_evasion``, ``camouflage_factor``).

        Args:
            trait   : Nombre del rasgo a consultar.
            default : Valor a devolver si el rasgo no existe en el diccionario.

        Returns:
            El valor del rasgo convertido a ``float``, o ``default`` si el
            rasgo no está presente.
        """
        return float(self.physical_traits.get(trait, default))

    # ---------------------------------------------------------------- lifecycle

    def reproduce(self, rng: random.Random) -> List["Creature"]:
        """Produce los descendientes de esta criatura al final del día.

        El progenitor muere (no se incluye a sí mismo en la lista devuelta).
        Cada descendiente recibe una copia idéntica del genoma: no hay mutación
        ni recombinación genética.

        El número de descendientes se sortea uniformemente en
        ``[min_offspring, max_offspring]`` usando el generador ``rng``.

        Args:
            rng : Generador de números aleatorios del simulador.  Se pasa
                  explícitamente para que toda la aleatoriedad de la simulación
                  quede controlada por la semilla global.

        Returns:
            Lista de nuevas criaturas del mismo tipo (``Herbivore`` o ``Predator``)
            con el mismo genoma y los mismos parámetros de reproducción.
        """
        num = rng.randint(self.min_offspring, self.max_offspring)
        return [
            self.__class__(list(self.genome), self.min_offspring, self.max_offspring)
            for _ in range(num)
        ]

    def __repr__(self) -> str:
        gene_names = [getattr(g, "name", type(g).__name__) for g in self.genome]
        return f"{self.__class__.__name__}({self.creature_id}, genes={gene_names})"


# ---------------------------------------------------------------------------


class Herbivore(Creature):
    """Una presa que cada día elige un árbol donde alimentarse y reacciona ante depredadores.

    El comportamiento concreto (qué árbol elegir, cómo responder al detectar
    un depredador) lo determinan los genes presentes en su genoma.
    """

    creature_type = "herbivore"

    def choose_tree(
        self,
        available_trees: list,
        all_assignments: Dict[int, list],
        cfg: Any,
        rng: random.Random,
    ) -> int:
        """Decide a qué árbol irá el herbívoro hoy.

        Se consultan todos los genes del genoma que implementen ``choose_tree``
        en orden de prioridad descendente.  El primer gen que devuelva un
        ``tree_id`` válido (distinto de ``None``) gana.  Si ningún gen define
        preferencia, se elige un árbol al azar entre los disponibles.

        Args:
            available_trees  : Lista de objetos ``Tree`` que aún tienen capacidad
                               libre en este momento (el herbívoro sólo puede ir
                               a uno de estos).
            all_assignments  : Diccionario ``{tree_id: [herbívoros asignados]}``,
                               que refleja el estado *actual* de todos los árboles
                               (incluyendo los ya llenos).  Permite a los genes
                               sociales/solitarios comparar cuántos herbívoros hay
                               en cada árbol, incluso si ya no tienen espacio libre.
            cfg              : Objeto ``SimulationConfig`` con los parámetros de la
                               simulación (por si un gen necesita umbrales).
            rng              : Generador de números aleatorios del simulador.

        Returns:
            El ``tree_id`` (entero) del árbol elegido.
        """
        # Ordenar por prioridad descendente; el primero que devuelva no-None gana
        behavior_genes = sorted(
            [g for g in self.genome if hasattr(g, "choose_tree")],
            key=lambda g: getattr(g, "PRIORITY", 0),
            reverse=True,
        )
        for g in behavior_genes:
            result = g.choose_tree(self, available_trees, all_assignments, cfg, rng)
            if result is not None:
                return result
        # Default: random available tree
        return rng.choice(available_trees).tree_id

    def handle_predator(
        self,
        assigned: List["Herbivore"],
        cfg: Any,
        rng: random.Random,
    ) -> Tuple[List["Herbivore"], List["Herbivore"]]:
        """Ejecuta la reacción de este herbívoro al detectar un depredador en su árbol.

        Este método es invocado por el simulador cuando el herbívoro resulta ser
        el "detector" del día (el primero en superar el umbral de detección).
        La respuesta concreta la define el gen de comportamiento de mayor prioridad
        presente en el genoma (cobarde, altruista, altruista selectivo, etc.).

        Si ningún gen define una respuesta, el comportamiento por defecto es no
        hacer nada: nadie huye y nadie muere directamente (todos los presentes
        quedan expuestos a la fase de caza del depredador).

        Args:
            assigned : Lista completa de herbívoros en el árbol en este momento,
                       incluyendo al propio detector.  El comportamiento del gen
                       puede afectar a cualquiera de ellos.
            cfg      : Objeto ``SimulationConfig`` con parámetros como
                       ``altruist_escape_prob``.
            rng      : Generador de números aleatorios del simulador.

        Returns:
            Una tupla ``(fled, directly_eaten)``:

            - ``fled``           – Herbívoros que logran escapar *antes* de que el
              depredador pueda atacar (salen de la fase de caza completamente a salvo).
            - ``directly_eaten`` – Herbívoros que son devorados como consecuencia
              directa de este comportamiento (p. ej. el altruista que se sacrifica
              para dar tiempo al grupo).

            Los herbívoros que no aparezcan en ninguna de las dos listas permanecen
            en el árbol y serán el objetivo de la fase de caza normal del depredador.
        """
        # Asegurarse de que el detector está incluido en la lista
        if self not in assigned:
            assigned = [self] + list(assigned)

        behavior_genes = sorted(
            [g for g in self.genome if hasattr(g, "predator_behavior")],
            key=lambda g: getattr(g, "PRIORITY", 0),
            reverse=True,
        )
        for g in behavior_genes:
            result = g.predator_behavior(self, assigned, cfg, rng)
            if result is not None:
                return result

        # Default: no special behaviour – nobody flees, nobody directly eaten.
        return [], []


# ---------------------------------------------------------------------------


class Predator(Creature):
    """Un depredador que cada día elige un árbol y caza herbívoros en él.

    El comportamiento concreto (qué árbol atacar, cuántas presas captura)
    lo determinan los genes presentes en su genoma.
    """

    creature_type = "predator"

    def choose_tree(
        self,
        trees: list,
        visible_herbivores: Dict[int, list],
        cfg: Any,
        rng: random.Random,
    ) -> int:
        """Decide qué árbol visitará el depredador hoy.

        El depredador toma su decisión basándose únicamente en los herbívoros
        *visibles*: aquellos sin el rasgo ``hidden_from_predator``.  Los
        herbívoros ocultos no figuran en ``visible_herbivores`` y, por tanto,
        no influyen en la elección del árbol.

        Se consultan los genes en orden de prioridad; el primero que devuelva
        un ``tree_id`` válido gana.  Si ningún gen define preferencia, el
        depredador va al árbol con más presas visibles (comportamiento por defecto).

        Args:
            trees              : Lista de todos los objetos ``Tree`` del mundo.
            visible_herbivores : Diccionario ``{tree_id: [herbívoros visibles]}``.  
                                 Construido por el simulador *antes* de llamar a
                                 este método: excluye a los herbívoros con el rasgo
                                 ``hidden_from_predator``.
            cfg                : Objeto ``SimulationConfig``.
            rng                : Generador de números aleatorios del simulador.

        Returns:
            El ``tree_id`` del árbol elegido.
        """
        # Ordenar por prioridad descendente; el primero que devuelva no-None gana
        behavior_genes = sorted(
            [g for g in self.genome if hasattr(g, "predator_choose_tree")],
            key=lambda g: getattr(g, "PRIORITY", 0),
            reverse=True,
        )
        for g in behavior_genes:
            result = g.predator_choose_tree(self, trees, visible_herbivores, cfg, rng)
            if result is not None:
                return result

        # Default: go to the tree with the most visible herbivores.
        non_empty = [t for t in trees if visible_herbivores.get(t.tree_id)]
        if not non_empty:
            return rng.choice(trees).tree_id
        max_count = max(len(visible_herbivores[t.tree_id]) for t in non_empty)
        candidates = [t for t in non_empty if len(visible_herbivores[t.tree_id]) == max_count]
        return rng.choice(candidates).tree_id

    def hunt(
        self,
        available_prey: List[Herbivore],
        cfg: Any,
        rng: random.Random,
    ) -> Tuple[List[Herbivore], List[Herbivore]]:
        """Realiza la caza sobre los herbívoros que quedaron en el árbol.

        Se llama una vez por depredador presente en el árbol, y sólo sobre
        los herbívoros que *no* huyeron durante la fase de alarma.  La presa
        capturada se retira del pool para que el siguiente depredador en el
        mismo árbol no pueda volver a atacarla.

        El número máximo de presas que este depredador puede capturar en una
        visita viene dado por ``cfg.predator_hunt_capacity``, y puede ser
        aumentado por genes como ``GreedyHunterGene``.  Adicionalmente, cada
        presa individual puede escapar si posee el rasgo ``hunt_evasion``.

        Args:
            available_prey : Lista de herbívoros expuestos a la caza (los que
                             no escaparon en la fase de alarma y aún no fueron
                             capturados por otro depredador en esta misma ronda).
            cfg            : Objeto ``SimulationConfig``; se usa para leer
                             ``predator_hunt_capacity``.
            rng            : Generador de números aleatorios del simulador.

        Returns:
            Una tupla ``(caught, escaped)``:

            - ``caught``  – Herbívoros capturados y devorados por este depredador.
            - ``escaped`` – Herbívoros que sobrevivieron a esta caza concreta
              (porque se superó la capacidad de caza o porque activaron su
              probabilidad de evasión individual ``hunt_evasion``).
        """
        # Los herbívoros que escapan aquí vuelven al pool disponible del árbol
        if not available_prey:
            return [], []

        hunt_capacity: int = getattr(cfg, "predator_hunt_capacity", 1)
        for g in self.genome:
            if hasattr(g, "modify_hunt_capacity"):
                hunt_capacity = g.modify_hunt_capacity(self, hunt_capacity, cfg)
        hunt_capacity = max(0, int(hunt_capacity))

        pool = list(available_prey)
        rng.shuffle(pool)
        caught: List[Herbivore] = []
        escaped: List[Herbivore] = []

        for prey in pool:
            if len(caught) >= hunt_capacity:
                escaped.append(prey)
                continue
            evasion: float = prey.get_trait_value("hunt_evasion", 0.0)
            if evasion > 0 and rng.random() < evasion:
                escaped.append(prey)
            else:
                caught.append(prey)

        return caught, escaped
