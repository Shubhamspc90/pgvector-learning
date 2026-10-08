# Phase 3 — pgvector

This phase focuses on using pgvector inside PostgreSQL for storing and comparing vectors.

## Topics Covered

1. pgvector Extension
2. `vector(n)` Data Type
3. Euclidean Distance
4. Cosine Distance
5. Inner Product
6. Nearest Neighbor Search

## Learning Objective

The goal of this phase is to understand how pgvector extends PostgreSQL with vector capabilities and how vectors can be stored, compared, and searched.

## What is pgvector?

pgvector is a PostgreSQL extension that adds support for vector data types and vector similarity search.

Basic architecture:

PostgreSQL
↓
pgvector Extension
↓
Vector Storage + Vector Operations + Vector Search

## 1. pgvector Extension

The extension is enabled inside a PostgreSQL database using:

```sql
CREATE EXTENSION IF NOT EXISTS vector;
```

The extension can be verified using:

```sql
SELECT *
FROM pg_extension
WHERE extname = 'vector';
```

## 2. `vector(n)` Data Type

`vector(n)` represents a vector with exactly `n` dimensions.

Example:

```sql
embedding vector(3)
```

Valid:

```text
[0.1, 0.2, 0.3]
```

Invalid:

```text
[0.1, 0.2, 0.3, 0.4]
```

because the column expects exactly 3 dimensions.

## 3. Distance and Similarity Operators

pgvector provides operators for comparing vectors.

| Operator | Operation              |
| -------- | ---------------------- |
| `<->`    | Euclidean distance     |
| `<=>`    | Cosine distance        |
| `<#>`    | Negative inner product |

For distance-based searches, a smaller distance generally means the vectors are closer.

## 4. Nearest Neighbor Search

A basic nearest-neighbor query can be performed by ordering vectors by distance:

```sql
SELECT
    name,
    embedding,
    embedding <-> '[0.2, 0.2, 0.3]'::vector AS distance
FROM vector_examples
ORDER BY embedding <-> '[0.2, 0.2, 0.3]'::vector
LIMIT 2;
```

The basic workflow is:

Query Vector
↓
Compare with Stored Vectors
↓
Calculate Distance
↓
ORDER BY Distance
↓
LIMIT K
↓
Top-K Nearest Vectors

## Phase 3 Result

After completing this phase, we understand how pgvector is enabled in PostgreSQL, how vectors are stored using `vector(n)`, how vector comparison operators work, and how basic nearest-neighbor searches are performed.
