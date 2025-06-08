import asyncio
import logging
from src.shared.embedding_model import EmbeddingModelFactory
from src.shared.llm_model import LLMModelFactory, LLMModel
from src.search.repository import SearchRepository


logger = logging.getLogger("SEARCH_SERVICE")



class SearchService:
    __PROMPT_TEMPLATE_TO_SOLVE_QUERY = """
        You are an AI assistant that helps users find relevant information in documents. 
        You will receive a query and a list of document chunks. Your task is to:

        1. Analyze the query and identify the key information needed.
        2. Evaluate which document chunks are most relevant to the query.
        3. Return a concise and accurate answer based ONLY on the relevant chunks.

        Rules:
        - Use only the information provided in the document chunks.
        - If no chunks are relevant, respond with "There is no relevant information available."
        - Keep the answer clear and concise, but ensure it fully addresses the query.
        - Do not add explanations, introductions, or notes—just the direct answer.

        Input:
        Query: {query}
        Document Chunks: {chunks}

        Answer:

    """

    def __init__(self, llm_model: LLMModel, embedding_model, repository):
        """Initialize the SearchService."""
        self.llm_model = llm_model
        self.embedding_model = embedding_model
        self.repository = repository

    async def _retrieve_relevant_chunks(self, tenant_id: str, query_id: str, query: str, chunks_limit: int):
        """
        Retrieve relevant document chunks based on the embedded query.

        Args:
            tenant_id (str): The ID of the tenant.
            query_id (str): The ID of the query.
            embedded_query (list[float]): The embedding vector of the query.
            chunks_limit (int): The maximum number of chunks to retrieve.
        Returns:
            List[ChunkQueryResult]: A list of document chunks sorted by similarity.
        """
        # Generate embedding for the query
        embedded_query = (await self.embedding_model.generate_texts_embeddings([query]))[0]

        # Retrieve chunks using vector similarity search
        chunks_result = await self.repository.get_chunks_by_vector_similarity(tenant_id, query_id, embedded_query, chunks_limit)

        # Here you could add reranking logic if needed

        return chunks_result
    
    async def _handle_no_results(self, message_id: str):
        """
        Handle the case when no relevant chunks are found.
        
        Args:
            message_id: The ID of the message.
            
        Returns:
            Dict with query results including status.
        """
        await self.repository.update_message_status(message_id, "failed")
        return 

    async def _process_llm_stream(self, message_id: str, prompt: str) -> None:
        """
        Process the streaming response from the LLM and store tokens.
        
        Args:
            message_id: The ID of the message.
            prompt: The prompt to send to the LLM.
        """
        token_number = 0
        async for token in self.llm_model.call_llm_stream(prompt):
            await self.repository.insert_result_token(message_id, token_number, token)
            token_number += 1


    async def _generate_answer(self, message_id: str, query: str, chunks_result) -> str:
        """
        Generate an answer using the LLM based on the query and relevant chunks.
        
        Args:
            message_id: The ID of the message.
            query: The query text.
            chunks_result: The relevant document chunks.
            
        Returns:
            The generated answer.
        """
        # Format chunks for the prompt
        chunks_text = "\n\n".join([chunk_res.chunk.chunk_text for chunk_res in chunks_result])
        
        # Prepare the prompt for the LLM
        prompt = self.__PROMPT_TEMPLATE_TO_SOLVE_QUERY.format(
            query=query,
            chunks=chunks_text
        )
        
        # Get streaming response from LLM and store tokens
        await self._process_llm_stream(message_id, prompt)
        
        # Assemble complete answer from stored tokens
        tokens_result = await self.repository.get_tokens_by_message_id(message_id)
        answer_text = "".join([token for token in tokens_result])
        # Update message with final answer
        await self.repository.update_message_text_and_status(message_id, answer_text)
        
        # Clean up temporary tokens
        await self.repository.clear_tokens_from_message_id(message_id)
        
        return answer_text


    async def answer_query(self, tenant_id: str, query_id: str, query: str, chunks_limit: int = 3) -> str:
        """
        Answer a query by searching for relevant documents.
        """
        # create in table message a new message with the query with status pending
        message_id = await self.repository.create_message_entry(tenant_id, query_id, query)
        try:
            # retrieve the chunks from the database based on the query
            print(f"CHUNKS LIMIT: {chunks_limit}")
            chunks_result = await self._retrieve_relevant_chunks(tenant_id, query_id, query, chunks_limit)

            if not chunks_result:  # ??????? if nothing is found is it a error or just no results? avoid answer something out of the rag
                await self._handle_no_results(message_id)
                return 
            print(f"TOTAL CHUNKS FOUND: {len(chunks_result)}")
            answer_text = await self._generate_answer(message_id, query, chunks_result)
            
            print(f"ANSWER GENERATED: {answer_text}")
            print(f"type of answer_text: {type(answer_text)}")
            #logger.info(f"Generated answer for query '{query}' with ID '{query_id}': {answer_text}")
            # update the message status to completed

            # add chunks used to the message
            #await self.repository.add_chunks_to_message(message_id, chunks_result)
            return answer_text
        except Exception as e:
            await self.repository.update_message_status(message_id, "failed")
            raise e


