"""
This module defines the data models used in the embedding pipeline. It includes
classes for representing document chunks and documents, with validation and utility
methods for handling their attributes.

Classes:
    DocumentInput: Represents the input data for creating a Document.
    Document: Represents a document composed of pages and text chunks.
    DocumentChunk: Represents a chunk of text extracted from a document page.

Usage:
    - Use `DocumentInput` to validate and parse input data for documents.
    - Use `Document` to represent a complete document with metadata and pages.
    - Use `DocumentChunk` to represent and validate individual text chunks.

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
    Document(doc_id=doc1, doc_name=Example Document, pages=2)
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
        pages (list[str]): List of text pages in the document.
    """

    doc_id: str
    doc_name: str
    pages: list[str]

    @field_validator("doc_id")
    def validate_doc_id(cls, value, info: ValidationInfo):
        """
        Validates the length of the document ID.

        Args:
            value (str): The document ID to validate.
            info (ValidationInfo): Additional validation context.

        Returns:
            str: The validated document ID.

        Raises:
            ValueError: If the document ID is not between 1 and 128 characters.
        """
        if len(value) < 1 or len(value) > 128:
            raise ValueError("doc_id must be between 1 and 128 characters")
        return value

    @field_validator("doc_name")
    def validate_doc_name(cls, value, info: ValidationInfo):
        """
        Validates the length of the document name.

        Args:
            value (str): The document name to validate.
            info (ValidationInfo): Additional validation context.

        Returns:
            str: The validated document name.

        Raises:
            ValueError: If the document name is not between 1 and 256 characters.
        """
        if len(value) < 1 or len(value) > 256:
            raise ValueError("doc_name must be between 1 and 256 characters")
        return value

    @field_validator("pages")
    def validate_pages(cls, value, info: ValidationInfo):
        """
        Validates that the pages list is not empty.

        Args:
            value (list[str]): The list of pages to validate.
            info (ValidationInfo): Additional validation context.

        Returns:
            list[str]: The validated list of pages.

        Raises:
            ValueError: If the pages list is empty.
        """
        if len(value) == 0:
            raise ValueError("pages cannot be empty")
        return value

    def __str__(self) -> str:
        """
        Return a human-readable string representation of the DocumentInput.

        Returns:
            str: A string displaying the document ID and name.
        """
        return f"DocumentInput(doc_id={self.doc_id}, doc_name={self.doc_name})"


class Document(DocumentInput):
    """
    Represents a document composed of pages and metadata.

    Attributes:
        embedding_model_name (str): Name of the embedding model used for the document.
    """

    embedding_model_name: str

    @field_validator("embedding_model_name")
    def validate_embedding_model_name(cls, value, info: ValidationInfo):
        """
        Validates the length of the embedding model name.

        Args:
            value (str): The embedding model name to validate.
            info (ValidationInfo): Additional validation context.

        Returns:
            str: The validated embedding model name.

        Raises:
            ValueError: If the embedding model name is not between 1 and 128 characters.
        """
        if len(value) < 1 or len(value) > 128:
            raise ValueError("embedding_model_name must be between 1 and 128 characters")
        return value

    def __str__(self) -> str:
        """
        Return a human-readable string representation of the Document.

        Returns:
            str: A string displaying the document ID, name, and number of pages.
        """
        return f"Document(doc_id={self.doc_id}, doc_name={self.doc_name}, pages={len(self.pages)})"


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
        doc_id (str): The ID of the document the chunk belongs to.
    """

    chunk_id: str
    chunk_text: str = Field(min_length=1)
    page_number: int = Field(ge=0)  # Must be >= 0
    begin_offset: int = Field(ge=0)  # Must be >= 0
    end_offset: int = Field(ge=0)  # Must be >= 0
    embedding: Optional[list[float]] = Field(default_factory=list)
    doc_id: str

    def __str__(self) -> str:
        """
        Return a human-readable string representation of the DocumentChunk.

        Returns:
            str: A string displaying the chunk ID, page number, and offsets.
        """
        return f"DocumentChunk(chunk_id={self.chunk_id}, page_number={self.page_number}, offsets=({self.begin_offset}, {self.end_offset}))"

    @field_validator("end_offset")
    def validate_end_offset(cls, value, info: ValidationInfo):
        """
        Validates that the end offset is greater than or equal to the begin offset.

        Args:
            value (int): The end offset to validate.
            info (ValidationInfo): Additional validation context.

        Returns:
            int: The validated end offset.

        Raises:
            ValueError: If the end offset is less than the begin offset.
        """
        begin_offset = info.data["begin_offset"]
        if begin_offset is None:
            raise ValueError("begin_offset must be provided before validating end_offset")
        if value < begin_offset:
            raise ValueError("end_offset must be greater than or equal to begin_offset")
        return value
