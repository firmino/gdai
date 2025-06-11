from pydantic import BaseModel
from typing import Optional

class SearchRequest(BaseModel):
    """
    Request model for search queries.
    """
    tenant_id: str
    query_id: str
    query_text: str
    chunks_limit: Optional[int] = 100

class SearchResponse(BaseModel):
    """
    Response model for search queries.
    """
    message: str
    query_id: str
    status: str
    list_chunks: Optional[list] = None
