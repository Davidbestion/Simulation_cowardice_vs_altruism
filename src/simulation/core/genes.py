"""Gene definitions.

Every gene derives from ``Gene`` and may override any combination of:

  * ``apply_physical_traits`` – contribute entries to a creature's physical-trait dict.
  * ``choose_tree``            – herbivore tree-selection behaviour.
  * ``predator_behavior``      – herbivore response when a predator is detected.
  * ``predator_choose_tree``   – predator tree-selection behaviour.
  * ``modify_hunt_capacity``   – adjust how many prey a predator can catch per visit.

Return ``None`` (or leave the default) to defer to the next-highest-priority gene.
"""

from abc import ABC
from typing import Any, Dict, List, Optional, Tuple
import random

from .creature import Creature, Herbivore, Predator


class Gene(ABC):
    """Clase base abstracta para todos los genes.

    Un gen es la unidad de comportamiento y fenotipo de una criatura.  Cada
    instancia de ``Gene`` puede contribuir en una o más de las siguientes
    dimensiones:

    - **Rasgos físicos** (``apply_physical_traits``): valores observables de la
      criatura (p. ej. camuflaje, barba verde, capacidad de evasión).
    - **Elección de árbol para herbívoros** (``choose_tree``): preferencia de
      arbolado social, solitario, etc.
    - **Comportamiento ante depredador** (``predator_behavior``): cobardía,
      altruismo, altruismo selectivo, etc.
    - **Elección de árbol para depredadores** (``predator_choose_tree``): emboscada,
      caza cautelosa, etc.
    - **Capacidad de caza** (``modify_hunt_capacity``): cuantas presas puede
      atrapar el depredador por visita.

    Cada gen tiene un campo ``PRIORITY`` (entero).  Cuando una criatura tiene
    varios genes del mismo tipo, el de mayor prioridad se evalúa primero; el
    primer resultado no-``None`` es el que se aplica.
    """

    name: str = "gene"
    # Higher-priority genes are evaluated first; the first non-None result wins.
    PRIORITY: int = 0

    def apply_physical_traits(self, creature: Creature) -> Dict[str, Any]:
        """Devuelve los rasgos físicos que este gen aporta a la criatura.

        Los rasgos son pares ``{nombre: valor}`` que se acumulan en el
        diccionario ``physical_traits`` de la criatura al momento de su
        creación.  Valores booleanos representan la presencia/ausencia de un
        rasgo; valores flotantes representan probabilidades o factores.

        Args:
            creature : La criatura a la que se le aplica este gen.  Se pasa
                       por si el gen necesita consultar otros rasgos ya
                       presentes (aunque en general no se usa).

        Returns:
            Diccionario ``{nombre_del_rasgo: valor}``.  Devolver un
            diccionario vacío equivale a no tener efecto físico.
        """
        return {}

    # ---------------------------------------------------------------- herbivore

    def choose_tree(
        self,
        creature: Herbivore,
        available_trees: list,
        all_assignments: Dict[int, list],
        cfg: Any,
        rng: random.Random,
    ) -> Optional[int]:
        """Define la preferencia de árbol del herbívoro portador de este gen.

        El simulador llama a este método (en orden de prioridad descendente)
        hasta obtener una respuesta no-``None``.

        Args:
            creature         : El herbívoro que está tomando la decisión.
            available_trees  : Árboles con capacidad libre en este momento.
            all_assignments  : Mapa completo de ocupantes actuales por árbol
                               (incluyendo árboles llenos), útil para comparar
                               densidades de población.
            cfg              : Parámetros de la simulación.
            rng              : Generador de números aleatorios.

        Returns:
            El ``tree_id`` preferido, o ``None`` para pasar al siguiente gen.
        """
        return None

    def predator_behavior(
        self,
        notifier: Herbivore,
        assigned: List[Herbivore],
        cfg: Any,
        rng: random.Random,
    ) -> Optional[Tuple[List[Herbivore], List[Herbivore]]]:
        """Define la respuesta del herbívoro ``notifier`` al detectar un depredador.

        El simulador llama a este método sobre el gen de mayor prioridad del
        detector.  El primer gen que devuelva algo distinto de ``None`` determina
        el desenlace completo para todos los herbívoros del árbol.

        Args:
            notifier : El herbívoro que detectó al depredador.  Puede decidir
                       alertar al grupo, huir solo, sacrificarse, etc.
            assigned : Lista de *todos* los herbívoros presentes en el árbol,
                       incluyendo al propio ``notifier``.  El gen puede afectar
                       a cualquiera de ellos.
            cfg      : Parámetros de la simulación; el más relevante suele ser
                       ``altruist_escape_prob`` (probabilidad de que un altruista
                       sobreviva al sacrificarse).
            rng      : Generador de números aleatorios.

        Returns:
            Una tupla ``(fled, directly_eaten)`` o ``None`` para pasar al
            siguiente gen:

            - ``fled``           – Herbívoros que escapan antes de la fase de caza.
            - ``directly_eaten`` – Herbívoros devorados directamente por esta acción.

            Los herbívoros en ``assigned`` que no figuren en ninguna lista
            se quedan en el árbol y enfrentan la caza normal del depredador.
        """
        return None

    # ---------------------------------------------------------------- predator

    def predator_choose_tree(
        self,
        predator: Predator,
        trees: list,
        visible_herbivores: Dict[int, list],
        cfg: Any,
        rng: random.Random,
    ) -> Optional[int]:
        """Define la preferencia de árbol del depredador portador de este gen.

        Sólo se reciben los herbívoros *visibles* (los ocultos ya fueron
        filtrados por el simulador antes de llamar a este método).

        Args:
            predator           : El depredador que está tomando la decisión.
            trees              : Lista de todos los árboles del mundo.
            visible_herbivores : Diccionario ``{tree_id: [herbívoros visibles]}``.  
                                 Herbívoros con ``hidden_from_predator`` no
                                 figuran aquí.
            cfg                : Parámetros de la simulación.
            rng                : Generador de números aleatorios.

        Returns:
            El ``tree_id`` preferido, o ``None`` para pasar al siguiente gen.
        """
        return None

    def modify_hunt_capacity(self, predator: Predator, current_capacity: int, cfg: Any) -> int:
        """Modifica el número máximo de presas que el depredador puede capturar por visita.

        Todos los genes del genoma del depredador que implementen este método
        son llamados en cadena: el resultado de uno se pasa como
        ``current_capacity`` al siguiente.  El valor final es el límite real
        de presas por visita.

        Args:
            predator         : El depredador al que se le aplica la modificación.
            current_capacity : Capacidad de caza acumulada hasta este gen
                               (empieza en ``cfg.predator_hunt_capacity``).
            cfg              : Parámetros de la simulación.

        Returns:
            La capacidad de caza modificada (entero).
        """
        return current_capacity


