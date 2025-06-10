"""
Configuração centralizada para todos os componentes do G-DAI.

Este módulo fornece uma estrutura organizada de configuração com carregamento
de variáveis de ambiente, validação e acesso a configurações organizadas por componente.
"""

import os
import logging
from pathlib import Path
from typing import Dict, Any, Optional, Union, TypeVar, Generic, Type
from dotenv import load_dotenv

# Carrega variáveis de ambiente com override para priorizar arquivo .env local
load_dotenv(override=True)

# Configura logger para configurações
logger = logging.getLogger("GDAI_CONFIG")

# Variável de tipo para classes de configuração de componentes
T = TypeVar('T')


class ConfigComponent:
    """Classe base para componentes de configuração com suporte a validação."""
    
    @classmethod
    def validate(cls) -> bool:
        """
        Método de validação padrão a ser substituído pelas subclasses.
        
        Returns:
            bool: True se a configuração for válida
        """
        return True


class DatabaseConfig(ConfigComponent):
    """Configuração de conexão com banco de dados."""
    
    # PGVector settings
    PGVECTOR_USER = os.getenv("PGVECTOR_USER")
    PGVECTOR_PASSWORD = os.getenv("PGVECTOR_PASSWORD")
    PGVECTOR_DATABASE = os.getenv("PGVECTOR_DATABASE")
    PGVECTOR_HOST = os.getenv("PGVECTOR_HOST")
    PGVECTOR_PORT = int(os.getenv("PGVECTOR_PORT", "5432"))
    PGVECTOR_MIN_POOL_CONNECTIONS = int(os.getenv("PGVECTOR_MIN_POOL_CONNECTIONS", "2"))
    PGVECTOR_MAX_POOL_CONNECTIONS = int(os.getenv("PGVECTOR_MAX_POOL_CONNECTIONS", "10"))
    
    @classmethod
    def validate(cls) -> bool:
        """Valida a configuração do banco de dados."""
        if not cls.PGVECTOR_USER:
            logger.error("PGVECTOR_USER não está definido")
            return False
        if not cls.PGVECTOR_PASSWORD:
            logger.error("PGVECTOR_PASSWORD não está definido")
            return False
        if not cls.PGVECTOR_DATABASE:
            logger.error("PGVECTOR_DATABASE não está definido")
            return False
        if not cls.PGVECTOR_HOST:
            logger.error("PGVECTOR_HOST não está definido")
            return False
        if cls.PGVECTOR_MIN_POOL_CONNECTIONS < 0:
            logger.error("PGVECTOR_MIN_POOL_CONNECTIONS configurado incorretamente")
            return False
        if cls.PGVECTOR_MAX_POOL_CONNECTIONS < 0:
            logger.error("PGVECTOR_MAX_POOL_CONNECTIONS configurado incorretamente")
            return False
        
        return True


class BrokerConfig(ConfigComponent):
    """Configuração do message broker."""
    
    # RabbitMQ settings
    RABBIT_MQ_HOST = os.getenv("RABBIT_MQ_HOST")
    RABBIT_MQ_PORT = int(os.getenv("RABBIT_MQ_PORT", "5672"))
    RABBIT_MQ_USER = os.getenv("RABBIT_MQ_USER")
    RABBIT_MQ_PASSWORD = os.getenv("RABBIT_MQ_PASSWORD")
    
   
    @classmethod
    def validate(cls) -> bool:
        """Valida a configuração do message broker."""
        if not cls.RABBIT_MQ_HOST:
            logger.error("RABBIT_MQ_HOST não está definido")
            return False
        if cls.RABBIT_MQ_PORT < 0:
            logger.error("RABBIT_MQ_PORT inválido")
            return False
        if not cls.RABBIT_MQ_USER:
            logger.error("RABBIT_MQ_USER não está definido")
            return False
        if not cls.RABBIT_MQ_PASSWORD:
            logger.error("RABBIT_MQ_PASSWORD não está definido")
            return False
       
        
        return True


