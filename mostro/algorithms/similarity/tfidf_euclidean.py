"""Similitud basada en distancia euclidiana entre vectores TF-IDF."""

from math import sqrt

from algorithms.similarity.common import distance_similarity


def euclidean_distance(first_vector, second_vector):
    """Calcula la distancia euclidiana entre dos vectores dispersos."""
    all_words = set(first_vector) | set(second_vector)
    squared_differences = sum(
        (first_vector.get(word, 0.0) - second_vector.get(word, 0.0)) ** 2
        for word in all_words
    )
    return sqrt(squared_differences)


def euclidean_similarity(first_vector, second_vector):
    """Convierte la distancia euclidiana TF-IDF en una similitud de cero a uno."""
    distance = euclidean_distance(first_vector, second_vector)
    return distance_similarity(distance)
