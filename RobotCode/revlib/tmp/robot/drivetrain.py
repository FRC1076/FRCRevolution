# SPDX-License-Identifier: GPL-3.0-only
import itertools
from contextlib import suppress
from threading import Timer

from ..mcu.rrrc_control import RevvyControl
from .imu import IMU
from .ports.common import PortInstance
from .ports.motors.dc_motor import MotorStatus, MotorConstants
from ..utils.awaiter import AwaiterImpl, Awaiter
from ..utils.functions import clip
from ..utils.logger import get_logger
from ..utils.stopwatch import Stopwatch


# noinspection PyProtectedMember
class DrivetrainController:
    def __init__(self, drivetrain: 'DifferentialDrivetrain'):
        self._drivetrain = drivetrain
        self._awaiter = AwaiterImpl()
        self._awaiter.on_cancelled(self._drivetrain._apply_release)
        self._awaiter.on_result(self._drivetrain._apply_release)

    @property
    def awaiter(self) -> Awaiter:
        return self._awaiter

    def update(self):
        raise NotImplementedError


# noinspection PyProtectedMember
class TimeController(DrivetrainController):

    def __init__(self, drivetrain: 'DifferentialDrivetrain', timeout):
        super().__init__(drivetrain)

        t = Timer(timeout, self._awaiter.finish)
        self._awaiter.on_cancelled(t.cancel)
        t.start()

    def update(self):
        pass


# noinspection PyProtectedMember
class TurnController(DrivetrainController):
    Kp = 0.75

    def __init__(self, drivetrain: 'DifferentialDrivetrain', turn_angle, wheel_speed=None, power_limit=None):
        super().__init__(drivetrain)

        self._max_turn_wheel_speed = wheel_speed
        self._max_turn_power = power_limit

        self._target_angle = turn_angle + drivetrain.yaw
        self._last_yaw_change_time = Stopwatch()
        self._last_yaw_angle = None

    def update(self):
        yaw = self._drivetrain.yaw
        if self._last_yaw_angle != yaw:
            self._last_yaw_angle = yaw
            self._last_yaw_change_time.reset()
            error = self._target_angle - yaw
            if abs(error) < 1:
                # goal reached
                self._awaiter.finish()
            else:
                # Kp=10, saturate on max allowed wheel speed
                p = clip(error * self.Kp, -self._max_turn_wheel_speed, self._max_turn_wheel_speed)
                self._drivetrain._apply_speeds(-p, p, self._max_turn_power)

        elif self._last_yaw_change_time.elapsed > 3:
            # yaw angle has not changed for 3 seconds
            self._awaiter.cancel()


# noinspection PyProtectedMember
class MoveController(DrivetrainController):
    def __init__(self, drivetrain: 'DifferentialDrivetrain', left, right,
                 left_speed=None, right_speed=None, power_limit=None):
        super().__init__(drivetrain)

        drivetrain._apply_positions(left, right, left_speed, right_speed, power_limit)

    def update(self):
        if all(m.status == MotorStatus.GOAL_REACHED for m in self._drivetrain.motors):
            self._awaiter.finish()


