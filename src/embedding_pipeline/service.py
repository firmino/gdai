"""
This module provides functionality for processing documents through an embedding pipeline.
It includes methods for splitting pages into text chunks and generating embeddings for these chunks.
"""

import os
import json
from src.embedding_pipeline.schema import Document, DocumentChunk, DocumentInput
from src.embedding_pipeline.embedding import EmbeddingModel
from src.embedding_pipeline.repository import DocumentRepository
from src.embedding_pipeline.exceptions import FolderNotFoundException
from src.embedding_pipeline.exceptions import InsertDocumentException
from src.embedding_pipeline.exceptions import DeleteDocumentException

# Constants for file validation
VALID_FILE_EXTENSION = ".json"
ERROR_INVALID_DOCUMENT = "Document must contain 'doc_id', 'doc_name', and 'pages' fields."


class EmbeddingPipelineService:
    """
    Service for processing documents through an embedding pipeline.

    Methods:
        _load_documents_from_folder(folder_path: str) -> list[DocumentInput]:
            Load and validate documents from a folder.

        _chunk_text(doc_id: str, page_number: int, page: str, chunk_size: int, overlap: int) -> list[DocumentChunk]:
            Split a page of text into smaller chunks with a specified overlap.

        _embed_chunks(chunks: list[DocumentChunk], embedding_model: EmbeddingModel) -> None:
            Generate embeddings for each text chunk using the provided embedding model.

        _process_document(document: Document, embedding_model: EmbeddingModel, chunk_size: int, overlap: int) -> list[DocumentChunk]:
            Process a document by splitting its pages into text chunks and embedding them.

        apply(documents_folder: str, embedding_model: EmbeddingModel, chunk_size: int, overlap: int) -> list[Document]:
            Apply the embedding pipeline to a list of documents.
    """

    @staticmethod
    def _chunk_text(doc_id: str, page_number: int, page: str, chunk_size: int, overlap: int) -> list[DocumentChunk]:
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
        if chunk_size <= overlap:
            raise ValueError("Chunk size must be greater than overlap.")

        page_chunks = []
        page_size = len(page)
        for i in range(0, page_size, chunk_size - overlap):
            chunk_text = page[i : i + chunk_size]
            chunk_id = f"{doc_id}-{page_number}-{i}"
            chunk = DocumentChunk(
                doc_id=doc_id,
                chunk_id=chunk_id,
                chunk_text=chunk_text,
                page_number=page_number,
                begin_offset=i,
                end_offset=min(i + chunk_size, page_size),
            )
            page_chunks.append(chunk)
        return page_chunks

    @staticmethod
    async def _embed_chunks(chunks: list[DocumentChunk], embedding_model: EmbeddingModel) -> None:
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

    @staticmethod
    async def _process_document(
        document: Document,
        embedding_model: EmbeddingModel,
        chunk_size: int = 1000,
        overlap: int = 50,
    ) -> list[DocumentChunk]:
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
        document_chunks = []
        for page_number, page in enumerate(document.pages or []):
            page_chunks = EmbeddingPipelineService._chunk_text(
                doc_id=document.doc_id,
                page_number=page_number,
                page=page,
                chunk_size=chunk_size,
                overlap=overlap,
            )
            await EmbeddingPipelineService._embed_chunks(page_chunks, embedding_model)
            document_chunks.extend(page_chunks)

        return document_chunks

    @staticmethod
    async def load_documents_from_folder(folder_path: str) -> list[DocumentInput]:
        """
        Load documents from a folder and validate their content.

        Args:
            folder_path (str): Path to the folder containing document files.

        Returns:
            list[DocumentInput]: A list of validated DocumentInput objects.

        Raises:
            FolderNotFoundException: If the folder does not exist.
            FileInvalidFormatException: If a file is not a valid JSON file.
            InvalidDocumentException: If a document is missing required fields.
        """
        if not os.path.exists(folder_path):
            raise FolderNotFoundException(f"Folder '{folder_path}' does not exist.")

        valid_documents = []
        invalid_documents_content = []
        non_json_files = []
        for file_name in os.listdir(folder_path):
            full_file_path = os.path.join(folder_path, file_name)

            if not file_name.endswith(VALID_FILE_EXTENSION):
                non_json_files.append(file_name)
                continue

            with open(full_file_path, "r") as file:
                try:
                    document_data = json.load(file)
                    document = DocumentInput(
                        doc_id=document_data["doc_id"],
                        doc_name=document_data["doc_name"],
                        pages=document_data["pages"],
                    )
                    valid_documents.append(document)

                except KeyError:
                    invalid_documents_content.append(file_name)
                    continue
                except json.JSONDecodeError:
                    invalid_documents_content.append(file_name)

        return valid_documents, invalid_documents_content, non_json_files

    @staticmethod
    async def save_document_into_db(document: Document, embedding_model: EmbeddingModel, repository: DocumentRepository, chunk_size: int = 1000, overlap: int = 50) -> list[DocumentChunk]:
        """
        Load a document and process it by splitting its pages into text chunks and embedding them.
        Args:
            document (Document): The document to load and process.
            embedding_model (EmbeddingModel): The embedding model to use.
            chunk_size (int): Maximum size of each chunk. Default is 1000.
            overlap (int): Number of overlapping characters between chunks. Default is 50.
        Returns:
            list[DocumentChunk]: A list of processed DocumentChunk objects.
        """

        document_chunks = await EmbeddingPipelineService._process_document(document, embedding_model, chunk_size, overlap)

        document_metadata = Document(
            doc_id=document.doc_id,
            doc_name=document.doc_name,
            pages=document.pages,
            embedding_model_name=str(embedding_model),
        )

        try:
            await repository.insert_document(document_metadata, document_chunks)
        except Exception as e:
            raise InsertDocumentException(f"Error while inserting document into database: {e}")

    @staticmethod
    async def delete_documents(documents: list[Document], repository: DocumentRepository) -> list[str]:
        """
        Delete a list of documents from the database.
        """
        non_deleted_documents = []
       
        for document in documents:
            try:
                await repository.delete_document(document.doc_id)
            except Exception as e:
                non_deleted_documents+= [document.doc_name]    
        return non_deleted_documents
