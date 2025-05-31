import os
import logging
from dotenv import load_dotenv


load_dotenv(override=True)
logger = logging.getLogger("CONFIG_SHARED")

class Config:
    """Centralized shared application configuration."""

    RABBIT_MQ_HOST = os.getenv("RABBIT_MQ_HOST")
    RABBIT_MQ_PORT = int(os.getenv("RABBIT_MQ_PORT"))
    RABBIT_MQ_USER = os.getenv("RABBIT_MQ_USER")
    RABBIT_MQ_PASSWORD = os.getenv("RABBIT_MQ_PASSWORD")

    PGVECTOR_USER = os.getenv("PGVECTOR_USER")  # Default PostgreSQL port
    PGVECTOR_PASSWORD = os.getenv("PGVECTOR_PASSWORD")
    PGVECTOR_DATABASE = os.getenv("PGVECTOR_DATABASE")
    PGVECTOR_HOST = os.getenv("PGVECTOR_HOST")
    PGVECTOR_PORT = int(os.getenv("PGVECTOR_PORT"))
    PGVECTOR_MIN_POOL_CONNECTIONS=int(os.getenv("PGVECTOR_MIN_POOL_CONNECTIONS"))
    PGVECTOR_MAX_POOL_CONNECTIONS=int(os.getenv("PGVECTOR_MAX_POOL_CONNECTIONS"))

    EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL")
    EMBEDDING_MODEL_API_KEY = os.getenv("EMBEDDING_API_KEY") 


    @classmethod
    def validate(cls):
        """Valida as configurações essenciais."""
        if not cls.RABBIT_MQ_HOST:
            logger.error("RABBIT_MQ_HOST is not set")
            return False
        if cls.RABBIT_MQ_PORT < 0:
            logger.error("RABBIT_MQ_PORT is not set")
            return False
        if not cls.RABBIT_MQ_USER:
            logger.error("RABBIT_MQ_USER is not set")
            return False
        if not cls.RABBIT_MQ_PASSWORD:
            logger.error("RABBIT_MQ_PASSWORD is not set")
            return False
        if not cls.PGVECTOR_USER:
            logger.error("PGVECTOR_USER is not set")
            return False
        if not cls.PGVECTOR_PASSWORD:
            logger.error("PGVECTOR_PASSWORD is not set")
            return False
        if not cls.PGVECTOR_DATABASE:
            logger.error("PGVECTOR_DATABASE is not set")
            return False
        if not cls.PGVECTOR_HOST:
            logger.error("PGVECTOR_HOST is not set")
            return False
        if cls.PGVECTOR_MIN_POOL_CONNECTIONS < 0:
            logger.error("PGVECTOR_MIN_POOL_CONNECTIONS is not set")
            return False
        if cls.PGVECTOR_MAX_POOL_CONNECTIONS < 0:
            logger.error("PGVECTOR_MAX_POOL_CONNECTIONS is not set")
            return False
        logger.info("Configuration validated successfully")
        return True


# Validar configuração ao importar o módulo
Config.validate()
