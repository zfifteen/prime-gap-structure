import unittest
from cih1_baselines.contamination import compute_contamination

class TestContaminationFlags(unittest.TestCase):
    def test_near_square(self):
        case = {'case_id': 'ns', 'N': 1099507433251}
        audit = {'case_id': 'ns', 'p': 1048559, 'q': 1048589}
        r = compute_contamination(case, audit)
        self.assertTrue(r['near_square_flag'])
        self.assertTrue(r['product_ok'])
        self.assertTrue(r['both_prime_ok'])
        self.assertFalse(r['audit_integrity_fail'])

    def test_non_near_square(self):
        case = {'case_id': 'nns', 'N': 1027435935526951}
        audit = {'case_id': 'nns', 'p': 30729371, 'q': 33434981}
        r = compute_contamination(case, audit)
        self.assertFalse(r['near_square_flag'])
        self.assertTrue(r['product_ok'])
        self.assertTrue(r['both_prime_ok'])
        self.assertFalse(r['audit_integrity_fail'])

    def test_bad_product(self):
        case = {'case_id': 'bad', 'N': 100}
        audit = {'case_id': 'bad', 'p': 7, 'q': 13}
        r = compute_contamination(case, audit)
        self.assertFalse(r['product_ok'])
        self.assertTrue(r['audit_integrity_fail'])
