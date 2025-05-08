import os
from src.parser.document_extractor import DocumentExtractor
from src.parser.exceptions import FileNotFoundException, InvalidDocumentPathFolderException
from src.parser.schema import Document


class ExtractDocumentService:
    """
    Service for extracting text from documents.
    """

    def __init__(self, document_folder_path: str, document_extractor: DocumentExtractor):
        """
        Initialize the ExtractDocumentService with a document repository.
        """
        if not os.path.isdir(document_folder_path):
            raise InvalidDocumentPathFolderException()

        self.document_extractor = document_extractor
        self.document_folder_path = document_folder_path

    def _extract_text(self, doc_path: str) -> str:
        """
        Extract text from a document.
        """
        if not os.path.exists(doc_path):
            raise FileNotFoundException()
        document_data = self.document_extractor.extract_document_data(doc_path)
        return document_data

    def extract_data_from_document(self, tenant_id: str, document_file_name: str) -> Document:
        """
        Extract text from a document.
        """
        document_full_path = os.path.join(self.document_folder_path, document_file_name)
        document = self._extract_text(document_full_path)
        document.tenant_id = tenant_id
        return document
