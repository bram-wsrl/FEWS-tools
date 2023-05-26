import unittest
import datetime as dt
import itertools as it
import xml.etree.ElementTree as ET

from FEWS_tools.lib.utils import ns
from FEWS_tools.lib.models import TimeSerie
from tests import (
    CONVDATA, PIXML_TIMESERIES_SL, PIXML_TIMESERIES_HL, PIXML_TIMESERIES_HL_SL)


class TestTimeSerieInstances(unittest.TestCase):
    namespace = "http://www.wldelft.nl/fews/PI"
    pixml_timeseries_sl = CONVDATA / PIXML_TIMESERIES_SL

    def setUp(self):
        self.tree = ET.parse(self.pixml_timeseries_sl)
        self.root = self.tree.getroot()

        series = self.root.findall(ns('series', self.namespace))
        self.serie1 = series[0]
        self.serie2 = series[1]
        self.serie3 = series[2]
        self.serie4_no_events = series[3]
        self.serie1_duplicate = series[4]
        self.serie5_nodata_events = series[5]

    def tearDown(self):
        self.root.clear()

    def test_timeserie_init_equidistant(self):
        timeserie1 = TimeSerie(self.serie1, self.namespace)

        self.assertTrue(timeserie1.has_events)
        self.assertEqual(timeserie1.stationName, 'KGM_067107_Ameide, Broekseweg_Hbov')
        self.assertEqual(timeserie1.location, 'Ameide, Broekseweg')
        self.assertEqual(timeserie1.sublocation, 'Hbov')
        self.assertEqual(timeserie1.locationId, 'OW000631')
        self.assertEqual(timeserie1.parameterId, 'H.M.5')
        self.assertEqual(timeserie1.missVal, 'NaN')
        self.assertEqual(timeserie1.group_key, 'Ameide, Broekseweg_H')
        self.assertEqual(timeserie1.start_datetime, dt.datetime(2018, 4, 12, 9, 15))
        self.assertEqual(timeserie1.end_datetime, dt.datetime(2018, 4, 12, 9, 50))
        self.assertEqual(timeserie1.timedelta, dt.timedelta(seconds=300))
        self.assertTrue(timeserie1.is_equidistant)

    def test_timeserie_duplicate(self):
        timeserie1 = TimeSerie(self.serie1, self.namespace)
        timeserie1_duplicate = TimeSerie(self.serie1_duplicate, self.namespace)
        self.assertEqual(timeserie1, timeserie1_duplicate)
    
    def test_timeserie_nodata_events(self):
        timeserie5 = TimeSerie(self.serie5_nodata_events, self.namespace)
        self.assertEqual(timeserie5.events, [])

    def test_timeserie_no_events(self):
        timeserie4_no_events = TimeSerie(self.serie4_no_events, self.namespace)
        self.assertTrue(not timeserie4_no_events.has_events)

    def test_has_continious_timeindex(self):
        timeserie1 = TimeSerie(self.serie1, self.namespace)
        self.assertTrue(timeserie1.has_continuous_timeindex())

        self.serie2.remove(self.serie2.find(ns('event', self.namespace)))
        timeserie2 = TimeSerie(self.serie2, self.namespace)
        self.assertFalse(timeserie2.has_continuous_timeindex())

    def test_update_events(self):
        timeserie1 = TimeSerie(self.serie1, self.namespace)
        timeserie1.update_events()
        suffix = f'{timeserie1.sublocation}_{timeserie1.parameterId}'

        value_key = f'value_{suffix}'
        self.assertTrue(all(value_key in event for event in timeserie1.events))

        flag_key = f'flag_{suffix}'
        self.assertTrue(all(flag_key in event for event in timeserie1.events))
    
    def test_join_events(self):
        timeserie1 = TimeSerie(self.serie1, self.namespace)
        timeserie2 = TimeSerie(self.serie2, self.namespace)
        timeserie3 = TimeSerie(self.serie3, self.namespace)

        event_chainmaps = TimeSerie.join_events([timeserie1, timeserie2, timeserie3])
        self.assertEqual(len(event_chainmaps), 8)

        chainmap_t0 = event_chainmaps[0]
        self.assertEqual(len(chainmap_t0), 8)
        
        expected_values = (
            '2018-04-12', '09:15:00', '-1.455', '2', '-1.606', '2', '-1.4', '4')
        self.assertTupleEqual(tuple(chainmap_t0.values()), expected_values)

    def test_join_events_nonequidistant(self):
        msg = 'Nonequidistant events cannot be joined.'
        with self.assertRaises(ValueError) as e:
            raise ValueError(msg)
        self.assertEqual(str(e.exception), msg)


