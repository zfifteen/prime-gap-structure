import unittest
from cih1_baselines.primality import is_prime_trial

class TestIntegrity(unittest.TestCase):
    def test_primality_audit(self):
        self.assertTrue(is_prime_trial(1048559)) # 40 bit p
        self.assertFalse(is_prime_trial(1048559 * 2))
