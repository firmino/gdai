import pytest 
import pytest_asyncio
from unittest.mock import AsyncMock

from src.embedding_pipeline.service import EmbeddingPipelineService
from src.embedding_pipeline.schema import Document, DocumentInput
from src.embedding_pipeline.embedding import EmbeddingModel
from src.embedding_pipeline.repository import DocumentRepository    




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
        await repo

    


    

# class TestEmbeddingPipelineService:

#     @pytest_asyncio.fixture(loop_scope="module")
#     async def mock_embedding_model(self):
#         """
#         Mock do modelo de embedding para gerar embeddings fictícios.
#         """
#         mock_model = AsyncMock(spec=EmbeddingModel)
#         mock_model.generate_texts_embeddings = AsyncMock(
#             return_value=[[0.9] * 1536 for _ in range(10)]  # Mock de embeddings
#         )
#         return mock_model

#     @pytest_asyncio.fixture(loop_scope="module") 
#     async def repository(self):  
#         repo = await DocumentRepository.create()
#         yield repo
#         await repo.clean_database()
#         await repo.close_connection_pool()

#     @pytest.mark.asyncio(loop_scope="module")
#     async def test_apply(self, tmp_path, mock_embedding_model, repository):
#         """
#         Testa o método apply do EmbeddingPipelineService.
#         """
#         # Cria um documento de teste no diretório temporário
#         document_data = {
#             "doc_id": "doc1",
#             "doc_name": "Test Document",
#             "pages": ["Page 1 content", "Page 2 content"],
#         }
#         document_path = tmp_path / "doc1.json"
#         document_path.write_text(json.dumps(document_data))

#         # Executa o pipeline
#         documents_folder = str(tmp_path)
#         processed_documents = await EmbeddingPipelineService.apply(
#             documents_folder=documents_folder,
#             embedding_model=mock_embedding_model,
#             chunk_size=10,
#             overlap=5,
#         )

#         # Verifica se o documento foi processado corretamente
#         assert len(processed_documents) == 1
#         assert processed_documents[0].doc_id == "doc1"
#         assert processed_documents[0].doc_name == "Test Document"
        
#         # get document
#         doc = await repository.get_document_metadata(processed_documents[0].doc_id)
#         assert doc is not None
#         assert doc["id"] == "doc1"


#         # search document by similarity
#         query_embedding = [0.9] * 1536
#         results = await repository.search_documents_by_similarity(embedded_query=query_embedding, limit=2)
#         assert len(results) >= 1
#         assert results[0]["fk_doc_id"] == "doc1"  # Chunk mais similar deve ser o primeiro
        
        