# SPDX-License-Identifier: GPL-3.0-only

from ...mcu.rrrc_control import RevvyControl
from .common import PortHandler
from .sensors.base import NullSensor


def create_sensor_port_handler(interface: RevvyControl):
    port_amount = interface.get_sensor_port_amount()
    port_types = interface.get_sensor_port_types()

    handler = PortHandler("Sensor", interface, NullSensor, port_amount, port_types)
    handler._set_port_type = interface.set_sensor_port_type

    return handler
