import asyncio
import logging
from typing import Optional
from fastapi import APIRouter, HTTPException, BackgroundTasks, Depends, status
from pydantic import BaseModel

from src.api.service import SearchService
from src.api.repository import SearchRepository
from src.shared.embedding_model import EmbeddingModelFactory
from src.shared.llm_model import LLMModelFactory

logger = logging.getLogger("API_ROUTER")


# Define request and response models
class SearchRequest(BaseModel):
    tenant_id: str
    query_id: str
    query_text: str
    chunks_limit: Optional[int] = 100


class SearchResponse(BaseModel):
    message: str
    query_id: str
    status: str


# Initialize components
async def get_search_service():
    try:
        embedding_model = await EmbeddingModelFactory.create()
        llm_model = await LLMModelFactory.create()
        search_repository = SearchRepository()
        search_service = SearchService(llm_model=llm_model, embedding_model=embedding_model, repository=search_repository)
        return search_service
    except Exception as e:
        logger.critical(f"Failed to initialize search components: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to initialize search service")


# Create router
router = APIRouter(prefix="/search", tags=["search"])


@router.post("/query", response_model=SearchResponse)
async def search_query_endpoint(request: SearchRequest, search_service: SearchService = Depends(get_search_service)):
    """
    Process a search query and return results
    """
    try:
        # Validate required fields
        if not request.tenant_id or not request.query_id or not request.query_text:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="tenant_id, query_id, and query_text are required")

        logger.info(f"Received search query for tenant: {request.tenant_id}, query_id: {request.query_id}")
        query_result = await search_service.answer_query(request.tenant_id, request.query_id, request.query_text, request.chunks_limit)
        return SearchResponse(message=query_result, query_id=request.query_id, status="success")

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error processing search query: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Error processing search query: {str(e)}")
