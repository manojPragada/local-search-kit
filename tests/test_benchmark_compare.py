import unittest
from benchmark import compare_metrics
class CompareTests(unittest.TestCase):
 def test_reports_candidate_delta_without_quality_claim(self):self.assertEqual(compare_metrics({'mean_reciprocal_rank':.5,'top_1_accuracy':.25},{'mean_reciprocal_rank':.75,'top_1_accuracy':.5}),{'mean_reciprocal_rank_delta':.25,'top_1_accuracy_delta':.25})
