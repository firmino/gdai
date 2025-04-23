class InvalidAPIKeyException(Exception):
    """
    Exception raised when an invalid API key is provided.
    """


class FolderNotFoundException(Exception):
    """
    Exception raised when a folder is not found.
    """


class FileInvalidFormatException(Exception):
    """
    Exception raised when a file has an invalid format.
    """


class InvalidDocumentException(Exception):
    """
    Exception raised when a document is invalid.
    """


class SearchByKeywordError(Exception):
    """
    Exception raised when a keyword search fails.
    """


class SearchByVectorError(Exception):
    """
    Exception raised when a vector similarity search fails.
    """


class InsertDocumentException(Exception):
    """
    Exception raised when inserting an object into a collection fails.
    """


class DeleteDocumentException(Exception):
    """
    Exception raised when deleting data from a collection fails.
    """
