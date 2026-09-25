import unittest
from cih1_baselines.decoy_reciprocal import find_decoys

class TestDecoyReciprocal(unittest.TestCase):
    def test_50bit_decoys_exist(self):
        N = 1027435935526951
        p = 30729371
        q = 33434981
        decoys, _ = find_decoys(N, p, q, window=5000, max_samples=5)
        self.assertGreater(len(decoys), 0)
        for x in decoys:
            y = N // x
            self.assertTrue(x * y != N)
            self.assertNotIn(x, [p, q])
            self.assertNotIn(y, [p, q])
