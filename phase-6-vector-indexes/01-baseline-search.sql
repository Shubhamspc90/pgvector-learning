
-- Inspect the execution plan for semantic search.
-- This query provides a baseline before adding a vector index.
-- Replace the example vector with a real 384-dimensional embedding.

EXPLAIN ANALYZE
SELECT
    id,
    content,
    embedding <=> '[YOUR_384_DIMENSIONAL_VECTOR]'::vector AS distance
FROM semantic_documents
ORDER BY embedding <=> '[YOUR_384_DIMENSIONAL_VECTOR]'::vector
LIMIT 5;