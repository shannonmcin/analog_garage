import pika

from analog_garage_test.lib.constants import STATS_QUEUE
from analog_garage_test.lib.rabbitmq_connection import RabbitMQConnection
from analog_garage_test.lib.sms_message import SmsMessage
from analog_garage_test.lib.stats_message import StatsMessage
from analog_garage_test.sender.wait_sender import WaitSender


def test_receive_message(mocker):
    # test that it acks the message, calls handle message with the message, then publishes the resulting stats msg
    delivery_tag = "tag123"
    msg = SmsMessage("i am a message", "8675309")
    stats_msg = StatsMessage(True, 1.02)

    mock_channel = mocker.MagicMock(spec=pika.channel.Channel)
    mock_method = mocker.MagicMock(
        spec=pika.spec.Basic.Deliver, delivery_tag=delivery_tag
    )
    mock_props = mocker.MagicMock(spec=pika.spec.BasicProperties)

    s = WaitSender(1.0, 0.0)
    mock_handle_message = mocker.patch.object(
        s, "handle_message", return_value=stats_msg
    )
    mock_connection = mocker.patch.object(s, "connection")

    s._receive_message(
        mock_channel, mock_method, mock_props, msg.to_json_string().encode()
    )
    mock_channel.basic_ack.assert_called_once_with(delivery_tag=delivery_tag)
    mock_handle_message.assert_called_once_with(msg)
    mock_connection.publish.assert_called_once_with(
        STATS_QUEUE, stats_msg.to_json_string()
    )


def test_handle_message(mocker):
    from analog_garage_test.sender import wait_sender

    msg = SmsMessage("mash em, boil em, stick em in a stew", "9876543210")
    wait_time = 5.5

    s = WaitSender(wait_time, 0.5)
    mock_pick_wait_time = mocker.patch.object(
        s, "_pick_wait_time", return_value=wait_time
    )
    mock_sleep = mocker.patch.object(wait_sender, "sleep")
    mock_random = mocker.patch.object(wait_sender, "random", side_effect=[0.3, 0.7])

    # first random() result is 0.3 < 0.5, so it will be a failure
    fail_stats = s.handle_message(msg)
    mock_pick_wait_time.assert_called_once()
    mock_sleep.assert_called_once_with(wait_time)
    assert fail_stats == StatsMessage(False, wait_time)

    # second random() results is 0.7 > 0.5, so it will be a success
    success_stats = s.handle_message(msg)
    assert success_stats == StatsMessage(True, wait_time)
