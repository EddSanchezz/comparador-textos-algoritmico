"""Agrupamiento jerárquico Complete Linkage."""

from algorithms.clustering.hierarchical import hierarchical_clustering


def complete_linkage_distance(first_members, second_members, distance_matrix):
    """Usa la mayor distancia entre los elementos de dos grupos."""
    distances = [
        distance_matrix[first][second]
        for first in first_members
        for second in second_members
    ]
    return max(distances)


def complete_linkage(distance_matrix):
    """Construye el árbol jerárquico usando Complete Linkage."""
    return hierarchical_clustering(distance_matrix, complete_linkage_distance)
