import unittest
from cih1_baselines.floor_density import floor_density

class TestFloorDensity50(unittest.TestCase):
    def test_density_high(self):
        N = 1027435935526951
        tested, passed, rate = floor_density(N, window=5000, stride=1)
        self.assertGreater(tested, 0)
        self.assertGreater(rate, 0.95)
