# SPDX-License-Identifier: GPL-3.0-only

from ..mcu.rrrc_control import RevvyControl
from ..utils.logger import get_logger


class McuStatusUpdater:
    mcu_updater_slots = {
        "motor_1": 0,
        "motor_2": 1,
        "motor_3": 2,
        "motor_4": 3,
        "motor_5": 4,
        "motor_6": 5,
        "sensor_1": 6,
        "sensor_2": 7,
        "sensor_3": 8,
        "sensor_4": 9,
        "battery": 10,
        "axl": 11,
        "gyro": 12,
        "yaw": 13,
        "reset": 14
    }
    """Class to read status from the MCU

    This class is the counterpart of McuStatusUpdater/McuStatusUpdaterWrapper implemented on the MCU and is used
    to enable and read specific data slots. It was designed to read multiple pieces of data in one run to decrease
    communication interface overhead, thus to allow lower latency updates"""
    def __init__(self, robot: RevvyControl):
        self._robot = robot
        self._is_enabled = [False] * 32
        self._is_enabled[self.mcu_updater_slots["reset"]] = True
        self._handlers = [None] * 32
        self._log = get_logger('McuStatusUpdater')

    def reset(self):
        self._log('reset all slots')
        self._is_enabled = [False] * 32
        self._is_enabled[self.mcu_updater_slots["reset"]] = True
        self._handlers = [None] * 32
        self._robot.status_updater_reset()

    def enable_slot(self, slot, callback):
        slot_idx = self.mcu_updater_slots[slot]
        if not self._is_enabled[slot_idx]:
            self._is_enabled[slot_idx] = True
            self._log(f'enable slot {slot_idx}')
            self._robot.status_updater_control(slot_idx, True)
        self._handlers[slot_idx] = callback

    def disable_slot(self, slot):
        slot_idx = self.mcu_updater_slots[slot]
        if self._is_enabled[slot_idx]:
            self._is_enabled[slot_idx] = False
            self._log(f'disable slot {slot_idx}')
            self._robot.status_updater_control(slot_idx, False)
        self._handlers[slot_idx] = None

    def read(self):
        data = self._robot.status_updater_read()

        idx = 0
        while idx < len(data):
            data_start = idx + 2
            slot, slot_length = data[idx:data_start]
            idx = data_start + slot_length

            handler = self._handlers[slot]
            if handler:
                # noinspection PyCallingNonCallable
                handler(data[data_start:idx])
