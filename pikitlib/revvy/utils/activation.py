# SPDX-License-Identifier: GPL-3.0-only


class EdgeDetector:
    """
    >>> ed = EdgeDetector()
    >>> print(", ".join(map(str, [ed.handle(1), ed.handle(2), ed.handle(2), ed.handle(1)])))
    1, 1, 0, -1
    """
    def __init__(self):
        self._previous = 0

    def handle(self, value):
        previous, self._previous = self._previous, value

        if value > previous:
            return 1
        elif value < previous:
            return -1
        else:
            return 0


class EdgeTrigger:
    def __init__(self):
        self._rising_edge = None
        self._falling_edge = None
        self._detector = EdgeDetector()

    def on_rising_edge(self, callback):
        self._rising_edge = callback

    def on_falling_edge(self, callback):
        self._falling_edge = callback

    def handle(self, value):
        detection = self._detector.handle(value)
        if detection == 1:
            rising_edge_cb = self._rising_edge
            if rising_edge_cb:
                rising_edge_cb()

        elif detection == -1:
            falling_edge_cb = self._falling_edge
            if falling_edge_cb:
                falling_edge_cb()


class LevelTrigger:
    def __init__(self):
        self._high = None
        self._low = None

    def on_high(self, callback):
        self._high = callback

    def on_low(self, callback):
        self._low = callback

    def handle(self, value):
        if value > 0:
            high_cb = self._high
            if high_cb:
                high_cb()
        else:
            low_cb = self._low
            if low_cb:
                low_cb()


class ToggleButton:
    def __init__(self):
        self._on_enabled = None
        self._on_disabled = None
        self._edge_detector = EdgeDetector()
        self._is_enabled = False

    def _toggle(self):
        self._is_enabled = not self._is_enabled
        if self._is_enabled:
            on_enabled_cb = self._on_enabled
            if on_enabled_cb:
                on_enabled_cb()
        else:
            on_disabled_cb = self._on_disabled
            if on_disabled_cb:
                on_disabled_cb()

    def on_enabled(self, callback):
        self._on_enabled = callback

    def on_disabled(self, callback):
        self._on_disabled = callback

    def handle(self, value):
        if self._edge_detector.handle(0 if value <= 0 else 1) == 1:
            self._toggle()
