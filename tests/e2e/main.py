from src.extractor.actor import document_extractor
from src.embedding.actor import embedding_document
from src.search.actor import search_query

if __name__ == "__main__":
    # Example usage
    #document_data = {"document_name": "arte_guerra.pdf", "tenant_id": "tenant_123"}
    document_data = {"document_name": "senhor_dos_aneis.pdf", "tenant_id": "tenant_321"}
    document_extractor.send(document_data)
    #embedding_document({"document_name": "document.pdf.json"} )
    #embedding_document.send({"document_name": "document.pdf.json"} )    
    #search_query.send({"tenant_id": "tenant_123", "query_id": "query_456", "query_text": "Como fazer pão? "})

# faq de data
# documentação de cliente
# documetação da  NATASHA de Q&A 
# memória da conversação 
# migrar embedding do cohere do gemini  
# processar vídeo de UGC mais importantes 
# verificar endpoint de age/gender 
# https://ai.google.dev/gemini-api/docs/video-understanding?hl=pt-br