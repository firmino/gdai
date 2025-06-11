
import os
import shutil
from fastapi import APIRouter, HTTPException, BackgroundTasks, Depends, status, UploadFile, File, Form
from pydantic import BaseModel
from typing import Optional

from src.api.service import SearchService
from src.api.repository import SearchRepository
from src.shared.embedding_model import EmbeddingModelFactory
from src.shared.llm_model import LLMModelFactory
from src.shared.logger import logger
from src.actor.extractor.actor import document_extractor
from src.shared.conf import ExtractorConfig



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
    list_chunks: Optional[list] = None



class DocumentUploadResponse(BaseModel):
    message: str
    document_name: str
    tenant_id: str
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
        return SearchResponse(message=query_result['msg'], list_chunks=query_result["chunks"],  query_id=request.query_id, status="success")

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error processing search query: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Error processing search query: {str(e)}")






@router.post("/document/upload", response_model=DocumentUploadResponse)
async def upload_document(
    background_tasks: BackgroundTasks,
    tenant_id: str = Form(...),
    document: UploadFile = File(...)
):
    """
    Upload a document to be processed by the document extractor
    """
    try:
        # Validate required fields
        if not tenant_id:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="tenant_id is required")
        
        # Validate file
        if not document:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Document file is required")
        
        # Get the document storage path from configuration
        document_folder_path = ExtractorConfig.FOLDER_RAW_DOC_PATH
        if not document_folder_path:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, 
                detail="Document storage path not configured"
            )
        
        # Ensure the directory exists
        os.makedirs(document_folder_path, exist_ok=True)
        
        # Save the file
        file_path = os.path.join(document_folder_path, document.filename)
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(document.file, buffer)
        
        # Call the document extractor actor
        document_data = {
            "document_name": document.filename,
            "tenant_id": tenant_id
        }

        document_extractor.send(document_data)
           
        logger.info(f"Document {document.filename} uploaded successfully for tenant: {tenant_id}")
        
        return DocumentUploadResponse(
            message=f"Document {document.filename} uploaded and queued for processing",
            document_name=document.filename,
            tenant_id=tenant_id,
            status="pending"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error uploading document: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, 
            detail=f"Error uploading document: {str(e)}"
        )