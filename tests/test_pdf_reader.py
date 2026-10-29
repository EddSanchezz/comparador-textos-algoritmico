import unittest
from pathlib import Path

from pdf_reader import (
    extract_abstract,
    extract_article,
    extract_authors_after_title,
    find_title_end_line,
)


class PdfReaderTests(unittest.TestCase):
    def test_abstract_stops_at_next_section(self):
        lines = [
            "A clear article title",
            "Abstract: First sentence of the abstract.",
            "Second sentence of the abstract.",
            "Keywords: algorithms, text",
            "Introduction",
        ]
        self.assertEqual(
            "First sentence of the abstract. Second sentence of the abstract.",
            extract_abstract(lines),
        )

    def test_abstract_skips_spaced_heading_and_keywords_before_text(self):
        lines = [
            "A B S T R A C T",
            "Keywords:",
            "Artificial intelligence",
            "Higher education",
            "This study reviews artificial intelligence in higher education.",
            "1. Introduction",
        ]
        self.assertEqual(
            "This study reviews artificial intelligence in higher education.",
            extract_abstract(lines),
        )

    def test_author_names_are_read_after_a_wrapped_title(self):
        lines = [
            "Article title about",
            "simple algorithms",
            "Author One, Author Two",
            "Department of Computer Science",
            "Abstract",
        ]
        title = "Article title about simple algorithms"
        self.assertEqual(1, find_title_end_line(lines, title))
        self.assertEqual("Author One, Author Two", extract_authors_after_title(lines, title))

    def test_all_twenty_pdfs_have_an_abstract_and_article_details(self):
        corpus_folder = Path(__file__).parent.parent / "pdfs"
        pdf_files = sorted(corpus_folder.glob("*.pdf"))
        if not pdf_files:
            self.skipTest("No PDFs are available in the pdfs folder.")

        articles = [extract_article(path.read_bytes(), path.name) for path in pdf_files]
        self.assertEqual(20, len(articles))
        for article in articles:
            word_count = len(article["abstract"].split())
            self.assertGreaterEqual(word_count, 30, article["filename"])
            self.assertLessEqual(word_count, 900, article["filename"])
            self.assertTrue(article["title"], article["filename"])
            self.assertTrue(article["authors"], article["filename"])
            self.assertNotIn("proof", article["title"].lower())
            self.assertNotIn("\ufeff", article["authors"])


if __name__ == "__main__":
    unittest.main()
