from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from src.api.routers.auth import router as auth_router
from src.api.routers.administration import router as admin_router
from src.api.routers.document import router as document_router

app = FastAPI(
    title='GDAI',
    #root_path="/api/"
)


origins = ["http://localhost:8000", "http://localhost:3000"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/ping", status_code=200)
async def ping():
    return "pong!"


app.include_router(document_router, prefix="/document")
app.include_router(auth_router, prefix="/auth")


