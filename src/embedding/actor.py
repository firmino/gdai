import json
import dramatiq
from src.embedding_pipeline.schema import Document
from src.embedding_pipeline.service import EmbeddingDocumentService


@dramatiq.actor
def embedding_document_actor(document: str):
    document_data = json.loads(document)
    document = Document(**document_data)
    embedding_service = EmbeddingDocumentService.create()
    embedding_service.process_document(document)
