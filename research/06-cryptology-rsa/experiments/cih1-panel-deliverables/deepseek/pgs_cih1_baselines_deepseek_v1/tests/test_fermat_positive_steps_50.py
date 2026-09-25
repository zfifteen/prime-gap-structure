import unittest
from cih1_baselines.fermat import fermat_steps

class TestFermat50BitManySteps(unittest.TestCase):
    def test_50bit_non_zero_steps(self):
        steps, f1, f2 = fermat_steps(1027435935526951)
        self.assertIsNotNone(steps)
        self.assertGreater(steps, 1000)
