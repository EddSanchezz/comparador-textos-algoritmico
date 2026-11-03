# Análisis de algoritmos en el contexto de la bibliometría

**Universidad del Quindío**
**Programa de Ingeniería de Sistemas y Computación**

**Descripción final del proyecto**

---

## 1. Introducción

El estudio computacional de textos permite explorar y analizar volúmenes de datos derivados de la producción científica utilizando métodos cuantitativos y cualitativos. Se fundamenta en las matemáticas y la estadística, para establecer descripciones, relaciones, inferencias y presentaciones de la información suministrada por publicaciones científicas. En este contexto, la extracción de patrones, el análisis de similitud textual, la búsqueda, entre otros, resultan fundamentales.

Para este proyecto, el dominio de conocimiento girará en torno a la inteligencia artificial generativa. Se busca que el estudiante enfrente el reto algorítmico de procesar lenguaje natural no estructurado, comprendiendo la transición matemática y lógica desde las estructuras de datos y algoritmos clásicos, hasta los modelos modernos implementados con Inteligencia Artificial (IA).

## 2. Fuentes de información

A diferencia de los procesos tradicionales de recolección automatizada sobre bases de datos científicas (tales como ACM, SAGE o ScienceDirect), para este proyecto se suministrará un corpus documental controlado y estático. La fuente de información consistirá en 20 artículos científicos entregados en formato PDF directamente por el docente.

El procesamiento computacional y la implementación de los algoritmos se enfocarán de manera estricta y primordial sobre el abstract (resumen) de cada artículo. Los metadatos adicionales presentes en los documentos, específicamente el título del proyecto y los autores, serán extraídos y utilizados para requerimientos funcionales muy precisos que exijan el cruce de información.

## 3. Propósito del proyecto

El objetivo central es implementar algoritmos que permitan el análisis computacional sobre un dominio de conocimiento, utilizando como base los documentos PDF. El desarrollo del proyecto se fundamentará en requerimientos funcionales que contemplan la implementación de diversas técnicas de análisis textual y diferentes tipos de algoritmos, exigiendo una evaluación comparativa entre enfoques clásicos y modelos de IA.

El proyecto exige un rigor analítico y matemático. El estudiante deberá demostrar el funcionamiento algorítmico interno mediante casos de estudio concretos sobre los textos procesados. Finalmente, para la culminación y entrega del proyecto es necesario el despliegue de la aplicación con la correspondiente documentación técnica.

A continuación se hace una descripción de los requerimientos funcionales del proyecto.

---

## Requerimiento 1: Análisis de Similitud Textual (Enfoques Clásicos e Inteligencia Artificial)

La aplicación deberá permitir la selección dinámica de dos o más artículos científicos del corpus para extraer sus respectivos abstracts y someterlos a un análisis comparativo de similitud textual. Para ello, es necesaria la implementación y el análisis de los siguientes algoritmos:

### Algoritmos clásicos (4 algoritmos)

Se deben construir cuatro algoritmos tradicionales de similitud. Se sugiere implementar una combinación de enfoques basados en programación dinámica y modelos de espacio vectorial. Por ejemplo:

- **Basados en distancia de edición:** Algoritmo de Levenshtein o Needleman-Wunsch.
- **Basados en vectorización y conjuntos:** Similitud del Coseno (usando TF-IDF) y Coeficiente de Jaccard.

### Modelos basados en Inteligencia Artificial (2 algoritmos)

Se deben implementar dos enfoques de similitud apoyados en la generación de embeddings (representaciones vectoriales densas). Los estudiantes pueden utilizar modelos preentrenados (por ejemplo, Word2Vec, FastText o modelos de lenguaje a través de APIs/librerías) para vectorizar los abstracts y, posteriormente, calcular la similitud métrica (distancia euclidiana o coseno) entre dichos vectores.

### Análisis algorítmico y matemático (documentación requerida)

El análisis de cada algoritmo implementado se debe presentar en el documento técnico (por escrito) con un caso de estudio práctico. Específicamente se requiere:

- **Caso de análisis concreto:** Seleccionar dos abstracts específicos de los artículos proporcionados.
- **Demostración paso a paso:** Utilizando los dos abstracts seleccionados, demostrar de forma detallada cómo funciona matemáticamente cada algoritmo, por ejemplo el llenado de la matriz en programación dinámica o el cálculo de los pesos y el ángulo en la similitud del coseno.
- **Análisis crítico:** Comparar los resultados de similitud obtenidos empíricamente por los algoritmos clásicos frente a los modelos de IA para ese mismo caso de estudio.

