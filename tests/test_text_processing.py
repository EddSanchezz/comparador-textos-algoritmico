import unittest

from utils.text_processing import normalize_text, tokenize_text


class TextProcessingTests(unittest.TestCase):
    def test_normalize_text_lowercases_and_preserves_accents(self):
        self.assertEqual(normalize_text("ÁI IN EDUCATION"), "ái in education")

    def test_tokenize_text_keeps_hyphens_and_apostrophes(self):
        words = tokenize_text("AI-driven systems aren't ready in 2025.")
        self.assertEqual(words, ["ai-driven", "systems", "aren't", "ready", "in"])

    def test_tokenize_text_can_remove_common_words(self):
        words = tokenize_text("AI is useful for education", remove_stop_words=True)
        self.assertEqual(words, ["ai", "useful", "education"])


if __name__ == "__main__":
    unittest.main()
