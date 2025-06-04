import os
from dotenv import load_dotenv
from src.shared.logger import logger


load_dotenv(override=True)

class Config:
    """Configuração centralizada do aplicativo."""

    RABBIT_MQ_QUEUE_SEARCH = os.getenv("SEARCH_QUEUE")
    MAX_RETRIES = int(os.getenv("SEARCH_MAX_RETRIES"))
    RETRY_DELAY = int(os.getenv("SEARCH_RETRY_DELAY"))

    @classmethod
    def validate(cls):
        """Validate the configuration settings."""
        if not cls.RABBIT_MQ_QUEUE_SEARCH:
            logger.error("SEARCH_QUEUE it is not set.")
            return False    
        if cls.MAX_RETRIES < 0:
            logger.error("SEARCH_MAX_RETRIES must be a non-negative integer.")
            return False
        if cls.RETRY_DELAY < 0:
            logger.error("SEARCH_RETRY_DELAY must be a non-negative integer.")
            return False  
        logger.info("Configuration validated successfully")
        return True


# Validar configuração ao importar o módulo
Config.validate()
