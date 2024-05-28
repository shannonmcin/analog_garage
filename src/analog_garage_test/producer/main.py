from time import sleep

from analog_garage_test.producer.producer import Producer


def main():
    prod = Producer()
    prod.connect()
    prod.queue_messages()
    # while True:
    #     print("hello from producer please?")
    #     sleep(1)
