"""Coeficiente de Jaccard para conjuntos de palabras."""

from algorithms.text_processing import tokenize


def jaccard_similarity(first_text, second_text):
    """Divide las palabras compartidas por todas las palabras distintas."""
    first_words = set(tokenize(first_text))
    second_words = set(tokenize(second_text))
    union = first_words | second_words

    if not union:
        return 1.0

    return len(first_words & second_words) / len(union)
