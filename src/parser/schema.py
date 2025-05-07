from pydantic import BaseModel, Field
from typing import Optional


class Text(BaseModel):
    page: int
    text: str

    def __str__(self) -> str:
        """
        Return a human-readable string representation of the Page.

        Returns:
            str: A string displaying the page number and a snippet of the text.
        """
        return f"Page {self.page}: {self.text[:500]}..." 


class Image(BaseModel):
    page: int
    position_x: int
    position_y: int
    width: int
    height: int


class Table(BaseModel):
    page: int
    cells: list[dict]


class Document(BaseModel):
    """
    Represents a document with metadata and pages.

    Attributes:
        embedding_model_name (str): Name of the embedding model used for the document.
    """
    doc_name: str
    texts: list[Text]
    tables: Optional[list[Table]] = Field()
    images: Optional[list[Image]] = Field()

  

    def __str__(self) -> str:
        """
        Return a human-readable string representation of the Document.

        Returns:
            str: A string displaying the document ID, name, and number of pages.
        """
        return f"Name: {self.doc_name}, Pages: {len(self.texts)}"