# ============================================================ HERBIVORE GENES


class CowardGene(Gene):
    """Comportamiento cobarde: el detector huye solo, dejando al resto a su suerte.

    Cuando el herbívoro portador detecta un depredador, activa su instinto
    de supervivencia individual y escapa inmediatamente sin avisar al grupo.
    Los demás herbívoros del árbol no reciben aviso y quedan expuestos a la
    fase de caza del depredador.

    Es el comportamiento más egoísta: maximiza la supervivencia propia
    a expensas del grupo.
    """

    name = "coward"
    PRIORITY = 10

    def predator_behavior(
        self,
        notifier: Herbivore,
        assigned: List[Herbivore],
        cfg: Any,
        rng: random.Random,
    ) -> Tuple[List[Herbivore], List[Herbivore]]:
        # Notifier flees; no one is directly eaten by this behaviour.
        # The remaining herbivores will face the predator's hunt phase.
        return [notifier], []


class AltruistGene(Gene):
    """Comportamiento altruista: el detector alerta al grupo entero.

    Al detectar un depredador, el portador advierte a todos los herbívoros
    del árbol, permitiendo que huyan.  El propio detector, sin embargo,
    corre un riesgo: escapa con probabilidad ``altruist_escape_prob``
    (definida en ``SimulationConfig``); en caso contrario es devorado como
    consecuencia directa de haberse quedado para hacer la señal.

    Es el comportamiento más cooperativo y "group-selected": maximiza la
    supervivencia del grupo a expensas de un riesgo personal elevado.
    """

    name = "altruist"
    PRIORITY = 20

    def predator_behavior(
        self,
        notifier: Herbivore,
        assigned: List[Herbivore],
        cfg: Any,
        rng: random.Random,
    ) -> Tuple[List[Herbivore], List[Herbivore]]:
        others = [c for c in assigned if c is not notifier]
        if rng.random() < getattr(cfg, "altruist_escape_prob", 0.5):
            return [notifier] + others, []   # everyone flees
        else:
            return others, [notifier]         # notifier sacrificed, others flee


