# SPDX-License-Identifier: GPL-3.0-only

from ...ports.common import PortDriver, PortInstance


class NullSensor(PortDriver):
    def __init__(self, port):
        super().__init__(port, 'NotConfigured')

    def on_port_type_set(self):
        pass

    def update_status(self, data):
        pass

    @property
    def value(self):
        return 0

    @property
    def raw_value(self):
        return 0


class BaseSensorPortDriver(PortDriver):
    def __init__(self, driver, port: PortInstance):
        super().__init__(port, driver)
        self._port = port
        self._interface = port.interface
        self._value = None
        self._raw_value = None

    def on_port_type_set(self):
        pass

    @property
    def has_data(self):
        return self._value is not None

    def update_status(self, data):
        if len(data) == 0:
            self._value = None
            return

        if self._raw_value == data:
            return

        self._raw_value = data
        converted = self.convert_sensor_value(data)

        self._raw_value = data
        if converted is not None:
            self._value = converted

        self.on_status_changed(self._port)

    @property
    def value(self):
        return self._value

    @property
    def raw_value(self):
        return self._raw_value

    def convert_sensor_value(self, raw): raise NotImplementedError
