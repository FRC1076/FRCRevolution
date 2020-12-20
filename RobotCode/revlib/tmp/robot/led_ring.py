# SPDX-License-Identifier: GPL-3.0-only

from ..mcu.rrrc_control import RevvyControl


class RingLed:
    Off = 0
    UserFrame = 1
    ColorWheel = 2
    ColorFade = 3
    BusyIndicator = 4
    BreathingGreen = 5
    Siren = 6
    TrafficLight = 7

    def __init__(self, interface: RevvyControl):
        self._interface = interface
        self._ring_led_count = self._interface.ring_led_get_led_amount()
        self._current_scenario = self.BreathingGreen

    @property
    def count(self):
        return self._ring_led_count

    @property
    def scenario(self):
        return self._current_scenario

    def start_animation(self, scenario):
        self._current_scenario = scenario
        self._interface.ring_led_set_scenario(scenario)

    def upload_user_frame(self, frame):
        self._interface.ring_led_set_user_frame(frame)

    def display_user_frame(self, frame):
        self.upload_user_frame(frame)
        self.start_animation(self.UserFrame)
