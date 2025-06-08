import os
import sys
import json
import shutil
import logging
from src.extractor.conf import Config
from src.shared.broker import dramatiq  # with broked configured
from src.extractor.service import ExtractDocumentService
from src.extractor.document_extractor import DoclingPDFExtractor, PyMuPDFExtractor
from src.embedding.actor import embedding_document


logger = logging.getLogger("ACTOR_EXTRACTOR")
#doc_extractor = DoclingPDFExtractor()
doc_extractor = PyMuPDFExtractor()
service = ExtractDocumentService(doc_extractor)


@dramatiq.actor(queue_name=Config.RABBIT_MQ_QUEUE_EXTRACT_DOCUMENT_DATA, max_retries=Config.MAX_RETRIES, min_backoff=Config.RETRY_DELAY)
def document_extractor(document_data: dict):
    try:
        logger.info(f"Received document data: {document_data}")
        document_name = document_data.get("document_name")
        if not document_name:
            logger.error("Document name is required")
            raise ValueError("Document name is required")
        tenant_id = document_data.get("tenant_id")
        if not tenant_id:
            logger.error("Tenant ID is required")
            raise ValueError("Tenant ID is required")
        document_full_path = os.path.join(Config.FOLDER_RAW_DOC_PATH, document_name)

        # Check if the file exists
        if not os.path.exists(document_full_path):
            logger.error(f"Document file {document_full_path} does not exist")
            raise FileNotFoundError(f"Document file {document_full_path} does not exist")

        # Check if the file is readable
        if not os.access(document_full_path, os.R_OK):
            logger.error(f"Document file {document_full_path} is not readable")
            raise PermissionError(f"Document file {document_full_path} is not readable")

        # Check file size
        file_size = os.path.getsize(document_full_path)
        if file_size == 0:
            logger.error(f"Document file {document_full_path} is empty")
            raise ValueError(f"Document file {document_full_path} is empty")

        if file_size > Config.MAX_FILE_SIZE_MB * 1024 * 1024:  # Limite configurável
            logger.error(f"Document file {document_full_path} exceeds maximum allowed size")
            raise ValueError(f"Document file {document_full_path} exceeds maximum allowed size")

        # Start the document extraction process
        try:
            logger.info(f"Beginning document extraction for {document_name} at {document_full_path}")
            extracted_doc_data = service.extract_data_from_document(tenant_id, document_full_path) 
            logger.info(f"Document extraction completed for {document_name}")
        except Exception as e:
            logger.error(f"Failed to extract document {document_name}: {str(e)}")
            raise

        # Serialize the extracted data to JSON and save to file
        try:
            extracted_doc_data_json = json.dumps(extracted_doc_data.model_dump(), default=str)
            logger.info(f"Extracted document size: {sys.getsizeof(extracted_doc_data_json)} bytes")
        except Exception as e:
            logger.error(f"Failed to serialize document {document_name}: {str(e)}")
            raise 

        output_path = os.path.join(Config.FOLDER_EXTRACTED_DOC_PATH, f"{document_name}.json")
        try:
            os.makedirs(os.path.dirname(output_path), exist_ok=True)  # Verificar se o diretório de saída existe

            # Check if there's enough disk space
            disk_usage = shutil.disk_usage(os.path.dirname(output_path))
            if disk_usage.free < sys.getsizeof(extracted_doc_data_json) * 2:  # 2x para ter margem
                logger.error("Not enough disk space to save extracted document")
                raise IOError("Not enough disk space to save extracted document")

            with open(os.path.join(Config.FOLDER_EXTRACTED_DOC_PATH, f"{document_name}.json"), "w", encoding="utf-8") as f:
                f.write(extracted_doc_data_json)
            logger.info(f"Extracted document data saved to {os.path.join(Config.FOLDER_EXTRACTED_DOC_PATH, f'{document_name}.json')}")
        except IOError as e:
            logger.error(f"Failed to write extracted document to disk: {str(e)}")
            raise

        # Send to next stage with error handling
        try:
            logger.info(f"Document extraction for {document_name} completed successfully")
            embedding_document.send({"document_name": f"{document_name}.json"})  # call next action
            logger.info(f"Document {document_name} sent for embedding processing")
        except Exception as e:
            logger.error(f"Failed to enqueue document for embedding: {str(e)}")
            raise

    except Exception as e:
        logger.error(f"Failed to extract document {document_name}: {str(e)}")
        # Allows Dramatiq to retry based on max_retries settings
        raise
