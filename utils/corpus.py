"""Prepara y carga los abstracts del corpus."""

import json
from pathlib import Path

from utils.pdf_extractor import extract_all_from_directory, validate_extraction

PROJECT_DIRECTORY = Path(__file__).resolve().parents[1]
PDF_DIRECTORY = PROJECT_DIRECTORY / "data" / "raw"
CATALOG_PATH = PROJECT_DIRECTORY / "data" / "processed" / "articles.json"


def build_catalog():
    """Extrae los artículos de los PDF y los guarda como JSON."""
    if not PDF_DIRECTORY.is_dir():
        raise FileNotFoundError(f"No existe la carpeta: {PDF_DIRECTORY}")

    articles = extract_all_from_directory(PDF_DIRECTORY)
    if not articles:
        raise FileNotFoundError(f"No hay archivos PDF en: {PDF_DIRECTORY}")

    CATALOG_PATH.parent.mkdir(parents=True, exist_ok=True)
    with CATALOG_PATH.open("w", encoding="utf-8") as catalog_file:
        json.dump(articles, catalog_file, ensure_ascii=False, indent=2)

    return articles


def load_catalog():
    """Carga los artículos que ya fueron extraídos."""
    if not CATALOG_PATH.is_file():
        raise FileNotFoundError("Ejecuta `python -m utils.corpus` para crear el catálogo.")

    with CATALOG_PATH.open("r", encoding="utf-8") as catalog_file:
        return json.load(catalog_file)


def main():
    articles = build_catalog()
    abstract_count = 0

    for article in articles:
        if article["abstract"]:
            abstract_count += 1
        for warning in article["warnings"]:
            print(f"Advertencia en {article['file']}: {warning}")

    for problem in validate_extraction(articles):
        print(f"Problema de validación: {problem}")

    print(f"PDF encontrados: {len(articles)}")
    print(f"Abstracts extraídos: {abstract_count}")
    print("Catálogo guardado en data/processed/articles.json")


if __name__ == "__main__":
    main()
