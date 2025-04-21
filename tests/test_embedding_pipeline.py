"""
Unit tests for the schema, repository, and service modules used in the embedding pipeline.
"""

import pytest
from unittest.mock import AsyncMock, MagicMock
from src.embedding_pipeline.schema import Document, DocumentChunk, DocumentInput
# from src.embedding_pipeline.exceptions import (
#     FieldValueError,
#     # CreateCollectionError,
#     # DropCollectionError,
#     # GetCollectionError,
#     # InsertObjectError,
#     # SearchByKeywordError,
#     # SearchByVectorError,
#     # DeleteDataError,
# )
# from src.embedding_pipeline.service import EmbeddingPipelineService
# from src.embedding_pipeline.embedding import EmbeddingModel
# from src.embedding_pipeline.exceptions import (
#     #FolderNotFoundException,
#     FileInvalidFormatException,
#     InvalidDocumentException,
# )


class TestSchemaDocumentInput:

    def test_valid_document_input(self):
        input_data = {
            "doc_id": "doc1",
            "doc_name": "Test Document",
            "pages": ["Page 1", "Page 2"],
        }
        document_input = DocumentInput(**input_data)
        assert document_input.doc_id == "doc1"
        assert document_input.doc_name == "Test Document"
        assert document_input.pages == ["Page 1", "Page 2"]
        

    def test_invalid_document_input(self):
        input_data = {
            "doc_id": "doc1",
            "doc_name": "Test Document",
            "pages": "Invalid Page",
        }
        with pytest.raises(ValueError):
            DocumentInput(**input_data)

    def test_invalid_document_input_without_pages(self):
        input_data = {
            "doc_id": "doc1",
            "doc_name": "Test Document",
        }
       
        with pytest.raises(ValueError):
            DocumentInput(**input_data)

    def test_doc_id_minimum_length(self):
        input_data = {
            "doc_id": "",
            "doc_name": "Test Document",
            "pages": ["Page 1", "Page 2"],
        }
        with pytest.raises(ValueError, match="doc_id must be between 1 and 128 characters"):
            DocumentInput(**input_data)

    def test_doc_id_maximum_length(self):
        input_data = {
            "doc_id": "d" * 129,
            "doc_name": "Test Document",
            "pages": ["Page 1", "Page 2"],
        }
        with pytest.raises(ValueError, match="doc_id must be between 1 and 128 characters"):
            DocumentInput(**input_data)

    def test_doc_name_minimum_length(self):
        input_data = {
            "doc_id": "doc1",
            "doc_name": "",
            "pages": ["Page 1", "Page 2"],
        }
        with pytest.raises(ValueError, match="doc_name must be between 1 and 256 characters"):
            DocumentInput(**input_data)

    def test_doc_name_maximum_length(self):
        input_data = {
            "doc_id": "doc1",
            "doc_name": "d" * 257,
            "pages": ["Page 1", "Page 2"],
        }
        with pytest.raises(ValueError, match="doc_name must be between 1 and 256 characters"):
            DocumentInput(**input_data)


class TestSchemaDocument:
    def test_valid_document(self):
        document = Document(
            doc_id="doc1",
            doc_name="Test Document",
            pages=["Page 1", "Page 2"],
            embedding_model_name="test_model",
        )
        assert document.doc_id == "doc1"
        assert document.doc_name == "Test Document"
        assert document.pages == ["Page 1", "Page 2"]
        assert document.embedding_model_name == "test_model"

    def test_invalid_document_without_doc_id(self):
        with pytest.raises(ValueError):
            Document(
                # doc_id is missing
                doc_name="Test Document",
                pages=["Page 1", "Page 2"],
                embedding_model_name="test_model",
            )

    def test_invalid_document_without_doc_name(self):
        with pytest.raises(ValueError):
            Document(
                doc_id="doc1",
                # doc_name is missing
                pages=["Page 1", "Page 2"],
                embedding_model_name="test_model",
            )

    def test_invalid_document_without_pages(self):
        with pytest.raises(ValueError):
            Document(
                doc_id="doc1",
                doc_name="Test Document",
                embedding_model_name="test_model",
            )

    def test_invalid_document_without_embedding_model_name(self):
        with pytest.raises(ValueError):

            Document(
                doc_id="doc1",
                doc_name="Test Document",
                pages=["Page 1", "Page 2"],
            )

