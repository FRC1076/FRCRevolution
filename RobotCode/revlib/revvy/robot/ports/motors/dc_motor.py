import struct
from enum import Enum
from functools import partial

from revvy.robot.ports.common import PortInstance, PortDriver
from revvy.robot.ports.motor import MotorConstants
from revvy.utils.awaiter import AwaiterImpl, Awaiter
from revvy.utils.functions import clip


def motor_port_control_command(port_idx, *command_data):
    header = ((len(command_data) << 3) & 0xF8) | port_idx

    return (header, *command_data)


def dc_motor_power_request(port_idx, power):
    power = clip(power, -100, 100)
    if power < 0:
        power = 256 + power
    return motor_port_control_command(port_idx, 0, power)


def dc_motor_speed_request(port_idx, speed, power_limit=None):
    if power_limit is None:
        control = struct.pack("<f", speed)
    else:
        control = struct.pack("<ff", speed, power_limit)

    return motor_port_control_command(port_idx, 1, *control)


def dc_motor_position_request(port_idx, request_type, position, speed_limit=None, power_limit=None):
    position = int(position)

    if speed_limit is None:
        if power_limit is None:
            control = struct.pack("<l", position)
        else:
            control = struct.pack("<lbf", position, 0, power_limit)
    else:
        if power_limit is None:
            control = struct.pack("<lbf", position, 1, speed_limit)
        else:
            control = struct.pack("<lff", position, speed_limit, power_limit)

    return motor_port_control_command(port_idx, request_type, *control)


class MotorStatus(Enum):
    NORMAL = 0
    BLOCKED = 1
    GOAL_REACHED = 2


class DcMotorController(PortDriver):
    """Generic driver for dc motors"""
    def __init__(self, port: PortInstance, port_config):
        super().__init__(port, 'DcMotor')
        self._port = port
        self._port_config = port_config

        self._configure = partial(port.interface.set_motor_port_config, port.id)

        self._pos = 0
        self._speed = 0
        self._power = 0
        self._pos_offset = 0

        self._awaiter = None
        self._status = MotorStatus.NORMAL

        self._timeout = 0

        self.create_set_power_command = partial(dc_motor_power_request, self._port.id - 1)
        self.create_set_speed_command = partial(dc_motor_speed_request, self._port.id - 1)
        self.create_absolute_position_command = partial(dc_motor_position_request, self._port.id - 1, 2)
        self.create_relative_position_command = partial(dc_motor_position_request, self._port.id - 1, 3)

    def on_port_type_set(self):
        (posP, posI, posD, speedLowerLimit, speedUpperLimit) = self._port_config['position_controller']
        (speedP, speedI, speedD, powerLowerLimit, powerUpperLimit) = self._port_config['speed_controller']
        (decMax, accMax) = self._port_config['acceleration_limits']
        max_current = self._port_config['max_current']

        resolution = self._port_config['encoder_resolution'] * self._port_config['gear_ratio']

        config = [
            *struct.pack("<f", resolution),
            *struct.pack("<5f", posP, posI, posD, speedLowerLimit, speedUpperLimit),
            *struct.pack("<5f", speedP, speedI, speedD, powerLowerLimit, powerUpperLimit),
            *struct.pack("<ff", decMax, accMax),
            *struct.pack("<f", max_current)
        ]
        for x, y in self._port_config.get('linearity', {}).items():
            config += struct.pack('<ff', x, y)

        self.log(f'Sending configuration: {config}')

        self._configure(config)

    def _cancel_awaiter(self):
        awaiter, self._awaiter = self._awaiter, None
        if awaiter:
            self.log('Cancelling previous request')
            awaiter.cancel()

    @property
    def speed(self):
        return self._speed

    @property
    def pos(self):
        return self._pos + self._pos_offset

    @pos.setter
    def pos(self, val):
        self._pos_offset = val - self._pos
        self.log(f'setting position offset to {self._pos_offset}')

    @property
    def power(self):
        return self._power

    def set_power(self, power):
        self._cancel_awaiter()
        self.log('set_power')

        self._port.interface.set_motor_port_control_value(self.create_set_power_command(power))

    def set_speed(self, speed, power_limit=None):
        self._cancel_awaiter()
        self.log('set_speed')

        self._port.interface.set_motor_port_control_value(self.create_set_speed_command(speed, power_limit))

    def set_position(self, position: int, speed_limit=None, power_limit=None, pos_type='absolute') -> Awaiter:
        """
        @param position: measured in degrees, depending on pos_type
        @param speed_limit: maximum speed in degrees per seconds
        @param power_limit: maximum power in percent
        @param pos_type: 'absolute': turn to this angle, counted from startup; 'relative': turn this many degrees
        """
        self._cancel_awaiter()
        self.log('set_position')

        def _finished():
            self._awaiter = None

        def _canceled():
            self.set_power(0)

        awaiter = AwaiterImpl()
        awaiter.on_result(_finished)
        awaiter.on_cancelled(_canceled)

        self._awaiter = awaiter

        if pos_type == 'absolute':
            position -= self._pos_offset
            command = self.create_absolute_position_command(position, speed_limit, power_limit)
        elif pos_type == 'relative':
            command = self.create_relative_position_command(position, speed_limit, power_limit)
        else:
            raise ValueError(f'Invalid pos_type {pos_type}')

        self._port.interface.set_motor_port_control_value(command)

        return awaiter

    @property
    def status(self):
        return self._status

    def _update_motor_status(self, status: MotorStatus):
        self._status = status
        awaiter = self._awaiter
        if awaiter:
            if status == MotorStatus.NORMAL:
                pass
            elif status == MotorStatus.GOAL_REACHED:
                awaiter.finish()
            elif status == MotorStatus.BLOCKED:
                awaiter.cancel()

    def update_status(self, data):
        if len(data) == 10:
            status, self._power, self._pos, self._speed = struct.unpack('<bblf', data)

            self._update_motor_status(MotorStatus(status))
            self.on_status_changed(self._port)
        else:
            self.log(f'Received {len(data)} bytes of data instead of 10')

    def stop(self, action=MotorConstants.ACTION_RELEASE):
        self.log("stop")
        if action == MotorConstants.ACTION_STOP_AND_HOLD:
            self.set_speed(0)
        else:
            self.set_power(0)
