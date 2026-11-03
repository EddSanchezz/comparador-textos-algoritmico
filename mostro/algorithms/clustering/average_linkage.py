"""Agrupamiento jerárquico Average Linkage."""

from algorithms.clustering.hierarchical import hierarchical_clustering


def average_linkage_distance(first_members, second_members, distance_matrix):
    """Usa el promedio de las distancias entre dos grupos."""
    distances = [
        distance_matrix[first][second]
        for first in first_members
        for second in second_members
    ]
    return sum(distances) / len(distances)


def average_linkage(distance_matrix):
    """Construye el árbol jerárquico usando Average Linkage."""
    return hierarchical_clustering(distance_matrix, average_linkage_distance)
