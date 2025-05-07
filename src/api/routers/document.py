from fastapi import APIRouter

router = APIRouter()


@router.post("/load", status_code=201, tags=["documents"])
async def document(body: dict):
    return "test"


@router.get("search", status_code=200, tags=["documents"])
async def search_documents(tenant_id: int, query: str, limit: int = 10, offset: int = 0):
    return "test"
