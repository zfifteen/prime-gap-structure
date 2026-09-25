import unittest
from cih1_analysis.exclude import exclusion_info
class T(unittest.TestCase):
    def test_default_abs_excludes(self):
        n=1000000*1000001
        r=exclusion_info({"N":n,"p":1000000,"q":1000001})
        self.assertTrue(r["excluded"])
        self.assertIn("near_square_abs",r["exclude_reason"])
if __name__=="__main__": unittest.main()
