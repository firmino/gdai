import dramatiq 
from dramatiq.brokers.rabbitmq import RabbitmqBroker


rabbitmq_broker = RabbitmqBroker(url="amqp://rabbitmq:rabbitmq@localhost:5672/%2f")
dramatiq.set_broker(rabbitmq_broker)
