import unittest
from cih1_baselines.floor_density import floor_density
from cih1_baselines.official_replay import FIXTURES

class TestFloorDensity(unittest.TestCase):
    def test_density_50bit(self):
        N = FIXTURES["50-bit"]["N"]
        tested, passed, rate = floor_density(N, window=5000, stride=1)
        self.assertGreater(rate, 0.95)
