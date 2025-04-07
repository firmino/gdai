class FolderNotFoundException(Exception):
    """
    Exception raised when a folder is not found.  
    """
    
class FileNotFoundException(Exception):
    """
    Exception raised when a file is not found.
    """ 

class FileInvalidFormatException(Exception):
    """
    Exception raised when a file has an invalid format.
    """ 

class InvalidDocumentException(Exception):
    """
    Exception raised when a document is invalid.
    """ 

class InsertDocumentBatchError(Exception):
    """
    Exception raised when there is an error inserting a batch of documents.
    """ 