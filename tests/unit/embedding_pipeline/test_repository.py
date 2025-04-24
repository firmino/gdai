import pytest
import pytest_asyncio
from src.embedding_pipeline.schema import Document, DocumentChunk
from src.embedding_pipeline.repository import DocumentRepository


class TestDocumentRepository:
    TENTANT_ID_TEST = "ABC123"

    @pytest_asyncio.fixture(scope="module")
    async def repository(self):
        repo = await DocumentRepository.create()
        yield repo
        await repo.clean_tenant_database(tentant_id=self.TENTANT_ID_TEST)
        await repo.close_connection_pool()

    @pytest_asyncio.fixture(scope="module")
    async def document(self):
        document = Document(
            doc_id="doc1",
            tenant_id=self.TENTANT_ID_TEST,
            doc_name="Test Document",
            pages=["Page 1", "Page 2"],
            embedding_model_name="test_model",
        )
        return document

    @pytest_asyncio.fixture(scope="module")
    async def chunks(self):
        chunks = [
            DocumentChunk(
                chunk_id="chunk1",
                tenant_id=self.TENTANT_ID_TEST,
                chunk_text="This is a test chunk.",
                page_number=1,
                begin_offset=0,
                end_offset=20,
                embedding=[0.1] * 1536,
                doc_id="doc1",
            ),
            DocumentChunk(
                chunk_id="chunk2",
                tenant_id=self.TENTANT_ID_TEST,
                chunk_text="Another test chunk.",
                page_number=2,
                begin_offset=0,
                end_offset=25,
                embedding=[0.4] * 1536,
                doc_id="doc1",
            ),
        ]
        return chunks

    @pytest.mark.asyncio(loop_scope="module")
    async def test_insert_and_get_document(self, repository, document, chunks):
        # Inserts the document and its chunks
        await repository.insert_document(document, chunks)

        doc = await repository.get_document_by_id(document.doc_id)
        assert doc is not None
        assert doc.doc_id == document.doc_id
        assert doc.doc_name == document.doc_name
        assert len(doc.pages) == len(document.pages)
        assert doc.embedding_model_name == document.embedding_model_name

        chunk1 = await repository.get_document_chunk_by_id(chunks[0].chunk_id)
        assert chunk1 is not None
        assert chunk1.chunk_text == chunks[0].chunk_text
        assert chunk1.page_number == chunks[0].page_number
        assert chunk1.begin_offset == chunks[0].begin_offset
        assert chunk1.end_offset == chunks[0].end_offset
        assert len(chunk1.embedding) == len(chunks[0].embedding)
        assert chunk1.doc_id == chunks[0].doc_id

        chunk2 = await repository.get_document_chunk_by_id(chunks[1].chunk_id)
        assert chunk2 is not None
        assert chunk2.chunk_text == chunks[1].chunk_text
        assert chunk2.page_number == chunks[1].page_number
        assert chunk2.begin_offset == chunks[1].begin_offset
        assert chunk2.end_offset == chunks[1].end_offset
        assert len(chunk2.embedding) == len(chunks[1].embedding)
        assert chunk2.doc_id == chunks[1].doc_id

    @pytest.mark.asyncio(loop_scope="module")
    async def test_get_document_by_id_not_found(self, repository):
        # Attempts to retrieve a document that does not exist
        document = await repository.get_document_by_id("nonexistent_id")
        assert document is None

    @pytest.mark.asyncio(loop_scope="module")
    async def test_get_document_chunk_by_id_not_found(self, repository):
        # Attempts to retrieve a chunk that does not exist
        chunk = await repository.get_document_chunk_by_id("nonexistent_id")
        assert chunk is None

    @pytest.mark.asyncio(loop_scope="module")
    async def test_clean_tenant_database(self, repository, document, chunks):
        # Inserts the document and its chunks
        await repository.insert_document(document, chunks)
        original_tenant_id = document.tenant_id
        original_doc_id = document.doc_id
        original_chunk_ids = [chunk.chunk_id for chunk in chunks]

        # Modify tenant_id and doc_id to simulate inserting another document
        document.tenant_id = "another_tenant"
        document.doc_id = "doc2"

        chunks[0].tenant_id = "another_tenant"
        chunks[0].doc_id = "doc2"
        chunks[0].chunk_id = "chunk3"

        chunks[1].tenant_id = "another_tenant"
        chunks[1].doc_id = "doc2"
        chunks[1].chunk_id = "chunk4"
        await repository.insert_document(document, chunks)

        # Cleans the database for the specified tenant
        await repository.clean_tenant_database("another_tenant")

        # Verifies that the document and chunks were removed
        document = await repository.get_document_by_id("doc2")
        assert document is None
        chunk1 = await repository.get_document_chunk_by_id(chunks[0].chunk_id)
        assert chunk1 is None
        chunk2 = await repository.get_document_chunk_by_id(chunks[1].chunk_id)
        assert chunk2 is None

        # Verifies that the other document remains in the database
        document = await repository.get_document_by_id(original_doc_id)
        assert document is not None
        assert document.tenant_id == original_tenant_id

        chunk1 = await repository.get_document_chunk_by_id(original_chunk_ids[0])
        assert chunk1 is not None

        chunk2 = await repository.get_document_chunk_by_id(original_chunk_ids[1])
        assert chunk2 is not None

    @pytest.mark.asyncio(loop_scope="module")
    async def test_clean_tenant_database_not_found(self, repository, document, chunks):
        await repository.insert_document(document, chunks)
        # Attempts to clean a tenant that does not exist
        await repository.clean_tenant_database("nonexistent_tenant")
        # Verifies that the database was not affected
        document = await repository.get_document_by_id("doc1")
        assert document is not None
        chunk1 = await repository.get_document_chunk_by_id("chunk1")
        assert chunk1 is not None
        chunk2 = await repository.get_document_chunk_by_id("chunk2")
        assert chunk2 is not None

    @pytest.mark.asyncio(loop_scope="module")
    async def test_delete_document_by_id(self, repository, document, chunks):
        # Inserts the document and its chunks
        await repository.insert_document(document, chunks)
        await repository.delete_document(document.doc_id)
        doc = await repository.get_document_by_id(document.doc_id)
        assert doc is None