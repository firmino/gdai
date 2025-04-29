from fastapi import APIRouter

router = APIRouter()


@router.post("/load-document", status_code=201, tags=['documents'])
async def document(body: dict):
    return "test"