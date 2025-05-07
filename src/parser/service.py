import os
import json
from src.document_parser.extractor import DoclingExtractor
from src.document_parser.exception import FileNotFoundException, InvalidDocumentPathFolderException
from src.document_parser.schema import Document


class ExtractDocumentService:
    """
    Service for extracting text from documents.
    """

    def __init__(self):
        """
        Initialize the ExtractDocumentService with a document repository.
        """
        document_extractor = os.getenv("DOCUMENT_EXTRACTOR")
        if not document_extractor:
            raise ValueError("DOCUMENT_EXTRACTOR environment variable is not set.")
        if document_extractor == "docling":
            self.document_extractor = DoclingExtractor()

        document_folder_path = os.getenv("FOLDER_DOC_PATH")
        if not document_folder_path:
            raise ValueError("FOLDER_DOC_PATH environment variable is not set.")

        if os.path.isdir(document_folder_path):
            raise InvalidDocumentPathFolderException()

        self.document_folder_path = document_folder_path

    async def _extract_text(self, doc_path: str) -> str:
        """
        Extract text from a document.
        """
        if not os.path.exists(doc_path):
            raise FileNotFoundException()

        document_data = self.document_extractor.extract_text(doc_path)
        return document_data

    async def extract_data_from_document(self, tenant_id: int, doc_id: int, document_file_name: str) -> str:
        """
        Extract text from a document.
        """
        document_full_path = os.path.join(self.document_folder_path, document_file_name)
        if not os.path.exists(document_full_path):
            raise FileNotFoundException()

        document_data = self._extract_text(document_full_path)
        document = Document(
            tenant_id=tenant_id,
            doc_id=doc_id,
            doc_name=document_file_name,
            pages=document_data,  # change to be a list
        )

        document_str = json.dumps(document)
        return document_str
