"""Repository for managing documents and chunks in PostgreSQL with pgvector."""

from src.shared.database import PGVectorDatabase
from src.shared.schema import  DocumentChunk, ChunkQueryResult
from typing import List
from src.shared.logger import logger


class SearchRepository:
    def __init__(self):
        """Initialize repository."""

    async def create_message_entry(self, tenant_id: str, query_id: str, query_text: str) -> str:
        """
        Create a new message entry in the database.

        Args:
            tenant_id (str): The ID of the tenant.
            query_id (str): The ID of the query.
            query_text (str): The text of the query.
        Returns:
            id (str): The ID of the newly created message entry.
        """
        try:
            async with PGVectorDatabase.get_connection() as conn:
                # Insert a new message with 'pending' status
                query = """
                    INSERT INTO message (tenant_id, query_id, query_text, status)
                    VALUES ($1, $2, $3, 'pending')
                    RETURNING id
                """
                result = await conn.fetchval(query, tenant_id, query_id, query_text)
                logger.info(f"Created message entry with ID: {result} for tenant: {tenant_id}, query_id: {query_id}")
                return result
        except Exception as e:
            logger.error(f"Error creating message entry: {e}")
            raise

    async def get_chunks_by_vector_similarity(self, tenant_id: str, query_id: str,  query_embedding: List[float], limit: int) -> List[ChunkQueryResult]:
        """
        Get document chunks by vector similarity.

        Args:
            tenant_id (str): The ID of the tenant.
            query_embedding (List[float]): The embedding vector of the query.
            limit (int): The maximum number of chunks to return.

        Returns:
            List[DocumentChunk]: A list of document chunks sorted by similarity.
        """
        try:
            async with PGVectorDatabase.get_connection() as conn:
                query = """
                    SELECT dc.id as chunk_id,  
                           dc.tenant_id as tenant_id, 
                           dc.chunk_text as chunk_text, 
                           dc.page_number as page_number, 
                           dc.begin_offset as begin_offset, 
                           dc.end_offset as end_offset, 
                           dc.fk_doc_id as doc_id, 
                           dc.embedding <-> $2 as similarity_score,
                           d.name as doc_name 
                    FROM document_chunk dc 
                         INNER JOIN document d ON dc.fk_doc_id = d.id
                    WHERE dc.tenant_id = $1
                    ORDER BY dc.embedding <-> $2
                    LIMIT $3
                """

                rows = await conn.fetch(query, tenant_id, query_embedding, limit)
                result = []
                for row in rows:
                    chunk = DocumentChunk(
                        tenant_id= row["tenant_id"],
                        chunk_id= row["chunk_id"],
                        doc_id= row["doc_id"],
                        doc_name= row['doc_name'],
                        chunk_text= row["chunk_text"],
                        page_number= row["page_number"],
                        begin_offset= row["begin_offset"],
                        end_offset= row["end_offset"])
                    
                    chunk_result = ChunkQueryResult(tenant_id=row["tenant_id"], 
                                                    query_id=query_id, 
                                                    chunk=chunk, 
                                                    similarity=row["similarity_score"])
                    result.append(chunk_result)
                return result
        except Exception as e:
            logger.error(f"Error fetching chunks by vector similarity: {e}")
            raise

    async def insert_result_token(self, message_id, token_number:int, token_txt: str) -> None:
        """Insert a token associated with a specific query ID into the database.
        Args:
            message_id (str): The ID of the message associated with the query.
            query_id (str): The ID of the query for which the token is being
            token (str): The token to be inserted.
        """     
        try:
            async with PGVectorDatabase.get_connection() as conn:
                query = """
                    INSERT INTO token (fk_message_id, token_number, token_text)
                    VALUES ($1, $2, $3)
                """
                await conn.execute(query, message_id, token_number, token_txt)
                logger.info(f"Inserted token for message ID: {message_id}")
        except Exception as e:
            logger.error(f"Error inserting token for message ID {message_id}: {e}")
            raise


    async def get_tokens_by_message_id(self, message_id: str) -> List[str]:
        """
        Retrieve all tokens associated with a specific message ID.

        Args:
            message_id (str): The ID of the message for which to retrieve tokens.

        Returns:
            List[str]: A list of tokens associated with the message ID.
        """
        try:
            async with PGVectorDatabase.get_connection() as conn:
                query = """SELECT token_text 
                           FROM token 
                           WHERE fk_message_id = $1 
                           ORDER BY token_number"""
                rows = await conn.fetch(query, message_id)
                tokens = [row["token_text"] for row in rows]
                logger.info(f"Retrieved {len(tokens)} tokens for message ID: {message_id}")
                return tokens
        except Exception as e:
            logger.error(f"Error retrieving tokens for message ID {message_id}: {e}")
            raise


    async def clear_tokens_from_message_id(self, message_id: str) -> None:
        """
        Clear all tokens associated with a specific message ID.

        Args:
            message_id (str): The ID of the message for which to clear tokens.
        """
        try:
            async with PGVectorDatabase.get_connection() as conn:
                query = "DELETE FROM token WHERE fk_message_id = $1"
                await conn.execute(query, message_id)
                logger.info(f"Cleared tokens for message ID: {message_id}")
        except Exception as e:
            logger.error(f"Error clearing tokens for message ID {message_id}: {e}")
            raise


    async def update_message_status(self, message_id: str, status: str) -> None:
        """
        Update the status of a message.

        Args:
            message_id (str): The ID of the message to update.
            status (str): The new status to set for the message.
        """
        try:
            async with PGVectorDatabase.get_connection() as conn:
                query = "UPDATE message SET status = $1 WHERE id = $2"
                await conn.execute(query, status, message_id)
                logger.info(f"Updated message {message_id} status to {status}")
        except Exception as e:
            logger.error(f"Error updating message status for {message_id}: {e}")
            raise

    
    async def update_message_text_and_status(self, message_id: str, text: str) -> None:
        """Update the text and status of a message.
        Args:
            message_id (str): The ID of the message to update.
            text (str): The new text to set for the message.
        """
        try:
            async with PGVectorDatabase.get_connection() as conn:
                query = """
                    UPDATE message 
                    SET result = $1, status = 'completed' 
                    WHERE id = $2
                """
                await conn.execute(query, text, message_id)
                logger.info(f"Updated message {message_id} text and status to completed")
        except Exception as e:
            logger.error(f"Error updating message text for {message_id}: {e}")
            raise
    
    async def add_chunks_to_message(self, message_id: str, chunks: List[ChunkQueryResult]) -> None:
        """
        Add chunks to a message.

        Args:
            message_id (str): The ID of the message to which chunks will be added.
            chunks (List[ChunkQueryResult]): A list of ChunkQueryResult objects to add.
        """
        try:
            async with PGVectorDatabase.get_connection() as conn:
                for chunk in chunks:
                    query = """
                        INSERT INTO chunk_message (fk_message_id, fk_document_chunk_id)
                        VALUES ($1, $2)
                    """
         
                    await conn.execute(query, message_id, chunk.chunk.chunk_id)
                logger.info(f"Added {len(chunks)} chunks to message ID: {message_id}")
        except Exception as e:
            logger.error(f"Error adding chunks to message ID {message_id}: {e}")
            raise