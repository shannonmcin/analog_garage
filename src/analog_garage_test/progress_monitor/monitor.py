import logging
from abc import ABC, abstractmethod
from threading import RLock, Thread, Event
from time import sleep
from typing import Optional

from analog_garage_test.lib.context_manager import StartStopContextManager
from analog_garage_test.lib.stats_message import StatsMessage


class Monitor(StartStopContextManager, ABC):
    """
    A progress monitor which tracks the statistics produced by senders,
    and displays an updated summary every `refresh_secs` seconds.
    """

    def __init__(self, refresh_secs: int = 5):
        self.data_lock = RLock()
        self.num_failures = 0
        self.num_successes = 0
        self.total_time = 0

        self.refresh_secs = refresh_secs

        self.logger = logging.getLogger(str(type(self)))

        # Thread will be used to run the refresh loop
        self.thread: Optional[Thread] = None
        # Event should be set from the main thread to stop the refresh loop
        self.event = Event()

    def run(self) -> None:
        """
        Start the refresh loop in the background thread and constantly listen
        for new messages in the main thread.
        """
        self.start_refresh_loop()
        self.listen()

    @abstractmethod
    def listen(self) -> None:
        """
        Constantly listen for new messages, and handle them as they come in.
        This method will run in the main thread and should be blocking/run infinitely.
        """
        pass

    @abstractmethod
    def refresh(self) -> None:
        """
        Refresh the progress monitor display with the current stats.
        """
        pass

    def stop(self) -> None:
        """
        Stop the progress monitor by stopping the resources controlled by the context manager,
        and ending the refresh loop thread.
        """
        super().stop()
        self.event.set()

    def update(self, msg: StatsMessage) -> None:
        """
        Update this monitor's stored statistics with the new information contained in the given message.
        """
        with self.data_lock:
            if msg.success:
                self.num_successes += 1
            else:
                self.num_failures += 1

            self.total_time += msg.time_waited

    def start_refresh_loop(self) -> None:
        """
        Start the refresh loop, which will call `refresh` in a background thread every `refresh_secs` seconds.
        This method is not blocking and does not monitor the thread once it is started.
        """

        def _refresh_loop():
            while not self.event.is_set():
                self.refresh()
                sleep(self.refresh_secs)

        self.event.clear()
        self.thread = Thread(target=_refresh_loop, daemon=True)
        self.thread.start()
