"""
Unit tests for the embedding pipeline, schema, and embedding modules.
"""

import torch

from src.embedding_pipeline.schema import Document, TextChunk
from src.embedding_pipeline.pipeline import EmbeddingPipeline
from src.embedding_pipeline.embedding import EmbeddingModel, MistralEmbeddingModel


class DummyEmbeddingModel(EmbeddingModel):
    """
    A dummy embedding model that always returns a fixed embedding.
    """

    def __init__(self):
        super().__init__("dummy")

    def embed_text(self, text: str) -> list[float]:
        return [1.0, 2.0, 3.0]


def test_document_str():
    """
    Test __str__ for the Document class.
    """
    doc = Document("doc1", "Test Document", ["Page 1", "Page 2"])
    # Append a dummy chunk manually in order to test chunk count.
    doc.chunks.append(TextChunk("chunk1", "sample", 0, 0, 6))
    s = str(doc)
    assert "doc_id=doc1" in s or "doc1" in s
    assert "doc_name=Test Document" in s or "Test Document" in s
    assert "pages=2" in s
    assert "chunks=1" in s


def test_text_chunk_str():
    """
    Test __str__ for the TextChunk class.
    """
    chunk = TextChunk("c1", "hello", 0, 0, 5)
    s = str(chunk)
    assert "chunk_id=c1" in s or "c1" in s
    assert "page_number=0" in s
    assert "offsets=(0, 5)" in s


def test_chunk_text():
    """
    Test the _chunk_text method of EmbeddingPipeline.
    """
    # Example page text of 10 characters.
    doc_id = "doc1"
    page_number = 0
    page = "0123456789"
    chunk_size = 4
    overlap = 2

    chunks = EmbeddingPipeline._chunk_text(
        doc_id, page_number, page, chunk_size, overlap
    )
    # Expected behavior:
    # Start positions: 0, (0+(4-2)=2), 4, 6. Thus 4 chunks.
    assert len(chunks) == 4
    assert chunks[0].chunk_text == "0123"
    assert chunks[1].chunk_text == "2345"
    assert chunks[2].chunk_text == "4567"
    # The last chunk may include characters beyond length if not trimmed,
    # but our implementation uses slicing so it'll correctly return "6789".
    assert chunks[3].chunk_text == "6789"


def test_embed_chunks():
    """
    Test the _embed_chunks method by ensuring each TextChunk gets the dummy embedding.
    """
    chunks = [
        TextChunk("chunk1", "hello", 0, 0, 5),
        TextChunk("chunk2", "world", 0, 5, 10),
    ]
    dummy = DummyEmbeddingModel()
    EmbeddingPipeline._embed_chunks(chunks, dummy)
    for chunk in chunks:
        assert chunk.embedding == [1.0, 2.0, 3.0]


def test_apply():
    """
    Test the apply method to ensure the document gets processed: pages are chunked and embedded.
    """
    # Create a document with one page.
    text = "abcdefghijklmnopqrstuvwxyz"  # 26 characters.
    doc = Document("doc1", "Alphabet", [text])
    dummy = DummyEmbeddingModel()

    # Use a chunk_size and overlap values for predictable splitting.
    updated_doc = EmbeddingPipeline.apply(doc, dummy, chunk_size=10, overlap=2)
    # Since 26 characters: start indices: 0, (0+8=8), 16 and then 24.
    expected_n_chunks = 4
    assert len(updated_doc.chunks) == expected_n_chunks

    for chunk in updated_doc.chunks:
        assert chunk.embedding == [1.0, 2.0, 3.0]


def test_embedding_model_str():
    """
    Test the __str__ method of the base EmbeddingModel.
    """
    dummy = DummyEmbeddingModel()
    assert str(dummy) == "dummy"


class DummyTokenizer:
    """
    A dummy tokenizer mimicking AutoTokenizer.
    """

    def __call__(self, text, return_tensors, padding, truncation):
        # Return a dummy dictionary that is compatible with the model call.
        return {"input_ids": torch.tensor([[0]])}


class DummyModel:
    """
    A dummy model mimicking AutoModel.
    This model is callable and returns a dummy output with a last_hidden_state property.
    """

    def __call__(self, **kwargs):
        return DummyOutput()


class DummyOutput:
    """
    A dummy output simulating model output.
    """

    @property
    def last_hidden_state(self):
        # Return a dummy tensor that, when averaged, returns [1.0, 2.0, 3.0].
        return torch.tensor([[1.0, 2.0, 3.0]])


def test_mistral_embedding_model(monkeypatch):
    """
    Test MistralEmbeddingModel by monkeypatching AutoTokenizer and AutoModel.
    """
    # Monkeypatch the from_pretrained methods to return dummy classes.
    monkeypatch.setattr(
        "src.embedding_pipeline.embedding.AutoTokenizer.from_pretrained",
        lambda model_name: DummyTokenizer(),
    )
    monkeypatch.setattr(
        "src.embedding_pipeline.embedding.AutoModel.from_pretrained",
        lambda model_name, device_map: DummyModel(),
    )

    mistral = MistralEmbeddingModel()
    # Check that __str__ returns "mistral" as defined.
    assert str(mistral) == "mistral"

    # Test embed_text using the dummy tokenizer and dummy model.
    embedding = mistral.embed_text("test sentence")
    # Our dummy processing returns tensor([[1.0, 2.0, 3.0]]), mean over dim=1 gives [1.0, 2.0, 3.0]
    assert embedding == [1.0, 2.0, 3.0]
