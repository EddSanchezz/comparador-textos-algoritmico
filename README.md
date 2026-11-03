# Análisis de abstracts científicos

Aplicación local en Streamlit para cargar artículos científicos en PDF, revisar
sus abstracts, comparar su similitud, agruparlos y buscar patrones de texto.

## Funciones

- Carga automática de los PDFs de la carpeta `pdfs/`.
- Carga manual de otros PDFs desde la interfaz.
- Extracción y corrección del título, los autores y el abstract.
- Cuatro métodos clásicos de similitud entre abstracts:
  - Distancia de Levenshtein sobre secuencias de palabras.
  - Similitud coseno con vectores TF-IDF.
  - Coeficiente de Jaccard.
  - Similitud a partir de la distancia euclidiana entre vectores TF-IDF.
- Dos medidas sobre embeddings del modelo `all-MiniLM-L6-v2`:
  - Similitud coseno.
  - Similitud a partir de la distancia euclidiana.
- Agrupamiento jerárquico con Single, Complete y Average Linkage.
- Dendrograma para cada método y selección del número de grupos con el
  coeficiente Silhouette.
- Búsqueda exacta de cadenas con KMP, Boyer-Moore y Rabin-Karp, con el número
  de ocurrencias, sus posiciones y el tiempo de cada algoritmo.

## Instalación y uso

Requiere Python 3.14.

```bat
iniciar.bat
```

El script instala las dependencias y abre la aplicación en el navegador. La
primera vez que se calculan embeddings se descarga el modelo, por lo que hace
falta conexión a Internet. También se puede iniciar manualmente:

```bat
py -3.14 -m pip install -r requirements.txt
py -3.14 -m streamlit run app.py
```

## Estructura

```
app.py                          Interfaz de la aplicación
pdf_reader.py                   Extracción de datos desde los PDFs
algorithms/text_processing.py   Separación del texto en palabras
algorithms/similarity/          Medidas de similitud
algorithms/clustering/          Agrupamiento jerárquico y Silhouette
algorithms/search/              Búsqueda exacta de cadenas
algorithms/dendrogram.py        Dibujo de dendrogramas
pdfs/                           Corpus de artículos
tests/                          Pruebas automáticas
```

## Métodos

### Similitud

- **Levenshtein:** programación dinámica que cuenta inserciones, eliminaciones y
  reemplazos entre secuencias de palabras. La similitud normaliza la distancia
  por la longitud de la secuencia más larga.
- **TF-IDF:** cada abstract se representa con la frecuencia de cada término
  multiplicada por su importancia inversa en el corpus.
- **Coseno:** mide el ángulo entre dos vectores TF-IDF.
- **Euclidiana:** mide la distancia entre los vectores y la convierte en
  similitud con `1 / (1 + distancia)`.
- **Jaccard:** palabras compartidas dividido por el total de palabras distintas.
- **Embeddings:** un modelo preentrenado transforma cada abstract en un vector
  denso; sobre esos vectores se aplican coseno y distancia euclidiana.

### Agrupamiento

Cada artículo empieza en su propio grupo y en cada paso se unen los dos grupos
más cercanos según la distancia coseno entre sus vectores TF-IDF:

- **Single Linkage:** la menor distancia entre los miembros de dos grupos.
- **Complete Linkage:** la mayor distancia entre los miembros de dos grupos.
- **Average Linkage:** el promedio de las distancias entre los miembros.

El dendrograma muestra el orden de las uniones y el coeficiente Silhouette
sugiere cuántos grupos conviene conservar.

### Búsqueda

- **KMP:** calcula la tabla de prefijos que también son sufijos para no repetir
  comparaciones.
- **Boyer-Moore:** compara desde el final del patrón y se desplaza según el
  último lugar del carácter que no coincidió.
- **Rabin-Karp:** usa un hash que se actualiza al mover la ventana y verifica los
  caracteres cuando los hashes coinciden.

## Pruebas

```bat
py -3.14 -m unittest discover -s tests -v
```
