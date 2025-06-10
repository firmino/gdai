class InvalidAPIKeyException(Exception):
    """
    Exception raised when an invalid API key is provided.
    """


class InvalidDocumentContentException(Exception):
    """
    Exception raised when a document is invalid.
    """


class InsertDocumentException(Exception):
    """
    Exception raised when inserting an object into a collection fails.
    """
