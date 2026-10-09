
-- Create an IVFFlat index for cosine-distance searches.
-- lists controls how many clusters the vectors are divided into.

CREATE INDEX semantic_documents_embedding_ivfflat_idx
ON semantic_documents
USING ivfflat (embedding vector_cosine_ops)
WITH (lists = 2);
