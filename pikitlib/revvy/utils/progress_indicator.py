# SPDX-License-Identifier: GPL-3.0-only
import math

from revvy.robot.led_ring import RingLed
from revvy.utils.functions import map_values


def _progress(current, total, n_leds):
    if total == 0:
        return 0, 0

    if current >= total:
        return n_leds, -1

    total_progress = map_values(current, 0, total, 0, n_leds)
    full_leds = math.floor(total_progress)
    minor_progress = (math.floor(map_values(total_progress - full_leds, 0, 1, 0, n_leds + 1)) + full_leds) % n_leds

    return full_leds, minor_progress


class ProgressIndicator:
    def __init__(self, led: RingLed, end, major_color, minor_color):
        self._led = led

        self._major_color = major_color
        self._minor_color = minor_color
        self.end = end

        self.set_indeterminate()

    def update(self, progress):
        full_leds, minor_progress = _progress(progress, self.end, 12)
        leds = [self._major_color if led < full_leds else 0 for led in range(12)]
        if self._minor_color != 0 and minor_progress >= 0:
            leds[minor_progress] = self._minor_color

        self._led.display_user_frame(leds)

    def set_indeterminate(self):
        self._led.start_animation(RingLed.ColorWheel)
