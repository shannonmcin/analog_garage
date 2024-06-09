import time
from datetime import datetime
from sys import stdout

from analog_garage_test.lib.rabbitmq_connection import RabbitMQConnection
from analog_garage_test.lib.stats_message import StatsMessage
from analog_garage_test.progress_monitor import monitor
from analog_garage_test.progress_monitor.monitor import Monitor
from analog_garage_test.progress_monitor.cli_monitor import CliMonitor


def test_update():
    success_msg = StatsMessage(True, 9.4)
    fail_msg = StatsMessage(False, 8.9)

    m = CliMonitor(1, output_stream=stdout)
    m.update(success_msg)
    assert m.num_successes == 1
    assert m.num_failures == 0
    assert m.total_time == 9.4

    m.update(fail_msg)
    assert m.num_successes == 1
    assert m.num_failures == 1
    assert m.total_time == 18.3


def test_start_refresh_loop(mocker):
    refresh_secs = 0.5
    num_loops = 4
    m = CliMonitor(refresh_secs, output_stream=stdout)
    mock_refresh = mocker.patch.object(m, "refresh")

    assert m.thread is None
    assert not m.event.is_set()

    m.start_refresh_loop()
    assert m.thread is not None
    assert m.thread.is_alive
    assert not m.event.is_set()

    # wait for the refresh loop to run num_loops times
    time.sleep(refresh_secs * num_loops)
    # stop the refresh loop by setting the event
    m.event.set()

    assert mock_refresh.call_count == num_loops


def test_cli_monitor_get_status():
    m = CliMonitor(1, output_stream=stdout)
    time = datetime.now()
    assert m._get_status(time) == CliMonitor.STATUS_FMT.format(
        time=time.strftime(CliMonitor.TIME_FMT),
        successes=0,
        failures=0,
        wait_time=CliMonitor.NAN_DEFAULT,
        failure_rate=CliMonitor.NAN_DEFAULT,
    )

    for stats_msg in [
        StatsMessage(True, 4.7),
        StatsMessage(True, 5.1),
        StatsMessage(False, 4.8),
        StatsMessage(True, 5.3),
        StatsMessage(False, 4.6),
    ]:
        m.update(stats_msg)

    assert m._get_status(time) == CliMonitor.STATUS_FMT.format(
        time=time.strftime(CliMonitor.TIME_FMT),
        successes=3,
        failures=2,
        wait_time=4.9,
        failure_rate=0.4,
    )
