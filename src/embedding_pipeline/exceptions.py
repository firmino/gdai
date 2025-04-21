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

class InsertDocumentBatchException(Exception):
    """
    Exception raised when there is an error inserting a batch of documents.
    """

class CreateCollectionError(Exception):
    """
    Exception raised when creating a collection fails.
    """

class DropCollectionError(Exception):
    """
    Exception raised when dropping a collection fails.
    """

class GetCollectionError(Exception):
    """
    Exception raised when retrieving a collection fails.
    """

class SearchByKeywordError(Exception):
    """
    Exception raised when a keyword search fails.
    """

class SearchByVectorError(Exception):
    """
    Exception raised when a vector similarity search fails.
    """


class InsertObjectError(Exception):
    """
    Exception raised when inserting an object into a collection fails.
    """

class DeleteDataError(Exception):
    """
    Exception raised when deleting data from a collection fails.
    """