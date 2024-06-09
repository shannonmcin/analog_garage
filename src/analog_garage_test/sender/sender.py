from abc import ABC, abstractmethod

from analog_garage_test.lib.context_manager import StartStopContextManager
from analog_garage_test.lib.sms_message import SmsMessage
from analog_garage_test.lib.stats_message import StatsMessage


class Sender(StartStopContextManager, ABC):
    """An abstract for an SMS Message Sender, which receives messages
    produced by Producers and reports statistics used by Monitors.
    """

    @abstractmethod
    def listen(self) -> None:
        pass

    @abstractmethod
    def handle_message(self, msg: SmsMessage) -> StatsMessage:
        """
        Process the given message and return a StatsMessage describing the result
        and length of processing.
        """
        pass
