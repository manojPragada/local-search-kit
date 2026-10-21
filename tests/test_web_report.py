import tempfile,unittest
from pathlib import Path
from web_report import html_report

class WebReportTests(unittest.TestCase):
    def test_results_have_escaped_clickable_local_citations(self):
        with tempfile.TemporaryDirectory() as root:
            html=html_report('API <token>',[{'source':'notes & plans.md','line':4,'score':.5,'excerpt':'Use <local> search'}],root)
            self.assertIn('file://',html);self.assertIn('notes%20%26%20plans.md#L4',html);self.assertIn('notes &amp; plans.md:4',html)
            self.assertIn('API &lt;token&gt;',html);self.assertNotIn('Use <local>',html)
    def test_empty_state_is_visible(self):
        self.assertIn('<p id="empty" >',html_report('missing',[],'.'))
