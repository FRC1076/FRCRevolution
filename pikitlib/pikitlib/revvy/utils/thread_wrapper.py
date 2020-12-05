# SPDX-License-Identifier: GPL-3.0-only

import time
import traceback
from threading import Event, Thread, Lock, RLock

from revvy.utils.logger import get_logger, LogLevel


def _call_callbacks(cb_list: list):
    while cb_list:
        cb = cb_list.pop()
        cb()


class ThreadWrapper:
    """
    Helper class to enable stopping/restarting threads from the outside
    Threads are not automatically stopped (as it is not possible), but a stop request can be read using the
    context object that is passed to the thread function
    """
    STOPPED = 0
    STARTING = 1
    RUNNING = 2
    STOPPING = 3
    EXITED = 4

    def __init__(self, func, name="WorkerThread"):
        self._log = get_logger(f'ThreadWrapper [{name}]')
        self._log('created')
        self._lock = Lock()  # lock used to ensure internal consistency
        self._interface_lock = RLock()  # prevent concurrent access. RLock so that callbacks may restart the thread
        self._func = func
        self._stopped_callbacks = []
        self._stop_requested_callbacks = []
        self._control = Event()  # used to wake up thread function when it is stopped
        self._stop_event = Event()  # used to signal thread function that it should stop
        self._thread_stopped_event = Event()  # caller can wait for thread to stop after calling stop()
        self._thread_stopped_event.set()
        self._thread_running_event = Event()  # caller can wait for the thread function to start running
        self._state = ThreadWrapper.STOPPED
        self._is_exiting = False
        self._thread = Thread(target=self._thread_func, args=())
        self._thread.start()

    def _wait_for_start(self):
        self._control.wait()
        self._control.clear()

        return self._state == ThreadWrapper.STARTING

    # noinspection PyBroadException
    def _thread_func(self):
        try:
            ctx = ThreadContext(self, self._stop_event)
            while self._wait_for_start():
                try:
                    self._enter_started()
                    self._func(ctx)
                except InterruptedError:
                    self._log('interrupted')
                except Exception:
                    self._log(traceback.format_exc(), LogLevel.ERROR)
                    self._log.flush()
                finally:
                    self._enter_stopped()
        finally:
            self._enter_stopped()
            self._state = ThreadWrapper.EXITED

    def _enter_started(self):
        with self._lock:
            self._stop_event.clear()
            self._state = ThreadWrapper.RUNNING
            self._thread_running_event.set()
        self._log('thread started')

    def _enter_stopped(self):
        self._log('stopped')
        with self._lock:
            self._state = ThreadWrapper.STOPPED
            self._thread_running_event.clear()
            _call_callbacks(self._stopped_callbacks)
            self._thread_stopped_event.set()

    @property
    def state(self):
        return self._state

    @property
    def is_running(self):
        return self._thread_running_event.is_set()

    def _start(self):
        if not self._is_exiting:
            self._log('starting')
            self._thread_stopped_event.clear()
            self._state = ThreadWrapper.STARTING
            self._control.set()

    def start(self):
        assert self._state != ThreadWrapper.EXITED, 'thread has already exited'
        assert not self._is_exiting, 'can not start an exiting thread'

        with self._interface_lock:
            with self._lock:
                if self._state in [ThreadWrapper.STARTING, ThreadWrapper.RUNNING]:
                    return self._thread_running_event

                if self._state == ThreadWrapper.STOPPING:
                    self._log('thread is stopping when start is called')
                    self.on_stopped(self._start)
                    return self._thread_running_event

            self._start()

            return self._thread_running_event

    def stop(self):
        with self._interface_lock:
            if self._state in [ThreadWrapper.STOPPING, ThreadWrapper.STOPPED, ThreadWrapper.EXITED]:
                self._log('stop already called')
            else:
                self._log('stopping')

                if self._state == ThreadWrapper.STARTING:
                    self._log('startup is in progress, wait for thread to start running')
                    self._thread_running_event.wait()

                with self._lock:
                    if self._state == ThreadWrapper.RUNNING:
                        self._log('request stop')

                        self._state = ThreadWrapper.STOPPING
                        self._stop_event.set()
                        call_callbacks = True
                    else:
                        call_callbacks = False

                if call_callbacks:
                    self._log('call stop requested callbacks')
                    _call_callbacks(self._stop_requested_callbacks)
                    self._log('stop requested callbacks finished')

            return self._thread_stopped_event

    def exit(self):
        with self._interface_lock:
            self._log('exiting')
            self._is_exiting = True

            evt = self.stop()
            self._log('waiting for stop event to be set')
            evt.wait()

            # wake up thread in case it is waiting to be started
            # thread will see STOPPED state and will exit
            self._control.set()

            self._log('joining thread')
            self._thread.join()
            self._log('exited')

    def on_stopped(self, callback):
        self._stopped_callbacks.append(callback)

    def on_stop_requested(self, callback):
        if self._state == ThreadWrapper.STOPPING:
            callback()
        else:
            self._stop_requested_callbacks.append(callback)


class ThreadContext:
    def __init__(self, thread: ThreadWrapper, stop_event: Event):
        self._stop_event = stop_event

        self.stop = thread.stop
        self.on_stopped = thread.on_stop_requested

    def sleep(self, s):
        if self._stop_event.wait(s):
            raise InterruptedError

    @property
    def stop_requested(self):
        return self._stop_event.is_set()


def periodic(fn, period, name="PeriodicThread"):
    """
    Call fn periodically

    :param fn: the function to run
    :param period: period time in seconds
    :param name: optional name to prefix the thread log messages
    :return: the created thread object
    """
    def _call_periodically(ctx: ThreadContext):
        _next_call = time.time()
        while not ctx.stop_requested:
            fn()

            _next_call += period
            diff = _next_call - time.time()
            if diff > 0:
                time.sleep(diff)
            else:
                # period was missed, let's restart
                _next_call = time.time()

    return ThreadWrapper(_call_periodically, name)
