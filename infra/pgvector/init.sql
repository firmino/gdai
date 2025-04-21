-- Ativa a extensão PGvector (caso não esteja ativada)
CREATE EXTENSION IF NOT EXISTS vector;

-- Tabela principal de documentos
CREATE TABLE documents (
    id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    pages TEXT[] NOT NULL,  -- Array de strings para as páginas
    embedding_model_name TEXT NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Tabela de chunks dos documentos com vetores
CREATE TABLE document_chunks (
    id TEXT PRIMARY KEY,
    chunk_text TEXT NOT NULL CHECK (chunk_text <> ''),  -- Equivalente ao min_length=1
    page_number INTEGER NOT NULL CHECK (page_number >= 0),
    begin_offset INTEGER NOT NULL CHECK (begin_offset >= 0),
    end_offset INTEGER NOT NULL CHECK (end_offset >= 0),
    embedding VECTOR(1536),  -- Ajuste a dimensão conforme seu modelo
    fk_doc_id TEXT NOT NULL REFERENCES documents(id) ON DELETE CASCADE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Índice para buscas vetoriais (ajuste lists conforme seu dataset)
CREATE INDEX idx_document_chunks_hnsw ON document_chunks 
USING hnsw (embedding vector_cosine_ops)
WITH (
    m = 16,               -- Número máximo de conexões por nó (16-48)
    ef_construction = 64   -- Precisão durante construção (40-200)
);

-- Índice para melhor performance nas relações
CREATE INDEX idx_document_chunks_fk_doc_id ON document_chunks(fk_doc_id);