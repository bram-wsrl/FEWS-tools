import unittest
import itertools
import datetime as dt
import xml.etree.ElementTree as ET

from lib.utils import ns
from lib.models import TimeSerie
from tests import DATAPATH, PIXML_TIMESERIES_SL, PIXML_TIMESERIES_HL


class TestTimeSerieInstances(unittest.TestCase):
    namespace = "http://www.wldelft.nl/fews/PI"
    pixml_timeseries_sl = DATAPATH / PIXML_TIMESERIES_SL

    def setUp(self):
        self.tree = ET.parse(self.pixml_timeseries_sl)
        self.root = self.tree.getroot()

        series = self.root.findall(ns('series', self.namespace))
        self.serie1 = series[0]
        self.serie2 = series[1]
        self.serie3 = series[2]
        self.serie4_no_events = series[3]
        self.serie1_duplicate = series[4]
    
    def tearDown(self):
        self.root.clear()

    def test_timeserie_init(self):
        timeserie = TimeSerie(self.serie1, self.namespace)

        self.assertTrue(timeserie.has_events)
        self.assertEqual(timeserie.location, 'Ameide, Broekseweg')
        self.assertEqual(timeserie.sublocation, 'Hbov')
        self.assertEqual(timeserie.locationId, 'OW000631')
        self.assertEqual(timeserie.parameterId, 'H.M.5')
        self.assertEqual(timeserie.group_key, 'Ameide, Broekseweg_H')
        self.assertEqual(timeserie.start_datetime, dt.datetime(2018, 4, 12, 9, 15))
        self.assertEqual(timeserie.end_datetime, dt.datetime(2023, 4, 14, 9, 15))
        self.assertEqual(timeserie.timestep_delta, dt.timedelta(seconds=300))
        self.assertTrue(timeserie.is_equidistant())

    def test_timeserie_duplicate(self):
        timeserie1 = TimeSerie(self.serie1, self.namespace)
        timeserie1_duplicate = TimeSerie(self.serie1_duplicate, self.namespace)
        self.assertEqual(timeserie1, timeserie1_duplicate)

    def test_timeserie_no_events(self):
        timeserie4_no_events = TimeSerie(self.serie4_no_events, self.namespace)
        self.assertTrue(not timeserie4_no_events.has_events)


class TestTimeSeriesCollections(unittest.TestCase):
        namespace = "http://www.wldelft.nl/fews/PI"
        pixml_timeseries_hl = DATAPATH / PIXML_TIMESERIES_HL

        def setUp(self):
            self.tree = ET.parse(self.pixml_timeseries_hl)
            self.root = self.tree.getroot()
            self.timeseries = [TimeSerie(i, self.namespace) for i in 
                               self.root.findall(ns('series', self.namespace))]

        def tearDown(self):
            self.root.clear()

        def test_timeserie_sort(self):
            timeseries = sorted(self.timeseries, key=TimeSerie.grouper)
            sorted_group_keys = [i.group_key for i in timeseries]

            self.assertEqual(sorted_group_keys[:4].count('Ameide, Broekseweg_H'), 4)
            self.assertEqual(sorted_group_keys[4:12].count('Ameide, Broekseweg_P1'), 8)
            self.assertEqual(sorted_group_keys[12:20].count('Ameide, Broekseweg_VL2'), 8)
            self.assertEqual(len(sorted_group_keys), 20)

        def test_timeserie_unique(self):
            unique_timeseries = set(self.timeseries)
            self.assertEqual(len(unique_timeseries), 18)

        def test_timeseries_groupby(self):
            gr_ = TimeSerie.grouper

            # non-empty unique timeseries sorted by sublocation/waterlevels
            # note that set operations are unstable so insertion order is not guaranteed
            timeseries = sorted([i for i in set(self.timeseries) if i.has_events], key=gr_)

            timeserie_groups = {k: list(v) for k, v in itertools.groupby(timeseries, key=gr_)}

            H_group = timeserie_groups['ameide, broekseweg_h']
            hbov, hben = sorted(H_group, key=lambda x: x.locationId)
            self.assertEqual(hbov.locationId, 'OW000631')
            self.assertEqual(hben.locationId, 'OW000632')
            
            P_group = timeserie_groups['ameide, broekseweg_p1']
            BS, SH, TT = sorted(P_group, key=lambda x: x.parameterId)
            self.assertEqual(BS.locationId, 'SL000323')
            self.assertEqual(BS.parameterId, 'BS.0')
            self.assertEqual(SH.locationId, 'SL000323')
            self.assertEqual(SH.parameterId, 'SH.0')
            self.assertEqual(TT.locationId, 'SL000323')
            self.assertEqual(TT.parameterId, 'TT.0')

            VL_group = timeserie_groups['ameide, broekseweg_vl2']
            Q, SD = sorted(VL_group, key=lambda x: x.parameterId)
            self.assertEqual(Q.locationId, 'SL000324')
            self.assertEqual(Q.parameterId, 'Q.R.0')
            self.assertEqual(SD.locationId, 'SL000324')
            self.assertEqual(SD.parameterId, 'SD.0')


class TestPixml2csv(unittest.TestCase):
    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_dummy(self):
        self.assertTrue(True)


if __name__ == '__main__':
    unittest.main()
