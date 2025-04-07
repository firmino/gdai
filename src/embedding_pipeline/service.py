"""
This module provides functionality for processing documents through an embedding pipeline.
It includes methods for splitting pages into text chunks and generating embeddings for these chunks.
"""
import os
import json
from src.embedding_pipeline.schema import Document, TextChunk, DocumentInput
from src.embedding_pipeline.embedding import EmbeddingModel
from src.embedding_pipeline.repository import DocumentRepository
from src.embedding_pipeline.exceptions import (
    FolderNotFoundException,
    FileNotFoundException,
    FileInvalidFormatException,
    InvalidDocumentException,
)


class EmbeddingPipelineService:
    @staticmethod
    async def _load_documents_from_folder(folder_path: str) -> list[DocumentInput]:
        """
        Load documents from a folder and apply the embedding pipeline to each document.
        """
        documents = []

        if not os.path.exists(folder_path):
            raise FolderNotFoundException(f"Folder '{folder_path}' does not exist.")

        for file_path in os.listdir(folder_path):
            full_file_path = os.path.join(folder_path, file_path)
            if not os.path.isfile(full_file_path):
                raise FileNotFoundException(f"File '{file_path}' does not exist.")

            if file_path.endswith(".json"):
                raise FileInvalidFormatException(
                    f"File '{file_path}' is not a JSON file."
                )

            with open(full_file_path, "r") as file:
                document_data = json.load(file)
                try:
                    valid_document = Document(
                        doc_id=document_data["doc_id"],
                        doc_name=document_data["doc_name"],
                        pages=document_data["pages"],
                    )
                    documents += [valid_document]
                except Exception as e:
                    raise InvalidDocumentException(
                        f"Invalid document content in file '{full_file_path}': Document must contain 'doc_id', 'doc_name', and 'pages' fields.\n {e}"
                    )
                return documents

    @staticmethod
    def _chunk_text(
        doc_id: str, page_number: int, page: str, chunk_size: int, overlap: int
    ) -> list[TextChunk]:
        """
        Split a page of text into smaller chunks with a specified overlap.

        The page text is divided into continuous chunks of a given size. Each chunk overlaps
        the previous chunk by the specified number of characters. Each chunk is wrapped in a
        TextChunk instance that contains metadata about the text extent and location.

        Args:
            doc_id (str): The unique identifier of the document.
            page_number (int): The page number containing the text.
            page (str): The text content of the page.
            chunk_size (int): The maximum number of characters for each chunk.
            overlap (int): The number of characters each chunk should overlap with the previous one.

        Returns:
            list[TextChunk]: A list of TextChunk objects representing each chunk of text.
        """
        page_chunks = []
        page_size = len(page)
        for i in range(0, page_size, chunk_size - overlap):
            chunk_text = page[i : i + chunk_size]
            chunk_id = f"{doc_id}-{page_number}-{i}"
            chunk = TextChunk(
                doc_id=doc_id,
                chunk_id=chunk_id,
                chunk_text=chunk_text,
                page_number=page_number,
                begin_offset=i,
                end_offset=i + chunk_size,
            )
            page_chunks.append(chunk)
        return page_chunks

    @staticmethod
    async def _embed_chunks(
        chunks: list[TextChunk], embedding_model: EmbeddingModel
    ) -> None:
        """
        Generate embeddings for each text chunk using the provided embedding model.

        This method iterates through the list of TextChunk objects and updates each with its
        corresponding text embedding, generated via the embedding_model.

        Args:
            chunks (list[TextChunk]): A list of text chunks to embed.
            embedding_model (EmbeddingModel): The model used to generate embeddings.
        """
        batch_size = 64
        total_chunks = len(chunks)
        for i in range(0, total_chunks, batch_size):
            begin_batch = i
            end_batch = min(i + batch_size, total_chunks)
            batch = [chunk.chunk_text for chunk in chunks[begin_batch:end_batch]]
            embeddings = await embedding_model.embed_texts(batch)
            [
                chunks[j].embedding.extend(embeddings[j])
                for j in range(begin_batch, end_batch)
            ]

    @staticmethod
    async def _process_document(
        document: DocumentInput,
        embedding_model: EmbeddingModel,
        chunk_size: int = 1000,
        overlap: int = 50,
    ) -> Document:
        """
        Process a Document by splitting its pages into text chunks and embedding them.

        Each page of the document is divided into smaller chunks based on the specified chunk size
        and overlap parameters. Each of these chunks is then processed by the embedding model to
        generate a corresponding embedding, which is added to the chunk.

        Args:
            document (Document): A Document object containing pages of text.
            embedding_model (EmbeddingModel): The embedding model to generate text embeddings.
            chunk_size (int, optional): Maximum number of characters per chunk. Defaults to 1000.
            overlap (int, optional): Number of characters that each chunk should overlap with the previous chunk.
                                      Defaults to 50.

        Returns:
            Document: The updated Document object with chunks populated with embeddings.
        """
        document_chunks = []
        for page_number, page in enumerate(document.pages):
            page_chunks = EmbeddingPipelineService._chunk_text(
                doc_id=document.doc_id,
                page_number=page_number,
                page=page,
                chunk_size=chunk_size,
                overlap=overlap,
            )
            await EmbeddingPipelineService._embed_chunks(page_chunks, embedding_model)
            document_chunks.extend(page_chunks)

        document = Document(
            doc_id=document.doc_id,
            doc_name=document.doc_name,
            pages=document.pages,
            chunks=document_chunks,
            embedding_model_name=embedding_model.name,
        )

        return document

    @staticmethod
    async def save_documents(documents: list[Document]) -> None:
        """
        Save a list of documents to the database.
        This method is a placeholder for the actual implementation of saving documents.
        It should be implemented based on the specific database or storage mechanism used.
        """
        DocumentRepository.save_batch_documents(documents)

    @staticmethod
    async def apply(
        documents_folder: str,
        embedding_model: EmbeddingModel,
        chunk_size: int = 1000,
        overlap: int = 50,
    ) -> list[Document]:
        """
        Apply the embedding pipeline to a list of documents.

        Iterates through the list of Document objects, processing each one by embedding its text chunks.

        Args:
            documents_list (list[Document]): A list of Document objects to process.
            embedding_model (EmbeddingModel): The embedding model to generate text embeddings.

        Returns:
            list[Document]: The list of processed Document objects with embedded text chunks.
        """
        input_documents_list = (
            await EmbeddingPipelineService._load_documents_from_folder(documents_folder)
        )

        documents = []
        for idx, document_to_process in enumerate(input_documents_list):
            document = await EmbeddingPipelineService._process_document(
                document=document_to_process,
                embedding_model=embedding_model,
                chunk_size=chunk_size,
                overlap=overlap,
            )
            documents.append(document)

        EmbeddingPipelineService.save_documents(documents)
