import unittest
from pathlib import Path

from algorithms.clustering.average_linkage import average_linkage
from algorithms.clustering.complete_linkage import complete_linkage
from algorithms.clustering.hierarchical import pairwise_cosine_distances
from algorithms.clustering.silhouette import best_silhouette_cut, clusters_at_count
from algorithms.clustering.single_linkage import single_linkage
from algorithms.similarity.tfidf import create_tfidf_vectors
from pdf_reader import extract_article


class ClusteringTests(unittest.TestCase):
    def test_three_linkage_methods_create_and_cut_a_tree(self):
        vectors = create_tfidf_vectors(
            ["apple fruit", "apple sweet", "car engine", "car wheel"]
        )
        distances = pairwise_cosine_distances(vectors)

        for cluster_method in (single_linkage, complete_linkage, average_linkage):
            merges = cluster_method(distances)
            self.assertEqual(3, len(merges))
            clusters = clusters_at_count(4, merges, 2)
            self.assertEqual(2, len(clusters))
            count, score = best_silhouette_cut(distances, merges)
            self.assertGreaterEqual(count, 2)
            self.assertLessEqual(count, 3)
            self.assertGreaterEqual(score, -1.0)
            self.assertLessEqual(score, 1.0)

    def test_three_linkage_methods_cluster_the_real_corpus(self):
        corpus_folder = Path(__file__).parent.parent / "pdfs"
        pdf_files = sorted(corpus_folder.glob("*.pdf"))
        if not pdf_files:
            self.skipTest("No PDFs are available in the pdfs folder.")

        articles = [extract_article(path.read_bytes(), path.name) for path in pdf_files]
        vectors = create_tfidf_vectors(
            [article["abstract"] for article in articles]
        )
        distances = pairwise_cosine_distances(vectors)

        for cluster_method in (single_linkage, complete_linkage, average_linkage):
            merges = cluster_method(distances)
            self.assertEqual(19, len(merges))
            cluster_count, score = best_silhouette_cut(distances, merges)
            self.assertGreaterEqual(cluster_count, 2)
            self.assertLess(cluster_count, 20)
            self.assertGreaterEqual(score, -1.0)
            self.assertLessEqual(score, 1.0)


if __name__ == "__main__":
    unittest.main()
