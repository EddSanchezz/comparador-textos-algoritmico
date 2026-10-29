# Análisis de abstracts científicos

Aplicación local en Streamlit para cargar artículos científicos en PDF y revisar
los datos extraídos de cada uno.

## Funciones

- Carga automática de los PDFs de la carpeta `pdfs/`.
- Carga manual de otros PDFs desde la interfaz.
- Extracción del título, los autores y el abstract.
- Corrección manual del título, los autores y el abstract.

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
app.py           Interfaz de la aplicación
pdf_reader.py    Extracción de datos desde los PDFs
pdfs/            Corpus de artículos
tests/           Pruebas automáticas
```

## Pruebas

```bat
py -3.14 -m unittest discover -s tests -v
```
