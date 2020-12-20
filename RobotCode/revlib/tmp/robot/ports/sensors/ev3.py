import struct
from functools import partial

from typing import NamedTuple

from ...ports.common import PortInstance
from .base import BaseSensorPortDriver
from ....utils.functions import split, map_values


class Ev3DataType(NamedTuple):
    data_size: int
    read_pattern: str
    name: str


class Ev3Mode:
    @staticmethod
    def parse(mode_info):
        (nSamples, dataType, figures, decimals,
         raw_min, raw_max,
         pct_min, pct_max,
         si_min, si_max) = struct.unpack('<4b6f', mode_info)

        return Ev3Mode(nSamples, dataType, figures, decimals, raw_min, raw_max, pct_min, pct_max, si_min,
                       si_max)

    _type_info = (
        Ev3DataType(data_size=1, read_pattern='B', name='u8'),
        Ev3DataType(data_size=1, read_pattern='b', name='s8'),
        Ev3DataType(data_size=2, read_pattern='<H', name='u16'),
        Ev3DataType(data_size=2, read_pattern='<h', name='s16'),
        Ev3DataType(data_size=2, read_pattern='>h', name='s16be'),
        Ev3DataType(data_size=4, read_pattern='<l', name='s32'),
        Ev3DataType(data_size=4, read_pattern='>l', name='s32be'),
        Ev3DataType(data_size=4, read_pattern='<f', name='float')
    )

    def __init__(self, n_samples, data_type, figures, decimals, raw_min, raw_max, pct_min, pct_max, si_min, si_max):
        self._nSamples = n_samples
        self._dataType = data_type
        self._figures = figures
        self._decimals = decimals
        self._raw_min = raw_min
        self._raw_max = raw_max
        self._pct_min = pct_min
        self._pct_max = pct_max
        self._si_min = si_min
        self._si_max = si_max

    def _convert_single(self, value):
        return map_values(value, self._raw_min, self._raw_max, self._si_min, self._si_max)

    def convert(self, data):
        type_info = self._type_info[self._dataType]

        values = []
        for chunk in split(data, type_info.data_size):
            (value,) = struct.unpack(type_info.read_pattern, chunk)

            values.append(self._convert_single(value))

        return values

    def __str__(self) -> str:
        return f'Datasets: {self._nSamples}\n' \
               f'DataType: {self._type_info[self._dataType].name}\n' \
               f'Format: {self._figures}.{self._decimals}\n' \
               f'Raw: {self._raw_min}-{self._raw_max}\n' \
               f'%: {self._pct_min}-{self._pct_max}\n' \
               f'SI: {self._si_min}-{self._si_max}'


class Ev3UARTSensor(BaseSensorPortDriver):
    STATE_RESET = 0
    STATE_CONFIGURE = 1
    STATE_DATA = 2

    MODE_MASK = 0x07
    REMOTE_STATUS_MASK = 0xC0
    REMOTE_STATES = {
        0x00: STATE_RESET,
        0x40: STATE_CONFIGURE,
        0x80: STATE_DATA
    }

    def __init__(self, port: PortInstance, modes=None):
        super().__init__('EV3', port)
        self._state = self.STATE_RESET
        self._modes = modes
        self._current_mode = 0

    def select_mode(self, mode):
        if mode < len(self._modes):
            self._interface.write_sensor_port(self._port.id, [mode])
            self._current_mode = mode

    def convert_sensor_value(self, raw):
        if len(raw) == 0:
            return None

        try:
            state = self.REMOTE_STATES[raw[0] & self.REMOTE_STATUS_MASK]

            if self._state != state:
                if state == self.STATE_DATA:
                    if self._modes is None:
                        self._modes = self._get_modes()
                    self.on_configured()
                self._state = state

            if state == self.STATE_DATA:

                mode_idx = raw[0] & self.MODE_MASK
                if mode_idx == self._current_mode:
                    try:
                        mode = self._modes[mode_idx]

                        return mode.convert(raw[1:])
                    except IndexError:
                        return None
                else:
                    # handle case when mode switch does not happen (count wrong messages, reconfigure/reset)
                    pass

        except KeyError:
            return None

    def _get_modes(self):
        sensor_info = self._interface.read_sensor_info(self._port.id, 0)

        if sensor_info:
            (sensor_type, speed, nModes, nViews) = struct.unpack('<blbb', sensor_info)

            modes = []
            for i in range(1, nModes+1):
                mode_info = self._interface.read_sensor_info(self._port.id, i)
                mode = Ev3Mode.parse(mode_info)
                modes.append(mode)
                self.log(f'New mode: {i}/{nModes}')
                self.log(str(mode))
                self.log('===============')

            return modes

    def on_configured(self):
        pass


class Color:
    def __init__(self, color_id, name, rgb):
        self._id = color_id
        self._name = name
        self._rgb = rgb

    @property
    def id(self):
        return self._id

    @property
    def name(self):
        return self._name

    @property
    def rgb(self):
        return self._rgb

    def __str__(self) -> str:
        return self._name


def ev3_color(port: PortInstance, _):
    sensor = Ev3UARTSensor(port)

    color_map = [
        {'name': 'No color', 'rgb': '#000000'},
        {'name': 'Black',    'rgb': '#000000'},
        {'name': 'Blue',     'rgb': '#0000ff'},
        {'name': 'Green',    'rgb': '#00ff00'},
        {'name': 'Yellow',   'rgb': '#00ffff'},
        {'name': 'Red',      'rgb': '#ff0000'},
        {'name': 'White',    'rgb': '#ffffff'},
        {'name': 'Brown',    'rgb': '#ffff00'}
    ]

    # we'll replace the general convert_sensor_value method with a specialized one so copy the old one
    ev3_convert = sensor.convert_sensor_value

    def convert(raw):
        value = ev3_convert(raw)
        if value:
            color_id = int(value[0])
            color_data = color_map[color_id]
            return Color(color_id=color_id, name=color_data['name'], rgb=color_data['rgb'])

    sensor.convert_sensor_value = convert
    sensor.on_configured = partial(sensor.select_mode, 2)

    return sensor
