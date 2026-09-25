import unittest
from cih1_analysis.validate_inputs import join_inputs
class T(unittest.TestCase):
    def test_join_on_case_id(self):
        p={"a":{"case_id":"a","bits":10,"N":15}}
        a={"a":{"case_id":"a","N":15,"p":3,"q":5}}
        c={"a":{"case_id":"a","carrier_w":3,"search_band_lo":1,"search_band_hi":10}}
        self.assertEqual(join_inputs(p,a,c)[0]["carrier_w"],3)
    def test_missing_carrier_fails(self):
        with self.assertRaises(ValueError): join_inputs({"a":{"case_id":"a","bits":1,"N":15}},{"a":{"case_id":"a","N":15,"p":3,"q":5}}, {})
if __name__=="__main__": unittest.main()
