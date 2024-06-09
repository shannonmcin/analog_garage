from random import choices, randint
from string import digits, printable

from analog_garage_test.lib import constants
from analog_garage_test.lib.context_manager import RabbitMQContextManager
from analog_garage_test.lib.sms_message import SmsMessage
from analog_garage_test.producer.producer import Producer


class RandomProducer(RabbitMQContextManager, Producer):
    MAX_MSG_LEN = 100

    def __init__(self, num_messages: int = 1000):
        super().__init__(num_messages)

    def queue_message(self, msg: SmsMessage) -> bool:
        """Queue the message by publishing it onto a RabbitMQ queue."""
        self.connection.publish(constants.MSG_QUEUE, msg.to_json_string())
        return True

    def get_next_message(self) -> SmsMessage:
        """
        Get the next message by randomly generating the text and phone number destination.
        """
        msg_len = randint(0, self.MAX_MSG_LEN)
        msg_text = "".join(choices(printable, k=msg_len))
        msg_dest = "".join(choices(digits, k=10))
        return SmsMessage(msg_text, msg_dest)
