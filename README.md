# Comparador de textos algorítmico

Proyecto académico para analizar los abstracts de 20 artículos científicos sobre inteligencia artificial generativa. El repositorio contiene el corpus y el esqueleto Python para los requisitos; la aplicación y sus algoritmos todavía están en desarrollo.

## Requisitos

| Requisito | Objetivo | Código previsto | Estado |
|---|---|---|---|
| **1. Similitud textual** | Seleccionar al menos dos artículos y comparar sus abstracts con cuatro métodos clásicos y dos enfoques con embeddings. | `rq_1/classic/`, `rq_1/ai/` | Estructura creada; algoritmos pendientes. |
| **2. Agrupamiento jerárquico** | Agrupar los 20 abstracts, evaluar los grupos y producir tres dendrogramas. | `rq_2/clustering/`, `rq_2/evaluation/`, `rq_2/visualization/` | Estructura creada; selección final de métodos y código pendientes. |
| **3. Búsqueda de patrones** | Encontrar patrones exactos en los abstracts con KMP, Boyer–Moore y Rabin–Karp. | `rq_3/` | Estructura creada; algoritmos pendientes. |
| **4. Despliegue y documentación** | Desplegar la aplicación y entregar documentación técnica para cada requisito. | Proceso externo al repositorio. | Pendiente y fuera del código de este repositorio. |

### Métodos previstos para el requisito 1

- **Clásicos:** Jaccard, Dice, Levenshtein normalizado y coseno con TF-IDF.
- **IA:** Word2Vec y FastText con modelos preentrenados.

Los archivos de algoritmos actuales son solo marcadores vacíos con una descripción; no contienen implementaciones.

## Estructura

```text
data/
├── raw/                         # Los 20 PDF originales
└── processed/
    ├── articles.json            # Abstracts y metadatos
    └── results/                 # Resultados futuros por requisito
utils/
├── corpus.py                    # Crear y cargar el catálogo
├── pdf_extractor.py             # Extraer información de los PDF
└── text_processing.py           # Normalizar y tokenizar texto
rq_1/
├── classic/                     # Jaccard, Dice, Levenshtein, TF-IDF
└── ai/                          # Word2Vec y FastText
rq_2/
├── clustering/                  # Linkage jerárquico
├── evaluation/                  # Métrica interna
└── visualization/               # Dendrogramas
rq_3/                            # KMP, Boyer–Moore y Rabin–Karp
tests/                           # Espacio para pruebas futuras por requisito
```

Se usa `rq_1`, `rq_2` y `rq_3` con guion bajo para que sean paquetes importables de Python. Los algoritmos Counting Sort, Radix Sort y Bucket Sort del proyecto vecino no se incluyen: ordenan términos por frecuencia y no cumplen estos requisitos.

## Preparar el corpus

Se requiere Python 3.11 o posterior. Desde la raíz del proyecto, en PowerShell:

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
python -m pip install -e .
python -m utils.corpus
```

El último comando vuelve a extraer los abstracts desde `data/raw/` y genera `data/processed/articles.json`. La extracción puede tardar; no hace falta repetirla hasta que cambien los PDF.

Todavía no hay un punto de entrada para ejecutar la aplicación ni pruebas de los requisitos. Esas partes se agregarán junto con sus implementaciones.

## Decisiones importantes

- `data/raw/` contiene datos que consume el programa. `data/processed/` contiene el catálogo y resultados generados; los resultados se ignoran en Git.
- El extractor se reutilizó del proyecto vecino porque ya procesa los 20 PDF. Es la parte más compleja por las diferencias de formato entre artículos; está separada de los algoritmos.
- El código nuevo debe usar nombres claros y cálculos explícitos. En el requisito 3 no se permiten funciones nativas como `find()` o `index()` para resolver la búsqueda.
- Los análisis técnicos, la declaración del uso de IA y el despliegue se gestionan fuera de este repositorio.