class SelectiveAltruistGene(Gene):
    """Altruismo selectivo: el detector solo alerta a herbívoros con el rasgo ``green_beard``.

    Modela la hipótesis de la "barba verde" de Richard Dawkins: un individuo
    ayuda preferentemente a otros que comparten una señal identificable
    (el rasgo ``green_beard``, aportado por ``GreenBeardGene``).  Si hay
    aliados con barba verde en el árbol, el portador los alerta y se sacrifica
    con la misma probabilidad que el altruista puro.  Si *no* hay aliados con
    barba verde, el portador recurre al comportamiento cobarde (solo huye).

    Combinar este gen con ``GreenBeardGene`` hace que el individuo sea a la
    vez receptor y emisor de ayuda selectiva.
    """

    name = "selective_altruist"
    PRIORITY = 25

    def predator_behavior(
        self,
        notifier: Herbivore,
        assigned: List[Herbivore],
        cfg: Any,
        rng: random.Random,
    ) -> Tuple[List[Herbivore], List[Herbivore]]:
        green_allies = [c for c in assigned if c.has_trait("green_beard") and c is not notifier]
        if green_allies:
            if rng.random() < getattr(cfg, "altruist_escape_prob", 0.5):
                return [notifier] + green_allies, []
            else:
                return green_allies, [notifier]
        else:
            # No allies with green beard → coward behaviour
            return [notifier], []


class GreenBeardGene(Gene):
    """Confiere el rasgo físico ``green_beard`` (barba verde).

    Este gen no define ningún comportamiento por sí mismo: únicamente marca
    a la criatura como portadora de la señal ``green_beard``.  Ese rasgo es
    reconocido por ``SelectiveAltruistGene``, que usará la señal para decidir
    a quién alertar.

    Puede combinarse con cualquier gen de comportamiento para crear individuos
    que son *receptores* del altruismo selectivo (con ``GreenBeardGene`` solo)
    o que son *emisores y receptores* (con ``GreenBeardGene`` + ``SelectiveAltruistGene``).
    """

    name = "green_beard"
    PRIORITY = 5

    def apply_physical_traits(self, creature: Creature) -> Dict[str, Any]:
        return {"green_beard": True}


class SocialGene(Gene):
    """El herbívoro prefiere árboles ya concurridos (seguridad en números).

    La lógica es que un grupo grande tiene más probabilidades de detectar
    a un depredador (más "ojos" vigilando).  El portador ordena los árboles
    disponibles por ocupación descendente y elige uno de los más poblados.

    Note: la ordenación usa ``all_assignments`` (ocupación completa, incluyendo
    árboles ya llenos) para comparar densidades, pero sólo puede ir a un
    árbol de ``available_trees`` (los que aún tienen espacio libre).
    """

    name = "social"
    PRIORITY = 15

    def choose_tree(
        self,
        creature: Herbivore,
        available_trees: list,
        all_assignments: Dict[int, list],
        cfg: Any,
        rng: random.Random,
    ) -> Optional[int]:
        if not available_trees:
            return None
        available_trees = sorted(
            available_trees,
            key=lambda t: len(all_assignments.get(t.tree_id, [])),
            reverse=True,
        )
        best_count = len(all_assignments.get(available_trees[0].tree_id, []))
        top = [t for t in available_trees if len(all_assignments.get(t.tree_id, [])) == best_count]
        return rng.choice(top).tree_id


