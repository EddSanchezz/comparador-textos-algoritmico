"""Paquete de extracción de información de PDFs."""
from .pdf_extractor import (
    extract_pdf,
    extract_all_from_directory,
    validate_extraction,
)

__all__ = ["extract_pdf", "extract_all_from_directory", "validate_extraction"]
