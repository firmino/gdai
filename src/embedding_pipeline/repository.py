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

    async def get_document_by_id(self, document_id: str) -> Document:
        """
        Retrieves a document by its ID.
        Args:
            document_id (str): The ID of the document to retrieve.
        Returns:
            Document: The retrieved document.
        """
        async with PGVectorDatabase.get_connection() as connection:
            result = await connection.fetchrow(
                """SELECT id, 
                                                        name, 
                                                        tenant_id, 
                                                        pages, 
                                                        embedding_model_name 
                                                FROM documents 
                                                WHERE id = $1""",
                document_id,
            )
            if result is None:
                return None
            doc = Document(doc_id=result["id"], tenant_id=result["tenant_id"], doc_name=result["name"], pages=result["pages"], embedding_model_name=result["embedding_model_name"])
            return doc

    async def get_document_chunk_by_id(self, chunk_id: str) -> DocumentChunk:
        """
        Retrieves document chunks associated with a specific document ID.
        Args:
            chunk_id (str): The ID of the document chunk.
        Returns:
            List[DocumentChunk]: A list of document chunks associated with the document.
        """
        async with PGVectorDatabase.get_connection() as connection:
            result = await connection.fetchrow(
                    """SELECT id, 
                            tenant_id, 
                            chunk_text, 
                            page_number, 
                            begin_offset, 
                            end_offset, 
                            embedding, 
                            fk_doc_id  
                    FROM document_chunks 
                    WHERE id = $1""",
                    chunk_id,)

            if result is None:
                return None
            doc_chunk = DocumentChunk(
                chunk_id=result["id"],
                tenant_id=result["tenant_id"],
                chunk_text=result["chunk_text"],
                page_number=result["page_number"],
                begin_offset=result["begin_offset"],
                end_offset=result["end_offset"],
                embedding=result["embedding"],
                doc_id=result["fk_doc_id"],
            )
        return doc_chunk

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
            async with PGVectorDatabase.get_connection() as connection:
                async with connection.transaction():
                    await connection.execute(
                        """
                        INSERT INTO documents (id, tenant_id, name, pages, embedding_model_name)
                        VALUES ($1, $2, $3, $4, $5)
                        ON CONFLICT (id) DO NOTHING;
                        """,
                        document.doc_id,
                        document.tenant_id,
                        document.doc_name,
                        document.pages,
                        document.embedding_model_name,
                    )

                    for chunk in document_chunks:
                        await connection.execute(
                            """
                            INSERT INTO document_chunks (id, chunk_text, page_number, begin_offset, end_offset, embedding, fk_doc_id, tenant_id)
                            VALUES ($1, $2, $3, $4, $5, $6::vector, $7, $8)
                            ON CONFLICT (id) DO NOTHING;
                            """,
                            chunk.chunk_id,
                            chunk.chunk_text,
                            chunk.page_number,
                            chunk.begin_offset,
                            chunk.end_offset,
                            chunk.embedding,
                            chunk.doc_id,
                            chunk.tenant_id,
                        )

        except Exception as e:
            print(f"Error inserting document: {e}")

    async def delete_document(self, document_id: str):
        """
        Deletes a specific document by its ID.
        Args:
            document_id (str): The ID of the document to delete.
        Returns:
            None
        """
        try:
            async with PGVectorDatabase.get_connection() as connection:
                async with connection.transaction():
                    await connection.execute("DELETE FROM document_chunks WHERE fk_doc_id = $1", document_id)
                    await connection.execute("DELETE FROM documents WHERE id = $1", document_id)
        except Exception as e:
            print(f"Error deleting document: {e}")

    async def clean_tenant_database(self, tenant_id: str):
        """
        Clears the entire database by deleting all data from tables.

        Returns:
            None
        """
        try:
            async with PGVectorDatabase.get_connection() as connection:
                async with connection.transaction():
                    await connection.execute("DELETE FROM document_chunks where tenant_id = $1", tenant_id)
                    await connection.execute("DELETE FROM documents where tenant_id = $1", tenant_id)
        except Exception as e:
            print(f"Error cleaning tenant database: {e}")
