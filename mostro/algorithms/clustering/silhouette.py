"""Cálculo del coeficiente Silhouette y selección del corte del dendrograma."""


def clusters_at_count(item_count, merges, desired_count):
    """Corta el árbol y devuelve los grupos para la cantidad solicitada."""
    active_clusters = {index: {index} for index in range(item_count)}

    for merge in merges:
        if len(active_clusters) <= desired_count:
            break
        left_members = active_clusters.pop(merge["left_id"])
        right_members = active_clusters.pop(merge["right_id"])
        active_clusters[merge["new_id"]] = left_members | right_members

    return list(active_clusters.values())


def silhouette_score(distance_matrix, clusters):
    """Calcula el promedio Silhouette con una matriz de distancias."""
    if len(clusters) < 2:
        return 0.0

    item_cluster = {}
    for cluster_index, members in enumerate(clusters):
        for item_index in members:
            item_cluster[item_index] = cluster_index

    scores = []
    for item_index in range(len(distance_matrix)):
        own_cluster = clusters[item_cluster[item_index]]

        if len(own_cluster) == 1:
            scores.append(0.0)
            continue

        own_distances = [
            distance_matrix[item_index][other_index]
            for other_index in own_cluster
            if other_index != item_index
        ]
        average_own_distance = sum(own_distances) / len(own_distances)

        nearest_other_average = float("inf")
        for other_cluster_index, other_cluster in enumerate(clusters):
            if other_cluster_index == item_cluster[item_index]:
                continue
            average_other_distance = sum(
                distance_matrix[item_index][other_index] for other_index in other_cluster
            ) / len(other_cluster)
            nearest_other_average = min(nearest_other_average, average_other_distance)

        largest_distance = max(average_own_distance, nearest_other_average)
        if largest_distance == 0:
            scores.append(0.0)
        else:
            scores.append(
                (nearest_other_average - average_own_distance) / largest_distance
            )

    return sum(scores) / len(scores)


def best_silhouette_cut(distance_matrix, merges):
    """Selecciona el corte con el coeficiente Silhouette más alto."""
    item_count = len(distance_matrix)
    if item_count <= 2:
        # Con dos elementos no se puede comparar grupos con más de un elemento.
        return item_count, 0.0

    best_count = 2
    best_score = float("-inf")

    for cluster_count in range(2, item_count):
        clusters = clusters_at_count(item_count, merges, cluster_count)
        score = silhouette_score(distance_matrix, clusters)
        if score > best_score:
            best_count = cluster_count
            best_score = score

    return best_count, best_score
