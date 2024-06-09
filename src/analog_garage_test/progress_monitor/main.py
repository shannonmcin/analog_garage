import os
import sys

from analog_garage_test.progress_monitor.file_monitor import FileMonitor


def get_output_loc():
    output_loc = os.environ["OUTPUT_LOCATION"]
    if output_loc == "stdout":
        return sys.stdout
    elif output_loc == "stderr":
        return sys.stderr
    else:
        return output_loc


def file_monitor():
    with FileMonitor(
        refresh_secs=float(os.environ["REFRESH_SECS"]), output_stream=get_output_loc()
    ) as monitor:
        monitor.run()
