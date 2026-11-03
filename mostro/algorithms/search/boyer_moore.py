"""Búsqueda Boyer-Moore con la regla del carácter incorrecto."""


def boyer_moore_search(text, pattern):
    """Busca apariciones y desplaza el patrón según el carácter que no coincide."""
    if not pattern or len(pattern) > len(text):
        return []

    # Guarda la última posición de cada carácter del patrón.
    last_position = {}
    for index, character in enumerate(pattern):
        last_position[character] = index

    matches = []
    shift = 0
    last_start = len(text) - len(pattern)

    while shift <= last_start:
        pattern_index = len(pattern) - 1

        while pattern_index >= 0 and pattern[pattern_index] == text[shift + pattern_index]:
            pattern_index -= 1

        if pattern_index < 0:
            matches.append(shift)
            shift += 1
        else:
            mismatched_character = text[shift + pattern_index]
            previous_position = last_position.get(mismatched_character, -1)
            shift += max(1, pattern_index - previous_position)

    return matches
