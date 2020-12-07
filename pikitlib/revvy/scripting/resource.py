# SPDX-License-Identifier: GPL-3.0-only

from threading import Lock

from revvy.robot.ports.common import FunctionAggregator
from revvy.utils.logger import get_logger, LogLevel


class NullHandle:
    def __init__(self):
        pass

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        pass

    def __bool__(self):
        return False

    def interrupt(self):
        pass

    def release(self):
        pass


null_handle = NullHandle()


class ResourceHandle:
    def __init__(self, resource: 'Resource'):
        self._resource = resource
        self._on_interrupted = FunctionAggregator()
        self._on_released = FunctionAggregator()
        self._is_interrupted = False

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.release()

    def __bool__(self):
        return True

    @property
    def on_interrupted(self):
        return self._on_interrupted

    @property
    def on_released(self):
        return self._on_released

    def release(self):
        self.on_released()
        self._resource.release(self)

    def interrupt(self):
        self._is_interrupted = True
        self.on_interrupted()

    def run_uninterruptable(self, callback):
        with self._resource:
            if not self._is_interrupted:
                return callback()

    @property
    def is_interrupted(self):
        return self._is_interrupted


class Resource:
    def __init__(self, name='Resource'):
        self._lock = Lock()
        self._log = get_logger(f'Resource [{name}]', LogLevel.DEBUG)
        self._current_priority = -1
        self._active_handle = null_handle

    def __enter__(self):
        self._lock.__enter__()

    def __exit__(self, exc_type, exc_val, exc_tb):
        self._lock.__exit__(exc_type, exc_val, exc_tb)

    def reset(self):
        self._log('Reset')
        with self._lock:
            handle, self._active_handle = self._active_handle, null_handle

            if handle:
                self._log('Interrupting active resource handle')
                handle.interrupt()

            self._current_priority = -1

    def request(self, with_priority=0, on_taken_away=None):
        with self._lock:
            if not self._active_handle:
                self._log(f'create handle for priority {with_priority}')
                self._create_new_handle(with_priority, on_taken_away)
                return self._active_handle

            elif self._current_priority >= with_priority:
                self._log(f'taking from lower prio owner (request: {with_priority}, holder: {self._current_priority})')
                self._active_handle.interrupt()
                self._create_new_handle(with_priority, on_taken_away)
                return self._active_handle

            else:
                self._log(f'failed to take resource (request: {with_priority}, holder: {self._current_priority})')
                return null_handle

    def _create_new_handle(self, with_priority, on_taken_away):
        self._current_priority = with_priority
        self._active_handle = ResourceHandle(self)
        if on_taken_away:
            self._active_handle.on_interrupted.add(on_taken_away)

    def release(self, resource_handle):
        with self._lock:
            if self._active_handle == resource_handle:
                self._active_handle = null_handle
                self._current_priority = -1
                self._log('released')
            else:
                self._log('failed to release, not owned')