---

## Requerimiento 2: Agrupamiento Jerárquico (Clustering)

Implementar tres algoritmos de agrupamiento jerárquico para construir un árbol (dendrograma) que represente la similitud entre los abstracts científicos extraídos de los 20 documentos PDF. Para llegar a este resultado, se debe realizar un preprocesamiento del texto (transformar el abstract), el cálculo de la similitud, la aplicación de clustering y la representación mediante un dendrograma.

### Análisis algorítmico y matemático (documentación requerida)

- Se debe determinar cuál de los algoritmos produce agrupamientos más coherentes. Esto debe sustentarse mediante la aplicación de una métrica matemática de evaluación interna.
- **Aplicación de clustering:** Implementar desde cero tres criterios distintos de agrupamiento jerárquico (por ejemplo: Single Linkage, Complete Linkage y Average Linkage o Ward).
- **Representación visual:** Construir el dendrograma correspondiente para cada uno de los tres algoritmos ejecutados.

---

## Requerimiento 3: Búsqueda de Patrones de Texto (Coincidencia Exacta de Cadenas)

La aplicación deberá permitir al usuario ingresar una cadena de texto (patrón de búsqueda) para localizar sus ocurrencias exactas dentro de los abstracts extraídos de los 20 artículos científicos del corpus. Para ello, se deben construir desde cero tres algoritmos tradicionales de coincidencia de cadenas (string matching). No se acepta el uso de funciones de alto nivel o nativas del lenguaje (como `find()` o `indexOf()`).

Los algoritmos son:

- **Algoritmo Knuth-Morris-Pratt (KMP):** Basado en el análisis de prefijos y sufijos para evitar retrocesos innecesarios sobre el texto.
- **Algoritmo Boyer-Moore:** Basado en heurísticas de desplazamiento (regla del carácter malo y/o regla del sufijo bueno).
- **Algoritmo Rabin-Karp:** Basado en aritmética modular y funciones de Rolling Hash.

El análisis de cada algoritmo implementado se debe presentar en el documento detallando un caso de estudio práctico. Específicamente se requiere:

- **Caso de análisis concreto:** Seleccionar un patrón de búsqueda específico (por ejemplo, `"algoritmos"`) y un párrafo extraído de uno de los abstracts procesados.
- **Demostración paso a paso:** Utilizando el patrón y el texto seleccionados, demostrar de forma detallada el funcionamiento matemático y lógico de las estructuras auxiliares de los tres algoritmos. Por ejemplo, detallar en Rabin-Karp el cálculo numérico iterativo para el hash (y sus posibles colisiones), y en Boyer-Moore el llenado de las tablas heurísticas, graficando las iteraciones y desplazamientos sobre el texto.
- **Análisis crítico:** Realizar una comparación formal fundamentada en la complejidad asintótica teórica (notación Big O) de los tres algoritmos, evaluando específicamente el impacto de los tiempos de preprocesamiento frente a los tiempos reales de búsqueda. Este análisis teórico debe ser contrastado con el rendimiento observado al ejecutar las implementaciones.

---

## Requerimiento 4

El proyecto debe estar desplegado y soportado con la documentación técnica para cada uno de los requerimientos.

---

## Documento final

El proyecto debe estar soportado en un documento de diseño con la correspondiente arquitectura. Se debe presentar para cada requerimiento una explicación técnica con detalles de implementación.

El uso de IA debe estar debidamente fundamentado y se proporcionará un documento con los aspectos que deben ser considerados. El uso de herramientas de inteligencia artificial generativa como apoyo al desarrollo del proyecto deberá ser declarado explícitamente. Dichas herramientas podrán utilizarse como soporte, pero no podrán reemplazar el diseño algorítmico ni el análisis formal solicitado en el curso.

No se acepta el uso de funciones de alto nivel que implementen directamente los algoritmos solicitados en el proyecto. Los algoritmos deberán ser implementados de forma explícita por los estudiantes, utilizando estructuras básicas del lenguaje de programación elegido, de manera que el comportamiento algorítmico sea completamente transparente y analizable.

> **Nota:** En caso de ser necesario, la presente descripción del proyecto puede ser modificada para efectos de dar mayor claridad en su especificación. En particular con los requerimientos funcionales, los cuales podrán ser explicados con mayor detalle.
