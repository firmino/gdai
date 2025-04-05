"""
Unit tests for the schema module used in the embedding pipeline.
"""
from src.embedding_pipeline.schema import Document, TextChunk
from src.embedding_pipeline.embedding import JinaEmbeddingModel
from scipy import spatial

def test_document_initialization():
    """
    Test that a Document is correctly initialized with the provided id, name, and pages.
    Also, ensure that chunks is an empty list and embedding_model_name is None.
    """
    pages = ["Page 1 text", "Page 2 text"]
    doc = Document(doc_id="doc1", doc_name="Test Document", pages=pages)

    assert doc.doc_id == "doc1"
    assert doc.doc_id == "doc1"
    assert doc.doc_name == "Test Document"
    assert doc.pages == pages
    assert doc.chunks == []
    assert doc.embedding_model_name is None


def test_document_str():
    """
    Test the __str__ method of Document to ensure it returns a human-readable string.
    """
    pages = ["Content of page 1", "Content of page 2"]
    doc = Document(doc_id="doc2", doc_name="Another Document", pages=pages)

    chunk_id = "chunk-001"
    text = "This is a test chunk."
    page_number = 1
    begin_offset = 1
    end_offset = len(text)
    chunk = TextChunk(chunk_id=chunk_id, chunk_text=text, page_number=page_number, begin_offset=begin_offset, end_offset=end_offset)
    doc.chunks.append(chunk)
    
    doc_str = str(doc)
    assert "doc_id=doc2" in doc_str
    assert "doc_name=Another Document" in doc_str
    assert "pages=2" in doc_str
    assert "chunks=1" in doc_str


def test_textchunk_initialization():
    """
    Test that a TextChunk is correctly initialized with the provided metadata.
    """
    chunk_id = "chunk-001"
    text = "This is a test chunk."
    page_number = 1
    begin_offset = 0
    end_offset = len(text)
    
    chunk = TextChunk(chunk_id=chunk_id, chunk_text=text, page_number=page_number, begin_offset=begin_offset, end_offset=end_offset)
    
    assert chunk.chunk_id == chunk_id
    assert chunk.chunk_text == text
    assert chunk.page_number == page_number
    assert chunk.begin_offset == begin_offset
    assert chunk.end_offset == end_offset
    


def test_textchunk_str():
    """
    Test the __str__ method of TextChunk to ensure it returns a human-readable string.
    """
    chunk_id = "chunk-001"
    text = "This is a test chunk."
    page_number = 1
    begin_offset = 0
    end_offset = len(text)
    
    chunk = TextChunk(chunk_id=chunk_id, chunk_text=text, page_number=page_number, begin_offset=begin_offset, end_offset=end_offset)
    
    chunk_str = str(chunk)
    
    assert f"chunk_id={chunk_id}" in chunk_str
    assert f"page_number={page_number}" in chunk_str
    assert f"offsets=({begin_offset}, {end_offset})" in chunk_str


def test_embedding_creation():
    """
    Test the EmbeddingModel class to ensure it correctly embeds text.
    """
    embedding_model = JinaEmbeddingModel()
    texts = ["This is a test text."]
    embedding = embedding_model.embed_text(texts) 
    assert isinstance(embedding, list)
    assert len(embedding) > 0



def test_embedding_similarity():
    """
    Test the similarity calculation between two embeddings.
    """
    embedding_model = JinaEmbeddingModel()
    text1 = "This is a test text."
    text2 = "This is another test text."
    embedding = embedding_model.embed_text([text1, text2])
    similarity = 1.0 - spatial.distance.cosine(embedding[0], embedding[1])  
    assert 0 <= similarity <= 1 