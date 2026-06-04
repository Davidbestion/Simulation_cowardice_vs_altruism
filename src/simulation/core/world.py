import random
from dataclasses import dataclass
from typing import List


@dataclass
class Tree:
    """Un sitio de pastoreo representado como un árbol.

    Cada árbol puede alimentar hasta ``capacity`` herbívoros por día.
    Esa capacidad se sortea al azar al crear el mundo y permanece fija
    durante toda la simulación (puede variar entre distintas simulaciones).

    Atributos:
        tree_id  : Identificador numérico único del árbol dentro del mundo.
        capacity : Máximo de herbívoros que el árbol puede albergar/alimentar
                   en un mismo día.
    """

    tree_id: int
    capacity: int = 2

    def __repr__(self) -> str:
        return f"Tree({self.tree_id}, cap={self.capacity})"


@dataclass
class World:
    """El ambiente completo de la simulación: un conjunto fijo de árboles.

    El mundo se crea una sola vez por simulación (antes del primer día)
    y sus árboles no cambian a lo largo de los días.  Sí puede variar
    entre distintas simulaciones, ya que las capacidades se sortean al azar.

    Atributos:
        trees : Lista de todos los árboles disponibles en el mundo.
    """

    trees: List[Tree]

    @property
    def num_trees(self) -> int:
        """Cantidad total de árboles en el mundo."""
        return len(self.trees)

    def total_capacity(self) -> int:
        """Suma de las capacidades de todos los árboles.

        Representa el máximo de herbívoros que pueden comer en un mismo día
        si todos los árboles estuviesen llenos.  Si la población supera este
        valor, los excedentes mueren de hambre antes de que comience la
        fase de interacción con depredadores.
        """
        return sum(t.capacity for t in self.trees)

    @staticmethod
    def create(
        num_trees: int,
        capacity_min: int,
        capacity_max: int,
        rng: random.Random,
    ) -> "World":
        """Construye un mundo nuevo con árboles de capacidad aleatoria.

        La capacidad de cada árbol se elige de forma independiente con una
        distribución uniforme discreta en el rango ``[capacity_min, capacity_max]``.
        Usar siempre el mismo ``rng`` con la misma semilla garantiza reproducibilidad.

        Args:
            num_trees    : Número de árboles a crear.
            capacity_min : Capacidad mínima posible para cualquier árbol.
            capacity_max : Capacidad máxima posible para cualquier árbol.
            rng          : Generador de números aleatorios (``random.Random``).
                           Se pasa explícitamente para que la semilla global
                           del simulador controle la reproducibilidad.

        Returns:
            Un nuevo objeto ``World`` listo para usar.
        """
        trees = [
            Tree(tree_id=i, capacity=rng.randint(capacity_min, capacity_max))
            for i in range(num_trees)
        ]
        return World(trees=trees)
