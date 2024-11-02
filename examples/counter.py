import ctypes
import time
from enum import IntEnum
from multiprocessing import Event, Value

from voxel.core.utils.logging import LoggingSubprocess


class State(IntEnum):
    """States for the counter process"""

    INIT = 0
    RUNNING = 1
    PAUSED = 2
    FINISHED = 3
    ERROR = 4


class Counter(LoggingSubprocess):
    """
    A counter process that counts up to a maximum value.

    :param name: Identifier for this counter
    :param max_count: The number to count up to
    :param log_queue: Queue for forwarding logs to main process
    """

    def __init__(self, name, max_count) -> None:
        super().__init__(name)
        self.max_count = max_count

        # State management
        self._state = Value(ctypes.c_int, State.INIT)
        self._resume_flag = Event()

    def _run(self) -> None:
        """Main process execution method"""
        try:
            self._transition_to(State.RUNNING)
            current = 0

            while current <= self.max_count:
                if self._state.value == State.PAUSED:
                    self._resume_flag.wait()  # Wait until resumed

                self.log.info(f"Count: {current} (State: {State(self._state.value).name})")
                current += 1
                time.sleep(0.5)

            self._transition_to(State.FINISHED)

        except Exception as e:
            self._transition_to(State.ERROR)
            self.log.error(f"Error: {str(e)}")

    def _transition_to(self, new_state):
        """Transition to a new state"""
        old_state = State(self._state.value)
        self._state.value = new_state
        self.log.info(f"State change: {old_state.name} -> {new_state.name}")

    def pause(self):
        """Pause the counter"""
        if self._state.value == State.RUNNING:
            self._transition_to(State.PAUSED)
            self._resume_flag.clear()
            self.log.debug("Pause requested")
        else:
            self.log.warning("Pause requested while not running")

    def resume(self):
        """Resume the counter if paused"""
        if self._state.value == State.PAUSED:
            self._transition_to(State.RUNNING)
            self._resume_flag.set()
            self.log.debug("Resume requested")
        else:
            self.log.warning("Resume requested while not paused")

    def start(self):
        """Override start to ensure proper state management"""
        if self._state.value == State.INIT:
            self.log.info("Starting counter")
            super().start()

    def get_state(self):
        """Get the current state"""
        return State(self._state.value)

    def is_finished(self):
        """Check if the counter has finished"""
        current_state = self.get_state()
        if current_state in (State.FINISHED, State.ERROR):
            self.join()  # Clean up the process
            return True
        return False


def main() -> None:

    # Create and start counter processes
    counter_names = ["A", "B", "C"]
    max_count = 5
    counters = [Counter(name, max_count) for name in counter_names]

    for counter in counters:
        counter.start()

    # Example of pausing/resuming the first counter
    # time.sleep(2)
    # counters[0].pause()
    # time.sleep(2)
    # counters[0].resume()

    # Keep running until all counters are done
    while any(not counter.is_finished() for counter in counters):
        time.sleep(0.1)


if __name__ == "__main__":
    from voxel.core.utils.logging import run_with_logging

    run_with_logging(main, subprocess=True, log_level="DEBUG")