class TestDocumentChunk:
    def test_valid_document_chunk(self):
        chunk = DocumentChunk(
            chunk_id="chunk1",
            chunk_text="This is a test chunk.",
            page_number=1,
            begin_offset=0,
            end_offset=20,
            doc_id="doc1",
        )
        assert chunk.chunk_id == "chunk1"
        assert chunk.chunk_text == "This is a test chunk."
        assert chunk.page_number == 1
        assert chunk.begin_offset == 0
        assert chunk.end_offset == 20
        assert chunk.doc_id == "doc1"

    def test_invalid_end_offset(self):
        with pytest.raises(ValueError, match="end_offset must be greater than or equal to begin_offset"):
            DocumentChunk(
                chunk_id="chunk1",
                chunk_text="This is a test chunk.",
                page_number=1,
                begin_offset=10,
                end_offset=5,
                doc_id="doc1",
            )

    def test_str_representation(self):
        chunk = DocumentChunk(
            chunk_id="chunk1",
            chunk_text="This is a test chunk.",
            page_number=1,
            begin_offset=0,
            end_offset=20,
            doc_id="doc1",
        )
        assert str(chunk) == "DocumentChunk(chunk_id=chunk1, page_number=1, offsets=(0, 20))"


# class TestDocument:
#     def test_valid_document(self):
#         document = Document(
#             doc_id="doc1",
#             doc_name="Test Document",
#             pages=["Page 1 text", "Page 2 text"],
#             embedding_model_name="test_model",
#         )
#         assert document.doc_id == "doc1"
#         assert document.doc_name == "Test Document"
#         assert document.pages == ["Page 1 text", "Page 2 text"]
#         assert document.embedding_model_name == "test_model"

#     def test_str_representation(self):
#         document = Document(
#             doc_id="doc1",
#             doc_name="Test Document",
#             pages=["Page 1 text", "Page 2 text"],
#         )
#         assert str(document) == "DocumentInput(doc_id=doc1, doc_name=Test Document)"


# class TestDocumentInput:
#     def test_valid_document_input(self):
#         document_input = DocumentInput(
#             doc_id="doc1",
#             doc_name="Test Document",
#             pages=["Page 1 text", "Page 2 text"],
#         )
#         assert document_input.doc_id == "doc1"
#         assert document_input.doc_name == "Test Document"
#         assert document_input.pages == ["Page 1 text", "Page 2 text"]

#     def test_str_representation(self):
#         document_input = DocumentInput(
#             doc_id="doc1",
#             doc_name="Test Document",
#         )
#         assert str(document_input) == "DocumentInput(doc_id=doc1, doc_name=Test Document)"


# class TestCollectionRepository:
#     @pytest.fixture
#     def mock_repository(self):
#         """
#         Fixture to create a mock CollectionRepository instance.
#         """
#         repo = CollectionRepository()
#         repo.client = MagicMock()
#         return repo

#     @pytest.mark.asyncio
#     async def test_create_collection_success(self, mock_repository):
#         mock_repository.client.collection.create = AsyncMock()
#         await mock_repository.create_collection("test_collection", [{"name": "field", "dataType": ["string"]}])
#         mock_repository.client.collection.create.assert_called_once_with(
#             {
#                 "name": "test_collection",
#                 "properties": [{"name": "field", "dataType": ["string"]}],
#             }
#         )

    #@pytest.mark.asyncio
    # async def test_create_collection_failure(self, mock_repository):
    #     mock_repository.client.collection.create = AsyncMock(side_effect=Exception("Creation failed"))
    #     with pytest.raises(CreateCollectionError, match="Failed to create collection 'test_collection'"):
    #         await mock_repository.create_collection("test_collection", [{"name": "field", "dataType": ["string"]}])

    # @pytest.mark.asyncio
    # async def test_delete_collection_success(self, mock_repository):
    #     mock_repository.client.collection.delete = AsyncMock()
    #     await mock_repository.delete_collection("test_collection")
    #     mock_repository.client.collection.delete.assert_called_once_with("test_collection")

    # @pytest.mark.asyncio
    # async def test_delete_collection_failure(self, mock_repository):
    #     mock_repository.client.collection.delete = AsyncMock(side_effect=Exception("Deletion failed"))
    #     with pytest.raises(DropCollectionError, match="Failed to delete collection 'test_collection'"):
    #         await mock_repository.delete_collection("test_collection")

    # @pytest.mark.asyncio
    # async def test_list_collections_success(self, mock_repository):
    #     mock_repository.client.collection.list = AsyncMock(return_value=["collection1", "collection2"])
    #     collections = await mock_repository.list_collections()
    #     assert collections == ["collection1", "collection2"]
    #     mock_repository.client.collection.list.assert_called_once()

    # @pytest.mark.asyncio
    # async def test_list_collections_failure(self, mock_repository):
    #     mock_repository.client.collection.list = AsyncMock(side_effect=Exception("Listing failed"))
    #     with pytest.raises(GetCollectionError, match="Failed to list collections"):
    #         await mock_repository.list_collections()

    # @pytest.mark.asyncio
    # async def test_insert_object_success(self, mock_repository):
    #     mock_repository.client.data_object.create = AsyncMock()
    #     await mock_repository.insert_object("test_collection", {"field": "value"})
    #     mock_repository.client.data_object.create.assert_called_once_with(
    #         {
    #             "class": "test_collection",
