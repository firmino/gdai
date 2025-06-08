from src.extractor.actor import document_extractor
from src.embedding.actor import embedding_document
from src.search.actor import search_query
import time


if __name__ == "__main__":
    # Example usage
    #document_data = {"document_name": "arte_guerra.pdf", "tenant_id": "tenant_123"}
    #document_data = {"document_name": "senhor_dos_aneis.pdf", "tenant_id": "tenant_321"}
    #document_extractor(document_data)
    #document_extractor.send(document_data)
    #embedding_document({"document_name": "senhor_dos_aneis.pdf.json"} )
    #embedding_document.send({"document_name": "document.pdf.json"} )    
    #search_query.send({"tenant_id": "tenant_123", "query_id": "query_456", "query_text": "Quem é frodo? "})
    start_time = time.time()
    search_query({"tenant_id": "tenant_321", "query_id": "query_666", "query_text": "Qual o papel de harry potter na história?"})
    end_time = time.time()
    execution_time = end_time - start_time
    print(f"Search 1 completed in {execution_time:.2f} seconds")

    start_time = time.time()
    search_query({"tenant_id": "tenant_321", "query_id": "query_666", "query_text": "Quem foi sauron?"})
    end_time = time.time()
    execution_time = end_time - start_time
    print(f"Search 2 completed in {execution_time:.2f} seconds")
    
    start_time = time.time()
    search_query({"tenant_id": "tenant_321", "query_id": "query_666", "query_text": "Quantas páginas tem o livro?"})
    end_time = time.time()
    execution_time = end_time - start_time
    print(f"Search 3 completed in {execution_time:.2f} seconds")

# faq de data
# documentação de cliente
# documetação da  NATASHA de Q&A 
# memória da conversação 
# migrar embedding do cohere do gemini  
# processar vídeo de UGC mais importantes 
# verificar endpoint de age/gender 
# https://ai.google.dev/gemini-api/docs/video-understanding?hl=pt-br