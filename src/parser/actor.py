import os
import sys
import json
import dramatiq
import logging
from dramatiq.brokers.rabbitmq import RabbitmqBroker
from dotenv import load_dotenv
from src.parser.service import ExtractDocumentService
from src.parser.document_extractor import DoclingPDFExtractor

load_dotenv(override=True)



FOLDER_RAW_DOC_PATH = os.getenv("FOLDER_RAW_DOC_PATH")
if not os.path.exists(FOLDER_RAW_DOC_PATH):
    raise ValueError(f"Raw document path {FOLDER_RAW_DOC_PATH} does not exist")


EXTRACTED_DOC_PATH = os.getenv("FOLDER_EXTRACTED_DOC_PATH")
if not os.path.exists(EXTRACTED_DOC_PATH):
    raise ValueError(f"Extracted document path {EXTRACTED_DOC_PATH} does not exist")


DOC_EXTRACTOR = DoclingPDFExtractor()
service = ExtractDocumentService(FOLDER_RAW_DOC_PATH, DOC_EXTRACTOR)
rabbitmq_broker = RabbitmqBroker(url="amqp://rabbitmq:rabbitmq@localhost:5672/")
dramatiq.set_broker(rabbitmq_broker)


logger = logging.getLogger("ACTOR_EXTRACTOR")

@dramatiq.actor
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
    # call other dramatiq actors to process the extracted document data
    logger.info(f"Document extraction for {document_name} completed successfully")
    


if __name__ == "__main__":
    # Example usage
    document_data = {"document_name": "document.pdf", "tenant_id": "tenant_123"}
    document_extractor.send(document_data)

