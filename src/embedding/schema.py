"""
This module defines the data models used in the embedding pipeline.

Classes:
    Document: Represents a document with metadata and pages.
    DocumentChunk: Represents a chunk of text extracted from a document.

Usage:
    - Use `Document` to represent a complete document with metadata and pages.
    - Use `DocumentChunk` to represent and validate individual text chunks.

Example:
   
    >>> document = Document(
    ...     tenant_id="tenant1",
    ...     doc_id="doc1",
    ...     doc_name="Example Document",
    ...     pages=["Page 1 text", "Page 2 text"],
    ...     embedding_model_name="example_model"
    ... )
    >>> print(document)
    Document(doc_id=doc1, doc_name=Example Document, pages=2)

    >>> chunk = DocumentChunk(
    ...     chunk_id="chunk1",
    ...     tenant_id="tenant1",
    ...     chunk_text="Example text",
    ...     page_number=1,
    ...     begin_offset=0,
    ...     end_offset=12,
    ...     doc_id="doc1"
    ... )
    >>> print(chunk)
    DocumentChunk(chunk_id=chunk1, page_number=1, offsets=(0, 12))
"""

from pydantic import BaseModel, Field, field_validator, ValidationInfo
from typing import Optional


class Document(BaseModel):
    """
    Represents a document with metadata and pages.

    Attributes:
        embedding_model_name (str): Name of the embedding model used for the document.
    """

    tenant_id: str
    doc_id: str
    doc_name: str
    pages: list[str]

    @field_validator("tenant_id")
    def validate_tenant_id(cls, value, info: ValidationInfo):
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
        if len(value) < 3 or len(value) > 256:
            raise ValueError("tenant_id must be between 3 and 256 characters")
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
    Represents a chunk of text extracted from a document.

    Attributes:
        chunk_id (str): Unique identifier for the text chunk.
        tenant_id (str): Identifier for the tenant.
        chunk_text (str): The text content of the chunk.
        page_number (int): Page number from which the chunk was extracted.
        begin_offset (int): Starting offset within the page.
        end_offset (int): Ending offset within the page.
        embedding (Optional[list[float]]): Embedding vector for the text chunk, if available.
        doc_id (str): The ID of the document the chunk belongs to.
    """

    tenant_id: str
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
