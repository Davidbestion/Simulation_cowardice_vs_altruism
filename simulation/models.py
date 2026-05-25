"""
Modelos de datos centrales de la simulación.

Contiene las entidades básicas del sistema:
- Trait       → rasgo de comportamiento (cobarde o altruista).
- BeardColor  → presencia o no de barba verde.
- Creature    → criatura individual con sus rasgos genéticos.
- DayStats    → snapshot estadístico al cierre de un día.
"""

from dataclasses import dataclass
from enum import Enum
from typing import List


class Trait(Enum):
    """
    Rasgo de comportamiento de una criatura ante un depredador.

    COWARD:
        La criatura es cobarde. Al detectar un depredador, huirá sin
        avisar a su compañera, dejándola a su suerte.
    ALTRUIST:
        La criatura es altruista. Al detectar un depredador, puede
        avisar a su compañera (según las reglas del experimento),
        asumiendo el riesgo de morir en el proceso.
    """
    COWARD   = "cobarde"
    ALTRUIST = "altruista"


class BeardColor(Enum):
    """
    Presencia de barba verde como marcador genético observable.

    En el Experimento 2: barba verde ↔ altruismo (correlación perfecta).
    En el Experimento 3: barba verde y altruismo son genes independientes;
    los cobardes también pueden tener barba verde ('tramposos').

    NONE:  Sin barba verde. No puede ser identificada visualmente.
    GREEN: Con barba verde. Señal observable de (supuesto) altruismo.
    """
    NONE  = "sin_barba"
    GREEN = "barba_verde"


@dataclass
class Creature:
    """
    Criatura individual con sus rasgos genéticos.

    Attributes:
        trait: Rasgo de comportamiento (COWARD o ALTRUIST).
        beard: Color de barba (NONE o GREEN).

    Notes:
        Experimento 1: beard siempre es NONE.
        Experimento 2: ALTRUIST ↔ GREEN (correlación total).
        Experimento 3: trait y beard son genes independientes (4 fenotipos).
    """
    trait: Trait
    beard: BeardColor = BeardColor.NONE

    def reproduce(self) -> List["Creature"]:
        """
        Genera uno o dos descendientes idénticos al progenitor.

        La criatura no se elimina al reproducirse: el progenitor permanece
        y además nacen 1 o 2 hijos que heredan exactamente los rasgos
        (`trait` y `beard`). El número de descendientes se elige aleatoriamente
        entre 1 y 2 (probabilidad 50/50).

        Returns:
            Lista con 1 o 2 nuevas instancias de `Creature`.
        """
        import random
        num_offspring = random.choice([1, 2])
        return [Creature(trait=self.trait, beard=self.beard) for _ in range(num_offspring)]

    def get_type_label(self) -> str:
        """
        Etiqueta descriptiva del fenotipo.

        Returns:
            String como 'Altruista (Barba Verde)' o 'Cobarde'.
        """
        beard_str = " (Barba Verde)" if self.beard == BeardColor.GREEN else ""
        return f"{self.trait.value.capitalize()}{beard_str}"

    def __repr__(self) -> str:
        return f"Creature({self.trait.value}, {self.beard.value})"


@dataclass
class DayStats:
    """
    Estadísticas recolectadas al cierre de un día de simulación.

    Attributes:
        day:                     Número del día (1-indexado).
        total_population:        Población total al final del día.
        altruist_count:          Cantidad de criaturas altruistas.
        coward_count:            Cantidad de criaturas cobardes.
        green_beard_count:       Criaturas con barba verde (cualquier rasgo).
        altruist_green_count:    Altruistas con barba verde (Experimento 3).
        altruist_no_green_count: Altruistas sin barba verde (Experimento 3).
        coward_green_count:      Cobardes con barba verde (Experimento 3).
        coward_no_green_count:   Cobardes sin barba verde (Experimento 3).
        deaths:                  Muertes ocurridas en el día.
        births:                  Nacimientos ocurridos en el día.
    """
    day:                     int
    total_population:        int
    altruist_count:          int
    coward_count:            int
    green_beard_count:       int
    altruist_green_count:    int = 0
    altruist_no_green_count: int = 0
    coward_green_count:      int = 0
    coward_no_green_count:   int = 0
    deaths:                  int = 0
    births:                  int = 0

    @property
    def altruist_fraction(self) -> float:
        """Fracción de altruistas en la población. Retorna 0 si población = 0."""
        return (self.altruist_count / self.total_population
                if self.total_population > 0 else 0.0)

    @property
    def coward_fraction(self) -> float:
        """Fracción de cobardes en la población. Retorna 0 si población = 0."""
        return (self.coward_count / self.total_population
                if self.total_population > 0 else 0.0)
