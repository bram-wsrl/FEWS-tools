import unittest
import tempfile
from pathlib import Path

import pandas as pd

from FEWS_tools.scripts.flagging2discharge import update_flagging
from tests import DEBUG, FLAGDATA, DAMO_POMP, OUTPUTPATH


class TestUpdateFlagging(unittest.TestCase):
    def setUp(self):
        self.tmp_output_folder = Path(tempfile.mkdtemp(dir=OUTPUTPATH, prefix='flag_'))

    def tearDown(self):
        if not DEBUG:
            for file in self.tmp_output_folder.iterdir():
                file.unlink()
            self.tmp_output_folder.rmdir()

    def test_convert_flagging_three_period_updates_t1(self):
        '''Bleskensgraaf Noordzijde'''
        update_flagging(FLAGDATA / 't1', DAMO_POMP, self.tmp_output_folder)
        written_files = sorted(Path(self.tmp_output_folder).iterdir())
        self.assertEqual(len(written_files), 1)

        result_df = pd.read_csv(written_files[0])
        updated_discharge_flags = result_df['flag_P1_Q.B.5'].tolist()

        expected_flags = [8,8,2,2,5,5,3,3,3,3]
        self.assertListEqual(updated_discharge_flags, expected_flags)

    def test_convert_flagging_missing_column_and_not_in_damopomp_t2(self):
        '''Land van de Zes Molens'''
        update_flagging(FLAGDATA / 't2', DAMO_POMP, self.tmp_output_folder)
        written_files = sorted(Path(self.tmp_output_folder).iterdir())
        self.assertEqual(len(written_files), 1)

        result_df = pd.read_csv(written_files[0])
        updated_discharge_flags = result_df['flag_P3_Q.B.5'].tolist()

        expected_flags = [2,2,2,2,5,5,5,5,8,8]
        self.assertListEqual(updated_discharge_flags, expected_flags)


if __name__ == '__main__':
    unittest.main()
