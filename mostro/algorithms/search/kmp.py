"""Búsqueda de cadenas Knuth-Morris-Pratt."""


def kmp_search(text, pattern):
    """Encuentra todas las apariciones usando prefijos y sufijos del patrón."""
    if not pattern or len(pattern) > len(text):
        return []

    # Cada posición guarda el prefijo propio más largo que también es sufijo.
    prefix_lengths = [0] * len(pattern)
    prefix_end = 0
    text_index = 1

    while text_index < len(pattern):
        if pattern[text_index] == pattern[prefix_end]:
            prefix_end += 1
            prefix_lengths[text_index] = prefix_end
            text_index += 1
        elif prefix_end:
            prefix_end = prefix_lengths[prefix_end - 1]
        else:
            text_index += 1

    matches = []
    text_index = 0
    pattern_index = 0

    while text_index < len(text):
        if text[text_index] == pattern[pattern_index]:
            text_index += 1
            pattern_index += 1

            if pattern_index == len(pattern):
                matches.append(text_index - pattern_index)
                pattern_index = prefix_lengths[pattern_index - 1]
        elif pattern_index:
            pattern_index = prefix_lengths[pattern_index - 1]
        else:
            text_index += 1

    return matches
