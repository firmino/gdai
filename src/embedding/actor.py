import os
import logging
import asyncio
from dotenv import load_dotenv
from src.shared.rabbitmq_broker import dramatiq # with broked configured
from src.embedding.embedding_model import CohereEmbeddingModel
from src.embedding.repository import DocumentRepository 
from src.embedding.service import EmbeddingDocumentService


load_dotenv(override=True)
logger = logging.getLogger("ACTOR_EMBEDDING")

EXTRACTED_DOC_PATH = os.getenv("FOLDER_EXTRACTED_DOC_PATH")
if not os.path.exists(EXTRACTED_DOC_PATH):
    raise ValueError(f"Extracted document path {EXTRACTED_DOC_PATH} does not exist")

CHUNK_SIZE = int(os.getenv("CHUNK_SIZE"))
if CHUNK_SIZE is None:
    raise ValueError("CHUNK_SIZE environment variable is not set.")

CHUNK_OVERLAP = int(os.getenv("CHUNK_OVERLAP"))
if CHUNK_OVERLAP is None:
    raise ValueError("CHUNK_OVERLAP environment variable is not set.")

EMBEDDING_MODEL_NAME = os.getenv("EMBEDDING_MODEL")
if EMBEDDING_MODEL_NAME is None:
    raise ValueError("EMBEDDING_MODEL environment variable is not set.")

embedding_model = None
if EMBEDDING_MODEL_NAME == "cohere/embed-v4.0":
    embedding_model = asyncio.run(CohereEmbeddingModel.create())
if embedding_model is None:
    raise ValueError(f"Unsupported embedding model: {EMBEDDING_MODEL_NAME}")


QUEUE_NAME = os.getenv("RABBIT_MQ_QUEUE_EMBEDDING_DOCUMENTS")
if QUEUE_NAME is None:
    raise ValueError("RABBIT_MQ_QUEUE_EMBEDDING_DOCUMENTS environment variable is not set.")


document_repository = DocumentRepository()
embedding_service = EmbeddingDocumentService(
    embedding_model=embedding_model, 
    document_repository=document_repository, 
    chunk_size=CHUNK_SIZE, 
    chunk_overlap=CHUNK_OVERLAP
)



@dramatiq.actor(queue_name="embedding_documents")
def embedding_document(document: str):
    logger.info(f"Received document for embedding: {document}")
    document_full_path = os.path.join(EXTRACTED_DOC_PATH, document)
    if not os.path.exists(document_full_path):
        logger.error(f"Document file {document_full_path} does not exist.")
        raise FileNotFoundError(f"Document file {document_full_path} does not exist.")
    logger.info(f"Beginning embedding for document {document} at {document_full_path}")
    asyncio.run(embedding_service.process_document(document_full_path))
    logger.info(f"Document embedding for {document} completed successfully")
