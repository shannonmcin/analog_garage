from os import getenv
from sys import stdout

from analog_garage_test.progress_monitor.cli_monitor import CliMonitor


def cli_monitor():
    with CliMonitor(
        refresh_secs=float(getenv("REFRESH_SECS")), output_stream=stdout
    ) as monitor:
        monitor.run()
