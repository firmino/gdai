"""
schema.py

This module defines the data models used in the embedding pipeline. It includes
classes for representing document chunks and documents, with validation and utility
methods for handling their attributes.

Classes:
    DocumentChunk: Represents a chunk of text extracted from a document page.
    Document: Represents a document composed of pages and text chunks.

Usage:
    - Use `DocumentChunk` to represent and validate individual text chunks.
    - Use `Document` to represent a complete document with pages and chunks.

Example:
    >>> chunk = DocumentChunk(
    ...     chunk_id="1",
    ...     chunk_text="Example text",
    ...     page_number=1,
    ...     begin_offset=0,
    ...     end_offset=12,
    ...     doc_id="doc1"
    ... )
    >>> print(chunk)
    DocumentChunk(chunk_id=1, page_number=1, offsets=(0, 12))

    >>> document = Document(
    ...     doc_id="doc1",
    ...     doc_name="Example Document",
    ...     pages=["Page 1 text", "Page 2 text"]
    ... )
    >>> print(document)
    Document(doc_id=doc1, doc_name=Example Document, pages=2, chunks=0)
"""

from pydantic import BaseModel, Field, field_validator, ValidationInfo
from typing import Optional


class DocumentInput(BaseModel):
    """
    Represents the input data for creating a Document.
    This is used for validation and parsing of input data.

    Attributes:
        doc_id (str): Unique identifier for the document.
        doc_name (str): Name or title of the document.
        pages (Optional[list[str]]): List of text pages in the document.
    """

    doc_id: str
    doc_name: str
    pages: list[str]

    @field_validator("doc_id")
    def validate_doc_id(cls, value, info: ValidationInfo):
        if len(value) < 1 or len(value) > 128:
            raise ValueError("doc_id must be between 1 and 128 characters")
        return value

    @field_validator("doc_name")
    def validate_doc_name(cls, value, info: ValidationInfo):
        if len(value) < 1 or len(value) > 256:
            raise ValueError("doc_name must be between 1 and 256 characters")
        return value

    @field_validator("pages")
    def validate_pages(cls, value, info: ValidationInfo):
        if len(value) == 0:
            raise ValueError("pages cannot be empty")
        return value

    def __str__(self) -> str:
        """
        Return a human-readable string representation of the DocumentInput.

        Returns:
            str: A string displaying the document id and name.
        """
        return f"DocumentInput(doc_id={self.doc_id}, doc_name={self.doc_name})"


class Document(DocumentInput):
    """
    Represents the input data for creating a Document.
    This is used for validation and parsing of input data.
    """

    embedding_model_name: str   # Model name for embedding

    @field_validator("embedding_model_name")
    def validate_embedding_model_name(cls, value, info: ValidationInfo):
        if len(value) < 1 or len(value) > 128:
            raise ValueError("embedding_model_name must be between 1 and 128 characters")
        return value

    def __str__(self) -> str:
        """
        Return a human-readable string representation of the Document.

        Returns:
            str: A string displaying the document id, name, number of pages, and number of chunks.
        """
        return f"DocumentInput(doc_id={self.doc_id}, doc_name={self.doc_name})"


class DocumentChunk(BaseModel):
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
    embedding: Optional[list[float]] = Field(default_factory=list)
    doc_id: str

    def __str__(self) -> str:
        return f"DocumentChunk(chunk_id={self.chunk_id}, page_number={self.page_number}, " f"offsets=({self.begin_offset}, {self.end_offset}))"

    @field_validator("end_offset")
    def validate_end_offset(cls, value, info: ValidationInfo):
        begin_offset = info.data["begin_offset"]
        if begin_offset is None:
            raise ValueError("begin_offset must be provided before validating end_offset")
        if value < begin_offset:
            raise ValueError("end_offset must be greater than or equal to begin_offset")
        return value
