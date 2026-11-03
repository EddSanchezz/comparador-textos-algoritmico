"""Búsqueda Rabin-Karp con hash rodante."""


def rabin_karp_search(text, pattern):
    """Busca el patrón con hash rodante y verifica cada posible coincidencia."""
    if not pattern or len(pattern) > len(text):
        return []

    base = 256
    modulus = 1_000_000_007
    pattern_length = len(pattern)
    highest_place = pow(base, pattern_length - 1, modulus)

    pattern_hash = 0
    window_hash = 0
    for index in range(pattern_length):
        pattern_hash = (pattern_hash * base + ord(pattern[index])) % modulus
        window_hash = (window_hash * base + ord(text[index])) % modulus

    matches = []
    last_start = len(text) - pattern_length

    for start in range(last_start + 1):
        if pattern_hash == window_hash:
            # Dos cadenas pueden compartir hash; se comparan los caracteres reales.
            if text[start : start + pattern_length] == pattern:
                matches.append(start)

        if start < last_start:
            outgoing_value = ord(text[start]) * highest_place
            window_hash = (window_hash - outgoing_value) % modulus
            window_hash = (window_hash * base + ord(text[start + pattern_length])) % modulus

    return matches
