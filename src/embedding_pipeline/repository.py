"""
repository.py

This module provides a repository for managing documents and their associated text chunks
in a Weaviate database using the API v4. It includes methods for creating collections,
inserting data, and performing searches.

Classes:
    DocumentRepository: A repository for managing documents and document chunks.

Constants:
    DOCUMENT_PROPERTIES: Defines the schema properties for a document collection.
    CHUNK_PROPERTIES: Defines the schema properties for a document chunk collection.
"""

from src.shared.database import WeaviateDatabase
from src.embedding_pipeline.schema import Document, DocumentChunk
from typing import List
from pydantic import BaseModel
from weaviate.classes.query import MetadataQuery



class Property(BaseModel):
    """
    Represents a property in a collection schema.
    """

    name: str
    dataType: List[str]


# Properties for Document and DocumentChunk collections
DOCUMENT_PROPERTIES: List[Property] = [
    Property(name="doc_id", dataType=["string"]),
    Property(name="doc_name", dataType=["string"]),
    Property(name="pages", dataType=["text[]"]),
    Property(name="embedding_model_name", dataType=["string"]),
]

CHUNK_PROPERTIES: List[Property] = [
    Property(name="doc_id", dataType=["string"]),
    Property(name="chunk_id", dataType=["string"]),
    Property(name="chunk_text", dataType=["text"]),
    Property(name="page_number", dataType=["int"]),
    Property(name="begin_offset", dataType=["int"]),
    Property(name="end_offset", dataType=["int"]),
    Property(name="embedding", dataType=["number[]"]),
]


class DocumentRepository:
    """
    A repository for managing documents and document chunks in a Weaviate database.
    """

    def __init__(self, document_collection_name: str):
        """
        Initializes the DocumentRepository with a Weaviate async client.
        """
        self.client = None
        self.document_collection_name = document_collection_name    
        self.document_chunk_collection_name = f"{document_collection_name}_chunks"


    @staticmethod
    async def list_all_collections(self)->  List[dict]:
        """
        Lists all collections in the Weaviate database.
        """
        client = await WeaviateDatabase.get_client()
        collections = await client.collections.list_all()
        return collections.to_dict()


    async def initialize_client(self):
        """
        Initializes the Weaviate async client.
        """
        self.client = await WeaviateDatabase.get_client()

    async def __create_document_collection(self):   
        await self.client.collections.create(
            self.document_collection_name,
            properties=DOCUMENT_PROPERTIES,
        )

    async def __create_document_chunk_collection(self):
        await self.client.collections.create(
            self.document_chunk_collection_name,
            properties=CHUNK_PROPERTIES,
        )

    async def create_document_collection(self, collection_name: str, properties: List[dict]) -> None:
        """
        Creates a collection with the specified properties using Weaviate API v4.
        """
        await self.__create_document_collection()
        await self.__create_document_chunk_collection()


    async def insert_document(self, collection_name: str, document: Document, documentChunks: list[DocumentChunk]) -> None:
        """
        Inserts a document into a specific collection.

        Args:
            collection_name (str): The name of the collection where the document will be inserted.
            data (dict): The document data to insert.

        Raises:
            InsertObjectError: If the document insertion fails.
        """
        collection_doc = await self.client.get(self.document_collection_name)
        await collection_doc.data.insert(document.dict())

        collection_chunks = await self.client.get(self.document_chunk_collection_name)
        for chunk in documentChunks:
            await collection_chunks.data.insert(
                properties={
                    "doc_id": document.doc_id,
                    "chunk_id": chunk.chunk_id,
                    "chunk_text": chunk.chunk_text,
                    "page_number": chunk.page_number,
                    "begin_offset": chunk.begin_offset,
                    "end_offset": chunk.end_offset,
                },
                vector={
                    "chunk_text": chunk.embedding
                }
            )

    async def drop_all_content(self) -> List[dict]:
        """
        Searches for documents in a specific collection based on a keyword.
        """ 
        await self.client.collections.delete(self.document_chunk_collection_name)
        await self.client.collections.delete(self.document_collection_name)

    async def get_document_metadata(self, document_id: str) -> dict:
        """
        Retrieves metadata for a specific document by its ID.
        """
        collection = await self.client.get(self.document_collection_name)
        return collection.to_dict()


    async def search_documents_by_keyword(self, search_keyword: str, limit=100, offset=0) -> List[dict]:
        """
        Searches for documents in a specific collection based on a keyword. 
        """
        
        collection = await self.client.get(self.docuument_chunk_collection_name)
        results = await collection.query.bm25(
            query=search_keyword, 
            properties=["chunk_text"],
            limit=limit, 
            offset=offset
        )

        return results.to_dict()

    
    async def search_documents_by_similarity(self, embeded_search_keyword:list[float], limit=10) -> List[dict]:
        """ 
        Searches for documents in a specific collection based on vector similarity. 
        """
        collection = await self.client.get(self.document_chunk_collection_name)
        results = await collection.query.near_vector(
            vector=embeded_search_keyword,
            return_metadata=MetadataQuery(distance=True),
            limit=limit
        )

        return results.to_dict()