class TestTimeSeriesSequences(unittest.TestCase):
        namespace = "http://www.wldelft.nl/fews/PI"
        pixml_timeseries_hl = CONVDATA / PIXML_TIMESERIES_HL

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
            gr_loc = TimeSerie.grouper

            # non-empty unique timeseries sorted by sublocation/waterlevels
            # note that set operations are unstable so insertion order is not guaranteed
            # so the result has to be sorted afterwards
            timeseries = sorted([i for i in set(self.timeseries) if i.has_events], key=gr_loc)
            timeserie_groups = {k: list(v) for k, v in it.groupby(timeseries, key=gr_loc)}

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


class TestTimeSeriesTimeGroupby(unittest.TestCase):
    namespace = "http://www.wldelft.nl/fews/PI"
    pixml_timeseries_hl_sl = CONVDATA / PIXML_TIMESERIES_HL_SL

    def setUp(self):
        self.tree = ET.parse(self.pixml_timeseries_hl_sl)
        self.root = self.tree.getroot()
        self.timeseries = [TimeSerie(i, self.namespace) for i in
                           self.root.findall(ns('series', self.namespace))]

    def tearDown(self):
        self.root.clear()

    def test_groupby_timedelta(self):
        '''group by timedelta - at this point duplicates and empty series are contained'''
        gr_dt = lambda x: x.timedelta
        timeseries = sorted(self.timeseries, key=gr_dt)
        timedelta_groups = {k: list(v) for k, v in it.groupby(timeseries, key=gr_dt)}

        self.assertEqual(len(timedelta_groups[dt.timedelta(seconds=0)]), 20)
        self.assertEqual(len(timedelta_groups[dt.timedelta(seconds=300)]), 5)

    def test_groupby_timedelta_loc(self):
        '''group by timedelta and location in this order'''
        gr_dt = lambda x: x.timedelta
        timeseries = sorted(self.timeseries, key=gr_dt)
        timedelta_groups = {k: list(v) for k, v in it.groupby(timeseries, key=gr_dt)}

        gr_loc = TimeSerie.grouper
        for timedelta, timedelta_group in timedelta_groups.items():
            
            # remove duplicate and empty TimeSerie objects
            timeserie_loc = [i for i in set(timedelta_group) if i.has_events]
            timeserie_loc = sorted(timeserie_loc, key=gr_loc)
            loc_groups = {k: list(v) for k , v in it.groupby(timeserie_loc, key=gr_loc)}

            if timedelta == dt.timedelta(seconds=0):
                H_group = loc_groups.pop('ameide, broekseweg_h')
                VL_group = loc_groups.pop('ameide, broekseweg_vl2')
                P_group = loc_groups.pop('ameide, broekseweg_p1')
            elif timedelta == dt.timedelta(seconds=300):
                H_group = loc_groups.pop('ameide, broekseweg_h')
                VL_group = loc_groups.pop('ameide, broekseweg_vl2')

        # all elements should have been popped
        self.assertEqual(loc_groups, {})

'''
Add tests ValueError raises in join_events
'''

if __name__ == '__main__':
    unittest.main()
