import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from app import search, indexed_search


class MatchTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name) / 'docs'
        self.root.mkdir()
        (self.root / 'notes.md').write_text('red blue\nred\nblue\nRED, blue red\nStraße café\n', encoding='utf-8')
        self.db = Path(self.temp.name) / 'index.sqlite3'

    def tearDown(self):
        self.temp.cleanup()

    def test_all_requires_same_line_not_whole_document(self):
        results = search(self.root, 'red blue', match='all')
        self.assertEqual([r['line'] for r in results], [1, 4])
        self.assertTrue(all(r['score'] == 1 for r in results))

    def test_default_any_is_backwards_compatible(self):
        results = search(self.root, 'red blue')
        self.assertEqual([r['line'] for r in results], [1, 4, 2, 3])

    def test_case_punctuation_duplicates_and_unicode(self):
        self.assertEqual(search(self.root, 'RED red, BLUE', match='all'), search(self.root, 'red blue', match='all'))
        self.assertEqual(search(self.root, 'STRASSE CAFÉ', match='all')[0]['line'], 5)

    def test_partial_results_excluded_and_no_phrase_semantics(self):
        self.assertEqual(search(self.root, 'red green', match='all'), [])
        self.assertEqual(len(search(self.root, 'blue red', match='all')), 2)

    def test_indexed_modes_match_direct_and_refresh(self):
        for mode in ['any', 'all']:
            self.assertEqual(search(self.root, 'red blue', match=mode), indexed_search(self.root, 'red blue', self.db, match=mode))
        (self.root / 'new.txt').write_text('red blue')
        self.assertEqual(len(indexed_search(self.root, 'red blue', self.db, match='all')), 3)

    def test_invalid_arguments_fail_before_creating_index(self):
        for options in [dict(match='phrase'), dict(limit=True), dict(limit=1.5), dict(limit=0)]:
            with self.assertRaises(ValueError):
                indexed_search(self.root, 'red', self.db, **options)
        self.assertFalse(self.db.exists())

    def test_cli_all_mode_json_and_markdown(self):
        command = [sys.executable, 'app.py', str(self.root), 'red blue', '--match', 'all', '--index', str(self.db)]
        result = subprocess.run(command, capture_output=True, text=True, check=True)
        self.assertEqual(len(json.loads(result.stdout)), 2)
        report = subprocess.run(command + ['--format', 'markdown'], capture_output=True, text=True, check=True)
        self.assertIn('2 matching line(s)', report.stdout)
