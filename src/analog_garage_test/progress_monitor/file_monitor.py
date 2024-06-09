import pika
from datetime import datetime
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from _typeshed import SupportsWrite

from analog_garage_test.lib import constants
from analog_garage_test.lib.context_manager import RabbitMQContextManager
from analog_garage_test.lib.stats_message import StatsMessage
from analog_garage_test.progress_monitor.monitor import Monitor


class FileMonitor(RabbitMQContextManager, Monitor):
    """
    A progress monitor which writes status updates to the given output stream.
    The monitor does not handle opening or closing the stream.
    """

    TIME_FMT = "%H:%M:%S.%f"
    STATUS_FMT = """
----------------------{time}-----------------------
    NUM SUCCESSES: {successes}
     NUM FAILURES: {failures}
AVERAGE WAIT TIME: {wait_time}
     FAILURE RATE: {failure_rate}
------------------------------------------------------------
"""
    NAN_DEFAULT = "N/A"

    def __init__(self, refresh_secs: int, output_stream: "SupportsWrite[str]"):
        super().__init__(refresh_secs)
        self.output_stream = output_stream

    def listen(self):
        self.connection.consume(constants.STATS_QUEUE, self._receive_message)

    def refresh(self) -> None:
        """
        Refresh the progress monitor display by writing the current status
        to this monitor's output stream.
        """
        self.output_stream.write(self._get_status(datetime.now()))

    def _get_status(self, time: datetime) -> str:
        """
        Get the current status to be written to the output stream.

        Args:
            time (datetime): The time to stamp this status message with.
        """
        with self.data_lock:
            total_msgs = self.num_failures + self.num_successes
            if total_msgs:
                wait_time = self.total_time / total_msgs
                failure_rate = self.num_failures / total_msgs
            else:
                wait_time = failure_rate = self.NAN_DEFAULT
            return self.STATUS_FMT.format(
                time=time.strftime(self.TIME_FMT),
                successes=self.num_successes,
                failures=self.num_failures,
                wait_time=wait_time,
                failure_rate=failure_rate,
            )

    def _receive_message(
        self,
        channel: pika.channel.Channel,
        method: pika.spec.Basic.Deliver,
        properties: pika.spec.BasicProperties,
        body: bytes,
    ):
        self.update(StatsMessage.from_json_string(body.decode()))
        channel.basic_ack(delivery_tag=method.delivery_tag)
