import unittest
from benchmark import promotion_gate
class GateTests(unittest.TestCase):
 def test_requires_representative_non_regressing_improvement(self):
  base={'cases':20,'case_set_sha256':'a'*64,'mean_reciprocal_rank':.5,'top_1_accuracy':.4};candidate={'cases':20,'case_set_sha256':'a'*64,'mean_reciprocal_rank':.55,'top_1_accuracy':.4};self.assertTrue(promotion_gate(base,candidate)['promote'])
  weak={**candidate,'cases':2};result=promotion_gate({**base,'cases':2},weak);self.assertFalse(result['promote']);self.assertIn('labelled cases',result['reasons'][0])
 def test_rejects_mismatched_cases(self):
  with self.assertRaisesRegex(ValueError,'same cases'):promotion_gate({'cases':20,'case_set_sha256':'a'*64,'mean_reciprocal_rank':.5,'top_1_accuracy':.5},{'cases':21,'case_set_sha256':'a'*64,'mean_reciprocal_rank':.6,'top_1_accuracy':.6})
 def test_rejects_same_size_different_case_sets(self):
  base={'cases':20,'case_set_sha256':'a'*64,'mean_reciprocal_rank':.5,'top_1_accuracy':.5};candidate={**base,'case_set_sha256':'b'*64,'mean_reciprocal_rank':.6}
  with self.assertRaisesRegex(ValueError,'fingerprinted case set'):promotion_gate(base,candidate)
