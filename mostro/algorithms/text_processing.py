"""Funciones sencillas para preparar texto antes del análisis."""


def tokenize(text):
    """Separa el texto en palabras minúsculas sin usar expresiones regulares."""
    words = []
    current_word = []

    for character in text.lower():
        if character.isalnum():
            current_word.append(character)
        elif current_word:
            words.append("".join(current_word))
            current_word = []

    if current_word:
        words.append("".join(current_word))

    return words
