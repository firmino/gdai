import os
import logging
from dotenv import load_dotenv
from pathlib import Path

load_dotenv(override=True)
logger = logging.getLogger("CONFIG_EXTRACTOR")

class Config:
    """Configuração centralizada do aplicativo."""

    # Caminhos de arquivo
    FOLDER_RAW_DOC_PATH = os.getenv("DOCUMENT_EXTRACTOR_FOLDER_RAW_DOC_PATH")
    FOLDER_EXTRACTED_DOC_PATH = os.getenv("DOCUMENT_EXTRACTOR_FOLDER_EXTRACTED_DOC_PATH")
    RABBIT_MQ_QUEUE_EXTRACT_DOCUMENT_DATA = os.getenv("EMBEDDING_QUEUE")
    MAX_FILE_SIZE_MB = int(os.getenv("DOCUMENT_EXTRACTOR_MAX_FILE_SIZE_MB")) 
    EXTRACTOR = os.getenv("DOCUMENT_EXTRACTOR_EXTRACTOR") 
    MAX_RETRIES = int(os.getenv("DOCUMENT_EXTRACTOR_MAX_RETRIES"))  
    RETRY_DELAY = int(os.getenv("DOCUMENT_EXTRACTOR_RETRY_DELAY"))  

    @classmethod
    def validate(cls):
        """Valida as configurações essenciais."""
        # Validação de caminhos
        if not cls.FOLDER_RAW_DOC_PATH or not Path(cls.FOLDER_RAW_DOC_PATH).exists():
            raise ValueError(f"Raw document path {cls.FOLDER_RAW_DOC_PATH} does not exist")

        if not cls.FOLDER_EXTRACTED_DOC_PATH or not Path(cls.FOLDER_EXTRACTED_DOC_PATH).exists():
            raise ValueError(f"Extracted document path {cls.FOLDER_EXTRACTED_DOC_PATH} does not exist")

        if not cls.RABBIT_MQ_QUEUE_EXTRACT_DOCUMENT_DATA:
            raise ValueError("RABBIT_MQ_QUEUE_EXTRACT_DOCUMENT_DATA environment variable is not set")

        if cls.MAX_FILE_SIZE_MB <= 0:
            raise ValueError("MAX_FILE_SIZE_MB must be a positive integer")

        if cls.MAX_RETRIES < 0:
            raise ValueError("DOCUMENT_EXTRACTOR_MAX_RETRIES must be a non-negative integer")
        if cls.RETRY_DELAY < 0:
            raise ValueError("DOCUMENT_EXTRACTOR_RETRY_DELAY must be a non-negative integer")

        logger.info("Configuration validated successfully")
        return True


# Validar configuração ao importar o módulo
Config.validate()
