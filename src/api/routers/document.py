from fastapi import APIRouter

router = APIRouter()


@router.post("/load", status_code=201, tags=["documents"])
async def document(body: dict):
    return "test"


@router.get("search", status_code=200, tags=["documents"])
async def search_document_chunks(tenant_id: int, query: str, top_k: int = 10):
    # embedding query  
    # get similar chunks for tenant_id 
    # rerank chunks based on query 
    # return top chunks results 
    pass