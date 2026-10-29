"""Normaliza abstracts y los separa en palabras."""

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


def normalize_text(text):
    """Pasa el texto a minúsculas y conserva sus acentos."""
    return unicodedata.normalize("NFC", text.lower())


def tokenize_text(text, remove_stop_words=False):
    """Separa palabras con un recorrido de caracteres, sin expresiones regulares."""
    words = []
    current_word = ""

    for character in normalize_text(text):
        if character.isalpha() or (character in "-'’" and current_word):
            current_word += character
        elif current_word:
            word = current_word.strip("-'’")
            if word and (not remove_stop_words or word not in STOP_WORDS):
                words.append(word)
            current_word = ""

    if current_word:
        word = current_word.strip("-'’")
        if word and (not remove_stop_words or word not in STOP_WORDS):
            words.append(word)

    return words
