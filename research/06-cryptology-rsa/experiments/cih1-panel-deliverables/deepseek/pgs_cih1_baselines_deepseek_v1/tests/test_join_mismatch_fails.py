import unittest
import tempfile
import os
from cih1_baselines.io_jsonl import write_jsonl
from cih1_baselines.run import cmd_corpus_baselines
import argparse

class TestJoinMismatch(unittest.TestCase):
    def test_mismatch_raises(self):
        with tempfile.TemporaryDirectory() as tmp:
            pub = os.path.join(tmp, 'pub.jsonl')
            aud = os.path.join(tmp, 'aud.jsonl')
            write_jsonl(pub, [{'case_id': 'a', 'N': 15}])
            write_jsonl(aud, [{'case_id': 'b', 'p': 3, 'q': 5}])
            ns = argparse.Namespace(
                public=pub, audit=aud, out_dir=os.path.join(tmp,'OUT'),
                seed=0, floor_window=100, floor_stride=1, decoy_samples=5
            )
            with self.assertRaises(ValueError):
                cmd_corpus_baselines(ns)
