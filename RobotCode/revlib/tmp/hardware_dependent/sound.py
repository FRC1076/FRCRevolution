# SPDX-License-Identifier: GPL-3.0-only

import subprocess
import threading

from ..utils.functions import map_values, clip
from ..utils.logger import get_logger


class SoundControlBase:
    def __init__(self, commands, default_volume):
        self._default_volume = default_volume
        self._commands = commands
        self._lock = threading.Lock()
        self._processes = []
        self._max_parallel_sounds = 4
        self._log = get_logger('SoundControl')

        self._run_command(self._commands['init_amp']).wait()

    def _run_command(self, commands):
        if type(commands) is str:
            commands = [commands]

        command = '; '.join(commands)
        return subprocess.Popen(command, stdout=subprocess.PIPE, shell=True)

    def _run_command_with_callback(self, commands, callback):
        def run_in_thread(args):
            process = self._run_command(args)
            with self._lock:
                self._processes.append(process)

            process.wait()

            with self._lock:
                self._processes.remove(process)

            callback()

        thread = threading.Thread(target=run_in_thread, args=(commands,))
        thread.start()

        return thread

    def _disable_amp_callback(self):
        self._log('Disable amp callback')
        with self._lock:
            self._log(f"Sounds playing: {len(self._processes)}")
            if not self._processes:
                self._log('Turning amp off')
                self._run_command(self._commands['disable_amp'])

    def set_volume(self, volume):
        scaled = map_values(clip(volume, 0, 100), 0, 100, -10239, 400)
        self._run_command(f'amixer cset numid=1 -- {scaled}')

    def reset_volume(self):
        self.set_volume(self._default_volume)

    def play_sound(self, sound, callback=None):
        if len(self._processes) <= self._max_parallel_sounds:
            self._log(f'Playing sound: {sound}')

            def cb():
                if callable(callback):
                    callback()

                self._disable_amp_callback()

            return self._run_command_with_callback([
                self._commands['enable_amp'],
                "mpg123 " + sound
            ], cb)
        else:
            self._log('Too many sounds are playing, skip')


class SoundControlV1(SoundControlBase):
    def __init__(self):
        super().__init__(commands={
            'init_amp': [
                'gpio -g mode 13 alt0',
                'gpio -g mode 22 out'
            ],
            'enable_amp': 'gpio write 3 1',
            'disable_amp': 'gpio write 3 0'
        }, default_volume=90)


class SoundControlV2(SoundControlBase):
    def __init__(self):
        super().__init__(commands={
            'init_amp': [
                'gpio -g mode 13 alt0',
                'gpio -g mode 22 out',
                'gpio write 3 1'
            ],
            'enable_amp': 'gpio write 3 0',
            'disable_amp': 'gpio write 3 1'
        }, default_volume=90)
