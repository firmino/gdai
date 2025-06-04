"""
Centralized configuration management for the G-DAI project.

This module provides a unified configuration system with environment variable loading,
validation, and access to settings organized by component.
"""

import os
from pathlib import Path
from typing import Dict, Any, Optional, Union, TypeVar, Type
from dotenv import load_dotenv
from src.shared.logger import logger

# Load environment variables with override to prioritize local .env file
load_dotenv(override=True)

# Type variable for component config classes
T = TypeVar('T', bound='BaseConfig')


class BaseConfig:
    """Base configuration class with validation support."""
    
    @classmethod
    def validate(cls) -> bool:
        """
        Default validation method to be overridden by subclasses.
        
        Returns:
            bool: True if configuration is valid
        """
        return True


class DatabaseConfig(BaseConfig):
    """Database connection configuration."""
    
    PGVECTOR_USER = os.getenv("PGVECTOR_USER")
    PGVECTOR_PASSWORD = os.getenv("PGVECTOR_PASSWORD")
    PGVECTOR_DATABASE = os.getenv("PGVECTOR_DATABASE")
    PGVECTOR_HOST = os.getenv("PGVECTOR_HOST")
    PGVECTOR_PORT = int(os.getenv("PGVECTOR_PORT", "5432"))
    PGVECTOR_MIN_POOL_CONNECTIONS = int(os.getenv("PGVECTOR_MIN_POOL_CONNECTIONS", "2"))
    PGVECTOR_MAX_POOL_CONNECTIONS = int(os.getenv("PGVECTOR_MAX_POOL_CONNECTIONS", "10"))
    
    @classmethod
    def validate(cls) -> bool:
        """Validate database configuration."""
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
            logger.error("PGVECTOR_MIN_POOL_CONNECTIONS is not set properly")
            return False
        if cls.PGVECTOR_MAX_POOL_CONNECTIONS < 0:
            logger.error("PGVECTOR_MAX_POOL_CONNECTIONS is not set properly")
            return False
        
        return True


class BrokerConfig(BaseConfig):
    """Message broker configuration."""
    
    RABBIT_MQ_HOST = os.getenv("RABBIT_MQ_HOST")
    RABBIT_MQ_PORT = int(os.getenv("RABBIT_MQ_PORT", "5672"))
    RABBIT_MQ_USER = os.getenv("RABBIT_MQ_USER")
    RABBIT_MQ_PASSWORD = os.getenv("RABBIT_MQ_PASSWORD")
    
    @classmethod
    def validate(cls) -> bool:
        """Validate message broker configuration."""
        if not cls.RABBIT_MQ_HOST:
            logger.error("RABBIT_MQ_HOST is not set")
            return False
        if cls.RABBIT_MQ_PORT < 0:
            logger.error("RABBIT_MQ_PORT is invalid")
            return False
        if not cls.RABBIT_MQ_USER:
            logger.error("RABBIT_MQ_USER is not set")
            return False
        if not cls.RABBIT_MQ_PASSWORD:
            logger.error("RABBIT_MQ_PASSWORD is not set")
            return False
        
        return True


class AIModelsConfig(BaseConfig):
    """AI models configuration."""
    
    # Embedding model settings
    EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL")
    EMBEDDING_MODEL_API_KEY = os.getenv("EMBEDDING_API_KEY")
    
    # LLM model settings
    LLM_MODEL = os.getenv("SEARCH_LLM_MODEL")
    LLM_MODEL_API_KEY = os.getenv("SEARCH_LLM_API_KEY")
    LLM_MAX_TOKENS = int(os.getenv("SEARCH_LLM_MAX_TOKENS", "1000"))
    LLM_TEMPERATURE = float(os.getenv("SEARCH_LLM_TEMPERATURE", "0.7"))
    
    @classmethod
    def validate(cls) -> bool:
        """Validate AI models configuration."""
        if not cls.EMBEDDING_MODEL:
            logger.error("EMBEDDING_MODEL is not set")
            return False
        if not cls.EMBEDDING_MODEL_API_KEY:
            logger.error("EMBEDDING_API_KEY is not set")
            return False
        if not cls.LLM_MODEL:
            logger.error("SEARCH_LLM_MODEL is not set")
            return False
        if not cls.LLM_MODEL_API_KEY:
            logger.error("SEARCH_LLM_API_KEY is not set")
            return False
        if cls.LLM_MAX_TOKENS <= 0:
            logger.error("SEARCH_LLM_MAX_TOKENS must be positive")
            return False
        if cls.LLM_TEMPERATURE < 0 or cls.LLM_TEMPERATURE > 1.0:
            logger.error("SEARCH_LLM_TEMPERATURE must be between 0.0 and 1.0")
            return False
        
        return True


