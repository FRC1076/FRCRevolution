# SPDX-License-Identifier: GPL-3.0-only

import struct

from ..common import PortInstance
from ..sensors.base import BaseSensorPortDriver


# noinspection PyUnusedLocal
def bumper_switch(port: PortInstance, cfg):
    sensor = BaseSensorPortDriver('BumperSwitch', port)

    def process_bumper(raw):
        assert len(raw) == 2
        return raw[0] == 1

    sensor.convert_sensor_value = process_bumper
    return sensor


# noinspection PyUnusedLocal
def hcsr04(port: PortInstance, cfg):
    sensor = BaseSensorPortDriver('HC_SR04', port)

    def process_ultrasonic(raw):
        assert len(raw) == 4
        (dst, ) = struct.unpack("<l", raw)
        if dst == 0:
            return None
        return dst

    sensor.convert_sensor_value = process_ultrasonic
    return sensor
