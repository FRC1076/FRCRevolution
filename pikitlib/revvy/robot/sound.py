# SPDX-License-Identifier: GPL-3.0-only
from functools import partial

from revvy.hardware_dependent.sound import SoundControlBase
from revvy.utils.logger import get_logger


class Sound:
    def __init__(self, sound_interface: SoundControlBase, sounds):
        self._sound = sound_interface
        self._playing = {}
        self._key = 0

        self._get_sound_path = sounds
        self.set_volume = sound_interface.set_volume
        self.reset_volume = sound_interface.reset_volume

        self._log = get_logger('Sound')

    def play_tune(self, name, callback=None):
        try:
            key, self._key = self._key, self._key + 1
            player_thread = self._sound.play_sound(self._get_sound_path(name), partial(self._finished, key))
            if player_thread:
                self._playing[key] = (player_thread, callback)
        except KeyError:
            self._log(f'Sound not found: {name}')

    def _finished(self, key):
        callback = self._playing[key][1]
        del self._playing[key]

        if callback:
            callback()

    def wait(self):
        playing = self._playing.copy()
        for play in playing.values():
            thread = play[0]
            thread.join()
