import unittest
from benchmark import compare_metrics
class CompareTests(unittest.TestCase):
 def test_reports_candidate_delta_without_quality_claim(self):self.assertEqual(compare_metrics({'mean_reciprocal_rank':.5,'top_1_accuracy':.25},{'mean_reciprocal_rank':.75,'top_1_accuracy':.5}),{'mean_reciprocal_rank_delta':.25,'top_1_accuracy_delta':.25})
 def test_reports_optional_top_three_delta(self):self.assertEqual(compare_metrics({'mean_reciprocal_rank':.5,'top_1_accuracy':.25,'top_3_accuracy':.5},{'mean_reciprocal_rank':.75,'top_1_accuracy':.5,'top_3_accuracy':.75})['top_3_accuracy_delta'],.25)
 def test_reports_optional_top_five_delta(self):self.assertAlmostEqual(compare_metrics({'mean_reciprocal_rank':.5,'top_1_accuracy':.25,'top_5_accuracy':.6},{'mean_reciprocal_rank':.75,'top_1_accuracy':.5,'top_5_accuracy':.8})['top_5_accuracy_delta'],.2)
 def test_reports_optional_median_rank_delta(self):self.assertEqual(compare_metrics({'mean_reciprocal_rank':.5,'top_1_accuracy':.25,'median_rank':4},{'mean_reciprocal_rank':.75,'top_1_accuracy':.5,'median_rank':2})['median_rank_delta'],-2)
 def test_reports_optional_worst_rank_delta(self):self.assertEqual(compare_metrics({'mean_reciprocal_rank':.5,'top_1_accuracy':.25,'worst_rank':8},{'mean_reciprocal_rank':.75,'top_1_accuracy':.5,'worst_rank':5})['worst_rank_delta'],-3)
