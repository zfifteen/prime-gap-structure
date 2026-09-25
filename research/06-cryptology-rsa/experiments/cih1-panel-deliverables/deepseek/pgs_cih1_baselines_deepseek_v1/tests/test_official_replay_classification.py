import unittest
from cih1_baselines import official_replay

class TestOfficialReplayClassification(unittest.TestCase):
    def test_classifications(self):
        results = official_replay.replay_official()
        for r in results:
            with self.subTest(bits=r['bits']):
                if r['bits'] == 40:
                    self.assertTrue(r['near_square_flag'])
                    self.assertEqual(r['classification'], 'near_square_fermat_class')
                elif r['bits'] == 50:
                    self.assertFalse(r['near_square_flag'])
                    self.assertEqual(r['classification'], 'non_near_square')
                elif r['bits'] == 64:
                    self.assertTrue(r['near_square_flag'])
                    self.assertEqual(r['classification'], 'near_square_fermat_class')
