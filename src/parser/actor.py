import dramatiq
from src.parser.service import ExtractDocumentService 



@dramatiq.actor
def document_extractor(document_name: str):
    pass