class SolitaryGene(Gene):
    """El herbívoro prefiere árboles poco concurridos (evita las muchedumbres).

    La lógica es que un árbol con pocos herbívoros es menos visible y menos
    atractivo para los depredadores que buscan concentraciones de presas.
    El portador ordena los árboles disponibles por ocupación ascendente y
    elige uno de los menos poblados.
    """

    name = "solitary"
    PRIORITY = 15

    def choose_tree(
        self,
        creature: Herbivore,
        available_trees: list,
        all_assignments: Dict[int, list],
        cfg: Any,
        rng: random.Random,
    ) -> Optional[int]:
        if not available_trees:
            return None
        available_trees = sorted(
            available_trees,
            key=lambda t: len(all_assignments.get(t.tree_id, [])),
        )
        min_count = len(all_assignments.get(available_trees[0].tree_id, []))
        bottom = [t for t in available_trees if len(all_assignments.get(t.tree_id, [])) == min_count]
        return rng.choice(bottom).tree_id


class CamouflageHerbivoreGene(Gene):
    """El herbívoro es difícil de detectar, tanto al elegir el depredador su árbol como durante la caza.

    Produce dos efectos combinados:

    1. **Invisibilidad para la elección de árbol** (``hidden_from_predator = True``):
       el simulador excluye a este herbívoro del mapa ``visible_herbivores`` que
       se entrega a los depredadores, por lo que su presencia no atrae depredadores
       al árbol.

    2. **Evasión durante la caza** (``hunt_evasion = 0.4``):
       incluso si el depredador llega al árbol (por otros herbívoros visibles),
       este herbívoro tiene un 40 % de probabilidad de escabullirse de cada
       intento de caza individual.
    """

    name = "hidden_herbivore"
    PRIORITY = 5

    def apply_physical_traits(self, creature: Creature) -> Dict[str, Any]:
        return {
            "hidden_from_predator": True,   # excluded from predator's visible count
            "hunt_evasion": 0.4,             # 40 % chance to evade the actual attack
        }


# ============================================================= PREDATOR GENES


class CamouflagePredatorGene(Gene):
    """El depredador es difícil de detectar por los herbívoros.

    Aporta el rasgo físico ``camouflage_factor`` (0–1) al depredador.  El
    simulador usa este valor para reducir la probabilidad base de detección:

        ``p_deteccion = base_detection_prob × (1 − camouflage_factor)``

    Con el valor por defecto de 0.6, la probabilidad de detección se reduce
    un 60 %.  Cuando hay varios depredadores en el mismo árbol, el simulador
    usa el factor máximo (el depredador más camuflado es el que domina).
    """

    name = "camouflage"
    PRIORITY = 10

    def apply_physical_traits(self, creature: Creature) -> Dict[str, Any]:
        return {"camouflage_factor": 0.6}   # 60 % reduction in detection probability


class AmbushGene(Gene):
    """El depredador elige el árbol con la mayor concentración de presas visibles.

    Estrategia de emboscada pura: maximiza el número de objetivos potenciales
    en cada visita.  Si todos los árboles están vacíos de presas visibles,
    elige uno al azar.
    """

    name = "ambush"
    PRIORITY = 10

    def predator_choose_tree(
        self,
        predator: Predator,
        trees: list,
        visible_herbivores: Dict[int, List[Herbivore]],
        cfg: Any,
        rng: random.Random,
    ) -> int:
        non_empty = [t for t in trees if visible_herbivores.get(t.tree_id)]
        if not non_empty:
            return rng.choice(trees).tree_id
        max_count = max(len(visible_herbivores[t.tree_id]) for t in non_empty)
        candidates = [t for t in non_empty if len(visible_herbivores[t.tree_id]) == max_count]
        return rng.choice(candidates).tree_id


