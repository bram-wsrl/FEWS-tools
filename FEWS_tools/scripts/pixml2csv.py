"""
Read PI-XML and convert to CSV

1. read xml-file
2. loop over all <series>-tags
3. use <header> and <event>-tags in dedicated object TimeSeries
4. write TimeSeries to disk if <event>-tags available
5. write back original xml without the events which are written to a separate csv
"""


import csv
import copy as cp
import itertools as it
import xml.etree.ElementTree as ET

from FEWS_tools import logger
from FEWS_tools.lib.utils import ns
from FEWS_tools.lib.models import TimeSerie


def events_to_csv(events, filepath):
    with open(filepath, 'w', newline='') as fw:
        columns = events[0].keys()
        writer = csv.DictWriter(fw, columns)
        writer.writeheader()
        writer.writerows(events)


def convert_pixml2csv(
        basename, xmlfilename, output_folder=None, join_events=True, H_to_SL=False):
    '''
    Convert pixml to csv - this function can be called from within FEWS.

    The basename is the directory where the exported xmlfilename is located.
    The xmlfilename is an exported PIXML-file by FEWS.
    The basename is used when the output_folder is not specified.
    The join_events argument specifies whether equidistant series
    should written to the same file.

    The original PIXML-file is copied to the output without
    the event tags and is stripped from duplicates and empty series.
    '''
    output_folder = output_folder or basename

    namespace = "http://www.wldelft.nl/fews/PI"
    tree = ET.parse(basename / xmlfilename)
    root = tree.getroot()

    # instantiate TimeSerie Objects
    timeseries = []
    for serie in root.iter(ns('series', namespace)):
        timeseries.append(TimeSerie(serie, namespace))
        logger.debug('Successfully parsed TimeSerie')

    # record original timeserie input order
    input_order = [f'{i.locationId}{i.parameterId}' for i in timeseries]

    # group functions
    gr_tdelta = lambda x: x.timedelta
    gr_subloc = TimeSerie.grouper

    # group by timedelta
    timeseries = sorted(timeseries, key=gr_tdelta)
    timedelta_groups = {
        k: list(v) for k, v in it.groupby(timeseries, key=gr_tdelta)}
    logger.debug(f'Grouped by {len(timedelta_groups)} timedeltas')

    for timedelta, timedelta_group in timedelta_groups.items():
        # remove duplicate and empty TimeSerie objects
        timeserie_subloc = [i for i in set(timedelta_group) if i.has_events]
        timeserie_subloc = sorted(timeserie_subloc, key=gr_subloc)
        logger.debug(f'Removed empty/duplicates and sorted remaining TimeSerie objects')

        # grouped by timedelta and sublocation
        timedelta_subloc_groups = {
            k: list(v) for k, v in it.groupby(timeserie_subloc, key=gr_subloc)}
        logger.debug(f'timestep {timedelta} contains {len(timedelta_subloc_groups)} subgroup(s)')

        # equidistant - possibility to write corresponding series to same file
        if timedelta and join_events:

            # get H_timeseries
            H_timeseries = []
            if H_to_SL:
                H_key = None
                for k, v in timedelta_subloc_groups.items():
                    if v[0].group_type == 'H':
                        H_key = k
                H_timeseries = timedelta_subloc_groups.pop(H_key, [])

            for k, v in timedelta_subloc_groups.items():
                # get original group_key as waterlevels might be added
                group_key = v[0].get_group_key()

                # possibly add waterlevels to same csv
                # make copies to keep the process symmetric
                v.extend([cp.deepcopy(i) for i in H_timeseries])

                # restore original sort order
                v = sorted(v, key=lambda x: input_order.index(f'{x.locationId}{x.parameterId}'))

                # join events on timeindex and update column names
                joined_events = TimeSerie.join_events(v)
                logger.debug(f'Joined events of {len(v)} TimeSerie objects')

                # write to disk
                csvfile = f'{group_key}_T{timedelta.seconds / 60:.0f}.csv'
                events_to_csv(joined_events, output_folder / csvfile)
                logger.info(f'Saved {csvfile}')

        # nonequidistant - write to single files
        else:
            for v in it.chain(*list(timedelta_subloc_groups.values())):

                # write to disk
                csvfile = f'{v.stationName}_{v.parameterId}.csv'
                events_to_csv(v.events, output_folder / csvfile)
                logger.info(f'Saved {csvfile}')
