"""
Read PI-XML and convert to CSV

1. read xml-file
2. loop over all <series>-tags
3. use <header> and <event>-tags in dedicated object TimeSeries
4. write TimeSeries to disk if <event>-tags available
5. write back original xml without the events which are written to a separate csv
"""


import csv
import itertools as it
import xml.etree.ElementTree as ET

from FEWS_tools.lib.utils import ns
from FEWS_tools.lib.models import TimeSerie


def events_to_csv(events, filepath):
    with open(filepath, 'w', newline='') as fw:
        columns = events[0].keys()
        writer = csv.DictWriter(fw, columns)
        writer.writeheader()
        writer.writerows(events)


def convert_pixml2csv(basename, filename, output_folder=None, join_events=True):
    '''
    Convert pixml to csv - this function can be called from within FEWS.

    The basename is the directory where the exported filename is located.
    The filename is an exported PIXML-file by FEWS.
    The basename is used when the output_folder is not specified.
    The join_events argument specifies whether equidistant series
    should written to the same file.

    The original PIXML-file is copied to the output without
    the event tags and is stripped from duplicates and empty series.
    '''
    output_folder = output_folder or basename

    namespace = "http://www.wldelft.nl/fews/PI"
    tree = ET.parse(basename / filename)
    root = tree.getroot()

    gr_tdelta = lambda x: x.timedelta
    gr_subloc = TimeSerie.grouper

    timeseries = []
    for serie in root.findall(ns('series', namespace)):
        timeseries.append(TimeSerie(serie, namespace))
        root.remove(serie)

    # group by timedelta
    timeseries = sorted(timeseries, key=gr_tdelta)
    timedelta_groups = {
        k: list(v) for k, v in it.groupby(timeseries, key=gr_tdelta)}

    for timedelta, timedelta_group in timedelta_groups.items():
        # remove duplicate and empty TimeSerie objects
        timeserie_subloc = [i for i in set(timedelta_group) if i.has_events]
        timeserie_subloc = sorted(timeserie_subloc, key=gr_subloc)

        # grouped by timedelta and sublocation
        timedelta_subloc_groups = {
            k: list(v) for k, v in it.groupby(timeserie_subloc, key=gr_subloc)}

        # equidistant - possibility to write corrosponding series to same file
        if timedelta and join_events:
            for v in timedelta_subloc_groups.values():

                # join events on timeindex and update column names
                joined_events = TimeSerie.join_events(v)

                # write to disk
                filename = f'{v[0].get_group_key()}_T{timedelta.seconds / 60}.csv'
                filepath = output_folder / filename
                events_to_csv(joined_events, filepath)

                # update metafile
                for i in v:
                    root.append(i.series)

        # nonequidistant - write to single files
        else:
            for v in it.chain(*list(timedelta_subloc_groups.values())):

                # keep value, flag names?
                # v.update_events()

                # write to disk
                filepath = output_folder / f'{v.stationName}_{v.parameterId}.csv'
                events_to_csv(v.events, filepath)

                # update metafile
                root.append(v.series)

    tree.write(output_folder / f'meta{filename}')
