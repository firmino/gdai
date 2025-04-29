from fastapi import APIRouter

router = APIRouter()


@router.post("/login", status_code=201, tags=['auth'])
async def login(body: dict):
   return "login"
