from os import getenv

from analog_garage_test.producer.random_producer import RandomProducer


def main():
    with RandomProducer(num_messages=int(getenv("NUM_MESSAGES"))) as prod:
        prod.queue_messages()
