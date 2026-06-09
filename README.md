# Estrategias evolutivas bajo presión de depredación

Proyecto de Simulación — Facultad de Matemática y Computación, Universidad de La Habana  
Asignatura: Simulación · 4.º año, Curso 2025–2026  
Autor: David Sánchez Iglesias

---

## Descripción

Simulación computacional basada en agentes del comportamiento evolutivo de herbívoros y depredadores en un entorno con recursos limitados. El sistema modela dos poblaciones con genomas independientes que coevolucionan generación a generación, permitiendo estudiar la estabilidad de estrategias cooperativas, el camuflaje y las dinámicas de agrupamiento bajo presión de depredación activa.

Se realizaron 9 experimentos de complejidad creciente, cada uno con 30 corridas independientes por condición experimental.

---

## Resultados principales

| Experimento | Pregunta central | Resultado |
| --- | --- | --- |
| 1 | Cobardía pura como línea base | Equilibrio estable; extinción estocástica del depredador frecuente |
| 2 | Cobardía vs Altruismo puro | Altruismo inestable; cobarde domina en ~70 % de corridas |
| 3 | Altruismo selectivo con barba verde | Estable con masa crítica ≥ 50 %; dependiente de p_escape |
| 4 | Cuatro estrategias desacopladas | Impostores destruyen la señal; converge a cobardía |
| 5 | Camuflaje en herbívoros | Fijación casi segura desde 50 %; muy robusto |
| 6 | Camuflaje en depredadores | Paradoja de la eficiencia: alta extinción predadora (14–27/30) |
| 7 | Coevolución de camuflajes | La presa gana la carrera armamentista en prácticamente todos los casos |
| 8 | Agrupamiento social vs camuflaje predador | Equilibrio solo con detección muy baja (0.10) |
| 9 | Social/Solitario vs Emboscador/Cauteloso | El emboscador camuflado domina; el solitario es la mejor respuesta de presa |

El cuaderno de experimentación completo con gráficas, tablas y conclusiones por experimento está en [`experimentacion_core.ipynb`](experimentacion_core.ipynb).

---

## Estructura del proyecto

```text
.
├── experimentacion_core.ipynb   # Cuaderno principal: experimentos, resultados y conclusiones
├── informe/
│   └── informe.tex              # Informe en LaTeX
└── src/
    └── simulation/
        ├── core/                # Motor de simulación
        │   ├── simulation.py    # SimulationConfig, Experiment, DayReport, TreeInteractionLog
        │   ├── world.py         # Tree, World
        │   ├── creature.py      # Creature, Herbivore, Predator
        │   ├── genes.py         # Gene (base) y todas las implementaciones
        │   └── simulator.py     # Simulator — ciclo principal
        ├── analysis/
        │   ├── runner.py        # SimpleExperiment, RandomPredatorGene, run_multiple
        │   └── plotting.py      # Funciones de visualización
        └── instances/
            ├── loader.py        # Descubrimiento dinámico de experimentos y configuraciones
            ├── experiments/     # Experimentos 1–9 como instancias de SimpleExperiment
            └── configurations/  # Configuración por defecto compartida
```

---

## Genes implementados

### Herbívoros

| Gen | Comportamiento |
| --- | --- |
| `CowardGene` | El detector huye solo; los demás quedan expuestos |
| `AltruistGene` | Avisa a todos; escapa con probabilidad `altruist_escape_prob` |
| `SelectiveAltruistGene` | Altruismo selectivo hacia portadores de `green_beard` |
| `GreenBeardGene` | Señal física `green_beard` sin comportamiento adicional |
| `GreenBeardAltruistGene` | Barba verde + altruismo selectivo en un solo gen |
| `CamouflageHerbivoreGene` | Invisible para depredadores; `hunt_evasion=0.5` |
| `CamouflageCowardGene` | Invisible + cobarde; `hunt_evasion=0.4` |
| `SocialGene` | Prefiere árboles con más ocupantes |
| `SolitaryGene` | Prefiere árboles con menos ocupantes |
| `SocialGreenBeardAltruistGene` | Social + barba verde + altruismo selectivo |
| `SolitaryCowardGene` | Solitario + cobarde |

### Depredadores

| Gen | Comportamiento |
| --- | --- |
| `CamouflagePredatorGene` | `camouflage_factor=0.6` (reduce detección un 60 %) |
| `AmbushGene` | Elige el árbol más poblado |
| `CautiousPredatorGene` | Elige el árbol menos poblado |
| `GreedyHunterGene` | Aumenta `predator_hunt_capacity` |
| `AmbushCamoGene` | Emboscada + `camouflage_factor=0.9` |
| `RandomPredatorGene` | Selección aleatoria de árbol (presión no dirigida) |

---

## Uso rápido

**Requisitos:** Python 3.10+, `matplotlib`, `numpy` (solo para plotting).

```python
import sys; sys.path.insert(0, "src")

from simulation.core import SimulationConfig, CowardGene, AltruistGene
from simulation.analysis.runner import SimpleExperiment, RandomPredatorGene, run_multiple

config = SimulationConfig(
    num_trees=25, tree_capacity_min=2, tree_capacity_max=2,
    num_generations=200, initial_population=80, initial_predators=8,
    base_detection_prob=0.30, altruist_escape_prob=0.50,
    predator_hunt_capacity=1, seed=42,
)

exp = SimpleExperiment(
    name="Mi experimento",
    description="50 % cobardes / 50 % altruistas",
    config=config,
    herbivore_specs=[
        (lambda: [CowardGene()],   0.5),
        (lambda: [AltruistGene()], 0.5),
    ],
    predator_specs=[(lambda: [RandomPredatorGene()], 1.0)],
)

# Corrida única
from simulation.core.simulator import Simulator
reports = Simulator(exp).run()
print(reports[-1].gene_frequencies)

# 30 corridas independientes
all_runs = run_multiple(exp, config, n_runs=30, base_seed=0)
```

**Descubrir todos los experimentos registrados:**

```python
from simulation.instances.loader import discover_experiments

for name, exp in discover_experiments().items():
    if not isinstance(exp, type):           # excluir clases sin instanciar
        print(name, "—", exp.name)
```

**Ejecutar el cuaderno:**

```bash
jupyter notebook experimentacion_core.ipynb
```

---

## Parámetros de simulación

| Parámetro | Descripción | Valor típico |
| --- | --- | --- |
| `num_trees` | Número de árboles en el mundo | 25 |
| `tree_capacity_min/max` | Rango de capacidad por árbol | 2–6 |
| `num_generations` | Duración de la simulación | 100–400 |
| `initial_population` | Herbívoros iniciales | 80 |
| `initial_predators` | Depredadores iniciales | 8 |
| `offspring_min/max` | Crías por herbívoro superviviente | 1–2 |
| `predator_offspring_min/max` | Crías por depredador que cazó | 1–2 |
| `base_detection_prob` | Probabilidad base de detección | 0.30 |
| `altruist_escape_prob` | Probabilidad de escape del altruista | 0.50 |
| `predator_hunt_capacity` | Presas máximas por depredador por visita | 1 |
| `seed` | Semilla del RNG (reproducibilidad) | 42 |
