import uvicorn
from fastapi import FastAPI
from src.api.router import router as search_router
from src.shared.conf import Config
from src.shared.logger import logger



# Create FastAPI app
app = FastAPI(
    title="G-DAI Search API",
    description="API for document search using LLM and embeddings",
    version="1.0.0",
)

# Include the search router
app.include_router(search_router)

# Default route
@app.get("/")
async def root():
    return {"status": "ok", "message": "G-DAI Search API is running"}

# Health check endpoint
@app.get("/health")
async def health():
    return {"status": "healthy"}

if __name__ == "__main__": 
    # Run the application
    uvicorn.run(
        "src.api.main:app", 
        host="0.0.0.0", 
        port=8000,   
        reload=True,
        log_level="info"
    )