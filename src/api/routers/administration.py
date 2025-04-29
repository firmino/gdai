from fastapi import APIRouter

router = APIRouter()


@router.post("/admin-something", status_code=201, tags=['administration'])
async def teste(body: dict):
   return "administration test"