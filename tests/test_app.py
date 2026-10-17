import tempfile
import unittest
from pathlib import Path
from app import search
class Tests(unittest.TestCase):
    def test_rank_and_citation(self):
        with tempfile.TemporaryDirectory() as d:
            Path(d,'a.md').write_text('hello\nhello world\n')
            result=search(d,'HELLO world');self.assertEqual(result[0]['line'],2);self.assertEqual(result[0]['score'],1);self.assertEqual(result[0]['source'],'a.md')
    def test_skips_hidden_binary_and_symlink(self):
        with tempfile.TemporaryDirectory() as d, tempfile.TemporaryDirectory() as outside:
            Path(d,'.env.md').write_text('secret');Path(d,'file.pdf').write_text('secret')
            target=Path(outside,'note.md');target.write_text('secret');Path(d,'linked.md').symlink_to(target)
            self.assertEqual(search(d,'secret'),[])
    def test_empty_query(self):
        with tempfile.TemporaryDirectory() as d:
            with self.assertRaises(ValueError):search(d,'!!!')
    def test_limit(self):
        with tempfile.TemporaryDirectory() as d:
            Path(d,'a.txt').write_text('word\nword\nword');self.assertEqual(len(search(d,'word',1)),1)
