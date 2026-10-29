"""Comando para extraer los abstracts y metadatos de los PDF."""

from utils.corpus import build_catalog
from utils.pdf_extractor import validate_extraction


def main() -> None:
    records = build_catalog()
    abstracts_found = 0

    for record in records:
        if record["abstract"]:
            abstracts_found += 1
        for warning in record["warnings"]:
            print(f"Advertencia en {record['file']}: {warning}")

    for problem in validate_extraction(records):
        print(f"Problema de validación: {problem}")

    print(f"PDF encontrados: {len(records)}")
    print(f"Abstracts extraídos: {abstracts_found}")
    print("Catálogo guardado en data/processed/articles.json")


if __name__ == "__main__":
    main()
