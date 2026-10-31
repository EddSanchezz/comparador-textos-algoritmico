import unittest

from algorithms.similarity.tfidf import create_tfidf_vectors
from algorithms.similarity.tfidf_cosine import cosine_similarity
from algorithms.similarity.tfidf_euclidean import euclidean_similarity


class SimilarityTests(unittest.TestCase):
    def test_tfidf_cosine(self):
        vectors = create_tfidf_vectors(["red blue", "red blue", "green"])
        self.assertAlmostEqual(1.0, cosine_similarity(vectors[0], vectors[1]))
        self.assertAlmostEqual(0.0, cosine_similarity(vectors[0], vectors[2]))

    def test_tfidf_euclidean(self):
        vectors = create_tfidf_vectors(["red blue", "red blue"])
        self.assertEqual(1.0, euclidean_similarity(vectors[0], vectors[1]))


if __name__ == "__main__":
    unittest.main()
