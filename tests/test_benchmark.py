import io,json,tempfile,unittest
from contextlib import redirect_stdout
from pathlib import Path
from unittest.mock import patch
from types import SimpleNamespace
from benchmark import evaluate,main

class BenchmarkTests(unittest.TestCase):
    def test_reports_bounded_ranking_metrics(self):
        cases=[{'query':'q','candidates':['wrong','right'],'relevant':1},{'query':'x','candidates':['right','wrong'],'relevant':0}]
        def runner(argv,**kwargs):
            payload=json.loads(kwargs['input']);return SimpleNamespace(returncode=0,stdout='[0.1,0.9]' if payload['query']=='q' else '[0.9,0.1]')
        result=evaluate(cases,'model',runner);self.assertEqual((result['cases'],result['mean_reciprocal_rank'],result['top_1_accuracy'],result['top_3_accuracy'],result['top_5_accuracy'],result['median_rank'],result['worst_rank']),(2,1.0,1.0,1.0,1.0,1.0,1));self.assertRegex(result['case_set_sha256'],r'^[0-9a-f]{64}$')
    def test_rejects_invalid_cases(self):
        for cases in [[],[{'query':'q','candidates':['x'],'relevant':2}]]:
            with self.assertRaises(ValueError):evaluate(cases,'model',lambda *a,**k:None)

    def test_cli_compares_saved_baseline_through_promotion_gate(self):
        root=Path(__file__).parents[1];cases=root/'examples'/'benchmark.json';reranker=root/'examples'/'tfidf_reranker.py'
        baseline=evaluate(json.loads(cases.read_text()),str(reranker),include_cases=True)
        with tempfile.TemporaryDirectory() as folder:
            baseline_path=Path(folder)/'baseline.json';baseline_path.write_text(json.dumps(baseline))
            output=io.StringIO()
            argv=['benchmark.py',str(cases),str(reranker),'--baseline-result',str(baseline_path),'--minimum-cases','1','--minimum-mrr-delta','0','--require-promotion']
            with patch('sys.argv',argv),redirect_stdout(output):code=main()
        result=json.loads(output.getvalue());self.assertEqual(code,0);self.assertTrue(result['promotion_gate']['promote']);self.assertIn('evaluation',result)
