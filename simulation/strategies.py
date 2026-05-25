"""
Estrategias de encuentro con depredadores.

Implementa el Patrón Strategy (GoF): cada experimento define su propia
subclase de PredatorEncounterStrategy sin modificar el motor de simulación
(Principio Abierto/Cerrado de SOLID).

Jerarquía:
    PredatorEncounterStrategy  (abstracta)
    ├── BaseEncounterStrategy   → todos mueren (línea de base)
    ├── Experiment1Strategy     → cobardía vs. altruismo simple
    ├── Experiment2Strategy     → altruismo con barba verde
    └── Experiment3Strategy     → cuatro fenotipos independientes
"""

import random
from abc import ABC, abstractmethod
from typing import List, Optional, Tuple

from .models import Creature, Trait, BeardColor


class PredatorEncounterStrategy(ABC):
    """
    Interfaz abstracta para la lógica de encuentro con depredadores.

    La clase Simulation depende solo de esta interfaz (no de implementaciones
    concretas), cumpliendo el Principio de Inversión de Dependencias.

    Para añadir un experimento nuevo: crear una subclase e implementar
    handle_encounter. No es necesario tocar ninguna otra clase.
    """

    @abstractmethod
    def handle_encounter(
        self,
        creatures: List[Creature],
        escape_probability: float,
    ) -> List[Creature]:
        """
        Resuelve el encuentro entre criaturas y un depredador.

        Args:
            creatures:          Lista con 1 o 2 criaturas en el árbol.
            escape_probability: Probabilidad (0-1) de que un altruista
                                escape al depredador tras avisar.

        Returns:
            Lista de criaturas que sobreviven al encuentro.
        """

    def _select_detector(
        self,
        creatures: List[Creature],
    ) -> Tuple[Creature, Optional[Creature]]:
        """
        Elige aleatoriamente qué criatura detecta primero al depredador.

        Args:
            creatures: Lista con 1 o 2 criaturas.

        Returns:
            Tupla (detectora, compañera). compañera es None si hay 1 sola.
        """
        if len(creatures) == 1:
            return creatures[0], None
        idx = random.randint(0, 1)
        return creatures[idx], creatures[1 - idx]


class BaseEncounterStrategy(PredatorEncounterStrategy):
    """
    Estrategia base: el depredador siempre mata a todas las criaturas.

    Sirve como línea de base para comparar con los experimentos.
    Los rasgos de las criaturas no tienen ningún efecto.
    """

    def handle_encounter(
        self,
        creatures: List[Creature],
        escape_probability: float,
    ) -> List[Creature]:
        """Retorna vacío: el depredador mata a todas las criaturas."""
        return []


class Experiment1Strategy(PredatorEncounterStrategy):
    """
    Estrategia del Experimento 1: Cobardía vs. Altruismo simple.

    Reglas para un árbol con depredador:
    
     1 criatura sola  → siempre muere.                               
     2 criaturas:                                                    
       Se elige aleatoriamente cuál detecta al depredador.           
       • DETECTORA es COBARDE:                                       
           → Huye (sobrevive). Compañera muere.                      
       • DETECTORA es ALTRUISTA:                                     
           → Avisa a compañera (compañera SIEMPRE escapa).           
           → Detectora se expone; escapa con P = escape_probability. 
    
    """

    def handle_encounter(
        self,
        creatures: List[Creature],
        escape_probability: float,
    ) -> List[Creature]:
        if not creatures:
            return []
        detector, other = self._select_detector(creatures)
        if other is None:
            return []  # Criatura sola: siempre muere
        if detector.trait == Trait.COWARD:
            return [detector]  # Cobarde huye, compañera muere
        # Altruista avisa → compañera siempre escapa
        survivors = [other]
        if random.random() < escape_probability:
            survivors.append(detector)
        return survivors


class Experiment2Strategy(PredatorEncounterStrategy):
    """
    Estrategia del Experimento 2: Altruismo con reconocimiento de Barba Verde.

    Los altruistas tienen barba verde para identificarse mutuamente.
    En este experimento: barba verde ↔ altruismo (correlación perfecta).

    Reglas para un árbol con depredador:
    
     1 criatura sola  → siempre muere.                              
     2 criaturas:                                                    
       • DETECTORA es COBARDE:                                       
           → Siempre huye. Compañera muere.                          
       • DETECTORA es ALTRUISTA:                                     
           → Si compañera tiene BARBA VERDE:                         
               Avisa (compañera SIEMPRE escapa).                     
               Detectora escapa con P = escape_probability.          
           → Si compañera NO tiene barba verde:                      
               Actúa como cobarde (huye, compañera muere).           
    

    Notes:
        El Experimento 3 desacopla altruismo y barba verde en genes
        independientes, pero usa exactamente la misma lógica de encuentro.
    """

    def handle_encounter(
        self,
        creatures: List[Creature],
        escape_probability: float,
    ) -> List[Creature]:
        if not creatures:
            return []
        detector, other = self._select_detector(creatures)
        if other is None:
            return []  # Criatura sola: siempre muere
        if detector.trait == Trait.COWARD:
            return [detector]  # Cobarde: siempre huye
        # Altruista: avisa solo si la compañera tiene barba verde
        if other.beard == BeardColor.GREEN:
            survivors = [other]
            if random.random() < escape_probability:
                survivors.append(detector)
            return survivors
        # Compañera sin barba verde → altruista actúa como cobarde
        return [detector]


class Experiment3Strategy(Experiment2Strategy):
    """
    Estrategia del Experimento 3: Cuatro fenotipos con genes independientes.

    Desacopla los genes de altruismo y barba verde, generando cuatro fenotipos:
      1. Altruista + Barba Verde  → avisa a criaturas con barba verde.
      2. Altruista + Sin Barba   → avisa a criaturas con barba verde.
      3. Cobarde   + Barba Verde  → huye, pero puede recibir avisos ('tramposo').
      4. Cobarde   + Sin Barba    → huye, no recibe avisos.

    La lógica de encuentro es idéntica al Experimento 2: la detectora altruista
    avisa solo si la compañera tiene barba verde, sin importar si esa compañera
    es altruista o cobarde.

    Esto permite estudiar si los cobardes con barba verde (tramposos) pueden
    explotar y desestabilizar el sistema de señalización honesta.

    Notes:
        Hereda de Experiment2Strategy sin cambios en la lógica de encuentro.
        La diferencia está en la composición de la población inicial.
    """
    pass  # Lógica de encuentro heredada sin modificaciones
