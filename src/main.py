import logging
from fastapi import FastAPI
import uvicorn
from src.api.router import router as search_router
from src.shared.conf import Config

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger("MAIN_APP")

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
    # Validate configuration before starting
    if not Config.validate():
        logger.error("Configuration validation failed. Exiting...")
        exit(1)
    
    # Run the application
    uvicorn.run(
        "src.main:app", 
        host="0.0.0.0", 
        port=8000,   
        reload=True,
        log_level="info"
    )