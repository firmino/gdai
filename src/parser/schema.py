from pydantic import BaseModel, Field
from typing import Optional


class Text(BaseModel):
    """
    Represents a text content extracted from a document page.

    Attributes:
        page (int): The page number from which the text was extracted.
        text (str): The extracted text content.
    """

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
    """
    Represents an image extracted from a document page.

    Attributes:
        page (int): The page number where the image is located.
        position_x (int): The x-coordinate of the image's position.
        position_y (int): The y-coordinate of the image's position.
        width (int): The width of the image in pixels.
        height (int): The height of the image in pixels.
    """

    page: int
    position_x: int
    position_y: int
    width: int
    height: int

    def __str__(self) -> str:
        """
        Return a human-readable string representation of the Image.

        Returns:
            str: A string displaying the page number and position information.
        """
        return f"Image on page {self.page}: Position({self.position_x}, {self.position_y}), Size({self.width}x{self.height})"


class Table(BaseModel):
    """
    Represents a table extracted from a document page.

    Attributes:
        page (int): The page number where the table is located.
        cells (list[dict]): A list of dictionaries, each representing a cell in the table
                          with its content and position information.
    """

    page: int
    cells: list[dict]

    def __str__(self) -> str:
        """
        Return a human-readable string representation of the Table.

        Returns:
            str: A string displaying the page number and number of cells.
        """
        return f"Table on page {self.page}: {len(self.cells)} cells"


class Document(BaseModel):
    """
    Represents a document with its content and metadata.

    A document can contain text content, tables, and images extracted from
    the original document file.

    Attributes:
        doc_name (str): The name or title of the document.
        texts (list[Text]): List of text elements extracted from the document.
        tables (Optional[list[Table]]): List of tables extracted from the document, if any.
        images (Optional[list[Image]]): List of images extracted from the document, if any.
    """

    tenant_id: Optional[str] = Field(default="")
    doc_name: str
    texts: list[Text]
    tables: Optional[list[Table]] = Field(default_factory=list)
    images: Optional[list[Image]] = Field(default_factory=list)

    def __str__(self) -> str:
        """
        Return a human-readable string representation of the Document.

        Returns:
            str: A string displaying the document ID, name, and number of pages.
        """
        return f"Name: {self.doc_name}, Pages: {len(self.texts)}"
