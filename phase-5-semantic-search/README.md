# Phase 5 — Semantic Search

## Overview

Phase 5 focuses on building a practical **semantic search system** using PostgreSQL, pgvector, and Sentence Transformers.

Instead of searching for exact keywords, semantic search finds documents based on their **meaning**.

The workflow is:

```text
Documents
    ↓
Generate Embeddings
    ↓
Store Embeddings in PostgreSQL
    ↓
User Query
    ↓
Generate Query Embedding
    ↓
Compare Vectors
    ↓
Cosine Distance
    ↓
Top-K Results
    ↓
Similarity Filtering
```

---

## Topics Covered

* Semantic Search
* Document Embeddings
* Query Embeddings
* PostgreSQL + pgvector
* Cosine Distance
* Similarity Score
* Top-K Search
* Similarity Threshold
* Duplicate Prevention
* Python + PostgreSQL Integration

---

## Learning Objective

By the end of this phase, we will be able to:

* Generate embeddings for documents
* Store embeddings in PostgreSQL using pgvector
* Convert a user query into an embedding
* Perform semantic similarity search
* Retrieve the most relevant documents
* Calculate similarity scores
* Filter results using a similarity threshold

---

# 1. Semantic Search

Traditional keyword search looks for matching words.

For example:

```text
Query:
"I enjoy coding"
```

A keyword search may not consider:

```text
"I love programming"
```

as a match because the words are different.

Semantic search understands that both sentences have a similar meaning.

```text
"I enjoy coding"
        ↓
   Similar Meaning
        ↓
"I love programming"
```

---

# 2. Documents and Embeddings

Documents are converted into numerical vectors using the Sentence Transformer model:

```text
all-MiniLM-L6-v2
```

This model generates:

```text
384-dimensional embeddings
```

Example:

```text
"I love programming"
        ↓
Sentence Transformer
        ↓
384-dimensional vector
```

These vectors are stored in PostgreSQL using pgvector.

---

# 3. PostgreSQL Table

File:

```text
01-semantic-documents-table.sql
```

Table:

```sql
CREATE TABLE semantic_documents (
    id SERIAL PRIMARY KEY,
    content TEXT NOT NULL,
    embedding vector(384) NOT NULL
);
```

The table contains:

| Column      | Description            |
| ----------- | ---------------------- |
| `id`        | Unique document ID     |
| `content`   | Original document text |
| `embedding` | 384-dimensional vector |

---

# 4. Preventing Duplicate Documents

File:

```text
02-unique-content.sql
```

A unique constraint is added to the document content:

```sql
ALTER TABLE semantic_documents
ADD CONSTRAINT unique_semantic_document_content
UNIQUE (content);
```

The Python loader also uses:

```sql
ON CONFLICT (content) DO NOTHING
```

Therefore, running the document loader multiple times does not create duplicate records.

---

# 5. Loading Documents

File:

```text
load_documents.py
```

The script:

1. Loads the Sentence Transformer model
2. Takes a list of documents
3. Generates embeddings
4. Connects to PostgreSQL
5. Stores documents and embeddings
6. Prevents duplicate insertion

Run:

```bash
python phase-5-semantic-search/load_documents.py
```

Example output:

```text
Successfully inserted 10 new documents.
```

If the documents already exist:

```text
Successfully inserted 0 new documents.
```

---

# 6. Semantic Search

File:

```text
search.py
```

The search process is:

```text
User Query
    ↓
Query Embedding
    ↓
Compare with Stored Embeddings
    ↓
Cosine Distance
    ↓
Order by Distance
    ↓
Top-K Results
```

Run:

```bash
python phase-5-semantic-search/search.py
```

The program asks for:

```text
Enter your search query:
Enter number of results:
Enter minimum similarity:
```

---

# 7. Cosine Distance

pgvector provides cosine distance using:

```sql
embedding <=> query_embedding
```

The search results are ordered by the smallest distance.

```sql
ORDER BY embedding <=> query_embedding
LIMIT top_k;
```

The important relationship is:

```text
Smaller Distance
       ↓
Higher Similarity
       ↓
More Relevant Result
```

---

# 8. Similarity Score

For this phase, similarity is calculated as:

```text
Similarity = 1 - Cosine Distance
```

For example:

```text
Distance = 0.20

Similarity = 1 - 0.20
           = 0.80
```

Therefore:

```text
Higher similarity = More semantically related
```

---

# 9. Top-K Search

Top-K defines how many results should be returned.

For example:

```text
Top-K = 5
```

means that the five most relevant documents are retrieved.

Example:

```text
Query:
"artificial intelligence"

Top 3 results:

1. Machine learning is a branch of artificial intelligence
2. Deep learning uses neural networks
3. Software development requires problem solving
```

---

# 10. Similarity Threshold

A similarity threshold allows us to remove weak results.

For example:

```text
Minimum Similarity = 0.40
```

Only results satisfying:

```text
Similarity >= 0.40
```

are displayed.

Example:

```text
Document                                      Similarity

Machine learning is a branch of AI              0.6084
Deep learning uses neural networks              0.4103
Software development requires problem solving   0.3303
```

With a threshold of `0.40`, the third result is removed.

---

# 11. Example Semantic Search

Query:

```text
artificial intelligence
```

Top-K:

```text
5
```

Similarity threshold:

```text
0.40
```

Example results:

```text
1. Machine learning is a branch of artificial intelligence
   Distance: 0.3916
   Similarity: 0.6084

2. Deep learning uses neural networks
   Distance: 0.5897
   Similarity: 0.4103
```

This demonstrates that the system can find semantically related documents even when the exact query is not stored.

---

# 12. Project Structure

```text
phase-5-semantic-search/
│
├── README.md
├── 01-semantic-documents-table.sql
├── 02-unique-content.sql
├── load_documents.py
└── search.py
```

---

# 13. Database Configuration

The project uses PostgreSQL on port `5433`.

`.env`:

```env
POSTGRES_HOST=localhost
POSTGRES_PORT=5433
POSTGRES_DB=pgvector_learning
POSTGRES_USER=postgres
POSTGRES_PASSWORD=your_password_here
```

The `.env` file contains local credentials and should not be committed to Git.

---

# 14. Key Learnings

In this phase, we learned:

* Semantic search is based on meaning rather than exact keywords.
* Documents can be converted into embeddings using Sentence Transformers.
* Query text must also be converted into an embedding.
* pgvector can compare document and query vectors.
* Cosine distance can be used for semantic search.
* Smaller cosine distance means greater similarity.
* Top-K controls the number of returned results.
* Similarity thresholds help remove weak results.
* PostgreSQL can store both text and vector embeddings.
* Python can connect the embedding model with PostgreSQL and pgvector.

---

## Phase Result

At the end of Phase 5, we have a working semantic search system:

```text
User Query
     ↓
Sentence Transformer
     ↓
Query Embedding
     ↓
PostgreSQL + pgvector
     ↓
Cosine Similarity Search
     ↓
Top-K Results
     ↓
Similarity Threshold
     ↓
Relevant Documents
```

---

## Next Phase

### Phase 6 — Vector Indexes

In the next phase, we will learn:

* Why vector indexes are needed
* HNSW
* IVFFlat
* Creating vector indexes
* Faster similarity search
* Index performance
* Comparing indexed and non-indexed searches
