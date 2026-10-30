import json,unittest
from types import SimpleNamespace
from benchmark import evaluate

class BenchmarkTests(unittest.TestCase):
    def test_reports_bounded_ranking_metrics(self):
        cases=[{'query':'q','candidates':['wrong','right'],'relevant':1},{'query':'x','candidates':['right','wrong'],'relevant':0}]
        def runner(argv,**kwargs):
            payload=json.loads(kwargs['input']);return SimpleNamespace(returncode=0,stdout='[0.1,0.9]' if payload['query']=='q' else '[0.9,0.1]')
        result=evaluate(cases,'model',runner);self.assertEqual((result['cases'],result['mean_reciprocal_rank'],result['top_1_accuracy']),(2,1.0,1.0));self.assertRegex(result['case_set_sha256'],r'^[0-9a-f]{64}$')
    def test_rejects_invalid_cases(self):
        for cases in [[],[{'query':'q','candidates':['x'],'relevant':2}]]:
            with self.assertRaises(ValueError):evaluate(cases,'model',lambda *a,**k:None)
