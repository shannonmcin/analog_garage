from os import getenv

from analog_garage_test.sender.wait_sender import WaitSender


def main():
    with WaitSender(
        float(getenv("MEAN_WAIT_TIME")), float(getenv("FAILURE_RATE"))
    ) as sender:
        sender.listen()
