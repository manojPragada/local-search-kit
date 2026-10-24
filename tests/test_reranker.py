import json,unittest
from types import SimpleNamespace
from reranker import rerank_results

RESULTS=[{'source':'a.md','line':1,'score':1.0,'excerpt':'alpha'},{'source':'b.md','line':2,'score':.5,'excerpt':'beta'}]
class RerankerTests(unittest.TestCase):
    def test_reranker_reorders_without_inventing_citations(self):
        def runner(argv,**kwargs):
            payload=json.loads(kwargs['input']);self.assertNotIn('source',payload['candidates'][0]);return SimpleNamespace(returncode=0,stdout='[0.1, 0.9]')
        ranked=rerank_results('query',RESULTS,'/local/model',runner);self.assertEqual([r['source'] for r in ranked],['b.md','a.md']);self.assertEqual(ranked[0]['line'],2)
    def test_invalid_scores_and_process_failure_are_rejected(self):
        for output in ['[2, 0]', '[0.5]', 'not json']:
            with self.assertRaises(ValueError):rerank_results('q',RESULTS,'x',lambda *a,**k:SimpleNamespace(returncode=0,stdout=output))
        with self.assertRaises(ValueError):rerank_results('q',RESULTS,'x',lambda *a,**k:SimpleNamespace(returncode=1,stdout='[]'))
