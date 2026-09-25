import unittest
from cih1_analysis.stats_tests import directional_p_value
class T(unittest.TestCase):
    def test_all_positive(self):
        p,two,pos,neg=directional_p_value([1,1,1,1,1])
        self.assertEqual(pos,5); self.assertEqual(neg,0)
        self.assertLess(p,0.05)
    def test_tie_only(self):
        p,two,pos,neg=directional_p_value([0,0])
        self.assertEqual(p,1.0); self.assertEqual(pos,0); self.assertEqual(neg,0)
if __name__=="__main__": unittest.main()
