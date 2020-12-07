# SPDX-License-Identifier: GPL-3.0-only

from revvy.mcu.rrrc_control import RevvyControl
from revvy.robot.ports.common import PortHandler, PortDriver

from revvy.utils.awaiter import Awaiter, AwaiterSignal, AwaiterImpl


class MotorConstants:
    DIRECTION_FWD = 0
    DIRECTION_BACK = 1
    DIRECTION_LEFT = 2
    DIRECTION_RIGHT = 3

    UNIT_ROT = 0
    UNIT_SEC = 1
    UNIT_DEG = 2
    UNIT_TURN_ANGLE = 3

    UNIT_SPEED_RPM = 0
    UNIT_SPEED_PWR = 1

    ACTION_STOP_AND_HOLD = 0
    ACTION_RELEASE = 1


def create_motor_port_handler(interface: RevvyControl):
    port_amount = interface.get_motor_port_amount()
    port_types = interface.get_motor_port_types()

    handler = PortHandler("Motor", interface, NullMotor, port_amount, port_types)
    handler._set_port_type = interface.set_motor_port_type

    return handler


class NullMotor(PortDriver):
    def __init__(self, port):
        super().__init__(port, 'NotConfigured')

    def on_port_type_set(self):
        pass

    @property
    def speed(self):
        return 0

    @property
    def position(self):
        return 0

    @property
    def power(self):
        return 0

    @property
    def is_moving(self):
        return False

    def set_speed(self, speed, power_limit=None):
        pass

    def set_position(self, position: int, speed_limit=None, power_limit=None, pos_type='absolute') -> Awaiter:
        return AwaiterImpl.from_state(AwaiterSignal.FINISHED)

    def set_power(self, power):
        pass

    def update_status(self, data):
        pass

    def stop(self, _=MotorConstants.ACTION_RELEASE):
        pass
