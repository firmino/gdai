"""
Unit tests for the schema module used in the embedding pipeline.
"""
import pytest
from src.embedding_pipeline.schema import Document, TextChunk
from src.embedding_pipeline.embedding import CohereEmbeddingModel
from src.embedding_pipeline.pipeline import EmbeddingPipeline
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
    chunk = TextChunk(
        chunk_id=chunk_id,
        chunk_text=text,
        page_number=page_number,
        begin_offset=begin_offset,
        end_offset=end_offset,
    )
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

    chunk = TextChunk(
        chunk_id=chunk_id,
        chunk_text=text,
        page_number=page_number,
        begin_offset=begin_offset,
        end_offset=end_offset,
    )

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

    chunk = TextChunk(
        chunk_id=chunk_id,
        chunk_text=text,
        page_number=page_number,
        begin_offset=begin_offset,
        end_offset=end_offset,
    )

    chunk_str = str(chunk)

    assert f"chunk_id={chunk_id}" in chunk_str
    assert f"page_number={page_number}" in chunk_str
    assert f"offsets=({begin_offset}, {end_offset})" in chunk_str

@pytest.mark.asyncio
async def test_embedding_creation():
    """
    Test the EmbeddingModel class to ensure it correctly embeds text.
    """
    embedding_model = CohereEmbeddingModel()
    text = "This is a test text."
    embedding = await embedding_model.embed_text(text)
    assert len(embedding) > 0

@pytest.mark.asyncio
async def test_embedding_similarity():
    """
    Test the similarity calculation between two embeddings.
    """
    embedding_model = CohereEmbeddingModel()
    text1 = "This is a test text."
    text2 = "This is another test text."
    embedding = await embedding_model.embed_texts([text1, text2])
    similarity = 1.0 - spatial.distance.cosine(embedding[0], embedding[1])
    assert 0 <= similarity <= 1


def test_pipeline_chunck_process():
    doc_id = "abc"
    page_number = 1
    page = "A role-playing game (sometimes spelled roleplaying game,[1][2] or abbreviated as RPG) is a game in which players assume the roles of characters in a fictional setting. Players take responsibility for acting out these roles within a narrative, either through literal acting or through a process of structured decision-making regarding character development.[3] Actions taken within many games succeed or fail according to a formal system of rules and guidelines.[4]"
    chunk_size = 10
    overlap = 0
    chunks = EmbeddingPipeline._chunk_text(
        doc_id, page_number, page, chunk_size, overlap
    )
    assert len(chunks) == 47
    assert len(chunks[0].chunk_text) == 10


@pytest.mark.asyncio
async def test_pipeline_execution_document():
    """
    Test the entire embedding pipeline to ensure it correctly processes a document.
    """
    doc_id = "doc1"
    doc_name = "Test Document"
    pages = [
        "A role-playing game (sometimes spelled roleplaying game,[1][2] or abbreviated as RPG) is a game in which players assume the roles of characters in a fictional setting. Players take responsibility for acting out these roles within a narrative, either through literal acting or through a process of structured decision-making regarding character development.[3] Actions taken within many games succeed or fail according to a formal system of rules and guidelines.[4]",
        "There are several forms of role-playing games. The original form, sometimes called the tabletop role-playing game (TRPG or TTRPG), is conducted through discussion, whereas in live action role-playing (LARP), players physically perform their characters' actions.[5] Both forms feature collaborative storytelling. In both TTRPGs and LARPs, often an arranger called a game master (GM) decides on the game system and setting to be used, while acting as a facilitator or referee. Each of the other players takes on the role of a single character in the fiction.[6]",
    ]
    doc = Document(doc_id=doc_id, doc_name=doc_name, pages=pages)
    
    embedding_model = CohereEmbeddingModel()  
    chunk_size = 10
    overlap = 0
    doc = await EmbeddingPipeline.process_document(doc, embedding_model, chunk_size, overlap)
    assert len(doc.chunks)  == 103 # test the number of chunks is right
    assert len(doc.chunks[0].embedding) > 0 



@pytest.mark.asyncio
async def test_pipeline_execution_multiple_documents():
    """
    Test the entire embedding pipeline to ensure it correctly processes a document.
    """
    doc_id1 = "doc1"
    doc_name1 = "Test Document"
    pages1 = [
        "A role-playing game (sometimes spelled roleplaying game,[1][2] or abbreviated as RPG) is a game in which players assume the roles of characters in a fictional setting. Players take responsibility for acting out these roles within a narrative, either through literal acting or through a process of structured decision-making regarding character development.[3] Actions taken within many games succeed or fail according to a formal system of rules and guidelines.[4]",
        "There are several forms of role-playing games. The original form, sometimes called the tabletop role-playing game (TRPG or TTRPG), is conducted through discussion, whereas in live action role-playing (LARP), players physically perform their characters' actions.[5] Both forms feature collaborative storytelling. In both TTRPGs and LARPs, often an arranger called a game master (GM) decides on the game system and setting to be used, while acting as a facilitator or referee. Each of the other players takes on the role of a single character in the fiction.[6]",
    ]
    doc1 = Document(doc_id=doc_id1, doc_name=doc_name1, pages=pages1)
    
    doc_id2 = "doc2"
    doc_name2 = "Test Document 2"
    pages2 = [
        "A role-playing game (sometimes spelled roleplaying game,[1][2] or abbreviated as RPG) is a game in which players assume the roles of characters in a fictional setting. Players take responsibility for acting out these roles within a narrative, either through literal acting or through a process of structured decision-making regarding character development.[3] Actions taken within many games succeed or fail according to a formal system of rules and guidelines.[4]",
        "There are several forms of role-playing games. The original form, sometimes called the tabletop role-playing game (TRPG or TTRPG), is conducted through discussion, whereas in live action role-playing (LARP), players physically perform their characters' actions.[5] Both forms feature collaborative storytelling. In both TTRPGs and LARPs, often an arranger called a game master (GM) decides on the game system and setting to be used, while acting as a facilitator or referee. Each of the other players takes on the role of a single character in the fiction.[6]",
    ]
    doc2 = Document(doc_id=doc_id2, doc_name=doc_name2, pages=pages2)
    
    docs = [doc1, doc2] 
    embedding_model = CohereEmbeddingModel()
    chunk_size = 10
    overlap = 0
    docs = await EmbeddingPipeline.apply(docs, embedding_model, chunk_size, overlap)
    assert len(docs) == 2   
    assert len(docs[0].chunks)  == 103 # test the number of chunks is right
