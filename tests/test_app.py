import tempfile
import unittest
from pathlib import Path
from app import search,indexed_search,sync_index
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


    def test_indexed_results_match_scan_and_persist(self):
        with tempfile.TemporaryDirectory() as d, tempfile.TemporaryDirectory() as cache:
            Path(d,'a.md').write_text('hello world\nhello')
            db=Path(cache)/'index.sqlite3'
            self.assertEqual(indexed_search(d,'hello world',db),search(d,'hello world'))
            self.assertEqual(sync_index(d,db),{'added':0,'updated':0,'removed':0,'unchanged':1})
            self.assertEqual(indexed_search(d,'hello',db),search(d,'hello'))
    def test_changed_and_deleted_documents_refresh(self):
        with tempfile.TemporaryDirectory() as d, tempfile.TemporaryDirectory() as cache:
            file=Path(d,'a.md');file.write_text('before');db=Path(cache)/'index.sqlite3'
            sync_index(d,db);file.write_text('after!')
            self.assertEqual(sync_index(d,db)['updated'],1)
            self.assertEqual(indexed_search(d,'before',db),[])
            self.assertEqual(indexed_search(d,'after',db)[0]['line'],1)
            file.unlink();self.assertEqual(sync_index(d,db)['removed'],1);self.assertEqual(indexed_search(d,'after',db),[])
    def test_hidden_and_symlink_files_stay_out_of_index(self):
        with tempfile.TemporaryDirectory() as d, tempfile.TemporaryDirectory() as cache:
            Path(d,'.hidden.md').write_text('secret');Path(d,'binary.txt').write_bytes(b'\xff')
            target=Path(cache,'external.md');target.write_text('secret');Path(d,'link.md').symlink_to(target)
            self.assertEqual(indexed_search(d,'secret',Path(cache)/'index.sqlite3'),[])
    def test_index_is_bound_to_its_original_root(self):
        with tempfile.TemporaryDirectory() as one, tempfile.TemporaryDirectory() as two, tempfile.TemporaryDirectory() as cache:
            db=Path(cache)/'index.sqlite3';sync_index(one,db)
            with self.assertRaises(ValueError):sync_index(two,db)
    def test_unchanged_documents_are_not_retokenized(self):
        from unittest.mock import patch
        with tempfile.TemporaryDirectory() as d, tempfile.TemporaryDirectory() as cache:
            Path(d,'a.md').write_text('hello');db=Path(cache)/'index.sqlite3';sync_index(d,db)
            with patch('app.terms',side_effect=AssertionError('unchanged file retokenized')):
                self.assertEqual(sync_index(d,db)['unchanged'],1)


