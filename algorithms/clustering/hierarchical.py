"""Funciones comunes para construir agrupamientos jerárquicos."""

from itertools import combinations

from algorithms.similarity.tfidf_cosine import cosine_similarity


def pairwise_cosine_distances(vectors):
    """Calcula la matriz simétrica de distancias coseno."""
    matrix = [[0.0 for _ in vectors] for _ in vectors]

    for first_index, second_index in combinations(range(len(vectors)), 2):
        similarity = cosine_similarity(vectors[first_index], vectors[second_index])
        distance = 1 - similarity
        matrix[first_index][second_index] = distance
        matrix[second_index][first_index] = distance

    return matrix


def hierarchical_clustering(distance_matrix, cluster_distance):
    """Une los grupos más cercanos usando el criterio de enlace recibido."""
    item_count = len(distance_matrix)
    active_clusters = [(index, (index,)) for index in range(item_count)]
    merges = []

    while len(active_clusters) > 1:
        best_pair = None
        best_distance = float("inf")

        for first_position in range(len(active_clusters)):
            for second_position in range(first_position + 1, len(active_clusters)):
                first_id, first_members = active_clusters[first_position]
                second_id, second_members = active_clusters[second_position]
                distance = cluster_distance(
                    first_members, second_members, distance_matrix
                )

                # En caso de empate se conserva el primer par para resultados estables.
                if distance < best_distance:
                    best_distance = distance
                    best_pair = (first_position, second_position)

        first_position, second_position = best_pair
        left_id, left_members = active_clusters[first_position]
        right_id, right_members = active_clusters[second_position]
        merged_members = tuple(sorted(left_members + right_members))
        new_id = item_count + len(merges)

        merges.append(
            {
                "left_id": left_id,
                "right_id": right_id,
                "new_id": new_id,
                "distance": best_distance,
                "members": merged_members,
            }
        )

        active_clusters = [
            cluster
            for position, cluster in enumerate(active_clusters)
            if position not in (first_position, second_position)
        ]
        active_clusters.append((new_id, merged_members))

    return merges