class CautiousPredatorGene(Gene):
    """El depredador elige el árbol con la menor concentración de presas visibles.

    Estrategia cautelosa: grupos pequeños tienen menos probabilidad de detectar
    al depredador antes de que ataque.  Si todos los árboles están vacíos de
    presas visibles, elige uno al azar.
    """

    name = "cautious_predator"
    PRIORITY = 10

    def predator_choose_tree(
        self,
        predator: Predator,
        trees: list,
        visible_herbivores: Dict[int, List[Herbivore]],
        cfg: Any,
        rng: random.Random,
    ) -> int:
        non_empty = [t for t in trees if visible_herbivores.get(t.tree_id)]
        if not non_empty:
            return rng.choice(trees).tree_id
        min_count = min(len(visible_herbivores[t.tree_id]) for t in non_empty)
        candidates = [t for t in non_empty if len(visible_herbivores[t.tree_id]) == min_count]
        return rng.choice(candidates).tree_id


class GreedyHunterGene(Gene):
    """El depredador puede capturar más presas por visita.

    Incrementa la capacidad de caza en ``bonus`` unidades.  Combinado con
    ``AmbushGene`` crea un depredador que va al árbol más poblado *y* puede
    cazar más presas en esa visita.

    Args (constructor):
        bonus : Número de presas adicionales que puede capturar este depredador
                por encima de ``cfg.predator_hunt_capacity``.  Por defecto 1.
    """

    name = "greedy_hunter"
    PRIORITY = 5

    def __init__(self, bonus: int = 1) -> None:
        self.bonus = bonus

    def modify_hunt_capacity(self, predator: Predator, current_capacity: int, cfg: Any) -> int:
        """Suma el bonus de caza a la capacidad acumulada hasta este gen.

        Args:
            predator         : El depredador portador (no se usa en este gen).
            current_capacity : Capacidad de caza acumulada hasta este punto.
            cfg              : Parámetros de la simulación (no se usa en este gen).

        Returns:
            ``current_capacity + self.bonus``.
        """
        return current_capacity + self.bonus


class SocialGreenBeardAltruistGene(Gene):
    """Barba verde + altruismo selectivo + comportamiento de manada en un solo gen.

    Combina tres rasgos:

    1. **Señal de barba verde** (``apply_physical_traits``): la criatura es
       reconocida como aliada por otros portadores del mismo gen.
    2. **Altruismo selectivo** (``predator_behavior``): al detectar un depredador,
       avisa a todos los portadores de barba verde del árbol; el notificador
       se sacrifica con probabilidad ``1 − altruist_escape_prob``.
    3. **Comportamiento social** (``choose_tree``): el herbívoro prefiere los
       árboles con mayor ocupación actual, buscando la seguridad del grupo.
       En caso de empate elige aleatoriamente entre los más concurridos.
    """

    name = "social_green_beard_altruist"
    PRIORITY = 35

    def apply_physical_traits(self, creature: Creature) -> Dict[str, Any]:
        return {"green_beard": True}

    def choose_tree(
        self,
        creature: Herbivore,
        available_trees: list,
        all_assignments: Dict[int, list],
        cfg: Any,
        rng: random.Random,
    ) -> Optional[int]:
        if not available_trees:
            return None
        available_trees = sorted(
            available_trees,
            key=lambda t: len(all_assignments.get(t.tree_id, [])),
            reverse=True,
        )
        best_count = len(all_assignments.get(available_trees[0].tree_id, []))
        top = [t for t in available_trees if len(all_assignments.get(t.tree_id, [])) == best_count]
        return rng.choice(top).tree_id

    def predator_behavior(
        self,
        notifier: Herbivore,
        assigned: List[Herbivore],
        cfg: Any,
        rng: random.Random,
    ) -> Tuple[List[Herbivore], List[Herbivore]]:
        green_targets = [c for c in assigned if c.has_trait("green_beard") and c is not notifier]
        if green_targets:
            if rng.random() < getattr(cfg, "altruist_escape_prob", 0.5):
                return [notifier] + green_targets, []
            else:
                return green_targets, [notifier]
        else:
            return [notifier], []


