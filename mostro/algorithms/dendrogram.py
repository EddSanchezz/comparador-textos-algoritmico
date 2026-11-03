"""Dibujo manual de dendrogramas a partir del historial de uniones."""

import matplotlib.pyplot as plt


def draw_dendrogram(article_names, merges, title):
    """Dibuja el árbol y ordena las hojas según sus uniones."""
    figure, axis = plt.subplots(figsize=(max(12, len(article_names) * 0.8), 7))
    merge_by_id = {merge["new_id"]: merge for merge in merges}
    node_positions = {}
    leaf_order = []

    def place_node(node_id):
        """Ubica cada hoja y cada unión en el gráfico."""
        if node_id < len(article_names):
            x_position = len(leaf_order)
            leaf_order.append(node_id)
            node_positions[node_id] = (x_position, 0.0)
            return x_position

        merge = merge_by_id[node_id]
        left_x = place_node(merge["left_id"])
        right_x = place_node(merge["right_id"])
        x_position = (left_x + right_x) / 2
        node_positions[node_id] = (x_position, merge["distance"])
        return x_position

    if merges:
        place_node(merges[-1]["new_id"])

    for merge in merges:
        left_x, left_height = node_positions[merge["left_id"]]
        right_x, right_height = node_positions[merge["right_id"]]
        merge_height = merge["distance"]

        axis.plot([left_x, left_x], [left_height, merge_height], color="#386cb0")
        axis.plot([right_x, right_x], [right_height, merge_height], color="#386cb0")
        axis.plot([left_x, right_x], [merge_height, merge_height], color="#386cb0")

    short_names = []
    for article_index in leaf_order:
        name = article_names[article_index]
        if len(name) > 36:
            name = name[:33] + "..."
        short_names.append(name)

    axis.set_xticks(range(len(short_names)))
    axis.set_xticklabels(short_names, rotation=55, ha="right", fontsize=7)
    axis.set_ylabel("Distancia coseno")
    axis.set_title(title)
    axis.grid(axis="y", alpha=0.2)
    figure.subplots_adjust(bottom=0.38, top=0.9)
    return figure
