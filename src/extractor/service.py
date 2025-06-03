import os
import uuid
from src.extractor.document_extractor import DocumentExtractor
from src.extractor.exceptions import FileNotFoundException
from src.shared.schema import Document


class ExtractDocumentService:
    """
    Service for extracting text from documents.
    """

    def __init__(self,  document_extractor: DocumentExtractor):
        """
        Initialize the ExtractDocumentService with a document repository.
        """
        self.document_extractor = document_extractor
        

    def extract_data_from_document(self, tenant_id: str, document_path: str) -> Document:
        """
        Extract text from a document.
        """
        if not os.path.exists(document_path):
            raise FileNotFoundException()
        
        document = self.document_extractor.extract_document_data(document_path)
        document.tenant_id = tenant_id
        document.doc_id = str(uuid.uuid4())
        return document