class DifferentialDrivetrain:
    max_rpm = 120

    def __init__(self, interface: RevvyControl, imu: IMU):
        self._interface = interface
        self._motors = []
        self._left_motors = []
        self._right_motors = []

        self._log = get_logger('Drivetrain')
        self._imu = imu
        self._controller = None

    @property
    def yaw(self):
        return self._imu.yaw_angle

    @property
    def motors(self):
        return self._motors

    @property
    def left_motors(self):
        return self._left_motors

    @property
    def right_motors(self):
        return self._right_motors

    def _abort_controller(self):
        controller, self._controller = self._controller, None
        if controller:
            controller.awaiter.cancel()

    def reset(self):
        self._log('reset')
        self._abort_controller()

        for motor in self._motors:
            motor.on_status_changed.remove(self._on_motor_status_changed)
            motor.on_config_changed.remove(self._on_motor_config_changed)

        self._motors.clear()
        self._left_motors.clear()
        self._right_motors.clear()

    def _add_motor(self, motor: PortInstance):
        self._motors.append(motor)

        motor.on_status_changed.add(self._on_motor_status_changed)
        motor.on_config_changed.add(self._on_motor_config_changed)

    def add_left_motor(self, motor: PortInstance):
        self._log(f'Add motor {motor.id} to left side')
        self._left_motors.append(motor)
        self._add_motor(motor)

    def add_right_motor(self, motor: PortInstance):
        self._log(f'Add motor {motor.id} to right side')
        self._right_motors.append(motor)
        self._add_motor(motor)

    def _on_motor_config_changed(self, motor, _):
        # if a motor config changes, remove the motor from the drivetrain
        self._motors.remove(motor)

        with suppress(ValueError):
            self._left_motors.remove(motor)

        with suppress(ValueError):
            self._right_motors.remove(motor)

    def _on_motor_status_changed(self, _):
        if all(m.status == MotorStatus.BLOCKED for m in self._motors):
            self._abort_controller()
        else:
            controller = self._controller
            if controller:
                controller.update()

    def _apply_release(self):
        commands = itertools.chain(
            *(motor.create_set_power_command(0) for motor in self._left_motors),
            *(motor.create_set_power_command(0) for motor in self._right_motors)
        )
        self._interface.set_motor_port_control_value(bytes(commands))

    def _apply_speeds(self, left, right, power_limit):
        commands = itertools.chain(
            *(motor.create_set_speed_command(left, power_limit) for motor in self._left_motors),
            *(motor.create_set_speed_command(right, power_limit) for motor in self._right_motors)
        )
        self._interface.set_motor_port_control_value(bytes(commands))

    def _apply_positions(self, left, right, left_speed, right_speed, power_limit):
        commands = itertools.chain(
            *(motor.create_relative_position_command(left, left_speed, power_limit) for motor in self._left_motors),
            *(motor.create_relative_position_command(right, right_speed, power_limit) for motor in self._right_motors)
        )
        self._interface.set_motor_port_control_value(bytes(commands))

    def _process_unit_speed(self, speed, unit_speed):
        if unit_speed == MotorConstants.UNIT_SPEED_RPM:
            power = None
        elif unit_speed == MotorConstants.UNIT_SPEED_PWR:
            power, speed = speed, self.max_rpm
        else:
            raise ValueError(f'Invalid unit_speed: {unit_speed}')

        return power, speed

    def stop_release(self):
        self._log('stop and release')
        self._abort_controller()

        self._apply_release()

    def set_speeds(self, left, right, power_limit=None):
        self._log('set speeds')
        self._abort_controller()

        self._apply_speeds(left, right, power_limit)

    def set_speed(self, direction, speed, unit_speed=MotorConstants.UNIT_SPEED_RPM):
        self._log("set speed")
        self._abort_controller()
        multipliers = {
            MotorConstants.DIRECTION_FWD: 1,
            MotorConstants.DIRECTION_BACK: -1,
        }

        power, speed = self._process_unit_speed(speed, unit_speed)

        left_speed = right_speed = multipliers[direction] * speed
        self._apply_speeds(left_speed, right_speed, power)

    def drive(self, direction, rotation, unit_rotation, speed, unit_speed):
        self._log("drive")
        self._abort_controller()

        multipliers = {
            MotorConstants.DIRECTION_FWD:   1,
            MotorConstants.DIRECTION_BACK: -1,
        }

        power, speed = self._process_unit_speed(speed, unit_speed)

        if unit_rotation == MotorConstants.UNIT_SEC:
            left_speed = right_speed = speed * multipliers[direction]
            self._apply_speeds(left_speed, right_speed, power_limit=power)

            self._controller = TimeController(self, timeout=rotation)

        elif unit_rotation == MotorConstants.UNIT_ROT:
            left = right = 360 * rotation * multipliers[direction]
            left_speed = right_speed = speed

            self._controller = MoveController(self, left, right, left_speed, right_speed, power)
        else:
            raise ValueError(f'Invalid unit_rotation: {unit_rotation}')

        return self._controller.awaiter

    def turn(self, direction, rotation, unit_rotation, speed, unit_speed):
        self._log("turn")
        self._abort_controller()

        multipliers = {
            MotorConstants.DIRECTION_LEFT:  1,  # +ve number -> CCW turn
            MotorConstants.DIRECTION_RIGHT: -1,  # -ve number -> CW turn
        }

        power, speed = self._process_unit_speed(speed, unit_speed)

        if unit_rotation == MotorConstants.UNIT_SEC:

            right_speed = speed * multipliers[direction]
            self._apply_speeds(-1 * right_speed, right_speed, power_limit=power)

            self._controller = TimeController(self, timeout=rotation)

        elif unit_rotation == MotorConstants.UNIT_TURN_ANGLE:

            self._controller = TurnController(self,
                                              turn_angle=rotation * multipliers[direction],
                                              wheel_speed=speed,
                                              power_limit=power)
            self._controller.update()

        else:
            raise ValueError(f'Invalid unit_rotation: {unit_rotation}')

        return self._controller.awaiter
