import time


class Stopwatch:
    """Class to measure elapsed time in seconds"""

    def __init__(self):
        """Initialize and start the stopwatch"""
        self._start_time = time.time()

    def reset(self):
        """Reset elapsed time"""
        self._start_time = time.time()

    @property
    def elapsed(self):
        """Read the elapsed time in seconds"""
        return time.time() - self._start_time
