import unittest
from benchmark import evaluate
class BenchmarkDiagnosticsTests(unittest.TestCase):
 def test_reports_bounded_case_ranks(self):
  cases=[{'query':'q','candidates':['a','b'],'relevant':1}]
  def runner(*args,**kwargs):
   class Result:returncode=0;stdout='[0, 1]';stderr=''
   return Result()
  result=evaluate(cases,'fake',runner,include_cases=True);self.assertEqual(result['case_ranks'],[{'case':1,'rank':1,'candidates':2}]);self.assertRegex(result['case_set_sha256'],r'^[0-9a-f]{64}$')
