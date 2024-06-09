class MockRabbitMQConnection:
    def __init__(self):
        self.connected = False

    def connect(self):
        self.connected = True

    def disconnect(self):
        self.connected = False

    def consume(self, queue, callback) -> None:
        pass

    def publish(self, queue, message) -> None:
        pass
