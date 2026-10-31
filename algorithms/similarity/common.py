"""Operaciones compartidas por las métricas de similitud."""


def distance_similarity(distance):
    """Convierte una distancia no negativa en una similitud entre cero y uno."""
    return 1 / (1 + distance)
