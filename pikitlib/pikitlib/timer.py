import threading
import time

class Timer:

    def __init__(self):
        self.startTime = self.getMsClock()
        self.running = False
        self.accumulatedTime = 0.0
        self.mutex = threading.RLock()

    def getMsClock(self):
        """
        returns system clock time in milliseconds
        """

        return int(round(time.time() * 1000))
    
    def get(self):
        """Get the current time from the timer. If the clock is running it is
        derived from the current system clock the start time stored in the
        timer class. If the clock is not running, then return the time when
        it was last stopped.
        :returns: Current time value for this timer in seconds
        """

        with self.mutex:
            if self.running:
                return (
                    self.accumulatedTime + (self.getMsClock() - self.startTime) / 1000
                )
            else:
                return self.accumulatedTime

    def reset(self) -> None:
        """Reset the timer by setting the time to 0.
        Make the timer startTime the current time so new requests will be
        relative now.
        """
        with self.mutex:
            self.accumulatedTime = 0.0
            self.startTime = self.getMsClock()
    
    def start(self) -> None:
        """Start the timer running.
        Just set the running flag to true indicating that all time requests
        should be relative to the system clock.
        """
        with self.mutex:
            self.startTime = self.getMsClock()
            self.running = True

    def stop(self) -> None:
        """Stop the timer.
        This computes the time as of now and clears the running flag, causing
        all subsequent time requests to be read from the accumulated time
        rather than looking at the system clock.
        """
        with self.mutex:
            temp = self.get()
            self.accumulatedTime = temp
            self.running = False

    def hasPeriodPassed(self, period: float) -> bool:
        """Check if the period specified has passed and if it has, advance the start
        time by that period. This is useful to decide if it's time to do periodic
        work without drifting later by the time it took to get around to checking.
 
        :param period: The period to check for (in seconds).
        :returns: If the period has passed.
        """

        with self.mutex:
            if self.get() > period:
                # Advance the start time by the period
                # Don't set it to the current time... we want to avoid drift
                self.startTime += period * 1000
                return True

            return False


