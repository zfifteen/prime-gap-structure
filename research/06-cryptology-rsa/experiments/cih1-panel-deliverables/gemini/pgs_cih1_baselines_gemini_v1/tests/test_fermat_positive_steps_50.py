import unittest
from cih1_baselines.official_replay import run_official_replay

class TestFermatPositiveSteps(unittest.TestCase):
    def test_50_bit_steps(self):
        results = run_official_replay()
        self.assertEqual(results["50-bit"]["fermat_steps"], 28534)
        self.assertEqual(results["50-bit"]["isqrt"], 32053641)
