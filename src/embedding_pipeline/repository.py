from src.embedding_pipeline.schema import Document, TextChunk
from src.shared.database import WeaviateDatabase
from src.embedding_pipeline.exceptions import InsertDocumentBatchError
from weaviate.classes.query import MetadataQuery


class DocumentRepository:
    """
    Repository for managing documents and their associated text chunks.
    """

    def __init__(self):
        """
        Initializes the repository.
        """
        client = WeaviateDatabase.get_client()
        self.client = client

    async def create_collection(self, collection_name: str):
        """
        Creates a collection for storing documents.
        """
        self.client.collections.create(name=collection_name)

    async def drop_collection(self, collection_name: str):
        """
        Drops a collection.
        """
        self.client.collections.delete(collection_name)

    async def get_collection(self, collection_name: str):
        """
        Gets a collection.
        """
        return self.client.collections.get(collection_name)

    async def insert_documents(self, collection_name, documents: list[Document]):
        """
        Inserts a document into
        the repository.
        """
        doc_collection = await self.get_collection(collection_name)

        # insert documents
        with doc_collection.batch.dynamic() as batch:
            for doc in documents:
                batch.add_object(
                    {
                        "doc_id": doc.doc_id,
                        "doc_name": doc.doc_name,
                        "pages": doc.pages,
                        "embedding_model_name": doc.embedding_model_name,
                    }
                )
                if batch.number_errors > 10:
                    raise InsertDocumentBatchError("Error inserting document batch")

        # insert chunks 
        chunks_collection_name = f"{collection_name}_chunks"
        chunks_collection = await self.get_collection(chunks_collection_name)
        with chunks_collection.batch.dynamic() as batch:
            for doc in documents:
                for chunk in doc.chunks:
                    batch.add_object(
                        {
                            "doc_id": doc.doc_id,
                            "chunk_id": chunk.chunk_id,
                            "chunk_text": chunk.chunk_text,
                            "embedding": chunk.embedding,
                            "embedding_model_name": doc.embedding_model_name,
                        }
                    )
                    if batch.number_errors > 10:
                        raise InsertDocumentBatchError("Error inserting chunks batch")

    async def search_by_keyword(self, collection_name: str, query: str, k: int) -> list[Document]:
        """
        Retrieves similar documents based on a query.
        """
        collection = await self.get_collection(collection_name)

        results = collection.query.bm25(
            query=query,
            query_properties=["pages"],
            return_metadata=MetadataQuery(score=True),
            limit=k,
        )
        return results

    async def search_by_vector_similarity(self, collection_name: str, vector: list[float], k: int) -> list[Document]:
        """
        Retrieves similar documents based on a query.
        """
        collection = await self.get_collection(collection_name)
        
        results = collection.query.fetch_objects(
            near_vector=vector, limit=k, return_metadata=MetadataQuery(distance=True)
        )
