"""
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

    Methods:
        create() -> DocumentRepository:
            Initializes the PostgreSQL connection and returns a repository instance.

        close_connection_pool() -> None:
            Closes the PostgreSQL connection pool.

        insert_document(document: Document, document_chunks: List[DocumentChunk]) -> None:
            Inserts a document and its associated chunks into the database.

        clean_database() -> None:
            Clears the entire database by deleting all data from tables.

        delete_document_content(document_id: str) -> None:
            Deletes all content associated with a specific document.

        get_document_metadata(document_id: str) -> dict:
            Retrieves metadata for a specific document by its ID.

        search_documents_by_keyword(search_keyword: str, limit: int, offset: int) -> List[dict]:
            Searches for document chunks based on a keyword.

        search_documents_by_similarity(embedded_query: List[float], limit: int) -> List[dict]:
            Searches for document chunks based on vector similarity.
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

        Returns:
            DocumentRepository: An instance of the repository with an active connection pool.
        """
        repository = DocumentRepository()
        await repository._load_connection_pool()
        return repository

    async def _load_connection_pool(self):
        """
        Loads the PostgreSQL connection pool.

        Returns:
            None
        """
        self.connection_pool = await PGVectorDatabase.get_connection_pool()

    async def close_connection_pool(self):
        """
        Closes the PostgreSQL connection pool.

        Returns:
            None
        """
        if self.connection_pool:
            await self.connection_pool.close()

    async def insert_document(self, document: Document, document_chunks: List[DocumentChunk]):
        """
        Inserts a document and its associated chunks into the database.

        Args:
            document (Document): The document to insert.
            document_chunks (List[DocumentChunk]): The chunks associated with the document.

        Returns:
            None
        """
        try:
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
        except Exception as e:
            print(f"Error inserting document: {e}")

    async def clean_database(self):
        """
        Clears the entire database by deleting all data from tables.

        Returns:
            None
        """
        connection = await self.connection_pool.acquire()
        async with connection.transaction():
            await connection.execute("DELETE FROM document_chunks")
            await connection.execute("DELETE FROM documents")
        await self.connection_pool.release(connection)

    

    async def delete_document(self, document_id: str):
        """
        Deletes a specific document by its ID.  
        Args:
            document_id (str): The ID of the document to delete.
        Returns:
            None
        """
        try:
            connection = await self.connection_pool.acquire()
            async with connection.transaction():
                await connection.execute("DELETE FROM document_chunks WHERE fk_doc_id = $1", document_id)
                await connection.execute("DELETE FROM documents WHERE id = $1", document_id)
            await self.connection_pool.release(connection)
        except Exception as e:
            print(f"Error deleting document: {e}")  

    # async def get_document_metadata(self, document_id: str) -> dict:
    #     """
    #     Retrieves metadata for a specific document by its ID.

    #     Args:
    #         document_id (str): The ID of the document.

    #     Returns:
    #         dict: The metadata of the document, or None if not found.
    #     """
    #     connection = await self.connection_pool.acquire()
    #     result = await connection.fetchrow(
    #         """
    #         SELECT id, name, pages, embedding_model_name
    #         FROM documents
    #         WHERE id = $1;
    #         """,
    #         document_id,
    #     )
    #     await self.connection_pool.release(connection)
    #     return dict(result) if result else None

    # async def search_documents_by_keyword(self, search_keyword: str, limit: int = 10, offset: int = 0) -> List[dict]:
    #     """
    #     Searches for document chunks based on a keyword.

    #     Args:
    #         search_keyword (str): The keyword to search for.
    #         limit (int): The maximum number of results to return. Default is 10.
    #         offset (int): The offset for pagination. Default is 0.

    #     Returns:
    #         List[dict]: A list of matching document chunks.
    #     """
    #     connection = await self.connection_pool.acquire()
    #     results = await connection.fetch(
    #         """
    #         SELECT id, fk_doc_id, chunk_text, page_number, begin_offset, end_offset
    #         FROM document_chunks
    #         WHERE chunk_text ILIKE $1
    #         LIMIT $2 OFFSET $3;
    #         """,
    #         f"%{search_keyword}%",
    #         limit,
    #         offset,
    #     )
    #     await self.connection_pool.release(connection)
    #     return [dict(result) for result in results]

    # async def search_documents_by_similarity(self, embedded_query: List[float], limit: int = 10) -> List[dict]:
    #     """
    #     Searches for document chunks based on vector similarity.

    #     Args:
    #         embedded_query (List[float]): The embedding vector to search for.
    #         limit (int): The maximum number of results to return. Default is 10.

    #     Returns:
    #         List[dict]: A list of matching document chunks ordered by similarity.
    #     """
    #     connection = await self.connection_pool.acquire()
    #     results = await connection.fetch(
    #         """
    #         SELECT id, fk_doc_id, chunk_text, page_number, begin_offset, end_offset,
    #                1 - (embedding <=> $1) AS similarity
    #         FROM document_chunks
    #         ORDER BY embedding <=> $1
    #         LIMIT $2;
    #         """,
    #         embedded_query,
    #         limit,
    #     )
    #     await self.connection_pool.release(connection)
    #     return [dict(result) for result in results]
