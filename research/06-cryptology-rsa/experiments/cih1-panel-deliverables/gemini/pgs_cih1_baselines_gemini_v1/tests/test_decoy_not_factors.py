import unittest
from cih1_baselines.decoy_reciprocal import find_decoy_reciprocals

class TestDecoys(unittest.TestCase):
    def test_decoys_not_factors(self):
        # 10000 = 100 * 100, let's pretend p=80, q=125 (N=10000)
        decoys = find_decoy_reciprocals(10000, 80, 125, samples=10, window=50)
        for x, y in decoys:
            self.assertNotIn(x, (80, 125))
