import pika

from random import normalvariate, random
from time import sleep
from typing import Optional

from analog_garage_test.lib import constants
from analog_garage_test.lib.context_manager import RabbitMQContextManager
from analog_garage_test.lib.sms_message import SmsMessage
from analog_garage_test.lib.stats_message import StatsMessage
from analog_garage_test.sender.sender import Sender


class WaitSender(RabbitMQContextManager, Sender):
    """
    A sender which handles each message by waiting a random amount of time,
    and then randomly choosing whether the message was successfully handled or not.
    """

    def __init__(
        self,
        mean_wait_time: float,
        failure_rate: float,
        wait_time_stddev: Optional[float] = None,
    ):
        super().__init__()
        self.mean_wait_time = mean_wait_time
        self.failure_rate = failure_rate
        self.wait_time_stddev = wait_time_stddev or 0.25 * mean_wait_time

    def listen(self):
        self.connection.consume(constants.MSG_QUEUE, self._receive_message)

    def handle_message(self, msg: SmsMessage) -> StatsMessage:
        """
        Handle the given message by waiting a random amount of time, and then
        randomly choosing if it's a failure.
        """
        wait_time = self._pick_wait_time()
        sleep(wait_time)
        return StatsMessage(random() > self.failure_rate, wait_time)

    def _pick_wait_time(self) -> float:
        """
        Pick a random amount of time to wait based on a normal distribution
        with this sender's mean and standard deviation.
        """
        return normalvariate(self.mean_wait_time, self.wait_time_stddev)

    def _receive_message(
        self,
        channel: pika.channel.Channel,
        method: pika.spec.Basic.Deliver,
        properties: pika.spec.BasicProperties,
        body: bytes,
    ) -> None:
        msg = SmsMessage.from_json_string(body.decode())
        stats_result = self.handle_message(msg)
        channel.basic_ack(delivery_tag=method.delivery_tag)

        self.connection.publish(constants.STATS_QUEUE, stats_result.to_json_string())
