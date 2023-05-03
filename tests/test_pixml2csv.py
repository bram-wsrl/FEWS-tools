import unittest
import tempfile
from pathlib import Path

from FEWS_tools.scripts.pixml2csv import convert_pixml2csv
from tests import (
    DEBUG, DATAPATH, OUTPUTPATH,
    PIXML_TIMESERIES_SL, PIXML_TIMESERIES_HL, PIXML_TIMESERIES_HL_SL)


class TestConvertXml2Csv(unittest.TestCase):
    def setUp(self):
        self.tmp_output_folder = Path(tempfile.mkdtemp(dir=OUTPUTPATH))

    def tearDown(self):
        if not DEBUG:
            for file in self.tmp_output_folder.iterdir():
                file.unlink()
            self.tmp_output_folder.rmdir()

    def test_equidistant_sublocation_separate_files(self):
        convert_pixml2csv(DATAPATH, PIXML_TIMESERIES_SL, self.tmp_output_folder, join_events=False)
        written_files = sorted(Path(self.tmp_output_folder).iterdir())

        self.assertEqual(len(written_files), 3)

    def test_nonequidistant_sublocations(self):
        convert_pixml2csv(DATAPATH, PIXML_TIMESERIES_HL, self.tmp_output_folder)
        written_files = sorted(Path(self.tmp_output_folder).iterdir())

        self.assertEqual(len(written_files), 7)

    def test_equidistant_sublocations_separate_files(self):
        convert_pixml2csv(DATAPATH, PIXML_TIMESERIES_HL_SL, self.tmp_output_folder, join_events=False)
        written_files = sorted(Path(self.tmp_output_folder).iterdir())

        self.assertEqual(len(written_files), 10)

    def test_equidistant_sublocations(self):
        convert_pixml2csv(DATAPATH, PIXML_TIMESERIES_HL_SL, self.tmp_output_folder)
        written_files = sorted(Path(self.tmp_output_folder).iterdir())

        self.assertEqual(len(written_files), 9)
