"""Similitud basada en distancia euclidiana entre embeddings densos."""

from math import sqrt

from algorithms.similarity.common import distance_similarity


def embedding_euclidean_similarity(first_vector, second_vector):
    """Convierte la distancia entre embeddings en una similitud de cero a uno."""
    squared_distance = sum(
        (first - second) ** 2 for first, second in zip(first_vector, second_vector)
    )
    distance = sqrt(squared_distance)
    return distance_similarity(distance)
