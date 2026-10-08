-- ==========================================
-- Phase 3.6 — Nearest Neighbor Search
-- ==========================================

-- Find the nearest vectors to a query vector.
SELECT
    name,
    embedding,
    embedding <-> '[0.2, 0.2, 0.3]'::vector AS distance
FROM vector_examples
ORDER BY embedding <-> '[0.2, 0.2, 0.3]'::vector;

-- Find the top 2 nearest vectors.
SELECT
    name,
    embedding,
    embedding <-> '[0.2, 0.2, 0.3]'::vector AS distance
FROM vector_examples
ORDER BY embedding <-> '[0.2, 0.2, 0.3]'::vector
LIMIT 2;