from src.shared.database import PGVectorDatabase
from src.shared.schema import DocumentChunk
from typing import List


class DocumentRepository:
    def __init__(self):
        """Initialize repository."""
        pass

    async def search_document_by_similarity(self, tenant_id: str, query_embedding: List[float], limit: int = 10) -> List[DocumentChunk]:
        """Search documents by similarity to a query embedding."""
        async with PGVectorDatabase.get_connection() as connection:
            results = await connection.fetch(
                """SELECT id, 
                          name, 
                          tenant_id, 
                          chunk_text, 
                          page_number, 
                          begin_offset,
                          end_offset,
                          created_at 
                   FROM document_chunks  
                   WHERE tenant_id = $1 
                   ORDER BY embedding <-> $2 
                   LIMIT $3""",
                tenant_id,
                query_embedding,
                limit,
            )
            similar_chunks = [
                DocumentChunk(
                    chunk_id=result["id"],
                    doc_name=result["name"],
                    tenant_id=result["tenant_id"],
                    chunk_text=result["chunk_text"],
                    page_number=result["page_number"],
                    begin_offset=result["begin_offset"],
                    end_offset=result["end_offset"],
                    created_at=result["created_at"],
                )
                for result in results
            ]

            return similar_chunks
