import unittest
from cih1_baselines.contamination import check_contamination

class TestContaminationFlags(unittest.TestCase):
    def test_near_square_logic(self):
        # Fake 100 near square
        contam = check_contamination(10000, 98, 102) # isqrt = 100, min_dist = 2
        self.assertTrue(contam["near_square"])
