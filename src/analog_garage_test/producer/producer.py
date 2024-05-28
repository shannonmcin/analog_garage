from random import choices, randint
from string import printable

import pika

from analog_garage_test.lib.sms_message import SmsMessage
from analog_garage_test.lib.constants import RABBITMQ_HOST


class Producer:
    MAX_MSG_LEN = 100

    def __init__(self, num_messages: int = 1000, num_phone_numbers: int = 10):
        self.num_msgs = num_messages
        self.connection = None
        self.channel = None

    def connect(self):
        self.connection = pika.BlockingConnection(
            pika.ConnectionParameters(host=RABBITMQ_HOST)
        )
        self.channel = self.connection.channel()

    def stop(self):
        self.connection.close()

    def queue_messages(self) -> None:
        for i in range(self.num_msgs):
            self.queue_message("6034595127")

    def queue_message(self, phone_num: str) -> None:
        msg = str(self.generate_message(phone_num))
        self.channel.basic_publish(exchange="", routing_key="task_queue", body=msg)

    def generate_message(self, phone_num: str) -> SmsMessage:
        msg_len = randint(0, self.MAX_MSG_LEN)
        text = "".join(choices(printable, k=msg_len))
        return SmsMessage(text, phone_num)
