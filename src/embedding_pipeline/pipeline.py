"""
This module provides functionality for processing documents through an embedding pipeline.
It includes methods for splitting pages into text chunks and generating embeddings for these chunks.
"""

from src.embedding_pipeline.schema import Document, TextChunk
from src.embedding_pipeline.embedding import EmbeddingModel


class EmbeddingPipeline:
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
            batch = [chunk.chunk_text for chunk in chunks[begin_batch : i + end_batch]]
            embeddings = await embedding_model.embed_texts(batch)
            [chunks[j].embedding.extend(embeddings[j])for j in range(begin_batch, end_batch)]

    @staticmethod
    async def apply(
        document: Document,
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
        for page_number, page in enumerate(document.pages):
            # The parameters below can be changed according to requirement.
            page_chunks = EmbeddingPipeline._chunk_text(
                doc_id=document.doc_id,
                page_number=page_number,
                page=page,
                chunk_size=chunk_size,
                overlap=overlap,
            )

            document.chunks.extend(page_chunks)
            await EmbeddingPipeline._embed_chunks(page_chunks, embedding_model)
        return document


# TODO: CHANGE FUNCTIONS TO ASYNC FUNCTIONS
