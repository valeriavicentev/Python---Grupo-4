# Parte 4: Bitácora de uso de IA 

## Parte 1: Scraping de decretos de emergencia

Caso 1 - Títulos genéricos escondían un decreto de lluvias

1. ¿Qué le pedimos a la IA?
Una función que entre a cada enlace de las normas y extraiga el título completo, con el fin de usarla posteriormente para para clasificar y filtrar los decretos por lluvias.

2. ¿Qué nos respondió?
La función titulo_completo(enlace)..., que extraía el texto de cada elemento de "div.description" de cada página web y, si no lo encontraba, devolvía el mensaje "No se encontró descripción". El resultado obtenido fue "Normas sin título completo: 0".

3. ¿Qué estaba mal y cómo nos dimos cuenta?
Aunque el código funcionaba correctamente y el contador indicaba que había "0 normas sin título completo", este resultado no garantizaba que esta operación fuera suficiente para clasificar las normas correctamente.
Ya que, luego una de exploración inicial de los resultados y de gob.pe, identificamos que los DS 007-2025-PCM y 008-2025-PCM solo decían "Declaratoria de Emergencia", sin mayor descripción del lugar o motivo.
Por este motivo, la función no los detectó como faltantes y quedaron clasificados como "otro" y como si no fueran de lluvias.
Luego de revisar los PDFs a mano, detectamos que uno de ellos estaba asociado a lluvias y el otro no.

4. ¿Cómo lo corregimos?
Se abrió el PDF de cada decreto, se copió el título real y se volvió a clasificar (ver ítem 10.1). La revisión permitió determinar que el **DS 007-2025-PCM sí estaba relacionado con lluvias,  mientras que el DS 008-2025-PCM correspondía a una emergencia por colapso del alcantarillado en Chiclayo. 

Tras el ajuste, el número de normas clasificadas como lluvias pasó de 17 a 18.

## Parte 2: API

1. ¿Qué le pedimos a la IA?

2. ¿Qué nos respondió?

3. ¿Qué estaba mal y cómo nos dimos cuenta?

4. ¿Cómo lo corregimos?