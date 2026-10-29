import json
import tempfile
import unittest
from pathlib import Path

from utils.corpus import load_catalog


class CorpusTests(unittest.TestCase):
    def test_load_catalog_reads_article_records(self):
        records = [{"id": 1, "abstract": "text example"}]

        with tempfile.TemporaryDirectory() as temporary_directory:
            catalog_path = Path(temporary_directory) / "articles.json"
            catalog_path.write_text(json.dumps(records), encoding="utf-8")

            self.assertEqual(load_catalog(catalog_path), records)

    def test_load_catalog_explains_how_to_create_missing_catalog(self):
        missing_path = Path("catalog-that-does-not-exist.json")

        with self.assertRaisesRegex(FileNotFoundError, "utils.prepare_corpus"):
            load_catalog(missing_path)


if __name__ == "__main__":
    unittest.main()
