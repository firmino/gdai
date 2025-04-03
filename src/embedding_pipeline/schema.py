"""
Module for defining the schema used in the embedding pipeline.

This module contains the Document and TextChunk classes used to represent a document,
its pages, and the generated text chunks along with the associated embeddings.
"""

from pydantic import BaseModel


class Document(BaseModel):
    """
    Represents a document composed of pages and text chunks.

    Attributes:
        doc_id (str): Unique identifier for the document.
        doc_name (str): Title or name of the document.
        pages (list[str]): List of text pages in the document.
        chunks (list[TextChunk]): List of derived text chunks.
        embedding_model_name (Optional[str]): Name of the embedding model used, if any.
    """

    def __init__(self, doc_id: str, doc_name: str, pages: list[str]):
        """
        Initialize a Document with an id, name, and pages.

        Args:
            doc_id (str): Unique identifier for the document.
            doc_name (str): Name or title of the document.
            pages (list[str]): List of text pages for the document.
        """
        super().__init__()
        self.doc_id = doc_id
        self.doc_name = doc_name
        self.pages = pages
        self.chunks: list[TextChunk] = []
        self.embedding_model_name = None

    def __str__(self) -> str:
        """
        Return a human-readable string representation of the Document.

        Returns:
            str: A string displaying the document id, name, number of pages, and number of chunks.
        """
        return (
            f"Document(doc_id={self.doc_id}, doc_name={self.doc_name}, "
            f"pages={len(self.pages)}, chunks={len(self.chunks)})"
        )


class TextChunk(BaseModel):
    """
    Represents a chunk of text extracted from a document page.

    Attributes:
        chunk_id (str): Unique identifier for the text chunk.
        chunk_text (str): The text content of the chunk.
        page_number (int): Page number from which the chunk was extracted.
        begin_offset (int): Starting offset within the page.
        end_offset (int): Ending offset within the page.
        embedding (Optional[list[float]]): Embedding vector for the text chunk (if available).
    """

    def __init__(
        self,
        chunk_id: str,
        chunk_text: str,
        page_number: int,
        begin_offset: int,
        end_offset: int,
    ):
        """
        Initialize a TextChunk with the necessary metadata.

        Args:
            chunk_id (str): Unique identifier for the text chunk.
            chunk_text (str): The text content of the chunk.
            page_number (int): The page number from which the text is extracted.
            begin_offset (int): The starting character offset within the page.
            end_offset (int): The ending character offset within the page.
        """
        super().__init__()
        self.chunk_id = chunk_id
        self.chunk_text = chunk_text
        self.page_number = page_number
        self.begin_offset = begin_offset
        self.end_offset = end_offset
        self.embedding = None

    def __str__(self) -> str:
        """
        Return a human-readable string representation of the TextChunk.

        Returns:
            str: A string displaying the chunk id, page number, and text offsets.
        """
        return (
            f"TextChunk(chunk_id={self.chunk_id}, page_number={self.page_number}, "
            f"offsets=({self.begin_offset}, {self.end_offset}))"
        )
