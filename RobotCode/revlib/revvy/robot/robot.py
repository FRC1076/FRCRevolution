# SPDX-License-Identifier: GPL-3.0-only

import os
from functools import partial

from revvy.hardware_dependent.sound import SoundControlV1, SoundControlV2
from revvy.mcu.commands import BatteryStatus
from revvy.mcu.rrrc_control import RevvyTransportBase
from revvy.robot.drivetrain import DifferentialDrivetrain
from revvy.robot.imu import IMU
from revvy.robot.led_ring import RingLed
from revvy.robot.ports.motor import create_motor_port_handler
from revvy.robot.ports.sensor import create_sensor_port_handler
from revvy.robot.sound import Sound
from revvy.robot.status import RobotStatusIndicator, RobotStatus
from revvy.robot.status_updater import McuStatusUpdater
from revvy.scripting.robot_interface import RobotInterface
from revvy.utils.assets import Assets
from revvy.utils.logger import get_logger
from revvy.utils.stopwatch import Stopwatch
from revvy.utils.version import Version


class Robot(RobotInterface):
    @staticmethod
    def _default_bus_factory() -> RevvyTransportBase:
        from revvy.hardware_dependent.rrrc_transport_i2c import RevvyTransportI2C

        return RevvyTransportI2C(1)

    def __init__(self, bus_factory=None):
        if bus_factory is None:
            bus_factory = self._default_bus_factory
        self._bus_factory = bus_factory

        self._assets = Assets()
        self._assets.add_source(os.path.join('data', 'assets'))

        self._log = get_logger('Robot')

    def __enter__(self):
        self._comm_interface = self._bus_factory()

        self._robot_control = self._comm_interface.create_application_control()
        self._bootloader_control = self._comm_interface.create_bootloader_control()

        self._stopwatch = Stopwatch()

        # read versions
        while True:
            try:
                self._hw_version = self._robot_control.get_hardware_version()
                self._fw_version = self._robot_control.get_firmware_version()
                break
            except OSError:
                try:
                    self._hw_version = self._bootloader_control.get_hardware_version()
                    self._fw_version = Version('0.0.0')
                except OSError:
                    self._log('Failed to read robot version')

        from revvy.firmware_updater import update_firmware
        update_firmware(os.path.join('data', 'firmware'), self)

        # read version again in case it was updated
        self._fw_version = self._robot_control.get_firmware_version()

        self._log(f'Hardware: {self._hw_version}')
        self._log(f'Firmware: {self._fw_version}')

        setup = {
            Version('1.0'): SoundControlV1,
            Version('1.1'): SoundControlV1,
            Version('2.0'): SoundControlV2,
        }

        self._ring_led = RingLed(self._robot_control)
        self._sound = Sound(setup[self._hw_version](), self._assets.category_loader('sounds'))

        self._status = RobotStatusIndicator(self._robot_control)
        self._status_updater = McuStatusUpdater(self._robot_control)
        self._battery = BatteryStatus(0, 0, 0)

        self._imu = IMU()

        def _set_updater(slot_name, port, config_name):
            if config_name is None:
                self._status_updater.disable_slot(slot_name)
            else:
                self._status_updater.enable_slot(slot_name, port.update_status)

        self._motor_ports = create_motor_port_handler(self._robot_control)
        for port in self._motor_ports:
            port.on_config_changed.add(partial(_set_updater, f'motor_{port.id}'))

        self._sensor_ports = create_sensor_port_handler(self._robot_control)
        for port in self._sensor_ports:
            port.on_config_changed.add(partial(_set_updater, f'sensor_{port.id}'))

        self._drivetrain = DifferentialDrivetrain(self._robot_control, self._imu)

        self.update_status = self._status_updater.read
        self.ping = self._robot_control.ping

        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self._comm_interface.close()

    @property
    def assets(self):
        return self._assets

    @property
    def robot_control(self):
        return self._robot_control

    @property
    def bootloader_control(self):
        return self._bootloader_control

    @property
    def hw_version(self) -> Version:
        return self._hw_version

    @property
    def fw_version(self) -> Version:
        return self._fw_version

    @property
    def battery(self):
        return self._battery

    @property
    def imu(self):
        return self._imu

    @property
    def status(self):
        return self._status

    @property
    def motors(self):
        return self._motor_ports

    @property
    def sensors(self):
        return self._sensor_ports

    @property
    def drivetrain(self):
        return self._drivetrain

    @property
    def led(self):
        return self._ring_led

    @property
    def sound(self):
        return self._sound

    def play_tune(self, name):
        self._sound.play_tune(name)

    def time(self):
        return self._stopwatch.elapsed

    def reset(self):
        self._log('reset()')
        self._ring_led.start_animation(RingLed.BreathingGreen)
        self._status_updater.reset()

        def _process_battery_slot(data):
            assert len(data) == 4
            main_status, main_percentage, _, motor_percentage = data

            self._battery = BatteryStatus(chargerStatus=main_status, main=main_percentage, motor=motor_percentage)

        self._status_updater.enable_slot("battery", _process_battery_slot)
        self._status_updater.enable_slot("axl", self._imu.update_axl_data)
        self._status_updater.enable_slot("gyro", self._imu.update_gyro_data)
        self._status_updater.enable_slot("yaw", self._imu.update_yaw_angles)
        # TODO: do something useful with the reset signal
        self._status_updater.enable_slot("reset", lambda _: self._log('MCU reset detected'))

        self._drivetrain.reset()
        self._motor_ports.reset()
        self._sensor_ports.reset()
        self._sound.reset_volume()

        self._status.robot_status = RobotStatus.NotConfigured
        self._status.update()

    def stop(self):
        self._sound.wait()
