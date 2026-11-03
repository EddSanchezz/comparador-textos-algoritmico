"""Vectorización TF-IDF explícita para abstracts."""

from collections import Counter
from math import log

from algorithms.text_processing import tokenize


def create_tfidf_vectors(texts):
    """Construye un vector disperso TF-IDF para cada texto."""
    documents = [tokenize(text) for text in texts]
    document_count = len(documents)
    document_frequency = Counter()

    for words in documents:
        document_frequency.update(set(words))

    vectors = []
    for words in documents:
        word_counts = Counter(words)
        word_total = len(words)
        vector = {}

        if word_total:
            for word, count in word_counts.items():
                term_frequency = count / word_total
                inverse_document_frequency = log(
                    (document_count + 1) / (document_frequency[word] + 1)
                ) + 1
                vector[word] = term_frequency * inverse_document_frequency

        vectors.append(vector)

    return vectors
