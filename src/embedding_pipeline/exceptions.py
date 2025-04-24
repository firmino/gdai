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


class InvalidDocumentContentException(Exception):
    """
    Exception raised when a document is invalid.
    """


class InsertDocumentException(Exception):
    """
    Exception raised when inserting an object into a collection fails.
    """


class DeleteDocumentException(Exception):
    """
    Exception raised when deleting data from a collection fails.
    """