class SolitaryCowardGene(Gene):
    """Solitario + cobarde: evita árboles concurridos y huye solo ante el depredador.

    Combina dos estrategias individualistas:
    1. **Elección de árbol** (``choose_tree``): prefiere los árboles con menos
       ocupantes, minimizando el tiempo de contacto con otros herbívoros.
    2. **Comportamiento ante depredador** (``predator_behavior``): al detectar un
       depredador, huye solo sin avisar al grupo (comportamiento cobarde).

    Hipótesis: la dispersión extrema reduce la presión de depredación local,
    pero al coste de perder toda protección cooperativa.
    """

    name = "solitary_coward"
    PRIORITY = 35

    def choose_tree(
        self,
        creature: Herbivore,
        available_trees: list,
        all_assignments: Dict[int, list],
        cfg: Any,
        rng: random.Random,
    ) -> Optional[int]:
        if not available_trees:
            return None
        available_trees = sorted(
            available_trees,
            key=lambda t: len(all_assignments.get(t.tree_id, [])),
        )
        min_count = len(all_assignments.get(available_trees[0].tree_id, []))
        bottom = [t for t in available_trees if len(all_assignments.get(t.tree_id, [])) == min_count]
        return rng.choice(bottom).tree_id

    def predator_behavior(
        self,
        notifier: Herbivore,
        assigned: List[Herbivore],
        cfg: Any,
        rng: random.Random,
    ) -> Tuple[List[Herbivore], List[Herbivore]]:
        return [notifier], []


class AmbushCamoGene(Gene):
    """Depredador emboscador con camuflaje muy alto.

    Combina dos ventajas ofensivas:
    1. **Selección de árbol** (``predator_choose_tree``): elige siempre el árbol
       con la mayor concentración de presas visibles (misma lógica que ``AmbushGene``).
    2. **Camuflaje extremo** (``apply_physical_traits``): factor de camuflaje 0.9,
       que reduce la probabilidad de detección en un 90 %.

    Hipótesis: la combinación de emboscada y sigilo máximo crea una presión de
    depredación tan intensa que puede llevar al colapso de la presa si no existe
    un mecanismo compensador (como el agrupamiento con alerta cooperativa).
    """

    name = "ambush_camo"
    PRIORITY = 20

    def apply_physical_traits(self, creature: Creature) -> Dict[str, Any]:
        return {"camouflage_factor": 0.9}

    def predator_choose_tree(
        self,
        predator: Predator,
        trees: list,
        visible_herbivores: Dict[int, List[Herbivore]],
        cfg: Any,
        rng: random.Random,
    ) -> int:
        non_empty = [t for t in trees if visible_herbivores.get(t.tree_id)]
        if not non_empty:
            return rng.choice(trees).tree_id
        max_count = max(len(visible_herbivores[t.tree_id]) for t in non_empty)
        candidates = [t for t in non_empty if len(visible_herbivores[t.tree_id]) == max_count]
        return rng.choice(candidates).tree_id


# ----------------------------------------------------------------- aliases

# Backward-compatibility aliases used in older experiment files
GreenBeardAltruistGene = SelectiveAltruistGene
NoPhysicalGene = Gene


class GreenBeardAltruistGene(Gene):
    """Barba verde + altruismo selectivo combinados en un solo gen.

    Equivale a tener ``GreenBeardGene`` + ``SelectiveAltruistGene`` juntos:
    la criatura porta la señal ``green_beard`` *y* alerta preferentemente a
    otros portadores de esa señal.  Si no hay aliados con barba verde,
    recurre al comportamiento cobarde.
    """

    name: str = "green_beard_altruist"
    PRIORITY: int = 30

    def apply_physical_traits(self, creature: Creature) -> Dict[str, Any]:
        return {"green_beard": True}

    def predator_behavior(
        self,
        notifier: Herbivore,
        assigned: List[Herbivore],
        cfg: Any,
        rng: random.Random,
    ) -> Tuple[List[Herbivore], List[Herbivore]]:
        green_targets = [c for c in assigned if c.has_trait("green_beard") and c is not notifier]
        if green_targets:
            if rng.random() < getattr(cfg, "altruist_escape_prob", 0.5):
                return [notifier] + green_targets, []
            else:
                return green_targets, [notifier]
        else:
            # No allies with green beard → coward behaviour
            return [notifier], []
