import unittest
from cih1_analysis.metrics import score_case
class T(unittest.TestCase):
    def test_exact_factor_is_zero(self):
        r=score_case({"p":100,"q":200,"carrier_w":100}, [10,20,30,40])
        self.assertEqual(r["D_c"],0)
        self.assertEqual(r["R"],0)
        self.assertTrue(r["carrier_beats_control_median"])
if __name__=="__main__": unittest.main()
