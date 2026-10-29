"""Normalización y separación sencilla de palabras."""

import unicodedata

STOP_WORDS = {
    "a", "about", "after", "again", "against", "all", "also", "am", "an",
    "and", "any", "are", "as", "at", "be", "because", "been", "before",
    "being", "below", "between", "both", "but", "by", "can", "could",
    "did", "do", "does", "doing", "down", "during", "each", "few", "for",
    "from", "further", "had", "has", "have", "having", "he", "her", "here",
    "hers", "him", "his", "how", "i", "if", "in", "into", "is", "it", "its",
    "just", "me", "more", "most", "my", "no", "nor", "not", "now", "of",
    "off", "on", "once", "only", "or", "other", "our", "ours", "out", "over",
    "own", "same", "she", "should", "so", "some", "such", "than", "that",
    "the", "their", "them", "then", "there", "these", "they", "this", "those",
    "through", "to", "too", "under", "until", "up", "very", "was", "we",
    "were", "what", "when", "where", "which", "while", "who", "whom", "why",
    "with", "would", "you", "your",
}

WORD_JOINERS = {"-", "'", "’"}


def normalize_text(text: str) -> str:
    """Pasa el texto a minúsculas y normaliza sus caracteres Unicode."""
    return unicodedata.normalize("NFC", text.lower())


def tokenize_text(text: str, remove_stop_words: bool = False) -> list[str]:
    """Separa palabras con un recorrido simple, sin expresiones regulares."""
    normalized_text = normalize_text(text)
    words = []
    current_word = []

    for character in normalized_text:
        if character.isalpha():
            current_word.append(character)
        elif character in WORD_JOINERS and current_word:
            current_word.append(character)
        else:
            add_word(words, current_word, remove_stop_words)
            current_word = []

    add_word(words, current_word, remove_stop_words)
    return words


def add_word(words: list[str], current_word: list[str], remove_stop_words: bool) -> None:
    """Agrega la palabra actual si no está vacía ni se debe omitir."""
    word = "".join(current_word).strip("-'’")
    if not word:
        return
    if remove_stop_words and word in STOP_WORDS:
        return
    words.append(word)
