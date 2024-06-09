import os
from urllib import request

import pytest

from analog_garage_test.lib import constants


@pytest.fixture(scope="session")
def rabbitmq_server(docker_services):
    host_ip = os.environ["HOST_IP_ADDRESS"]

    def _check_up():
        try:
            with request.urlopen(f"http://{host_ip}:5672") as resp:
                return True
        except Exception as e:
            return "AMQP" in str(e)

    docker_services.wait_until_responsive(timeout=20.0, pause=1.0, check=_check_up)


@pytest.fixture(scope="function", autouse=True)
def rabbitmq_host(monkeypatch):

    host_ip = os.environ["HOST_IP_ADDRESS"]
    monkeypatch.setattr(constants, "RABBITMQ_HOST", host_ip)