class AIModelsConfig(ConfigComponent):
    """Configuração de modelos de IA."""
    
    # Embedding model settings
    EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "cohere/embed-v4.0")
    EMBEDDING_MODEL_API_KEY = os.getenv("EMBEDDING_API_KEY")
    
    # LLM model settings
    LLM_MODEL = os.getenv("SEARCH_LLM_MODEL", "openai/gpt-4o")
    LLM_MODEL_API_KEY = os.getenv("SEARCH_LLM_API_KEY")
    LLM_MAX_TOKENS = int(os.getenv("SEARCH_LLM_MAX_TOKENS", "1000"))
    LLM_TEMPERATURE = float(os.getenv("SEARCH_LLM_TEMPERATURE", "0.7"))
    
    @classmethod
    def validate(cls) -> bool:
        """Valida a configuração dos modelos de IA."""
        if not cls.EMBEDDING_MODEL:
            logger.error("EMBEDDING_MODEL não está definido")
            return False
        if not cls.EMBEDDING_MODEL_API_KEY:
            logger.error("EMBEDDING_API_KEY não está definido")
            return False
        if not cls.LLM_MODEL:
            logger.error("SEARCH_LLM_MODEL não está definido")
            return False
        if not cls.LLM_MODEL_API_KEY:
            logger.error("SEARCH_LLM_API_KEY não está definido")
            return False
        if cls.LLM_MAX_TOKENS <= 0:
            logger.error("SEARCH_LLM_MAX_TOKENS deve ser positivo")
            return False
        if not (0 <= cls.LLM_TEMPERATURE <= 1.0):
            logger.error("SEARCH_LLM_TEMPERATURE deve estar entre 0.0 e 1.0")
            return False
        
        return True


class ExtractorConfig(ConfigComponent):
    """Configuração do extrator de documentos."""
    
    FOLDER_RAW_DOC_PATH = os.getenv("DOCUMENT_EXTRACTOR_FOLDER_SOURCE_PATH")
    FOLDER_EXTRACTED_DOC_PATH = os.getenv("DOCUMENT_EXTRACTOR_FOLDER_TARGET_PATH")
    MAX_FILE_SIZE_MB = int(os.getenv("DOCUMENT_EXTRACTOR_MAX_FILE_SIZE_MB", "100"))
    EXTRACTOR = os.getenv("DOCUMENT_EXTRACTOR", "docling")
    MAX_RETRIES = int(os.getenv("DOCUMENT_EXTRACTOR_MAX_RETRIES", "3"))
    RETRY_DELAY = int(os.getenv("DOCUMENT_EXTRACTOR_RETRY_DELAY", "5"))
    QUEUE = os.getenv("DOCUMENT_EXTRACTOR_QUEUE")
    
    @classmethod
    def validate(cls) -> bool:
        """Valida a configuração do extrator de documentos."""
        if not cls.FOLDER_RAW_DOC_PATH:
            logger.error("DOCUMENT_EXTRACTOR_FOLDER_RAW_DOC_PATH não está definido")
            return False
            
        raw_path = Path(cls.FOLDER_RAW_DOC_PATH)
        if not raw_path.exists():
            logger.warning(f"Diretório de documentos brutos não existe: {cls.FOLDER_RAW_DOC_PATH}")
            # Tenta criar o diretório
            try:
                raw_path.mkdir(parents=True, exist_ok=True)
                logger.info(f"Diretório criado: {cls.FOLDER_RAW_DOC_PATH}")
            except Exception as e:
                logger.error(f"Não foi possível criar o diretório: {e}")
                return False
                
        if not cls.FOLDER_EXTRACTED_DOC_PATH:
            logger.error("DOCUMENT_EXTRACTOR_FOLDER_EXTRACTED_DOC_PATH não está definido")
            return False
            
        extracted_path = Path(cls.FOLDER_EXTRACTED_DOC_PATH)
        if not extracted_path.exists():
            logger.warning(f"Diretório de documentos extraídos não existe: {cls.FOLDER_EXTRACTED_DOC_PATH}")
            # Tenta criar o diretório
            try:
                extracted_path.mkdir(parents=True, exist_ok=True)
                logger.info(f"Diretório criado: {cls.FOLDER_EXTRACTED_DOC_PATH}")
            except Exception as e:
                logger.error(f"Não foi possível criar o diretório: {e}")
                return False
                
        if cls.MAX_FILE_SIZE_MB <= 0:
            logger.error("MAX_FILE_SIZE_MB deve ser um valor positivo")
            return False
        if cls.MAX_RETRIES < 0:
            logger.error("DOCUMENT_EXTRACTOR_MAX_RETRIES deve ser um valor não-negativo")
            return False
        if cls.RETRY_DELAY < 0:
            logger.error("DOCUMENT_EXTRACTOR_RETRY_DELAY deve ser um valor não-negativo")
            return False
        
        if cls.QUEUE is None:
            logger.error("DOCUMENT_EXTRACTOR_QUEUE não está definido")
            return False
        
        return True