# class CollectionRepository:
#     def __init__(self):
#         """
#         Initializes the CollectionRepository with a Weaviate async client.
#         """
#         self.client = None

#     async def initialize_client(self):
#         """
#         Initializes the Weaviate async client.
#         """
#         self.client = await WeaviateDatabase.get_client()

#     async def create_collection(self, collection_name: str, properties: List[dict]) -> None:
#         """
#         Creates a collection with the specified properties using Weaviate API v4.

#         Args:
#             collection_name (str): The name of the collection to create.
#             properties (List[dict]): The schema properties for the collection.

#         Raises:
#             CreateCollectionError: If the collection creation fails.
#         """
#         try:
#             collection_config = {
#                 "name": collection_name,
#                 "properties": properties,
#             }
#             await self.client.collection.create(collection_config)
#         except Exception as e:
#             raise CreateCollectionError(f"Failed to create collection '{collection_name}' using API v4: {e}")

#     async def delete_collection(self, collection_name: str) -> None:
#         """
#         Deletes a collection using Weaviate API v4.

#         Args:
#             collection_name (str): The name of the collection to delete.

#         Raises:
#             DropCollectionError: If the collection deletion fails.
#         """
#         try:
#             await self.client.collection.delete(collection_name)
#         except Exception as e:
#             raise DropCollectionError(f"Failed to delete collection '{collection_name}': {e}")

#     async def list_collections(self) -> List[str]:
#         """
#         Lists all collections in the Weaviate database.

#         Returns:
#             List[str]: A list of collection names.

#         Raises:
#             GetCollectionError: If retrieving the collections fails.
#         """
#         try:
#             collections = await self.client.collection.list()
#             return [collection["name"] for collection in collections]
#         except Exception as e:
#             raise GetCollectionError(f"Failed to list collections: {e}")

#     async def insert_data(self, collection_name: str, data: list[dict]) -> None:
#         """
#         Inserts data into a specific collection.

#         Args:
#             collection_name (str): The name of the collection where the data will be inserted.
#             data (dict): The data to insert into the collection.

#         Raises:
#             InsertObjectError: If the data insertion fails.
#         """
#         try:
#             await self.client.collection.insert(collection_name, data)
#         except Exception as e:
#             raise InsertObjectError(f"Failed to insert data into collection '{collection_name}': {e}")

#     async def delete_document_by_id(self, collection_name: str, document_id: str) -> None:
#         """
#         Deletes a specific document from a collection by its ID.

#         Args:
#             collection_name (str): The name of the collection.
#             document_id (str): The ID of the document to delete.

#         Raises:
#             DeleteDataError: If the document deletion fails.
#         """
#         try:
#             await self.client.collection.delete_object(collection_name, document_id)
#         except Exception as e:
#             raise DeleteDataError(f"Failed to delete document with ID '{document_id}' from collection '{collection_name}': {e}")

#     async def search_text_in_pages(self, collection_name: str, query: str, limit: int = 10, fields=list) -> List[dict]:
#         """
#         Performs a textual search in the pages of documents within a collection.

#         Args:
#             collection_name (str): The name of the collection to search in.
#             query (str): The textual query to search for.
#             limit (int): The maximum number of results to return.

#         Returns:
#             List[dict]: A list of documents matching the query.

#         Raises:
#             SearchByKeywordError: If the search operation fails.
#         """
#         try:
#             results = await self.client.collection.search(
#                 collection_name=collection_name,
#                 query=query,
#                 fields=fields,
#                 limit=limit,
#             )
#             return results
#         except Exception as e:
#             raise SearchByKeywordError(f"Failed to perform textual search in collection '{collection_name}': {e}")

#     async def search_by_vector(self, collection_name: str, vector: list[float], limit: int = 10, fields: list = None) -> List[dict]:
#         """
#         Performs a vector similarity search in a collection.

#         Args:
#             collection_name (str): The name of the collection to search in.
#             vector (list[float]): The vector to use for similarity search.
#             limit (int): The maximum number of results to return.
#             fields (list): The fields to retrieve in the search results.

#         Returns:
#             List[dict]: A list of documents matching the vector similarity.

#         Raises:
#             SearchByVectorError: If the vector search operation fails.
#         """
#         try:
#             results = await self.client.collection.search(
#                 collection_name=collection_name,
#                 vector=vector,
#                 fields=fields or ["doc_id", "doc_name", "pages"],
#                 limit=limit,
#             )
#             return results
#         except Exception as e:
#             raise SearchByVectorError(f"Failed to perform vector search in collection '{collection_name}': {e}")
