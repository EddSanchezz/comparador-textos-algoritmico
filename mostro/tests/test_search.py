import unittest
from itertools import product
from pathlib import Path

from algorithms.search.boyer_moore import boyer_moore_search
from algorithms.search.kmp import kmp_search
from algorithms.search.rabin_karp import rabin_karp_search
from pdf_reader import extract_article


class StringSearchTests(unittest.TestCase):
    def test_all_algorithms_find_overlapping_matches(self):
        text = "abababa"
        expected = [0, 2, 4]
        self.assertEqual(expected, kmp_search(text, "aba"))
        self.assertEqual(expected, boyer_moore_search(text, "aba"))
        self.assertEqual(expected, rabin_karp_search(text, "aba"))

    def test_search_missing_or_empty_pattern(self):
        for search in (kmp_search, boyer_moore_search, rabin_karp_search):
            self.assertEqual([], search("text", "missing"))
            self.assertEqual([], search("text", ""))

    def test_search_algorithms_match_small_brute_force_cases(self):
        def all_positions(text, pattern):
            if not pattern:
                return []
            return [
                start
                for start in range(len(text) - len(pattern) + 1)
                if text[start : start + len(pattern)] == pattern
            ]

        sample_texts = [
            "".join(characters)
            for length in range(6)
            for characters in product("ab", repeat=length)
        ]
        sample_patterns = [
            "".join(characters)
            for length in range(1, 4)
            for characters in product("ab", repeat=length)
        ]

        for text in sample_texts:
            for pattern in sample_patterns:
                expected = all_positions(text, pattern)
                self.assertEqual(expected, kmp_search(text, pattern))
                self.assertEqual(expected, boyer_moore_search(text, pattern))
                self.assertEqual(expected, rabin_karp_search(text, pattern))

    def test_search_algorithms_agree_on_real_abstracts(self):
        corpus_folder = Path(__file__).parent.parent / "pdfs"
        pdf_files = sorted(corpus_folder.glob("*.pdf"))
        if not pdf_files:
            self.skipTest("No PDFs are available in the pdfs folder.")

        articles = [extract_article(path.read_bytes(), path.name) for path in pdf_files]
        pattern = "artificial intelligence"

        for article in articles:
            text = article["abstract"].lower()
            expected = kmp_search(text, pattern)
            self.assertEqual(expected, boyer_moore_search(text, pattern))
            self.assertEqual(expected, rabin_karp_search(text, pattern))


if __name__ == "__main__":
    unittest.main()
