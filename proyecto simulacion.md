proyecto simulacion

Simulacion:
Hay criaturas, arboles, depredadores y casas. Cada dia las criaturas salen de sus casas hacia algun arbol para comer fruta. Cada arbol posee cada dia suficiente fruta para alimentar a dos criaturas. Algunos arboles poseen depredadores escondidos. Cuando una o dos criaturas van a un arbol con un depredador, este se los come. Luego de comer, las criaturas regresan a sus casas y se reproducen, creando una o dos criaturas mas, y terminando el dia. Cada dia hay la misma cantidad de depredadores pero distribuidos sobre arboles distintos. EL ciclo se repite durante una cantidad de dias determinados.

- 1era modificacion/experimentacion:
 Hacer q las criaturas puedan ser cobardes o altruistas. Cuando dos criaturas a1 y a2 van a un mismo arbol con depredador, una de ellas siempre notara al depredador. Si la q lo detecta (supongamos q es a1) es cobarde, huira, dejando a la segunda a su muerte. Si la q lo detecta (a1) es altruista, avisara a su companera (a2), permitiendole huir, pero atraera la atencion del depredador (a a1), y a1 podra escapar del depredador con un 50% (valor cambiable) de probabilidad de exito.

- 2do experimento:
 Dotar a las criaturas altruistas de una barba verde que pueden usar para identificarse entre ellas, o sea, si dos criaturas van al mismo arbol, si una de ellas es altruista, podra saber si la otra tambien lo es al verla por la barba verde. AHora, si dos criaturas van al mismo arbol, si el arbol tiene un depredador, aquella criatura q sea altruista y q haya detectado al depredador avisara a la otra solamente si esa otra criatura posee una barba verde (en este caso, es altruista). Probar con varios %s distintos de probabilidad de escape del altruista al avisar a la otra criatura, y con la distribucion de la poblacion inicial (q porciento de la poblacion es altruista).

- 3er experimento:
 Crear dos genes con dos variantes cada uno: uno q denota la presencia o no de la barba verde y otro q denota la presencia de altruismo o no, generando 4 tipos de criaturas:

  - altruistas con barba verde
  - altruistas sin barba verde
  - cobardes con barba verde
  - cobardes sin barba verde

Los porcientos de nuevo deben poder ser modificados para experimentacion.

En todos los casos debo analisar comportamiento de las diferentes poblaciones resultantes, la evolucion de estas poblaciones, corriendo cada experimento varias veces, graficando los datos.

EL codigo debe ser mantenible, extensible, teniendo en cuenta q planeo hacer mas experimentacion con otros datos y agregos a esta simulacion, aplicando principios SOLID, con mucha documentacion (comentarios, docstring bien explicados, etc) y usando buenas practicas de programacion.
Prefiero q sea en un jupyter notebook para poder ejecutar cada simulacion por partes y ver la evolucion.
