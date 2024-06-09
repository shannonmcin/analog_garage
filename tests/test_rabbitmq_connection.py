import time
from threading import Thread

from analog_garage_test.lib.rabbitmq_connection import RabbitMQConnection


from .conftest import rabbitmq_server


def test_connect_already_connected(rabbitmq_server):
    conn = RabbitMQConnection()
    assert conn.connect()
    first_connection = conn.connection
    first_channel = conn.channel

    # Calling connect again should be a no-op, and the internal connection+channel
    # should not be replaced
    assert not conn.connect()
    assert conn.connection is first_connection
    assert conn.channel is first_channel


def test_disconnect_already_disconnected(rabbitmq_server):
    conn = RabbitMQConnection()
    conn.connect()

    assert conn.disconnect()
    assert conn.connection is None
    assert conn.channel is None

    # Calling disconnect again should be a no-op
    assert not conn.disconnect()


def test_consume_and_publish_consumer_first(rabbitmq_server):
    """
    Make sure that a RabbitMQConnection can publish messages to and consume messages
    from a queue, when the consumer is started first.
    If the queue was not declared before the consumer was started, messages would
    be dropped.
    """
    expected_messages = ["message1", "message2", "message3", "message4", "message5"]
    msgs_received = []
    queue = "queue"
    tag = "test-consumer"

    # First start a consumer
    def thread_target():
        def callback(channel, method, props, msg):
            nonlocal msgs_received
            msgs_received.append(msg.decode())
            channel.basic_ack(delivery_tag=method.delivery_tag)
            if len(msgs_received) == len(expected_messages):
                channel.basic_cancel(tag)

        thread_conn = RabbitMQConnection()
        thread_conn.connect()
        thread_conn.consume(queue, callback, consumer_tag=tag)
        thread_conn.disconnect()

    Thread(target=thread_target, daemon=True).start()
    # wait for consumer to start
    time.sleep(3)

    # Then publish messages
    conn = RabbitMQConnection()
    conn.connect()
    for m in expected_messages:
        conn.publish(queue, m)

    # Wait for consumer to be cancelled
    time.sleep(5)
    conn.disconnect()

    assert set(msgs_received) == set(expected_messages)


def test_consume_and_publish_publisher_first(rabbitmq_server):
    """
    Make sure that a RabbitMQConnection can publish messages to and consume messages
    from a queue, when the messages are published before the consumer is started.
    If the queue was not declared before the messages were published, messages would
    be dropped.
    """
    expected_messages = ["message1", "message2", "message3", "message4", "message5"]
    msgs_received = []
    queue = "queue"
    tag = "test-consumer"

    # First publish messages
    conn = RabbitMQConnection()
    conn.connect()
    for m in expected_messages:
        conn.publish(queue, m)

    # Then start consumer
    def thread_target():
        def callback(channel, method, props, msg):
            nonlocal msgs_received
            msgs_received.append(msg.decode())
            channel.basic_ack(delivery_tag=method.delivery_tag)
            if len(msgs_received) == len(expected_messages):
                channel.basic_cancel(tag)

        thread_conn = RabbitMQConnection()
        thread_conn.connect()
        thread_conn.consume(queue, callback, consumer_tag=tag)
        thread_conn.disconnect()

    Thread(target=thread_target, daemon=True).start()

    # Wait for consumer to be cancelled
    time.sleep(5)

    conn.disconnect()
    assert set(msgs_received) == set(expected_messages)
