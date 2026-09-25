import unittest, tempfile, json, pathlib
from cih1_analysis.run import main
class T(unittest.TestCase):
    def test_same_seed_same_summary(self):
        base=pathlib.Path(__file__).resolve().parents[1]
        with tempfile.TemporaryDirectory() as d:
            d1=pathlib.Path(d)/"a"; d2=pathlib.Path(d)/"b"
            args=["run","--public",str(base/"examples/tiny_public.jsonl"),"--audit",str(base/"examples/tiny_audit.jsonl"),"--carrier",str(base/"examples/tiny_carrier.jsonl"),"--out-dir",str(d1),"--seed","7"]
            self.assertEqual(main(args),0)
            args[-3]=str(d2)
            self.assertEqual(main(args),0)
            a=json.loads((d1/"experiment_summary.json").read_text())
            b=json.loads((d2/"experiment_summary.json").read_text())
            for k in ("decision","median_R","f_beat","p_value"):
                self.assertEqual(a[k],b[k])
if __name__=="__main__": unittest.main()
