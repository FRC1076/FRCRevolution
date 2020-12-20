from enum import Enum

from ..mcu.rrrc_control import RevvyControl
from ..utils.logger import get_logger


class ErrorType(Enum):
    HardFault = 0
    StackOverflow = 1
    AssertFailure = 2
    TestError = 3
    ImuError = 4
    I2CError = 5


class McuErrorReader:
    def __init__(self, interface: RevvyControl):
        self._log = get_logger('McuErrorReader')
        self._interface = interface
        self._count = interface.error_memory_read_count()
        self._log(f'Stored errors: {self._count}')

    def update(self):
        self._count = self._interface.error_memory_read_count()

    @property
    def count(self):
        return self._count

    def read_all(self):
        remaining = self._count
        last_error_idx = 0
        while remaining > 0:
            errors = self._interface.error_memory_read_errors(last_error_idx)
            if not errors:
                self._log('No errors returned, exiting')
                return

            remaining -= len(errors)
            self._log(f'{len(errors)} errors returned, {remaining} to read')

            for error_entry in errors:
                last_error_idx += 1
                yield error_entry

    def clear(self):
        self._log("Clearing error memory")
        self._interface.error_memory_clear()
        self.update()
        self._log(f"Error memory cleared, {self._count} errors present")
