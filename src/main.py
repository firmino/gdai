#from src.parser.actor import document_extractor
from src.embedding.actor import embedding_document

if __name__ == "__main__":
    # Example usage
    #document_data = {"document_name": "document.pdf", "tenant_id": "tenant_123"}
    #document_extractor.send(document_data)
    embedding_document("document.pdf.json")
    #embedding_document.send({"document_name": "document.pdf.json"} )    