#             "properties": {"field": "value"},
#         }
#     )

    # @pytest.mark.asyncio
    # async def test_insert_object_failure(self, mock_repository):
    #     mock_repository.client.data_object.create = AsyncMock(side_effect=Exception("Insertion failed"))
    #     with pytest.raises(InsertObjectError, match="Failed to insert object into collection 'test_collection'"):
    #         await mock_repository.insert_object("test_collection", {"field": "value"})

    # @pytest.mark.asyncio
    # async def test_search_by_keyword_success(self, mock_repository):
    #     mock_repository.client.query.get.return_value = MagicMock(
    #         with_bm25=MagicMock(
    #             return_value=MagicMock(
    #                 with_limit=MagicMock(
    #                     return_value=MagicMock(do=MagicMock(return_value={"data": {"Get": {"test_collection": [{"doc_id": "doc1", "doc_name": "Test Document", "pages": ["Page 1 text"]}]}}}))
    #                 )
    #             )
    #         )
    #     )

    #     results = await mock_repository.search_by_keyword("test_collection", "test", 1)
    #     assert len(results) == 1
    #     assert results[0].doc_id == "doc1"
    #     assert results[0].doc_name == "Test Document"

    # @pytest.mark.asyncio
    # async def test_search_by_keyword_failure(self, mock_repository):
    #     mock_repository.client.query.get = MagicMock(side_effect=Exception("Failed to search by keyword"))
    #     with pytest.raises(SearchByKeywordError, match="Failed to search by keyword"):
    #         await mock_repository.search_by_keyword("test_collection", "test", 1)

    # @pytest.mark.asyncio
    # async def test_search_by_vector_similarity_success(self, mock_repository):
    #     mock_repository.client.query.get = MagicMock(
    #         return_value=MagicMock(
    #             with_near_vector=MagicMock(
    #                 return_value=MagicMock(
    #                     with_limit=MagicMock(
    #                         return_value=MagicMock(do=MagicMock(return_value={"data": {"Get": {"test_collection": [{"doc_id": "doc1", "doc_name": "Test Document", "pages": ["Page 1 text"]}]}}}))
    #                     )
    #                 )
    #             )
    #         )
    #     )
    #     results = await mock_repository.search_by_vector_similarity("test_collection", [0.1, 0.2, 0.3], 1)
    #     assert len(results) == 1
    #     assert results[0].doc_id == "doc1"
    #     assert results[0].doc_name == "Test Document"

    # @pytest.mark.asyncio
    # async def test_search_by_vector_similarity_failure(self, mock_repository):
    #     mock_repository.client.query.get = MagicMock(side_effect=Exception("Failed to search by vector similarity"))
    #     with pytest.raises(SearchByVectorError, match="Failed to search by vector similarity"):
    #         await mock_repository.search_by_vector_similarity("test_collection", [0.1, 0.2, 0.3], 1)


# class TestEmbeddingPipelineService:
#     @pytest.mark.asyncio
#     async def test_load_documents_from_folder_success(self, tmp_path):
#         folder = tmp_path / "documents"
#         folder.mkdir()
#         valid_file = folder / "doc1.json"
#         valid_file.write_text('{"doc_id": "doc1", "doc_name": "Test Doc", "pages": ["Page 1", "Page 2"]}')

