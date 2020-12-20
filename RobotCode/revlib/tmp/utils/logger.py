from collections import deque
from threading import Lock

from .stopwatch import Stopwatch

_log_lock = Lock()


class LogLevel:
    DEBUG = 0
    INFO = 1
    WARNING = 2
    ERROR = 3


levels = ('Debug', 'Info', 'Warning', 'Error')


class BaseLogger:
    def log(self, message, level):
        pass

    def flush(self):
        pass


class Logger(BaseLogger):
    def __init__(self, buffer_size=1000):
        self._sw = Stopwatch()
        self._buffer = deque(maxlen=buffer_size)
        self.minimum_level = LogLevel.INFO
        self.on_flush = None

    def log(self, message, level=LogLevel.INFO):
        if level >= self.minimum_level:
            message = f'{self._sw.elapsed} {levels[level]}: {message}'
            print(message)
            self._buffer.append(message + '\n')

    def flush(self):
        if self.on_flush:
            self.on_flush(self._buffer)
            self._buffer.clear()


class LogWrapper(BaseLogger):
    def __init__(self, logger: BaseLogger, tag, default_log_level=LogLevel.INFO):
        self._tag = tag + ': '
        self._logger = logger
        self._default_log_level = default_log_level

    def log(self, message, level=None):
        message = self._tag + message
        if level is None:
            level = self._default_log_level
        self._logger.log(message, level)

    def __call__(self, message, level=None):
        self.log(message, level)

    def flush(self):
        self._logger.flush()


logger = Logger()


def get_logger(tag, default_log_level=LogLevel.INFO, base=None):
    return LogWrapper(base or logger, tag, default_log_level)
