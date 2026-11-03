"""Similitud de Levenshtein calculada con programación dinámica."""

from algorithms.text_processing import tokenize


def levenshtein_similarity(first_text, second_text):
    """Compara secuencias de palabras con inserciones, borrados y reemplazos."""
    first_words = tokenize(first_text)
    second_words = tokenize(second_text)

    if not first_words and not second_words:
        return 1.0

    # La secuencia más corta ocupa la fila para reducir el uso de memoria.
    if len(first_words) < len(second_words):
        first_words, second_words = second_words, first_words

    previous_row = list(range(len(second_words) + 1))

    for first_index, first_word in enumerate(first_words, start=1):
        current_row = [first_index]
        for second_index, second_word in enumerate(second_words, start=1):
            insert_cost = current_row[second_index - 1] + 1
            delete_cost = previous_row[second_index] + 1
            replace_cost = previous_row[second_index - 1]
            if first_word != second_word:
                replace_cost += 1
            current_row.append(min(insert_cost, delete_cost, replace_cost))
        previous_row = current_row

    longest_text = max(len(first_words), len(second_words))
    return 1 - previous_row[-1] / longest_text
