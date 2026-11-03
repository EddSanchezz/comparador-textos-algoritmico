"""Similitud coseno entre vectores dispersos TF-IDF."""

from math import sqrt


def cosine_similarity(first_vector, second_vector):
    """Calcula el coseno del ángulo entre dos vectores dispersos."""
    first_length = sqrt(sum(value * value for value in first_vector.values()))
    second_length = sqrt(sum(value * value for value in second_vector.values()))

    if first_length == 0 or second_length == 0:
        return 0.0

    smaller, larger = first_vector, second_vector
    if len(smaller) > len(larger):
        smaller, larger = larger, smaller

    dot_product = sum(value * larger.get(word, 0.0) for word, value in smaller.items())
    return dot_product / (first_length * second_length)
