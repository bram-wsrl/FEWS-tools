import datetime as dt
from collections import ChainMap
from xml.etree.ElementTree import Element

from lib.utils import ns
from lib.dtypes import GroupSet


class TimeSerie(GroupSet):
    '''
    Abstraction of <series>-tag in PIXML_timeseries.

    The object subclasses GroupSet where the
    timeseries' location is the group_key and
    the unique sort keys are a combination of
    the locationId and parameterId.
    '''
    def __init__(self, series: Element, namespace: str) -> None:
        self.series = series
        self.namespace = namespace

        self.header = series.find(ns('header', namespace))

        # events to list of dicts
        self.events = []
        for event in series.findall(ns('event', namespace)):
            self.events.append(event.attrib)
            self.series.remove(event)

        # group by (VL | P | H)
        group_key = f'{self.location}_{self.sublocation}'
        if self.sublocation.startswith('H'):
            group_key = f'{self.location}_H'

        # instantiate GroupSet
        super().__init__(group_key, self.locationId, self.parameterId)

    def __repr__(self) -> str:
        return f'<TimeSerie({self.location}, {self.locationId}, {self.parameterId})>'

    @property
    def has_events(self) -> bool:
        return len(self.events) != 0

    @property
    def stationName(self) -> str:
        return self.header.find(ns('stationName', self.namespace)).text

    @property
    def location(self) -> str:
        return self.stationName.split('_')[-2]

    @property
    def sublocation(self) -> str:
        return self.stationName.split('_')[-1]

    @property
    def locationId(self) -> str:
        return self.header.find(ns('locationId', self.namespace)).text

    @property
    def parameterId(self) -> str:
        return self.header.find(ns('parameterId', self.namespace)).text

    @property
    def start_datetime(self) -> dt.datetime:
        element = ns('startDate', self.namespace)
        date, time = self.header.find(element).attrib.values()
        return dt.datetime.strptime(f'{date} {time}', '%Y-%m-%d %H:%M:%S')

    @property
    def end_datetime(self) -> dt.datetime:
        element = ns('endDate', self.namespace)
        date, time = self.header.find(element).attrib.values()
        return dt.datetime.strptime(f'{date} {time}', '%Y-%m-%d %H:%M:%S')

    @property
    def timedelta(self) -> dt.timedelta:
        timeStep = self.header.find(ns('timeStep', self.namespace)).attrib
        unit = timeStep['unit']

        if unit == 'nonequidistant':
            return dt.timedelta()
        try:
            multiplier = timeStep['multiplier']
            return dt.timedelta(**{f'{unit}s': int(multiplier)})
        except TypeError as e:
            raise e(f'{unit} is not implemented as a valid timestep.')

    @property
    def is_equidistant(self) -> bool:
        return bool(self.timedelta)

    def has_continuous_timeindex(self) -> bool:
        '''each timestep is present - start & end inclusive'''
        if self.is_equidistant:
            dt = self.timedelta
            start = self.start_datetime
            end = self.end_datetime
            return (end - start + dt) / dt == len(self.events)
        return False

    def update_events(self) -> None:
        '''update event keys with series specific names'''
        column_suffix = f'{self.parameterId}_{self.locationId}'
        for event in self.events:
            event[f'value_{column_suffix}'] = event.pop('value')
            event[f'flag_{column_suffix}'] = event.pop('flag')

    @staticmethod
    def join_events(timeseries) -> list[ChainMap]:
        '''join events on same timestep to a single collection'''
        if isinstance(timeseries, TimeSerie):
            timeseries = [timeseries]

        if not all(t.is_equidistant for t in timeseries):
            raise ValueError('Nonequidistant events cannot be joined.')

        if not len(set(t.start_datetime for t in timeseries)) == 1:
            raise ValueError('Equidistant events should have equal start times.')

        if not all(t.has_continuous_timeindex for t in timeseries):
            raise ValueError(f'Not all events have a continuous time index.')

        # update events with series specific names
        for timeserie in timeseries:
            timeserie.update_events()

        # construct single collection per timestep
        # insertion order is reversed because of reversal in chainmap
        events = [t.events for t in reversed(timeseries)]
        return [ChainMap(*i) for i in zip(*events)]
