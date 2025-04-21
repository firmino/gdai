"""
repository.py

This module provides a repository for managing documents and their associated text chunks
in a PostgreSQL database using pgvector. It includes methods for creating tables,
inserting data, and performing searches.

Classes:
    DocumentRepository: A repository for managing documents and document chunks.
"""

from src.shared.database import PGVectorDatabase
from src.embedding_pipeline.schema import Document, DocumentChunk
from typing import List


class DocumentRepository:
    """
    A repository for managing documents and document chunks in a PostgreSQL database using pgvector.
    """

    def __init__(self):
        """
        Initializes the DocumentRepository with a PostgreSQL connection.
        """
        self.connection_pool = None

    @staticmethod
    async def create():
        """
        Initializes the PostgreSQL connection.
        """
        repository = DocumentRepository()
        await repository.load_connection_pool()
        return repository


    async def load_connection_pool(self):
        """
        Loads the PostgreSQL connection pool.
        """
        self.connection_pool = await PGVectorDatabase.get_connection_pool()

    async def close_connection_pool(self):
        """
        Closes the PostgreSQL connection pool.
        """
        if self.connection_pool:
            await self.connection_pool.close()

    async def insert_document(self, document: Document, document_chunks: List[DocumentChunk]):
        """
        Inserts a document and its associated chunks into the database.

        Args:
            document (Document): The document to insert.
            document_chunks (List[DocumentChunk]): The chunks associated with the document.
        """
        connection = await self.connection_pool.acquire()
        async with connection.transaction():
            await connection.execute(
                """
                INSERT INTO documents (id, name, pages, embedding_model_name)
                VALUES ($1, $2, $3, $4)
                ON CONFLICT (id) DO NOTHING;
            """,
                document.doc_id,
                document.doc_name,
                document.pages,
                document.embedding_model_name,
            )

            for chunk in document_chunks:
                await connection.execute(
                    """
                    INSERT INTO document_chunks (id, chunk_text, page_number, begin_offset, end_offset, embedding, fk_doc_id)
                    VALUES ($1, $2, $3, $4, $5, $6::vector, $7)
                    ON CONFLICT (id) DO NOTHING;
                """,
                    chunk.chunk_id,
                    chunk.chunk_text,
                    chunk.page_number,
                    chunk.begin_offset,
                    chunk.end_offset,
                    chunk.embedding,
                    chunk.doc_id,
                )
        await self.connection_pool.release(connection)

    async def clean_database(self):
        """
        Clears the entire database by dropping all tables.
        """
        connection = await self.connection_pool.acquire()
        async with connection.transaction():
            await connection.execute("delete from document_chunks")
            await connection.execute("delete from documents")
        await self.connection_pool.release(connection)

    async def delete_document_content(self, document_id: str):
        """
        Delete all content from a specific document.
        """
        connection = await self.connection_pool.acquire()
        async with connection.transaction():
            await connection.execute("delete from document_chunks where fk_doc_id  = $1", document_id)
            await connection.execute("delete from documents where id  = $1", document_id)
        await self.connection_pool.release(connection)

    async def get_document_metadata(self, document_id: str) -> dict:
        """
        Retrieves metadata for a specific document by its ID.

        Args:
            document_id (str): The ID of the document.

        Returns:
            dict: The metadata of the document.
        """
        connection = await self.connection_pool.acquire()
        result = await connection.fetchrow(
            """
            SELECT id, name, pages, embedding_model_name
            FROM documents
            WHERE id = $1;
        """,
            document_id,
        )
        await self.connection_pool.release(connection)
        return dict(result) if result else None

    async def search_documents_by_keyword(self, search_keyword: str, limit: int = 10, offset: int = 0) -> List[dict]:
        """
        Searches for document chunks based on a keyword.

        Args:
            search_keyword (str): The keyword to search for.
            limit (int): The maximum number of results to return.
            offset (int): The offset for pagination.

        Returns:
            List[dict]: A list of matching document chunks.
        """
        connection = await self.connection_pool.acquire()
        results = await connection.fetch(
            """
            SELECT id, fk_doc_id, chunk_text, page_number, begin_offset, end_offset
            FROM document_chunks
            WHERE chunk_text ILIKE $1
            LIMIT $2 OFFSET $3;
        """,
            f"%{search_keyword}%",
            limit,
            offset,
        )
        await self.connection_pool.release(connection)
        return [dict(result) for result in results]

    async def search_documents_by_similarity(self, embedded_query: List[float], limit: int = 10) -> List[dict]:
        """
        Searches for document chunks based on vector similarity.

        Args:
            embedded_query (List[float]): The embedding vector to search for.
            limit (int): The maximum number of results to return.

        Returns:
            List[dict]: A list of matching document chunks.
        """
        connection = await self.connection_pool.acquire()
        results = await connection.fetch(
            """
            SELECT id, fk_doc_id, chunk_text, page_number, begin_offset, end_offset,
                   1 - (embedding <=> $1) AS similarity
            FROM document_chunks
            ORDER BY embedding <=> $1
            LIMIT $2;
        """,
            embedded_query,
            limit,
        )
        await self.connection_pool.release(connection)
        return [dict(result) for result in results]
