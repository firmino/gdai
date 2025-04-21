"""
Unit tests for the schema, repository, and service modules used in the embedding pipeline.
"""

import pytest
import pytest_asyncio
import json
from unittest.mock import AsyncMock, patch
from src.embedding_pipeline.embedding import EmbeddingModel
from src.embedding_pipeline.schema import Document, DocumentChunk, DocumentInput
from src.embedding_pipeline.repository import DocumentRepository

from src.embedding_pipeline.service import EmbeddingPipelineService
# from src.embedding_pipeline.embedding import EmbeddingModel
from src.embedding_pipeline.exceptions import (
    # FolderNotFoundException,
    FileInvalidFormatException,
    InvalidDocumentException,
)


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


class TestDocumentRepository:

    @pytest_asyncio.fixture(scope="module") 
    async def repository(self):  
        repo = await DocumentRepository.create()
        yield repo
        await repo.clean_database()
        await repo.close_connection_pool()
    

    @pytest.mark.asyncio(loop_scope="module")
    async def test_insert_and_get_document(self, repository):
        # Criação de um documento e seus chunks
        document = Document(
            doc_id="doc1",
            doc_name="Test Document",
            pages=["Page 1", "Page 2"],
            embedding_model_name="test_model",
        )
        chunks = [
            DocumentChunk(
                chunk_id="chunk1",
                chunk_text="This is a test chunk.",
                page_number=1,
                begin_offset=0,
                end_offset=20,
                embedding=[0.1] * 1536,
                doc_id="doc1",
            ),
            DocumentChunk(
                chunk_id="chunk2",
                chunk_text="Another test chunk.",
                page_number=2,
                begin_offset=0,
                end_offset=25,
                embedding=[0.4] * 1536,
                doc_id="doc1",
            ),
        ]

        # Limpa os dados existentes para evitar conflitos
        await repository.delete_document_content(document_id=document.doc_id)

        # Insere o documento e seus chunks
        await repository.insert_document(document, chunks)

        # Recupera os metadados do documento
        docs = await repository.get_document_metadata(document_id=document.doc_id)

        # Verifica se os dados estão corretos
        assert docs["id"] == document.doc_id
        assert docs["name"] == document.doc_name
        assert len(docs["pages"]) == len(document.pages)
        assert docs["embedding_model_name"] == document.embedding_model_name

    @pytest.mark.asyncio(loop_scope="module")
    async def test_search_document_by_keyword(self, repository):
        # Criação de um documento e seus chunks
        document = Document(
            doc_id="doc11",
            doc_name="Test Document",
            pages=["Page 1", "Page 2"],
            embedding_model_name="test_model",
        )
        chunks = [
            DocumentChunk(
                chunk_id="chunk11",
                chunk_text="This is a test chunk.",
                page_number=1,
                begin_offset=0,
                end_offset=20,
                embedding=[0.1] * 1536,
                doc_id="doc11",
            ),
            DocumentChunk(
                chunk_id="chunk21",
                chunk_text="Another test chunk with keyword.",
                page_number=2,
                begin_offset=0,
                end_offset=25,
                embedding=[0.4] * 1536,
                doc_id="doc11",
            ),
        ]

        # Insere o documento e seus chunks
        await repository.insert_document(document, chunks)

        # Pesquisa o documento usando uma palavra-chave
        results = await repository.search_documents_by_keyword(search_keyword="keyword")
      
        # Verifica os resultados da pesquisa
        assert len(results) == 1
        assert results[0]["id"] == "chunk21"
        assert "keyword" in results[0]["chunk_text"]

    @pytest.mark.asyncio(loop_scope="module")
    async def test_search_document_by_similarity(self, repository):
        # Criação de um documento e seus chunks com embeddings
        document = Document(
            doc_id="doc13",
            doc_name="Test Document",
            pages=["Page 1", "Page 2"],
            embedding_model_name="test_model",
        )
        chunks = [
            DocumentChunk(
                chunk_id="chunk121",
                chunk_text="This is a test chunk.",
                page_number=1,
                begin_offset=0,
                end_offset=20,
                embedding=[0.7] * 1536,  # Embedding para similaridade
                doc_id="doc13",
            ),
            DocumentChunk(
                chunk_id="chunk221",
                chunk_text="Another test chunk.",
                page_number=2,
                begin_offset=0,
                end_offset=25,
                embedding=[0.4] * 1536,  # Embedding para similaridade
                doc_id="doc13",
            ),
        ]

        # Insere o documento e seus chunks
        await repository.insert_document(document, chunks)
        
        # Consulta de similaridade com um embedding de consulta
        query_embedding = [0.7] * 1536
        results = await repository.search_documents_by_similarity(embedded_query=query_embedding, limit=2)

        # Verifica os resultados da busca por similaridade
        assert len(results) == 2
        assert results[0]["id"] == "chunk121"  # Chunk mais similar deve ser o primeiro
       


class TestEmbeddingPipelineService:

    @pytest_asyncio.fixture(loop_scope="module")
    async def mock_embedding_model(self):
        """
        Mock do modelo de embedding para gerar embeddings fictícios.
        """
        mock_model = AsyncMock(spec=EmbeddingModel)
        mock_model.generate_texts_embeddings = AsyncMock(
            return_value=[[0.9] * 1536 for _ in range(10)]  # Mock de embeddings
        )
        return mock_model

    @pytest_asyncio.fixture(loop_scope="module") 
    async def repository(self):  
        repo = await DocumentRepository.create()
        yield repo
        await repo.clean_database()
        await repo.close_connection_pool()

    @pytest.mark.asyncio(loop_scope="module")
    async def test_apply(self, tmp_path, mock_embedding_model, repository):
        """
        Testa o método apply do EmbeddingPipelineService.
        """
        # Cria um documento de teste no diretório temporário
        document_data = {
            "doc_id": "doc1",
            "doc_name": "Test Document",
            "pages": ["Page 1 content", "Page 2 content"],
        }
        document_path = tmp_path / "doc1.json"
        document_path.write_text(json.dumps(document_data))

        # Executa o pipeline
        documents_folder = str(tmp_path)
        processed_documents = await EmbeddingPipelineService.apply(
            documents_folder=documents_folder,
            embedding_model=mock_embedding_model,
            chunk_size=10,
            overlap=5,
        )

        # Verifica se o documento foi processado corretamente
        assert len(processed_documents) == 1
        assert processed_documents[0].doc_id == "doc1"
        assert processed_documents[0].doc_name == "Test Document"
        
        # get document
        doc = await repository.get_document_metadata(processed_documents[0].doc_id)
        assert doc is not None
        assert doc["id"] == "doc1"


        # search document by similarity
        query_embedding = [0.9] * 1536
        results = await repository.search_documents_by_similarity(embedded_query=query_embedding, limit=2)
        assert len(results) >= 1
        assert results[0]["fk_doc_id"] == "doc1"  # Chunk mais similar deve ser o primeiro
        
        
