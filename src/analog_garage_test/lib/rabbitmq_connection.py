import pika
from typing import Callable, Optional
from analog_garage_test.lib import constants

# A callback that can be passed to various pika.channel.Channel methods that receive messages
RabbitMQCallback = Callable[
    [pika.channel.Channel, pika.spec.Basic.Deliver, pika.spec.BasicProperties, bytes],
    None,
]


class RabbitMQConnection:
    """
    Manages a RabbitMQ connection and provides methods to send and receive messages.
    """

    def __init__(self):
        self.connection = None
        self.channel = None

    def connect(self) -> bool:
        """
        If the connection is not already initialized, set up a new connection to RabbitMQ.
        """
        if not self.connection:
            self.connection = pika.BlockingConnection(
                pika.ConnectionParameters(host=constants.RABBITMQ_HOST)
            )
            self.channel = self.connection.channel()
            self.channel.basic_qos(prefetch_count=1)
            return True
        return False

    def disconnect(self) -> bool:
        """
        If the connection is initialized and open, close it.
        """
        conn_close = False
        channel_close = False
        if self.channel:  # and (self.channel.is_open or self.channel.is_opening):
            self.channel.close()
            self.channel = None
            conn_close = True
        if self.connection:  # and self.connection.is_open:
            self.connection.close()
            self.connection = None
            channel_close = True
        return conn_close and channel_close

    def consume(
        self,
        queue: str,
        callback: RabbitMQCallback,
        consumer_tag: Optional[str] = "consumer",
    ) -> None:
        """Consumes messages from the given queue, calling the given callback with each new message.

        Args:
            queue (str): The queue to listen for messages on.
            callback (RabbitMQCallback): The function to call with each new received message
        """
        self._declare_queue(queue)
        self.channel.basic_consume(
            queue=queue, on_message_callback=callback, consumer_tag=consumer_tag
        )
        self.channel.start_consuming()

    def publish(self, queue: str, message: str) -> None:
        """Publish a single message to the given queue.

        Args:
            queue (str): The queue to publish the message to.
            message (str): The message to publish.
        """
        self._declare_queue(queue)
        self.channel.basic_publish(exchange="", routing_key=queue, body=message)

    def _declare_queue(self, queue: str):
        self.channel.queue_declare(queue=queue, durable=True)
