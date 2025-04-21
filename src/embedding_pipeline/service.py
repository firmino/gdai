"""
This module provides functionality for processing documents through an embedding pipeline.
It includes methods for splitting pages into text chunks and generating embeddings for these chunks.
"""
import os
import json
from src.embedding_pipeline.schema import Document, DocumentChunk, DocumentInput
from src.embedding_pipeline.embedding import EmbeddingModel
from src.embedding_pipeline.repository import  CollectionRepository, DOCUMENT_PROPERTIES, CHUNK_PROPERTIES
from src.embedding_pipeline.exceptions import (
    FolderNotFoundException,
    FileInvalidFormatException,
    InvalidDocumentException,
)

# Constants for file validation
VALID_FILE_EXTENSION = ".json"
ERROR_INVALID_DOCUMENT = "Document must contain 'doc_id', 'doc_name', and 'pages' fields."


class EmbeddingPipelineService:
    """
    Service for processing documents through an embedding pipeline.
    """

    @staticmethod
    async def _load_documents_from_folder(folder_path: str) -> list[DocumentInput]:
        """
        Load documents from a folder and validate their content.
        """
        if not os.path.exists(folder_path):
            raise FolderNotFoundException(f"Folder '{folder_path}' does not exist.")

        documents = []
        for file_name in os.listdir(folder_path):
            full_file_path = os.path.join(folder_path, file_name)

            if not file_name.endswith(VALID_FILE_EXTENSION):
                raise FileInvalidFormatException(f"File '{file_name}' is not a JSON file.")

            with open(full_file_path, "r") as file:
                try:
                    document_data = json.load(file)
                    document = DocumentInput(
                        doc_id=document_data["doc_id"],
                        doc_name=document_data["doc_name"],
                        pages=document_data["pages"],
                    )
                    documents.append(document)
                except KeyError as e:
                    raise InvalidDocumentException(f"Invalid document content in '{file_name}': {ERROR_INVALID_DOCUMENT}\n{e}")
                except json.JSONDecodeError as e:
                    raise FileInvalidFormatException(f"File '{file_name}' is not a valid JSON file.\n{e}")

        return documents

    @staticmethod
    def _chunk_text(doc_id: str, page_number: int, page: str, chunk_size: int, overlap: int) -> list[DocumentChunk]:
        """
        Split a page of text into smaller chunks with a specified overlap.
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
    async def apply(
        documents_folder: str,
        embedding_model: EmbeddingModel,
        document_repository_name: str, 
        chunk_size: int = 1000,
        overlap: int = 50,
    ) -> list[Document]:
        """
        Apply the embedding pipeline to a list of documents.
        """
        chunk_repository_name = f"{document_repository_name}_chunks"
        input_documents = await EmbeddingPipelineService._load_documents_from_folder(documents_folder)
        repository = CollectionRepository()
        await repository.initialize_client()

        # Create document and chunk collections
        await repository.create_collection(document_repository_name, [prop.dict() for prop in DOCUMENT_PROPERTIES])
        await repository.create_collection(chunk_repository_name, [prop.dict() for prop in CHUNK_PROPERTIES])

        for document in input_documents:
            # Process document to generate chunks
            document_chunks = await EmbeddingPipelineService._process_document(
                document, embedding_model, chunk_size, overlap
            )

            # Insert document and chunks into respective collections
            await repository.insert_data(document_repository_name, document.dict())
            await repository.insert_data(chunk_repository_name, [chunk.dict() for chunk in document_chunks])

        return input_documents
