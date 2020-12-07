from enum import Enum
from threading import Lock, Condition


class AwaiterSignal(Enum):
    NONE = 0,
    CANCEL = 1,
    FINISHED = 2


class WaitableValue:
    def __init__(self, default=None):
        self._value = default
        self._condition = Condition(Lock())

    def exchange_if(self, expected, new):
        """Compare and exchange. Returns the stored value, stores the new one if the stored value equals the expected"""
        with self._condition:
            if self._value == expected:
                old, self._value = self._value, new
                self._condition.notify_all()
                return old
            else:
                return self._value

    def set(self, value):
        """Update the stored value. Wake up threads waiting for a value"""
        with self._condition:
            self._value = value
            self._condition.notify_all()

    def get(self):
        """Return the current value"""
        with self._condition:
            return self._value

    def wait(self, timeout=None):
        """Wait for a value to be set()"""
        with self._condition:
            if self._condition.wait(timeout):
                return self._value
            else:
                raise TimeoutError

    def map(self, callback):
        """Perform an operation on the current value"""
        with self._condition:
            return callback(self._value)


class Awaiter:
    def on_cancelled(self, callback):
        """Register a callback to be called when the awaiter is cancelled or times out"""
        raise NotImplementedError

    def on_result(self, callback):
        """Register a callback to be called when the awaiter has finished successfully"""
        raise NotImplementedError

    def cancel(self):
        """Cancel the pending awaiter. Does nothing if the awaiter has already finished"""
        raise NotImplementedError

    def wait(self, timeout=None):
        raise NotImplementedError


class AwaiterImpl(Awaiter):
    @classmethod
    def from_state(cls, state):
        return cls(state)

    def __init__(self, initial_state=AwaiterSignal.NONE):
        self._lock = Lock()
        self._signal = WaitableValue(initial_state)

        self._cancellation_callbacks = []
        self._completion_callbacks = []

    def _add_callback(self, callbacks: list, callback, call_for_state: AwaiterSignal):
        def _append_callback(current_state):
            if current_state == AwaiterSignal.NONE:
                callbacks.append(callback)
                return False
            elif current_state == call_for_state:
                return True

        call_immediately = self._signal.map(_append_callback)

        if call_immediately:
            callback()

    def on_cancelled(self, callback):
        self._add_callback(self._cancellation_callbacks, callback, AwaiterSignal.CANCEL)

    def on_result(self, callback):
        self._add_callback(self._completion_callbacks, callback, AwaiterSignal.FINISHED)

    def cancel(self):
        if self._signal.exchange_if(AwaiterSignal.NONE, AwaiterSignal.CANCEL) == AwaiterSignal.NONE:
            for callback in self._cancellation_callbacks:
                callback()

    def finish(self):
        """Mark the pending awaiter as finished."""
        if self._signal.exchange_if(AwaiterSignal.NONE, AwaiterSignal.FINISHED) == AwaiterSignal.NONE:
            for callback in self._completion_callbacks:
                callback()

    @property
    def state(self):
        return self._signal.get()

    def wait(self, timeout=None):
        """
        Wait for the operation to finish

        @param timeout:
        @return: True if the operation was finished by calling finish(), False if cancelled or timed out
        """
        if self._signal.get() != AwaiterSignal.NONE:
            return True

        try:
            self._signal.wait(timeout)
            return self._signal.get() == AwaiterSignal.FINISHED
        except TimeoutError:
            return False
