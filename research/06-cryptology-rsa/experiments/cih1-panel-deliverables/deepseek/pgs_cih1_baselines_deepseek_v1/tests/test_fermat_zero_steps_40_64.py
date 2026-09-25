import unittest
from cih1_baselines.fermat import fermat_steps

class TestFermatZeroSteps(unittest.TestCase):
    def test_40bit_fermat_zero(self):
        steps, f1, f2 = fermat_steps(1099507433251)
        self.assertEqual(steps, 0)
        self.assertEqual(f1, 1048559)
        self.assertEqual(f2, 1048589)

    def test_64bit_fermat_zero(self):
        steps, f1, f2 = fermat_steps(10376454699372036973)
        self.assertEqual(steps, 0)
        self.assertEqual(f1, 3221225473)
        self.assertEqual(f2, 3221275501)
