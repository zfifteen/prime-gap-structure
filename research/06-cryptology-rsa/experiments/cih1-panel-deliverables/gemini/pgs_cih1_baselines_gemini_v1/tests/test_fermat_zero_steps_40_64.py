import unittest
from cih1_baselines.official_replay import run_official_replay

class TestFermatZeroSteps(unittest.TestCase):
    def test_zero_steps(self):
        results = run_official_replay()
        self.assertEqual(results["40-bit"]["fermat_steps"], 0)
        self.assertEqual(results["64-bit"]["fermat_steps"], 0)
        self.assertEqual(results["64-bit"]["isqrt"], 3221250486)
