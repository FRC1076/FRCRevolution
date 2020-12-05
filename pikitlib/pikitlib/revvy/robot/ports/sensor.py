# SPDX-License-Identifier: GPL-3.0-only

from revvy.mcu.rrrc_control import RevvyControl
from revvy.robot.ports.common import PortHandler
from revvy.robot.ports.sensors.base import NullSensor


def create_sensor_port_handler(interface: RevvyControl):
    port_amount = interface.get_sensor_port_amount()
    port_types = interface.get_sensor_port_types()

    handler = PortHandler("Sensor", interface, NullSensor, port_amount, port_types)
    handler._set_port_type = interface.set_sensor_port_type

    return handler
