"""Carga y preparación del catálogo de artículos del corpus."""

import json
from pathlib import Path

from utils.pdf_extractor import extract_all_from_directory

PROJECT_DIRECTORY = Path(__file__).resolve().parents[1]
RAW_PDF_DIRECTORY = PROJECT_DIRECTORY / "data" / "raw"
PROCESSED_DIRECTORY = PROJECT_DIRECTORY / "data" / "processed"
CATALOG_PATH = PROCESSED_DIRECTORY / "articles.json"


def build_catalog(
    pdf_directory: Path = RAW_PDF_DIRECTORY,
    catalog_path: Path = CATALOG_PATH,
) -> list[dict]:
    """Extrae los datos de los PDF y guarda el catálogo como JSON."""
    pdf_directory = Path(pdf_directory)
    catalog_path = Path(catalog_path)

    if not pdf_directory.is_dir():
        raise FileNotFoundError(f"No existe la carpeta de PDF: {pdf_directory}")

    records = extract_all_from_directory(pdf_directory)
    if not records:
        raise FileNotFoundError(f"No se encontraron archivos PDF en: {pdf_directory}")

    catalog_path.parent.mkdir(parents=True, exist_ok=True)
    with catalog_path.open("w", encoding="utf-8") as catalog_file:
        json.dump(records, catalog_file, ensure_ascii=False, indent=2)

    return records


def load_catalog(catalog_path: Path = CATALOG_PATH) -> list[dict]:
    """Lee el catálogo JSON generado desde los PDF."""
    catalog_path = Path(catalog_path)
    if not catalog_path.is_file():
        raise FileNotFoundError(
            f"No existe el catálogo: {catalog_path}. "
            "Créalo con `python -m utils.prepare_corpus`."
        )

    with catalog_path.open("r", encoding="utf-8") as catalog_file:
        records = json.load(catalog_file)

    if not isinstance(records, list):
        raise ValueError("El catálogo debe contener una lista de artículos.")

    return records
