# SPDX-License-Identifier: GPL-3.0-only

from collections import namedtuple
from threading import Event

from revvy.utils.activation import EdgeDetector
from revvy.utils.stopwatch import Stopwatch
from revvy.utils.thread_wrapper import ThreadWrapper, ThreadContext
from revvy.utils.logger import get_logger

RemoteControllerCommand = namedtuple('RemoteControllerCommand', ['analog', 'buttons'])


class RemoteController:
    def __init__(self):
        self._log = get_logger('RemoteController')

        self._analogActions = []  # ([channel], callback) pairs
        self._analogStates = []  # the last analog values, used to compare if a callback needs to be fired
        self._buttonHandlers = [EdgeDetector() for _ in range(32)]
        self._buttonActions = [None] * 32  # callbacks to be fired if a button gets pressed

        for handler in self._buttonHandlers:
            handler.handle(1)

    def reset(self):
        self._log('RemoteController: reset')
        self._analogActions.clear()
        self._analogStates.clear()

        self._buttonActions = [None] * 32

        for handler in self._buttonHandlers:
            handler.handle(1)

    def tick(self, message: RemoteControllerCommand):
        # handle analog channels
        if message.analog != self._analogStates:
            previous_analog_states, self._analogStates = self._analogStates, message.analog
            for channels, action in self._analogActions:
                try:
                    try:
                        changed = any(previous_analog_states[x] != message.analog[x] for x in channels)
                    except IndexError:
                        changed = True

                    if changed:
                        action([message.analog[x] for x in channels])
                except IndexError:
                    # looks like an action was registered for an analog channel that we didn't receive
                    self._log(f'Skip analog handler for channels {", ".join(map(str, channels))}')

        # handle button presses
        for handler, button, action in zip(self._buttonHandlers, message.buttons, self._buttonActions):
            pressed = handler.handle(button)
            if pressed == 1 and action:
                # noinspection PyCallingNonCallable
                action()

    def on_button_pressed(self, button, action: callable):
        self._buttonActions[button] = action

    def on_analog_values(self, channels, action):
        self._analogActions.append((channels, action))


class RemoteControllerScheduler:

    first_message_timeout = 2
    message_max_period = 0.5

    def __init__(self, rc: RemoteController):
        self._controller = rc
        self._data_ready_event = Event()
        self._controller_detected_callback = None
        self._controller_lost_callback = None
        self._message = None
        self._log = get_logger('RemoteControllerScheduler')

    def data_ready(self, message: RemoteControllerCommand):
        self._message = message
        self._data_ready_event.set()

    def _wait_for_message(self, ctx, wait_time):
        timeout = not self._data_ready_event.wait(wait_time)
        self._data_ready_event.clear()

        return not (timeout or ctx.stop_requested)

    def handle_controller(self, ctx: ThreadContext):
        self._log('Waiting for controller')

        self._data_ready_event.clear()

        ctx.on_stopped(self._data_ready_event.set)

        # wait for first message
        stopwatch = Stopwatch()
        if self._wait_for_message(ctx, self.first_message_timeout):
            self._log(f"Time to first message: {stopwatch.elapsed}s")
            if self._controller_detected_callback:
                self._controller_detected_callback()

            self._controller.tick(self._message)

            # wait for the other messages
            while self._wait_for_message(ctx, self.message_max_period):
                self._controller.tick(self._message)

        if not ctx.stop_requested:
            if self._controller_lost_callback:
                self._controller_lost_callback()

        # reset here, controller was lost or stopped
        self._controller.reset()
        self._log('exited')

    def on_controller_detected(self, callback: callable):
        self._log('Register controller found handler')
        self._controller_detected_callback = callback

    def on_controller_lost(self, callback: callable):
        self._log('Register controller lost handler')
        self._controller_lost_callback = callback


def create_remote_controller_thread(rcs: RemoteControllerScheduler):
    return ThreadWrapper(rcs.handle_controller, "RemoteControllerThread")
