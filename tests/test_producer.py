from analog_garage_test.lib.rabbitmq_connection import RabbitMQConnection
from analog_garage_test.lib.sms_message import SmsMessage
from analog_garage_test.producer import random_producer
from analog_garage_test.producer.random_producer import RandomProducer


def test_random_prod_get_next_message(mocker):
    def mock_choices(choose_from, k):
        res = []
        i = 0
        while len(res) < k:
            res.append(choose_from[i])
            i = (i + 1) % k
        return res

    mocker.patch.object(random_producer, "randint", return_value=100)
    mocker.patch.object(random_producer, "choices", side_effect=mock_choices)

    expected_text = "0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ!\"#$%&'()*+,-./:;<=>?@[\\]^_`{|}~ \t\n\r\x0b\x0c"
    expected_dst = "0123456789"
    p = RandomProducer()
    assert p.get_next_message() == SmsMessage(expected_text, expected_dst)


def test_queue_messages(mocker):
    num_msgs = 10
    msgs = [f"msg{i}" for i in range(num_msgs)]
    p = RandomProducer(10)
    mock_queue_msg = mocker.patch.object(p, "queue_message")
    mock_get_next = mocker.patch.object(p, "get_next_message", side_effect=msgs)

    p.queue_messages()

    expected_calls = [mocker.call(m) for m in msgs]
    assert mock_queue_msg.call_count == num_msgs
    mock_queue_msg.assert_has_calls(expected_calls)

    assert mock_get_next.call_count == num_msgs
