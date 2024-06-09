from abc import ABC, abstractmethod
from typing import Self

from analog_garage_test.lib.rabbitmq_connection import RabbitMQConnection


class StartStopContextManager(ABC):
    """
    An interface for a mixin that provides `start` and `stop` methods and uses them
    in context manager enter and exit methods.
    Public `start` and `stop` functions are provided for cases where the object
    is not used as a context manager.
    """

    @abstractmethod
    def start(self):
        pass

    @abstractmethod
    def stop(self):
        pass

    def __enter__(self) -> Self:
        self.start()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        self.stop()


class RabbitMQContextManager(StartStopContextManager):
    """
    A context manager mixin that keeps a RabbitMQ connection alive
    for the duration of the context.
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.connection = RabbitMQConnection()

    def start(self):
        self.connection.connect()

    def stop(self):
        self.connection.disconnect()
