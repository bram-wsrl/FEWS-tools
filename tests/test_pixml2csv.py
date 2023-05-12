import unittest
import tempfile
from pathlib import Path

from FEWS_tools.scripts.pixml2csv import convert_pixml2csv
from tests import (
    DEBUG, DATAPATH, OUTPUTPATH,
    PIXML_TIMESERIES_SL, PIXML_TIMESERIES_HL, PIXML_TIMESERIES_HL_SL, PIXML_TIMESERIES_HL_ORDER)


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
    
    def test_equidistant_timeseries_H_to_SL(self):
        convert_pixml2csv(DATAPATH, PIXML_TIMESERIES_HL_ORDER, self.tmp_output_folder, H_to_SL=True)
        written_files = sorted(Path(self.tmp_output_folder).iterdir())

        self.assertEqual(len(written_files), 2)

    def test_equidistant_timeseries_inputorder_is_outputorder(self):
        convert_pixml2csv(DATAPATH, PIXML_TIMESERIES_HL_ORDER, self.tmp_output_folder)

        H_group = 'Ameide, Broekseweg_H_T5.csv'
        P1_group = 'Ameide, Broekseweg_P1_T5.csv'
        VL2_group = 'Ameide, Broekseweg_VL2_T5.csv'

        H_columns = (
            'value_Hben_H.M.5', 'flag_Hben_H.M.5', 'value_Hbov_H.M.5', 'flag_Hbov_H.M.5')
        P1_columns = (
            'value_P1_BS.5', 'flag_P1_BS.5', 'value_P1_SH.5', 'flag_P1_SH.5',
            'value_P1_TT.5', 'flag_P1_TT.5', 'value_P1_PF.5', 'flag_P1_PF.5',
            'value_P1_A.5', 'flag_P1_A.5', 'value_P1_Q.B.5', 'flag_P1_Q.B.5')
        VL2_columns = (
            'value_VL2_SD.5', 'flag_VL2_SD.5', 'value_VL2_MWAR.5', 'flag_VL2_MWAR.5',
            'value_VL2_Q.B.5', 'flag_VL2_Q.B.5')

        groups = [H_group, P1_group, VL2_group]
        group_columns = [H_columns, P1_columns, VL2_columns]

        for file, columns in zip(groups, group_columns):
            with open(self.tmp_output_folder / file, 'r') as fr:
                # match column names in file with input xml order
                self.assertEqual(tuple(fr.readline().strip().split(',')[2:]), columns)

    def test_equidistant_timeseries_xmlfilepattern(self):
        xmlfilepattern = 'ExportOpvlWerkT*.xml'
        convert_pixml2csv(DATAPATH, xmlfilepattern, self.tmp_output_folder)
        written_files = sorted(Path(self.tmp_output_folder).iterdir())

        self.assertEqual(len(written_files), 3)

    def test_equidistant_timeseries_xmlfilepattern_separate_events(self):
        xmlfilepattern = 'ExportOpvlWerkT*.xml'
        convert_pixml2csv(DATAPATH, xmlfilepattern, self.tmp_output_folder, join_events=False)
        written_files = sorted(Path(self.tmp_output_folder).iterdir())

        self.assertEqual(len(written_files), 11)

    def test_equidistant_timeseries_xmlfilepattern_H_to_SL(self):
        xmlfilepattern = 'ExportOpvlWerkT*.xml'
        convert_pixml2csv(DATAPATH, xmlfilepattern, self.tmp_output_folder, H_to_SL=True)
        written_files = sorted(Path(self.tmp_output_folder).iterdir())

        self.assertEqual(len(written_files), 2)


if __name__ == '__main__':
    unittest.main()
