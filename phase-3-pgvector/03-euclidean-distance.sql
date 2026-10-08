-- ==========================================
-- Phase 3.3 — Euclidean Distance
-- Operator: <->
-- ==========================================

-- Calculate the Euclidean distance between two vectors.
SELECT
    '[0.1, 0.2, 0.3]'::vector
    <->
    '[0.4, 0.5, 0.6]'::vector
    AS distance;

-- Calculate the distance from a query vector
-- to every stored vector.
SELECT
    name,
    embedding,
    embedding <-> '[0.1, 0.2, 0.3]'::vector AS distance
FROM vector_examples
ORDER BY distance;