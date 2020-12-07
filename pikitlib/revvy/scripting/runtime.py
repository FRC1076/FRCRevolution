# SPDX-License-Identifier: GPL-3.0-only

import time
from typing import NamedTuple

from revvy.scripting.robot_interface import RobotWrapper
from revvy.utils.logger import get_logger
from revvy.utils.thread_wrapper import ThreadContext, ThreadWrapper


class ScriptDescriptor(NamedTuple):
    name: str
    runnable: callable
    priority: int


class TimeWrapper:
    def __init__(self, ctx: ThreadContext):
        self.time = time.time
        self.sleep = ctx.sleep


class ScriptHandle:
    def _default_sleep(self, _):
        self.log('Error: default sleep called')
        raise Exception('Script not running')

    def __init__(self, owner: 'ScriptManager', script, name, global_variables: dict):
        self._owner = owner
        self._globals = global_variables.copy()
        self._inputs = {}
        self._runnable = script
        self.sleep = self._default_sleep
        self._thread = ThreadWrapper(self._run, f'ScriptThread: {name}')
        self.log = get_logger(f'Script: {name}')

        self.stop = self._thread.stop
        self.cleanup = self._thread.exit
        self.on_stopped = self._thread.on_stopped
        self.on_stopping = self._thread.on_stop_requested

        assert(callable(script))

        self.log('Created')

    @property
    def is_stop_requested(self):
        return self._thread.state in [ThreadWrapper.STOPPING, ThreadWrapper.STOPPED]

    @property
    def is_running(self):
        return self._thread.is_running

    def assign(self, name, value):
        self._globals[name] = value

    def _run(self, ctx):
        try:
            # script control interface
            def _terminate():
                self.stop()
                raise InterruptedError

            ctx.terminate = _terminate
            ctx.terminate_all = self._owner.stop_all_scripts

            self.sleep = ctx.sleep
            self.log("Starting script")
            self._runnable(Control=ctx, ctx=ctx, time=TimeWrapper(ctx), **self._inputs)
        except InterruptedError:
            self.log('Interrupted')
            raise
        finally:
            # restore to release reference on context
            self.log("Script finished")
            self.sleep = self._default_sleep

    def start(self, **kwargs):
        if not kwargs:
            self._inputs = self._globals
        else:
            self._inputs = {**self._globals, **kwargs}
        return self._thread.start()


class ScriptManager:
    def __init__(self, robot):
        self._robot = robot
        self._globals = {}
        self._scripts = {}
        self._log = get_logger('ScriptManager')

    def reset(self):
        self._log('stopping scripts')
        self.stop_all_scripts()
        for script in self._scripts.values():
            script.cleanup()

        self._log('resetting state')
        self._globals.clear()
        self._scripts.clear()

    def assign(self, name, value):
        self._globals[name] = value
        for script in self._scripts.values():
            script.assign(name, value)

    def add_script(self, script: ScriptDescriptor):
        if script.name in self._scripts:
            self._log(f'Stopping {script.name} before overriding')
            self._scripts[script.name].cleanup()

        self._log(f'New script: {script.name}')
        script_handle = ScriptHandle(self, script.runnable, script.name, self._globals)
        try:
            robot = self._robot
            interface = RobotWrapper(script_handle, robot.robot, robot.config, robot.resources, script.priority)
            script_handle.on_stopping(interface.release_resources)
            script_handle.on_stopped(interface.release_resources)
            script_handle.assign('robot', interface)
            self._scripts[script.name] = script_handle

            return script_handle
        except Exception:
            script_handle.cleanup()
            raise

    def __getitem__(self, name):
        return self._scripts[name]

    def stop_all_scripts(self):
        for script in self._scripts.values():
            script.stop()
