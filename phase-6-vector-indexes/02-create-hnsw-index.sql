
-- Create an HNSW index for cosine-distance searches.
-- This index helps pgvector find nearby vectors efficiently.

CREATE INDEX semantic_documents_embedding_hnsw_idx
ON semantic_documents
USING hnsw (embedding vector_cosine_ops);