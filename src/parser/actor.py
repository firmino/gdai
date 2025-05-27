import os
import sys
import json
import logging
from dotenv import load_dotenv
from src.shared.rabbitmq_broker import dramatiq # with broked configured
from src.parser.service import ExtractDocumentService
from src.parser.document_extractor import DoclingPDFExtractor
from src.embedding.actor import embedding_document


load_dotenv(override=True)
logger = logging.getLogger("ACTOR_EXTRACTOR")


FOLDER_RAW_DOC_PATH = os.getenv("FOLDER_RAW_DOC_PATH")
if not os.path.exists(FOLDER_RAW_DOC_PATH):
    raise ValueError(f"Raw document path {FOLDER_RAW_DOC_PATH} does not exist")

EXTRACTED_DOC_PATH = os.getenv("FOLDER_EXTRACTED_DOC_PATH")
if not os.path.exists(EXTRACTED_DOC_PATH):
    raise ValueError(f"Extracted document path {EXTRACTED_DOC_PATH} does not exist")

QUEUE_NAME = os.getenv("RABBIT_MQ_QUEUE_EXTRACT_DOCUMENT_DATA")
if QUEUE_NAME is None:
    raise ValueError("RABBIT_MQ_QUEUE_EXTRACT_DOCUMENT_DATA environment variable is not set.")

DOC_EXTRACTOR = DoclingPDFExtractor()
service = ExtractDocumentService(DOC_EXTRACTOR)


@dramatiq.actor(queue_name="extract_documents")
def document_extractor(document_data: dict):
    logger.info(f"Received document data: {document_data}")
    document_name = document_data.get("document_name")
    if not document_name:
        logger.error("Document name is required")
        raise ValueError("Document name is required")
    tenant_id = document_data.get("tenant_id")
    if not tenant_id:
        logger.error("Tenant ID is required")
        raise ValueError("Tenant ID is required")
    document_full_path = os.path.join(FOLDER_RAW_DOC_PATH, document_name)
    logger.info(f"Beginning document extraction for {document_name} at {document_full_path}")
    extracted_doc_data = service.extract_data_from_document(tenant_id, document_full_path)
    logger.info(f"Document extraction completed for {document_name}")
    extracted_doc_data_json = json.dumps(extracted_doc_data.model_dump(), default=str)
    logger.info(f"Extracted document size: {sys.getsizeof(extracted_doc_data_json)} bytes")
    with open(os.path.join(EXTRACTED_DOC_PATH, f"{document_name}.json"), "w", encoding="utf-8") as f:
        f.write(extracted_doc_data_json)
    logger.info(f"Extracted document data saved to {os.path.join(EXTRACTED_DOC_PATH, f'{document_name}.json')}")
    logger.info(f"Document extraction for {document_name} completed successfully")
    embedding_document.send(f'{document_name}.json') # call next action
    logger.info(f"Document {document_name} sent for embedding processing")