class EmbeddingConfig(ConfigComponent):
    """Configuração do serviço de embedding de documentos."""
    
    FOLDER_EXTRACTED_DOC_PATH = os.getenv("EMBEDDING_FOLDER_SOURCE_PATH")
    CHUNK_SIZE = int(os.getenv("EMBEDDING_CHUNK_SIZE"))
    CHUNK_OVERLAP = int(os.getenv("EMBEDDING_CHUNK_OVERLAP"))
    MAX_RETRIES = int(os.getenv("EMBEDDING_MAX_RETRIES"))
    RETRY_DELAY = int(os.getenv("EMBEDDING_RETRY_DELAY"))
    MAX_MEMORY_USAGE_PERCENT = int(os.getenv("EMBEDDING_MAX_MEMORY_USAGE_PERCENT"))
    QUEUE = os.getenv("EMBEDDING_QUEUE")
    
    @classmethod
    def validate(cls) -> bool:
        """Valida a configuração de embedding."""
        if not cls.FOLDER_EXTRACTED_DOC_PATH:
            logger.error("EMBEDDING_FOLDER_SOURCE_PATH não está definido")
            return False
            
        if not cls.FOLDER_EXTRACTED_DOC_PATH:
            logger.error("EMBEDDING_FOLDER_SOURCE_PATH não está definido")
            return False
                
        if cls.CHUNK_SIZE <= 0:
            logger.error("EMBEDDING_CHUNK_SIZE deve ser um valor positivo")
            return False
        if cls.CHUNK_OVERLAP < 0:
            logger.error("EMBEDDING_CHUNK_OVERLAP deve ser um valor não-negativo")
            return False
        if cls.MAX_MEMORY_USAGE_PERCENT <= 0 or cls.MAX_MEMORY_USAGE_PERCENT > 100:
            logger.error("EMBEDDING_MAX_MEMORY_USAGE_PERCENT deve estar entre 1 e 100")
            return False
        if cls.MAX_RETRIES < 0:
            logger.error("EMBEDDING_MAX_RETRIES deve ser um valor não-negativo")
            return False
        if cls.RETRY_DELAY < 0:
            logger.error("EMBEDDING_RETRY_DELAY deve ser um valor não-negativo")
            return False
        if cls.QUEUE is None:
            logger.error("EMBEDDING_QUEUE não está definido")
            return False
        

        
        return True


class SearchConfig(ConfigComponent):
    """Configuração do serviço de busca."""
    
    LLM_MAX_TOKENS = int(os.getenv("SEARCH_LLM_MAX_TOKENS"))
    LLM_TEMPERATURE = float(os.getenv("SEARCH_LLM_TEMPERATURE"))

    @classmethod
    def validate(cls) -> bool:
        """Valida a configuração de busca."""
        if cls.LLM_MAX_TOKENS < 0:
            logger.error("SEARCH_MAX_RETRIES deve ser um valor não-negativo")
            return False
        if cls.LLM_TEMPERATURE < 0:
            logger.error("SEARCH_RETRY_DELAY deve ser um valor não-negativo")
            return False
        
        return True


class Config:
    """
    Classe principal de configuração que agrupa todos os componentes.
    
    Esta classe serve como ponto de acesso central para todas as configurações
    e fornece métodos de validação para toda a configuração.
    """
    
    # Componentes de configuração
    db = DatabaseConfig
    broker = BrokerConfig
    ai = AIModelsConfig
    extractor = ExtractorConfig
    embedding = EmbeddingConfig
    search = SearchConfig
    
    # Mapeamento de componentes
    _components = {
        'db': db,
        'broker': broker,
        'ai': ai,
        'extractor': extractor,
        'embedding': embedding,
        'search': search,
    }
    
    @classmethod
    def validate_all(cls) -> bool:
        """
        Valida todos os componentes de configuração.
        
        Returns:
            bool: True se todos os componentes forem válidos, False caso contrário
        """
        all_valid = True
        
        for name, component in cls._components.items():
            logger.info(f"Validando configuração de {name}...")
            if not component.validate():
                logger.error(f"Validação de configuração de {name.upper()} falhou")
                all_valid = False
            else:
                logger.info(f"Configuração de {name.upper()} validada com sucesso")
        
        if all_valid:
            logger.info("Todas as configurações foram validadas com sucesso")
        else:
            logger.error("Validação de configurações falhou")
            
        return all_valid
    
    @classmethod
    def get_component(cls, component_name: str) -> Optional[Type[ConfigComponent]]:
        """
        Obtém um componente de configuração pelo nome.
        
        Args:
            component_name: O nome do componente a ser recuperado
            
        Returns:
            A classe de configuração do componente ou None se não encontrado
        """
        return cls._components.get(component_name.lower())


# Valida todas as configurações ao importar este módulo
Config.validate_all()