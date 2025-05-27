from src.api.repository import DocumentRepository

class DocumentSearchService:

    def __init__(self, repository: 'DocumentRepository'):
        self.repository = repository

    async def search_chunks(self, tenant_id:str,  query: str, top_k:int):
        # embedding query  
        # get similar chunks for tenant_id 
        # rerank chunks based on query 
        # return top chunks results 
        pass 

    async def solve_on_llm(self, chunks: list, query: str):
        # Call LLM with the chunks and query
        # Return the response from the LLM
        pass