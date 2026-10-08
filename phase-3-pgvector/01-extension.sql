-- ==========================================
-- Phase 3.1 — pgvector Extension
-- ==========================================

-- Enable pgvector in the current database.
CREATE EXTENSION IF NOT EXISTS vector;

-- Verify the installed pgvector extension.
SELECT *
FROM pg_extension
WHERE extname = 'vector';

-- Check whether pgvector is available.
SELECT *
FROM pg_available_extensions
WHERE name = 'vector';