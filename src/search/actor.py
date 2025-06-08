import asyncio  
import logging
from src.shared.broker import dramatiq
from src.search.repository import SearchRepository
from src.search.service import SearchService
from src.shared.embedding_model import EmbeddingModelFactory
from src.shared.llm_model import LLMModelFactory
from src.search.conf import Config 

logger = logging.getLogger("ACTOR_SEARCH")
try:
    embedding_model = asyncio.run(EmbeddingModelFactory.create())
    llm_model = asyncio.run(LLMModelFactory.create())
    search_repository = SearchRepository()
    search_service = SearchService(
        llm_model=llm_model,
        embedding_model=embedding_model,
        repository=search_repository
    )
    logger.info(f"Search service initialized successfully with model: {str(llm_model)}")
except Exception as e:
    logger.critical(f"Failed to initialize search components: {str(e)}")
    raise RuntimeError("Search service initialization failed") from e   


@dramatiq.actor(queue_name=Config.RABBIT_MQ_QUEUE_SEARCH, max_retries=Config.MAX_RETRIES, min_backoff=Config.RETRY_DELAY)
def search_query(message_data: dict):
    """
    Actor function to handle search queries.
    
    Args:
        message_data (dict): The data containing the query and related information.
    """

    try:
        if not isinstance(message_data, dict):
            logger.error(f"Invalid message data type: {type(message_data)}")
            raise TypeError("message_data must be a dictionary")

        tenant_id = message_data.get("tenant_id")
        query_id = message_data.get("query_id")
        query_text = message_data.get("query_text")
        
        
        if not tenant_id or not query_id or not query_text:
            logger.error("Missing required fields in message data")
            raise ValueError("tenant_id, query_id, and query_text are required in message data")
        logger.info(f"Received search query for tenant: {tenant_id}, query_id: {query_id}")
        # Process the search query
        asyncio.run(search_service.answer_query(tenant_id, query_id, query_text, chunks_limit=100))
    except Exception as e:
        logger.error(f"Error processing search query: {str(e)}")
        raise e from e  