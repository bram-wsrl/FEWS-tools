import datetime as dt

from lib.utils import ns
from lib.dtypes import GroupSet



class TimeSerie(GroupSet):
    def __init__(self, series, namespace):
        self.series = series
        self.namespace = namespace

        self.header = series.find(ns('header', namespace))

        self.events = []
        for event in series.findall(ns('event', namespace)):
            self.events.append(event.attrib)
            self.series.remove(event)

        self.has_events = True if len(self.events) else False

        # group by (VL | P | H)
        group_key = f'{self.location}_{self.sublocation}'
        if self.sublocation.startswith('H'):
            group_key = f'{self.location}_H'

        # instantiate GroupSet
        super().__init__(group_key, self.locationId, self.parameterId)

    def __repr__(self):
        return f'<TimeSerie({self.location}, {self.locationId}, {self.parameterId})>'

    @property
    def location(self):
        stationName = self.header.find(ns('stationName', self.namespace))
        return stationName.text.split('_')[-2]

    @property
    def sublocation(self):
        stationName = self.header.find(ns('stationName', self.namespace))
        return stationName.text.split('_')[-1]

    @property
    def locationId(self):
        return self.header.find(ns('locationId', self.namespace)).text

    @property
    def parameterId(self):
        return self.header.find(ns('parameterId', self.namespace)).text

    @property
    def start_datetime(self):
        element = ns('startDate', self.namespace)
        date, time = self.header.find(element).attrib.values()
        return dt.datetime.strptime(f'{date} {time}', '%Y-%m-%d %H:%M:%S')

    @property
    def end_datetime(self):
        element = ns('endDate', self.namespace)
        date, time = self.header.find(element).attrib.values()
        return dt.datetime.strptime(f'{date} {time}', '%Y-%m-%d %H:%M:%S')

    @property
    def timestep_delta(self):
        timeStep = self.header.find(ns('timeStep', self.namespace)).attrib
        unit = timeStep['unit']
        multiplier = timeStep['multiplier']

        if unit == 'equidistant':
            return dt.timedelta()
        try:
            return dt.timedelta(**{f'{unit}s': int(multiplier)})
        except TypeError as e:
            raise e(f'{unit} is not implemented as a valid timestep.')

    def is_equidistant(self):
        return bool(self.timestep_delta)
