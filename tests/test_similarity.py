import unittest

from algorithms.similarity.embedding_cosine import embedding_cosine_similarity
from algorithms.similarity.embedding_euclidean import embedding_euclidean_similarity
from algorithms.similarity.jaccard import jaccard_similarity
from algorithms.similarity.levenshtein import levenshtein_similarity
from algorithms.similarity.tfidf import create_tfidf_vectors
from algorithms.similarity.tfidf_cosine import cosine_similarity
from algorithms.similarity.tfidf_euclidean import euclidean_similarity


class SimilarityTests(unittest.TestCase):
    def test_tfidf_cosine_and_jaccard(self):
        vectors = create_tfidf_vectors(["red blue", "red blue", "green"])
        self.assertAlmostEqual(1.0, cosine_similarity(vectors[0], vectors[1]))
        self.assertAlmostEqual(0.0, cosine_similarity(vectors[0], vectors[2]))
        self.assertEqual(0.0, jaccard_similarity("red blue", "green"))

    def test_levenshtein_similarity(self):
        self.assertEqual(1.0, levenshtein_similarity("same text", "same text"))
        self.assertEqual(0.0, levenshtein_similarity("one", "two"))
        self.assertEqual(1.0, levenshtein_similarity("", ""))

    def test_tfidf_euclidean(self):
        vectors = create_tfidf_vectors(["red blue", "red blue"])
        self.assertEqual(1.0, euclidean_similarity(vectors[0], vectors[1]))

    def test_embedding_measures(self):
        self.assertAlmostEqual(1.0, embedding_cosine_similarity([1.0, 0.0], [1.0, 0.0]))
        self.assertAlmostEqual(0.0, embedding_cosine_similarity([1.0, 0.0], [0.0, 1.0]))
        self.assertEqual(1.0, embedding_euclidean_similarity([1.0, 0.0], [1.0, 0.0]))


if __name__ == "__main__":
    unittest.main()
