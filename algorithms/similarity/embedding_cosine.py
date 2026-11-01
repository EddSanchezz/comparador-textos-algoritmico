"""Similitud coseno entre embeddings densos."""

from math import sqrt


def embedding_cosine_similarity(first_vector, second_vector):
    """Calcula la similitud coseno entre dos embeddings."""
    dot_product = sum(first * second for first, second in zip(first_vector, second_vector))
    first_length = sqrt(sum(value * value for value in first_vector))
    second_length = sqrt(sum(value * value for value in second_vector))

    if first_length == 0 or second_length == 0:
        return 0.0

    return dot_product / (first_length * second_length)
