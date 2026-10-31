# Análisis de abstracts científicos

Aplicación local en Streamlit para cargar artículos científicos en PDF, revisar
sus abstracts y comparar su similitud.

## Funciones

- Carga automática de los PDFs de la carpeta `pdfs/`.
- Carga manual de otros PDFs desde la interfaz.
- Extracción y corrección del título, los autores y el abstract.
- Similitud entre abstracts con vectores TF-IDF:
  - Similitud coseno.
  - Similitud basada en la distancia euclidiana.

## Instalación y uso

Requiere Python 3.14.

```bat
iniciar.bat
```

El script instala las dependencias y abre la aplicación en el navegador. También
se puede iniciar manualmente:

```bat
py -3.14 -m pip install -r requirements.txt
py -3.14 -m streamlit run app.py
```

## Estructura

```
app.py                     Interfaz de la aplicación
pdf_reader.py              Extracción de datos desde los PDFs
algorithms/text_processing.py   Separación del texto en palabras
algorithms/similarity/     Medidas de similitud
pdfs/                      Corpus de artículos
tests/                     Pruebas automáticas
```

## Pruebas

```bat
py -3.14 -m unittest discover -s tests -v
```
