"""Agrupamiento jerárquico Single Linkage."""

from algorithms.clustering.hierarchical import hierarchical_clustering


def single_linkage_distance(first_members, second_members, distance_matrix):
    """Usa la menor distancia entre los elementos de dos grupos."""
    distances = [
        distance_matrix[first][second]
        for first in first_members
        for second in second_members
    ]
    return min(distances)


def single_linkage(distance_matrix):
    """Construye el árbol jerárquico usando Single Linkage."""
    return hierarchical_clustering(distance_matrix, single_linkage_distance)
