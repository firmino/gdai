"""
This module provides functionality for processing documents through an embedding pipeline.
It includes methods for splitting pages into text chunks and generating embeddings for these chunks.
"""

import os
from src.embedding_pipeline.schema import Document, DocumentChunk
from src.embedding_pipeline.embedding import EmbeddingModel, CohereEmbeddingModel
from src.embedding_pipeline.repository import DocumentRepository


class EmbeddingDocumentService:
    """
    Service for processing documents through an embedding pipeline.

    Methods:
        _chunk_text(doc_id: str, page_number: int, page: str, chunk_size: int, overlap: int) -> list[DocumentChunk]:
            Split a page of text into smaller chunks with a specified overlap.

        _embed_chunks(chunks: list[DocumentChunk], embedding_model: EmbeddingModel) -> None:
            Generate embeddings for each text chunk using the provided embedding model.

        process_document(document: Document) -> None:
            Process a document by splitting its pages into text chunks and embedding them.
    """

    EMBEDDING_SERVICE = None

    def __init__(self, embedding_model: EmbeddingModel, document_repository: DocumentRepository, chunk_size: int = 1000, chunk_overlap: int = 50):
        """
        Initialize the EmbeddingDocumentActor with an embedding model and a document repository.
        """
        self.embedding_model: EmbeddingModel = embedding_model
        self.chunk_size: int = chunk_size
        self.chunk_overlap: int = chunk_overlap
        self.repository = document_repository

        if self.chunk_size <= self.chunk_overlap:
            raise ValueError("Chunk size must be greater than overlap.")

    @staticmethod
    async def create():
        """
        Create an instance of the EmbeddingDocumentService.
        This method initializes the service with the embedding model and document repository.
        It uses environment variables to configure the chunk size, overlap, and embedding model.
        If the service is already initialized, it returns the existing instance.
        Raises:
            ValueError: If any of the environment variables are not set.
            ValueError: If the chunk size is less than or equal to the overlap.
        Returns:
            EmbeddingDocumentService: An instance of the EmbeddingDocumentService.
        """
        
        if EmbeddingDocumentService.EMBEDDING_SERVICE is None:
            chunk_size = int(os.getenv("CHUNK_SIZE"))
            chunk_overlap = int(os.getenv("CHUNK_OVERLAP"))
            embedding_model_name = os.getenv("EMBEDDING_MODEL")

            if embedding_model_name is None:
                raise ValueError("EMBEDDING_MODEL environment variable is not set.")
            if chunk_size is None:
                raise ValueError("CHUNK_SIZE environment variable is not set.")
            if chunk_overlap is None:
                raise ValueError("CHUNK_OVERLAP environment variable is not set.")

            if embedding_model_name == "cohere/embed-v4.0":
                embedding_model = await CohereEmbeddingModel.create()

            document_repository = DocumentRepository()
            EmbeddingDocumentService.EMBEDDING_SERVICE = EmbeddingDocumentService(
                embedding_model=embedding_model, document_repository=document_repository, chunk_size=chunk_size, chunk_overlap=chunk_overlap
            )
        return EmbeddingDocumentService.EMBEDDING_SERVICE

    async def _chunk_page(self, tenant_id, doc_id, page_number, page) -> list[DocumentChunk]:
        page_size = len(page)
        page_chunks = []

        for i in range(0, page_size, self.chunk_size - self.chunk_overlap):
            chunk_text = page[i : i + self.chunk_size]
            chunk_id = f"{tenant_id}_{doc_id}_{page_number}_{i}"
            chunk = DocumentChunk(
                chunk_id=chunk_id,
                doc_id=doc_id,
                tenant_id=tenant_id,
                chunk_text=chunk_text,
                page_number=page_number,
                begin_offset=i,
                end_offset=i + self.chunk_size,
            )
            page_chunks.append(chunk)
        return page_chunks

    async def _chunk_document(self, doc: str) -> list[DocumentChunk]:
        """
        Split a page of text into smaller chunks with a specified overlap.

        Args:
            doc_id (str): Document ID.
            page_number (int): Page number.
            page (str): Text content of the page.
            chunk_size (int): Maximum size of each chunk.
            overlap (int): Number of overlapping characters between chunks.

        Returns:
            list[DocumentChunk]: A list of DocumentChunk objects.

        Raises:
            ValueError: If chunk_size is less than or equal to overlap.
        """
        page_chunks = []
        num_pages = len(doc.pages)
        for i in range(num_pages):
            page_number = i + 1
            page_chunks.extend(await self._chunk_page(doc.tenant_id, doc.doc_id, page_number, doc.pages[i]))
        return page_chunks

    async def _embed_chunks(self, chunks: list[DocumentChunk], embedding_model: EmbeddingModel) -> None:
        """
        Generate embeddings for each text chunk using the provided embedding model.

        Args:
            chunks (list[DocumentChunk]): List of DocumentChunk objects.
            embedding_model (EmbeddingModel): The embedding model to use.

        Returns:
            None
        """
        batch_size = 64
        for i in range(0, len(chunks), batch_size):
            batch = chunks[i : i + batch_size]
            texts = [chunk.chunk_text for chunk in batch]
            embeddings = await embedding_model.generate_texts_embeddings(texts)
            for chunk, embedding in zip(batch, embeddings):
                chunk.embedding = embedding

    async def process_document(self, document: Document) -> None:
        """
        Process a Document by splitting its pages into text chunks and embedding them.

        Args:
            document (Document): The document to process.
            embedding_model (EmbeddingModel): The embedding model to use.
            chunk_size (int): Maximum size of each chunk. Default is 1000.
            overlap (int): Number of overlapping characters between chunks. Default is 50.

        Returns:
            list[DocumentChunk]: A list of processed DocumentChunk objects.
        """
        
        document_chunks = await self._chunk_document(document)
        await self._embed_chunks(document_chunks, self.embedding_model)
        await self.repository.insert_document_metadata(document)
        await self.repository.insert_document_chunks(document_chunks)
