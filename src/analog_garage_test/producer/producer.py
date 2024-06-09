from abc import ABC, abstractmethod

from analog_garage_test.lib.sms_message import SmsMessage
from analog_garage_test.lib.context_manager import StartStopContextManager


class Producer(StartStopContextManager, ABC):
    """
    An interface for a producer which produces some number of messages and queues them.
    If messages are published to a shared resource, that resource should be managed in the
    `start` and `stop` methods.
    """

    def __init__(self, num_messages: int = 1000):
        self.num_messages = num_messages

    def queue_messages(self) -> None:
        for _ in range(self.num_messages):
            self.queue_message(self.get_next_message())

    @abstractmethod
    def get_next_message(self) -> SmsMessage:
        """Get the next message to be queued."""
        pass

    @abstractmethod
    def queue_message(self, msg: SmsMessage) -> bool:
        """Queue the given message to be consumed downstream."""
        pass
