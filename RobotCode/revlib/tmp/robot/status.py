# SPDX-License-Identifier: GPL-3.0-only

from enum import Enum
from ..mcu.rrrc_control import RevvyControl
from ..utils.logger import get_logger


class RobotStatus(Enum):
    StartingUp = 0
    NotConfigured = 1
    Configured = 2
    Configuring = 3
    Updating = 4
    Stopped = 5


class RemoteControllerStatus(Enum):
    NotConnected = 0
    ConnectedNoControl = 1
    Controlled = 2


class RobotStatusIndicator:
    MasterLeds = {
        RobotStatus.StartingUp: 0,
        RobotStatus.NotConfigured: 1,
        RobotStatus.Configured: lambda controller: 3 if controller == RemoteControllerStatus.Controlled else 2,
        RobotStatus.Configuring: 4,
        RobotStatus.Updating: 5,
        RobotStatus.Stopped: None
    }

    BluetoothLeds = {
        RemoteControllerStatus.NotConnected: 0,
        RemoteControllerStatus.ConnectedNoControl: 1,
        RemoteControllerStatus.Controlled: 1
    }

    def __init__(self, interface: RevvyControl):
        self._interface = interface

        self._log = get_logger('RobotStatusIndicator')

        self._robot_status = RobotStatus.StartingUp
        self._controller_status = RemoteControllerStatus.NotConnected

        self._master_led = None
        self._bluetooth_led = None

    def _update_master_led(self):
        led = RobotStatusIndicator.MasterLeds[self._robot_status]
        if led is None:
            return
        elif callable(led):
            led = led(self._controller_status)

        if led != self._master_led:
            self._master_led = led
            self._interface.set_master_status(led)

    def _update_bluetooth_led(self):
        led = RobotStatusIndicator.BluetoothLeds[self._controller_status]
        if led != self._bluetooth_led:
            self._bluetooth_led = led
            self._interface.set_bluetooth_connection_status(led)

    def update(self):
        self._update_master_led()
        self._update_bluetooth_led()

    @property
    def robot_status(self):
        return self._robot_status

    @robot_status.setter
    def robot_status(self, value):
        self._log(f'Robot: {self._robot_status} -> {value}')
        if self._robot_status != RobotStatus.Stopped:
            self._robot_status = value
            self._update_master_led()

    @property
    def controller_status(self):
        return self._controller_status

    @controller_status.setter
    def controller_status(self, value):
        if value != self._controller_status:
            self._log(f'Controller: {self._controller_status} -> {value}')
            self._controller_status = value

            self._update_master_led()
            self._update_bluetooth_led()
