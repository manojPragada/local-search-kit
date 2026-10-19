import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from reporting import markdown_report

class ReportTests(unittest.TestCase):
    def test_citations_and_coverage_are_readable(self):
        report=markdown_report('hello world',[{'source':'notes.md','line':2,'score':.5,'excerpt':'hello'}])
        self.assertIn('"notes.md":2',report);self.assertIn('50% query-word coverage',report)
        self.assertIn('    hello',report)
    def test_source_text_cannot_become_report_markup(self):
        report=markdown_report('query\n# injected',[{'source':'name`with``ticks.md','line':1,'score':1,'excerpt':'<script>example</script>\n# source heading'}])
        self.assertIn('``` "name`with``ticks.md":1 ```',report)
        self.assertIn('    <script>example</script>\n    # source heading',report)
        self.assertNotIn('\n# injected',report)
    def test_empty_report_explains_no_matches(self):
        self.assertIn('No matching lines',markdown_report('missing',[]))
    def test_markdown_cli_works_with_persistent_index(self):
        with tempfile.TemporaryDirectory() as d:
            db=Path(d)/'search.sqlite3'
            result=subprocess.run([sys.executable,'app.py','examples','keyword','--index',str(db),'--format','markdown'],capture_output=True,text=True)
            self.assertEqual(result.returncode,0,result.stderr)
            self.assertIn('# Local Search Report',result.stdout);self.assertIn('notes.md',result.stdout)
