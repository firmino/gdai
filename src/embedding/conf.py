import os
import logging
from dotenv import load_dotenv
from pathlib import Path

# Carregar variáveis de ambiente
load_dotenv(override=True)
logger = logging.getLogger("CONFIG_EMBEDDING")


class Config:
    """Configuração centralizada do aplicativo."""

    FOLDER_EXTRACTED_DOC_PATH = os.getenv("EMBEDDING_EXTRACTED_DOCS_FOLDER_PATH")
    CHUNK_SIZE = int(os.getenv("EMBEDDING_CHUNK_SIZE"))
    CHUNK_OVERLAP = int(os.getenv("EMBEDDING_CHUNK_OVERLAP"))
    RABBIT_MQ_QUEUE_EMBEDDING_DOCUMENTS = os.getenv("EMBEDDING_QUEUE")
    MAX_RETRIES = int(os.getenv("EMBEDDING_MAX_RETRIES"))
    RETRY_DELAY = int(os.getenv("EMBEDDING_RETRY_DELAY"))
    MAX_MEMORY_USAGE_PERCENT = int(os.getenv("EMBEDDING_MAX_MEMORY_USAGE_PERCENT"))

    @classmethod
    def validate(cls):
        """Valida as configurações essenciais."""
      
        if not cls.FOLDER_EXTRACTED_DOC_PATH:
            raise ValueError("EMBEDDING_EXTRACTED_DOCS_FOLDER_PATH environment variable is not set")

        if not cls.FOLDER_EXTRACTED_DOC_PATH or not Path(cls.FOLDER_EXTRACTED_DOC_PATH).exists():
            raise ValueError(f"Extracted document path {cls.FOLDER_EXTRACTED_DOC_PATH} does not exist")
        
        if not cls.CHUNK_SIZE or cls.CHUNK_SIZE <= 0:
            raise ValueError("CHUNK_SIZE must be a positive integer")
        
        if not cls.CHUNK_OVERLAP or cls.CHUNK_OVERLAP < 0:
            raise ValueError("CHUNK_OVERLAP must be a non-negative integer")
        
        if not cls.RABBIT_MQ_QUEUE_EMBEDDING_DOCUMENTS:
            raise ValueError("RABBIT_MQ_QUEUE_EMBEDDING_DOCUMENTS environment variable is not set")


        logger.info("Configuration validated successfully")
        return True


# Validar configuração ao importar o módulo
Config.validate()