#         documents = await EmbeddingPipelineService._load_documents_from_folder(str(folder))
#         assert len(documents) == 1
#         assert documents[0].doc_id == "doc1"
#         assert documents[0].doc_name == "Test Doc"
#         assert documents[0].pages == ["Page 1", "Page 2"]

#     @pytest.mark.asyncio
#     async def test_load_documents_from_folder_invalid_format(self, tmp_path):
#         folder = tmp_path / "documents"
#         folder.mkdir()
#         invalid_file = folder / "doc1.txt"
#         invalid_file.write_text("Invalid content")

#         with pytest.raises(FileInvalidFormatException, match="File 'doc1.txt' is not a JSON file."):
#             await EmbeddingPipelineService._load_documents_from_folder(str(folder))

#     @pytest.mark.asyncio
#     async def test_load_documents_from_folder_invalid_content(self, tmp_path):
#         folder = tmp_path / "documents"
#         folder.mkdir()
#         invalid_file = folder / "doc1.json"
#         invalid_file.write_text('{"invalid_key": "value"}')

#         with pytest.raises(InvalidDocumentException, match="Invalid document content in 'doc1.json'"):
#             await EmbeddingPipelineService._load_documents_from_folder(str(folder))

#     def test_chunk_text_success(self):
#         page = "This is a test page."
#         chunks = []

#         chunks.extend(
#             EmbeddingPipelineService._chunk_text(
#                 doc_id="doc1",
#                 page_number=1,
#                 page=page,
#                 chunk_size=10,
#                 overlap=5,
#             )
#         )

#         assert len(chunks) == 4
#         assert chunks[0].chunk_text == "This is a "
#         assert chunks[1].chunk_text == "is a test "
#         assert chunks[2].chunk_text == "test page."

#     def test_chunk_text_invalid_chunk_size(self):
#         with pytest.raises(ValueError, match="Chunk size must be greater than overlap."):
#             EmbeddingPipelineService._chunk_text(
#                 doc_id="doc1",
#                 page_number=1,
#                 page="This is a test page.",
#                 chunk_size=5,
#                 overlap=10,
#             )

#     @pytest.mark.asyncio
#     async def test_embed_chunks_success(self):
#         chunks = [
#             DocumentChunk(
#                 doc_id="doc1",
#                 chunk_id="chunk1",
#                 chunk_text="This is a test chunk.",
#                 page_number=1,
#                 begin_offset=0,
#                 end_offset=20,
#             )
#         ]
#         mock_embedding_model = MagicMock(spec=EmbeddingModel)
#         mock_embedding_model.generate_texts_embeddings = AsyncMock(return_value=[[0.1, 0.2, 0.3]])

#         await EmbeddingPipelineService._embed_chunks(chunks, mock_embedding_model)
#         assert chunks[0].embedding == [0.1, 0.2, 0.3]

#     @pytest.mark.asyncio
#     async def test_process_document_success(self):
#         document = Document(
#             doc_id="doc1",
#             doc_name="Test Document",
#             pages=["This is page 1.", "This is page 2."],
#         )
#         mock_embedding_model = MagicMock(spec=EmbeddingModel)
#         mock_embedding_model.generate_texts_embeddings = AsyncMock(return_value=[[0.1, 0.2, 0.3]])

#         chunks = await EmbeddingPipelineService._process_document(document, mock_embedding_model, chunk_size=10, overlap=5)

#         assert len(chunks) == 6
#         assert chunks[0].chunk_text == "This is pa"
#         assert chunks[0].embedding == [0.1, 0.2, 0.3]

#     @pytest.mark.asyncio
#     async def test_apply_success(self, tmp_path):
#         folder = tmp_path / "documents"
#         folder.mkdir()
#         valid_file = folder / "doc1.json"
#         valid_file.write_text('{"doc_id": "doc1", "doc_name": "Test Doc", "pages": ["Page 1", "Page 2"]}')

#         mock_embedding_model = MagicMock(spec=EmbeddingModel)
#         mock_embedding_model.generate_texts_embeddings = AsyncMock(return_value=[[0.1, 0.2, 0.3]])

#         mock_repository = MagicMock(spec=CollectionRepository)
#         mock_repository.insert_document_chunks = AsyncMock()

#         documents = await EmbeddingPipelineService.apply(documents_folder=str(folder), document_repository_name="test_repository", embedding_model=mock_embedding_model, chunk_size=10, overlap=5)
#         assert len(documents) == 2
#         assert documents[0].doc_id == "doc1"
