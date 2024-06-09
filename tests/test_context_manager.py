from analog_garage_test.lib import context_manager
from analog_garage_test.lib.context_manager import (
    RabbitMQConnection,
    RabbitMQContextManager,
)


def test_context_manager(mocker):
    mock_rabbitmq_conn = mocker.MagicMock(spec=RabbitMQConnection)
    mocker.patch.object(context_manager, "RabbitMQConnection").return_value = (
        mock_rabbitmq_conn
    )

    cm = RabbitMQContextManager()
    with cm:
        mock_rabbitmq_conn.connect.assert_called_once()
        mock_rabbitmq_conn.disconnect.assert_not_called()
    mock_rabbitmq_conn.disconnect.assert_called_once()
