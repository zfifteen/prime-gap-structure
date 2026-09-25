import unittest
from cih1_baselines.official_replay import run_official_replay

class TestOfficialReplay(unittest.TestCase):
    def setUp(self):
        self.results = run_official_replay()
        
    def test_classification_correctness(self):
        # 40-bit is highly near-square (Fermat 0 step)
        self.assertTrue(self.results["40-bit"]["near_square"])
        
        # 50-bit is official V3 residual, NOT near-square
        self.assertFalse(self.results["50-bit"]["near_square"])
        
        # 64-bit is near-square (mutual cert exact close, Fermat 0 step)
        self.assertTrue(self.results["64-bit"]["near_square"])
