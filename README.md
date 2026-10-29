# Comparador de textos algorítmico

Proyecto académico para comparar abstracts de artículos científicos sobre inteligencia artificial generativa. El desarrollo comienza con el requisito 1: análisis de similitud textual. **Los algoritmos de similitud todavía no están implementados.**

## Estructura

```text
data/
├── raw/                 # PDF originales del corpus
└── processed/
    ├── articles.json    # Abstracts y metadatos extraídos de los PDF
    └── results/         # Resultados y gráficas generados por la aplicación
docs/                    # Guías y documentos del proyecto
utils/                   # Extracción del corpus y procesamiento de texto
rq_1/                    # Código del requisito 1
├── classic/             # Algoritmos clásicos (pendientes)
└── ai/                  # Enfoques con embeddings (pendientes)
tests/                   # Pruebas de las utilidades
```

`rq_1` usa guion bajo para que Python pueda importarlo como paquete. Los ordenamientos Counting Sort, Radix Sort y Bucket Sort del proyecto `algoritmos-seguimiento-1` no se incluyen: ordenan términos por frecuencia y no calculan similitud entre abstracts.

## Requisito 1

El requisito pide elegir dos o más artículos y comparar sus abstracts con cuatro algoritmos clásicos y dos enfoques basados en embeddings. La propuesta acordada es:

- Clásicos: Jaccard, Dice, Levenshtein normalizado y coseno con TF-IDF.
- IA: Word2Vec y FastText, usando vectores preentrenados.

Estos seis métodos aún están pendientes. El extractor y la preparación del corpus ya están disponibles en `utils/`.

## Preparar el proyecto

Se requiere Python 3.11 o posterior.

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
python -m pip install -e .
```

Extraer el catálogo de abstracts y metadatos desde los PDF:

```powershell
python -m utils.prepare_corpus
```

El comando guarda los registros en `data/processed/articles.json` y muestra advertencias de extracción. La lectura y extracción de PDF toma más tiempo que cargar el catálogo; para regenerarlo, vuelve a ejecutar el comando.

Ejecutar las pruebas de las utilidades:

```powershell
python -m unittest discover -s tests -v
```

## Datos y documentos

- `data/raw/` contiene los 20 artículos PDF originales copiados desde `algoritmos-seguimiento-1/data/raw/`.
- `data/processed/articles.json` se genera a partir de esos PDF y conserva ID, nombre de archivo, título, autores, abstract y advertencias.
- `data/processed/results/` queda reservado para salidas futuras; sus archivos generados no se versionan.
- `docs/Presentacion.pdf` contiene el documento de descripción del proyecto y sus requisitos.

El extractor de PDF se tomó del proyecto vecino y se mantiene aislado en `utils/pdf_extractor/`. El procesamiento de similitud se implementará aparte, de forma explícita y fácil de revisar.