class ExtractorConfig(BaseConfig):
    """Document extraction configuration."""
    
    FOLDER_RAW_DOC_PATH = os.getenv("DOCUMENT_EXTRACTOR_FOLDER_RAW_DOC_PATH")
    FOLDER_EXTRACTED_DOC_PATH = os.getenv("DOCUMENT_EXTRACTOR_FOLDER_EXTRACTED_DOC_PATH")
    MAX_FILE_SIZE_MB = int(os.getenv("DOCUMENT_EXTRACTOR_MAX_FILE_SIZE_MB", "100"))
    EXTRACTOR = os.getenv("DOCUMENT_EXTRACTOR", "docling")
    MAX_RETRIES = int(os.getenv("DOCUMENT_EXTRACTOR_MAX_RETRIES", "3"))
    RETRY_DELAY = int(os.getenv("DOCUMENT_EXTRACTOR_RETRY_DELAY", "5"))
    QUEUE = os.getenv("DOCUMENT_EXTRACTOR_QUEUE", "extract_data")
    
    @classmethod
    def validate(cls) -> bool:
        """Validate document extractor configuration."""
        if not cls.FOLDER_RAW_DOC_PATH or not Path(cls.FOLDER_RAW_DOC_PATH).exists():
            logger.error(f"Raw document path {cls.FOLDER_RAW_DOC_PATH} does not exist")
            return False
        if not cls.FOLDER_EXTRACTED_DOC_PATH or not Path(cls.FOLDER_EXTRACTED_DOC_PATH).exists():
            logger.error(f"Extracted document path {cls.FOLDER_EXTRACTED_DOC_PATH} does not exist")
            return False
        if not cls.QUEUE:
            logger.error("DOCUMENT_EXTRACTOR_QUEUE environment variable is not set")
            return False
        if cls.MAX_FILE_SIZE_MB <= 0:
            logger.error("MAX_FILE_SIZE_MB must be a positive integer")
            return False
        if cls.MAX_RETRIES < 0:
            logger.error("DOCUMENT_EXTRACTOR_MAX_RETRIES must be a non-negative integer")
            return False
        if cls.RETRY_DELAY < 0:
            logger.error("DOCUMENT_EXTRACTOR_RETRY_DELAY must be a non-negative integer")
            return False
        
        return True


class EmbeddingConfig(BaseConfig):
    """Document embedding configuration."""
    
    FOLDER_EXTRACTED_DOC_PATH = os.getenv("EMBEDDING_EXTRACTED_DOCS_FOLDER_PATH")
    CHUNK_SIZE = int(os.getenv("EMBEDDING_CHUNK_SIZE", "1000"))
    CHUNK_OVERLAP = int(os.getenv("EMBEDDING_CHUNK_OVERLAP", "10"))
    QUEUE = os.getenv("EMBEDDING_QUEUE", "embedding_documents")
    MAX_RETRIES = int(os.getenv("EMBEDDING_MAX_RETRIES", "3"))
    RETRY_DELAY = int(os.getenv("EMBEDDING_RETRY_DELAY", "5"))
    MAX_MEMORY_USAGE_PERCENT = int(os.getenv("EMBEDDING_MAX_MEMORY_USAGE_PERCENT", "90"))
    
    @classmethod
    def validate(cls) -> bool:
        """Validate embedding configuration."""
        if not cls.FOLDER_EXTRACTED_DOC_PATH or not Path(cls.FOLDER_EXTRACTED_DOC_PATH).exists():
            logger.error(f"Extracted document path {cls.FOLDER_EXTRACTED_DOC_PATH} does not exist")
            return False
        if cls.CHUNK_SIZE <= 0:
            logger.error("CHUNK_SIZE must be a positive integer")
            return False
        if cls.CHUNK_OVERLAP < 0:
            logger.error("CHUNK_OVERLAP must be a non-negative integer")
            return False
        if not cls.QUEUE:
            logger.error("EMBEDDING_QUEUE environment variable is not set")
            return False
        if cls.MAX_MEMORY_USAGE_PERCENT <= 0 or cls.MAX_MEMORY_USAGE_PERCENT > 100:
            logger.error("EMBEDDING_MAX_MEMORY_USAGE_PERCENT must be between 1 and 100")
            return False
        
        return True


class SearchConfig(BaseConfig):
    """Search service configuration."""
    
    QUEUE = os.getenv("SEARCH_QUEUE", "search_documents")
    MAX_RETRIES = int(os.getenv("SEARCH_MAX_RETRIES", "3"))
    RETRY_DELAY = int(os.getenv("SEARCH_RETRY_DELAY", "5"))
    
    @classmethod
    def validate(cls) -> bool:
        """Validate search configuration."""
        if not cls.QUEUE:
            logger.error("SEARCH_QUEUE is not set")
            return False
        if cls.MAX_RETRIES < 0:
            logger.error("SEARCH_MAX_RETRIES must be a non-negative integer")
            return False
        if cls.RETRY_DELAY < 0:
            logger.error("SEARCH_RETRY_DELAY must be a non-negative integer")
            return False
        
        return True


class Config:
    """
    Main configuration class that groups all component configurations.
    
    This class serves as the central access point for all configuration settings
    and provides validation methods for the entire configuration.
    """
    
    # Component configuration
    DB = DatabaseConfig
    BROKER = BrokerConfig
    AI = AIModelsConfig
    EXTRACTOR = ExtractorConfig
    EMBEDDING = EmbeddingConfig
    SEARCH = SearchConfig
    
    # Component mapping
    _components = {
        'DB': DB,
        'BROKER': BROKER,
        'AI': AI,
        'EXTRACTOR': EXTRACTOR,
        'EMBEDDING': EMBEDDING,
        'SEARCH': SEARCH,
    }
    
    @classmethod
    def validate_all(cls) -> bool:
        """
        Validate all configuration components.
        
        Returns:
            bool: True if all components are valid, False otherwise
        """
        all_valid = True
        
        for name, component in cls._components.items():
            logger.info(f"Validating {name} configuration...")
            if not component.validate():
                logger.error(f"{name.upper()} configuration validation failed")
                all_valid = False
            else:
                logger.info(f"{name.upper()} configuration validated successfully")
        
        if all_valid:
            logger.info("All configurations validated successfully")
        else:
            logger.error("Configuration validation failed")
            
        return all_valid
    
    @classmethod
    def get_component(cls, component_name: str) -> Optional[Type[BaseConfig]]:
        """
        Get a configuration component by name.
        
        Args:
            component_name: The name of the component to retrieve
            
        Returns:
            The component configuration class or None if not found
        """
        return cls._components.get(component_name.lower())


# Validate all configurations when this module is imported
Config.validate_all()
