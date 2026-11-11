import unittest
from benchmark import compare_case_ranks,promotion_gate
class GateTests(unittest.TestCase):
 def test_requires_representative_non_regressing_improvement(self):
  base={'cases':20,'case_set_sha256':'a'*64,'mean_reciprocal_rank':.5,'top_1_accuracy':.4};candidate={'cases':20,'case_set_sha256':'a'*64,'mean_reciprocal_rank':.55,'top_1_accuracy':.4};self.assertTrue(promotion_gate(base,candidate)['promote'])
  weak={**candidate,'cases':2};result=promotion_gate({**base,'cases':2},weak);self.assertFalse(result['promote']);self.assertIn('labelled cases',result['reasons'][0])
 def test_rejects_mismatched_cases(self):
  with self.assertRaisesRegex(ValueError,'same cases'):promotion_gate({'cases':20,'case_set_sha256':'a'*64,'mean_reciprocal_rank':.5,'top_1_accuracy':.5},{'cases':21,'case_set_sha256':'a'*64,'mean_reciprocal_rank':.6,'top_1_accuracy':.6})
 def test_rejects_same_size_different_case_sets(self):
  base={'cases':20,'case_set_sha256':'a'*64,'mean_reciprocal_rank':.5,'top_1_accuracy':.5};candidate={**base,'case_set_sha256':'b'*64,'mean_reciprocal_rank':.6}
  with self.assertRaisesRegex(ValueError,'fingerprinted case set'):promotion_gate(base,candidate)
 def test_case_rank_diagnostics_block_hidden_regressions(self):
  old=[{'case':1,'rank':2,'candidates':3},{'case':2,'rank':1,'candidates':3}];new=[{'case':1,'rank':1,'candidates':3},{'case':2,'rank':2,'candidates':3}]
  self.assertEqual(compare_case_ranks({'case_ranks':old},{'case_ranks':new}),{'improved_cases':1,'unchanged_cases':0,'regressed_cases':1,'worst_rank_regression':1})
  base={'cases':2,'case_set_sha256':'a'*64,'mean_reciprocal_rank':.5,'top_1_accuracy':.4,'case_ranks':old};candidate={**base,'mean_reciprocal_rank':.55,'top_1_accuracy':.4,'case_ranks':new}
  result=promotion_gate(base,candidate,minimum_cases=2);self.assertFalse(result['promote']);self.assertIn('individual case ranks',result['reasons'][-1])
 def test_rejects_incomplete_case_rank_diagnostics(self):
  base={'cases':2,'case_set_sha256':'a'*64,'mean_reciprocal_rank':.5,'top_1_accuracy':.4,'case_ranks':[{'case':1,'rank':1,'candidates':2}]}
  with self.assertRaisesRegex(ValueError,'declared case count'):promotion_gate(base,{**base})
 def test_rejects_malformed_case_rank_diagnostics(self):
  valid={'case_ranks':[{'case':1,'rank':1,'candidates':2}]}
  invalid=(
   {'case_ranks':[{'case':2,'rank':1,'candidates':2}]},
   {'case_ranks':[{'case':1,'rank':0,'candidates':2}]},
   {'case_ranks':[{'case':1,'rank':3,'candidates':2}]},
   {'case_ranks':[{'case':1,'rank':1,'candidates':0}]},
  )
  for result in invalid:
   with self.subTest(result=result),self.assertRaises(ValueError):compare_case_ranks(valid,result)
 def test_worst_rank_regression_blocks_promotion_without_case_details(self):
  base={'cases':20,'case_set_sha256':'a'*64,'mean_reciprocal_rank':.5,'top_1_accuracy':.4,'worst_rank':4};candidate={**base,'mean_reciprocal_rank':.55,'worst_rank':5}
  result=promotion_gate(base,candidate);self.assertFalse(result['promote']);self.assertIn('worst relevant-result rank regressed',result['reasons'])
 def test_top_three_regression_blocks_promotion(self):
  base={'cases':20,'case_set_sha256':'a'*64,'mean_reciprocal_rank':.5,'top_1_accuracy':.4,'top_3_accuracy':.8};candidate={**base,'mean_reciprocal_rank':.55,'top_3_accuracy':.75}
  result=promotion_gate(base,candidate);self.assertFalse(result['promote']);self.assertIn('top-3 accuracy regressed',result['reasons'])
 def test_top_five_regression_blocks_promotion(self):
  base={'cases':20,'case_set_sha256':'a'*64,'mean_reciprocal_rank':.5,'top_1_accuracy':.4,'top_5_accuracy':.9};candidate={**base,'mean_reciprocal_rank':.55,'top_5_accuracy':.85}
  result=promotion_gate(base,candidate);self.assertFalse(result['promote']);self.assertIn('top-5 accuracy regressed',result['reasons'])
 def test_median_rank_regression_blocks_promotion(self):
  base={'cases':20,'case_set_sha256':'a'*64,'mean_reciprocal_rank':.5,'top_1_accuracy':.4,'median_rank':2};candidate={**base,'mean_reciprocal_rank':.55,'median_rank':3}
  result=promotion_gate(base,candidate);self.assertFalse(result['promote']);self.assertIn('median relevant-result rank regressed',result['reasons'])
 def test_rejects_invalid_gate_thresholds(self):
  result={'cases':20,'case_set_sha256':'a'*64,'mean_reciprocal_rank':.5,'top_1_accuracy':.4}
  for kwargs in ({'minimum_cases':0},{'minimum_mrr_delta':-0.1},{'minimum_mrr_delta':float('nan')}):
   with self.assertRaises(ValueError):promotion_gate(result,result,**kwargs)
