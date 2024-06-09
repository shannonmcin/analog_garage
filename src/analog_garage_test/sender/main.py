import os

from analog_garage_test.sender.wait_sender import WaitSender


def main():
    with WaitSender(
        float(os.environ["MEAN_WAIT_TIME"]), float(os.environ["FAILURE_RATE"])
    ) as sender:
        sender.listen()
