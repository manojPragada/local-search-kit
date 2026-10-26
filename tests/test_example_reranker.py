import json,subprocess,sys,unittest
from pathlib import Path

class ExampleRerankerTests(unittest.TestCase):
    def test_tfidf_example_prefers_query_overlap(self):
        script=Path(__file__).parents[1]/'examples'/'tfidf_reranker.py';payload={'version':1,'query':'offline citations','candidates':[{'excerpt':'hosted service'},{'excerpt':'offline file citations'}]}
        result=subprocess.run([sys.executable,str(script)],input=json.dumps(payload),text=True,capture_output=True,check=True)
        scores=json.loads(result.stdout);self.assertEqual(len(scores),2);self.assertGreater(scores[1],scores[0]);self.assertTrue(all(0<=score<=1 for score in scores))
