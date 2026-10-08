-- ==========================================
-- Phase 3.5 — Inner Product
-- Operator: <#>
-- ==========================================

-- Calculate the negative inner product between two vectors.
SELECT
    '[0.1, 0.2, 0.3]'::vector
    <#>
    '[0.4, 0.5, 0.6]'::vector
    AS negative_inner_product;

-- Calculate negative inner product against stored vectors.
SELECT
    name,
    embedding,
    embedding <#> '[0.1, 0.2, 0.3]'::vector AS negative_inner_product
FROM vector_examples
ORDER BY negative_inner_product;