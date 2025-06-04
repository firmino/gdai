import dramatiq
from src.shared.logger import logger
from dramatiq.brokers.rabbitmq import RabbitmqBroker
from src.shared.conf import Config


def _get_broker_url():
    """Gets the broker URL from environment variables """
    url = f"amqp://{Config.RABBIT_MQ_USER}:{Config.RABBIT_MQ_PASSWORD}@{Config.RABBIT_MQ_HOST}:{Config.RABBIT_MQ_PORT}/%2f"
    logger.error(f"Connecting to RabbitMQ broker at: {Config.RABBIT_MQ_HOST}:{Config.RABBIT_MQ_PORT}")
    return url

try:
    logger.error("Configuring RabbitMQ broker...")
    rabbitmq_broker = RabbitmqBroker(url=_get_broker_url())
    dramatiq.set_broker(rabbitmq_broker)
    logger.info("RabbitMQ broker configured successfully")
except Exception as e:
    logger.error(f"Failed to configure RabbitMQ broker: {str(e)}")
    raise
