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

Caso 2 - Claude generó DataFrames con códigos complejos que impedían trabajar en los siguientes ítems

1. ¿Qué le pedimos a la IA?
Que armara un DataFrame con las normas extraídas de cada mes, con las columnas número de la norma, fecha de publicación, título y enlace.

2. ¿Qué nos respondió?
Un código que, además de crear el DataFrame, transformaba los datos, pues recortaba la denominación completa de la nomrma, dejando solo la numeración (e.g. "018-2025-PCM"); y convertía la fecha "Publicado: 30 de enero de 2025" a tipo fecha.

3. ¿Qué estaba mal y cómo nos dimos cuenta?
El código era más complejo de lo que pedía el ejercicio y nos dimos cuenta de que no servía cuando quisimos avanzar con los pasos siguientes, pues al recortar el número de la norma se perdía el texto original ("Decreto Supremo N.° 007-2025-PCM"), que después usamos para ubicar y corregir los DS 007 y 008.

4. ¿Cómo lo corregimos?
Simplificamos el código. En cada mes solo guardamos la lista de normas y la mostramos con PD.DataFrame, sin transformar los datos. 
El número y la fecha se dejaron como texto original ("Decreto Supremo N.° 007-2025-PCM", "Publicado: 10 de enero de 2025") y así se guardaron en `datos/decretos_lluvias.csv`. 

## Parte 2: API

Caso 3 - Claude complejizó extracción de datos de Wikipedia. 

1. ¿Qué le pedimos a la IA?

Le pedimos a Claude que nos ayude a elaborar los códigos para la limpieza de la base de datos, con la información extraída de las tablas de Wikipedia.

2. ¿Qué nos respondió?

Dentro de los códigos, también incluyó ejemplos de verificaciones para cada paso. Elaboró códigos para probar cada parte del proceso con casos individuales.

3. ¿Qué estaba mal y cómo nos dimos cuenta?

⁠Eso alargó innecesariamente los códigos  y complejizó el proceso. 

4. ¿Cómo lo corregimos?

⁠Revisamos cada parte de de la redacción de los códigos y ejecutamos solo lo necesario para no extender la resolución del problema.