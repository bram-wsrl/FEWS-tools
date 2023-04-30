"""
Read PI-XML and convert to CSV

1. read xml-file
2. loop over all <series>-tags
3. use <header> and <event>-tags in dedicated object TimeSeries
4. write TimeSeries to disk if <event>-tags available
5. write back original xml without the events which are written to a separate csv


create function
"""


import csv
import itertools as it
import xml.etree.ElementTree as ET

from lib.utils import ns
from lib.models import TimeSerie

from tests import DATAPATH, OUTPUTPATH, PIXML_TIMESERIES_HL, PIXML_TIMESERIES_SL, PIXML_TIMESERIES_HL_SL


def events_to_csv(events, filepath):
    with open(filepath, 'w', newline='') as fw:
        columns = events[0].keys()
        writer = csv.DictWriter(fw, columns)
        writer.writeheader()
        writer.writerows(events)


basename = DATAPATH
filename = PIXML_TIMESERIES_HL_SL
output_folder = OUTPUTPATH

join_events = True
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
        for k, v in timedelta_subloc_groups.items():

            # join events on timeindex and update column names
            joined_events = TimeSerie.join_events(v)

            # write to disk
            filepath = output_folder / f'{k}_T{timedelta.seconds}.csv'
            events_to_csv(joined_events, filepath)

            # update metafile
            for i in v:
                root.append(i.series)

    # nonequidistant - write to single files
    else:
        for v in it.chain(*list(timedelta_subloc_groups.values())):

            # update column names
            v.update_events()

            # write to disk
            filepath = output_folder / f'{v.location}_{v.parameterId}.csv'
            events_to_csv(v.events, filepath)

            # update metafile
            root.append(v.series)

tree.write(output_folder / f'meta{filename}')




def convert_pixml_to_csv(basename, filename, output_folder=None):
    '''
    Collect metadata in one xml and write events to separate csv's
    '''
    output_folder = output_folder or basename

    namespace = "http://www.wldelft.nl/fews/PI"
    tree = ET.parse(basename / filename)
    root = tree.getroot()

    # get all series elements
    for series in root.findall(ns('series', namespace)):
        timeserie = TimeSerie(series, namespace)
        root.remove(series)

        # write if series contains events
        if timeserie.has_events:
            root.append(timeserie.series)
            timeserie.series_to_csv(output_folder)

    tree.write(output_folder / f'meta_{filename}')


if __name__ == '__main__':
    import sys
    import argparse
    from pathlib import Path

    sys.stdout.write('INFO - Hello, World!')

    parser = argparse.ArgumentParser()

    parser.add_argument('-b', '--basename', required=True, type=Path)
    parser.add_argument('-f', '--filename', required=True, type=str)
    parser.add_argument('-o', '--output', type=Path)
    parser.add_argument('-v', '--verbose', action='store_true')

    args = parser.parse_args()

    convert_pixml_to_csv(args.basename, args.filename, args.output)
