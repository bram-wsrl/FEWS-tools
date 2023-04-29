"""
Read PI-XML and convert to CSV

1. read xml-file
2. loop over all <series>-tags
3. use <header> and <event>-tags in dedicated object TimeSeries
4. write TimeSeries to disk if <event>-tags available
5. write back original xml without the events which are written to a separate csv
6. TODO[option]: join TimeSeries in same file when equidistant
6. TODO[option]: filter for duplicate series, write only once
"""


import csv
import xml.etree.ElementTree as ET

from lib.utils import ns


class TimeSerie:
    '''
    Objectification of header and event-tags of series element
    '''
    def __init__(self, series, namespace):
        self.series = series
        self.header = series.find(ns('header', namespace))

        self.events = []
        for event in series.findall(ns('event', namespace)):
            self.events.append(event.attrib)
            self.series.remove(event)

        self.has_events = True if len(self.events) else False
        self.filename = self.create_stem_filename(namespace)

    def __repr__(self):
        return f'<TimeSerie(events={len(self.events)})>'

    def create_stem_filename(self, namespace):
        stationname = self.header.find(ns('stationName', namespace))
        parameterid = self.header.find(ns('parameterId', namespace))
        return f'{stationname.text}_{parameterid.text}'

    def series_to_csv(self, basename):
        if self.has_events:
            filepath = basename / f'{self.filename}.csv'

            with open(filepath, 'w', newline='') as fw:
                columns = self.events[0].keys()
                writer = csv.DictWriter(fw, columns)
                writer.writeheader()
                writer.writerows(self.events)


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
