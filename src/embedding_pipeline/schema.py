"""
Module for defining the schema used in the embedding pipeline.

This module contains the Document and TextChunk classes used to represent a document,
its pages, and the generated text chunks along with the associated embeddings.
"""

from pydantic import BaseModel, Field,  field_validator


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

    chunk_id: str
    chunk_text: str = Field(min_length=1)
    page_number: int = Field(ge=0)  # >= 0
    begin_offset: int = Field(ge=0)  # >= 0
    end_offset: int = Field(ge=0)
    embedding: list[float] = []
    
    def __str__(self) -> str:
        return (
            f"TextChunk(chunk_id={self.chunk_id}, page_number={self.page_number}, "
            f"offsets=({self.begin_offset}, {self.end_offset}))"
        )

    @field_validator("end_offset")
    def validate_end_offset(cls, value, values):
        if value < values.data["begin_offset"]:
            raise ValueError("end_offset must be greater than or equal to begin_offset")
        return value


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

    doc_id: str
    doc_name: str
    pages: list[str] | None = None
    chunks: list[TextChunk] = []
    embedding_model_name: str | None = None

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
