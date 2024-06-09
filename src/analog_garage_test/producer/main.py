import os

from analog_garage_test.producer.random_producer import RandomProducer


def main():
    with RandomProducer(num_messages=int(os.environ["NUM_MESSAGES"])) as prod:
        prod.queue_messages()
