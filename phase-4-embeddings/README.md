# Phase 4 — Embeddings

This phase focuses on understanding **text embeddings** and learning how to generate, compare, and store embeddings using **Sentence Transformers, PostgreSQL, and pgvector**.

## Objectives

In this phase, we learn how to:

* Understand text embeddings
* Generate embeddings using Sentence Transformers
* Use the `all-MiniLM-L6-v2` embedding model
* Understand embedding dimensions
* Generate 384-dimensional vectors
* Compare semantic similarity between sentences
* Store embeddings in PostgreSQL using pgvector
* Connect Python applications with PostgreSQL
* Use environment variables for database configuration

---

## 1. What are Embeddings?

An embedding is a numerical representation of data, such as text.

A sentence is converted into a vector containing many numerical values.

For example:

```text
"I love programming"
        ↓
Embedding Model
        ↓
[0.021, -0.034, 0.056, ...]
        ↓
384-dimensional vector
```

The numbers in the vector represent the semantic characteristics of the text.

Similar meanings generally produce vectors that are closer together in vector space.

---

## 2. Sentence Transformers

**Sentence Transformers** is a Python library used to generate meaningful vector representations of sentences and text.

Installation:

```bash
pip install sentence-transformers
```

In this phase, we use:

```text
all-MiniLM-L6-v2
```

---

## 3. all-MiniLM-L6-v2

The `all-MiniLM-L6-v2` model converts text into a fixed-size vector representation.

For this project, the model produces:

```text
384 dimensions
```

Example:

```python
from sentence_transformers import SentenceTransformer

model = SentenceTransformer("all-MiniLM-L6-v2")

text = "I love programming"

embedding = model.encode(text)

print(len(embedding))
```

Output:

```text
384
```

---

## 4. Multiple Text Embeddings

The model can also generate embeddings for multiple sentences.

Example:

```python
sentences = [
    "I love programming",
    "I enjoy coding",
    "The weather is very hot today"
]

embeddings = model.encode(sentences)
```

Each sentence receives its own 384-dimensional vector.

---

## 5. Semantic Similarity

Embeddings allow us to compare the meaning of different sentences.

For example:

```text
"I love programming"
"I enjoy coding"
```

These sentences have similar meanings, so their embeddings are relatively close.

Whereas:

```text
"I love programming"
"The weather is very hot today"
```

have very different meanings, so their embeddings are much less similar.

In our experiment:

```text
"I love programming"
vs
"I enjoy coding"
```

Cosine similarity:

```text
0.8172091
```

And:

```text
"I love programming"
vs
"The weather is very hot today"
```

Cosine similarity:

```text
0.036443558
```

This demonstrates how embeddings can capture semantic relationships between sentences.

---

## 6. Storing Embeddings with PostgreSQL + pgvector

We created a PostgreSQL table using the pgvector `vector` data type.

```sql
CREATE TABLE embedding_examples (
    id SERIAL PRIMARY KEY,
    text TEXT NOT NULL,
    embedding vector(384)
);
```

The important part is:

```sql
embedding vector(384)
```

This means the column can store vectors containing exactly **384 dimensions**.

Example:

```text
Text:
I love programming

Embedding:
[0.021..., -0.034..., ...]

Dimensions:
384
```

---

## 7. Python → PostgreSQL Workflow

The complete workflow is:

```text
Text
 ↓
Sentence Transformer
 ↓
384-dimensional embedding
 ↓
Python
 ↓
PostgreSQL
 ↓
pgvector
 ↓
vector(384)
```

Python uses `psycopg` to connect to PostgreSQL.

Database configuration is loaded using environment variables from `.env`.

The `.env` file is intentionally excluded from Git to prevent database credentials from being committed.

---

## 8. Project Files

```text
phase-4-embeddings/
│
├── README.md
├── embedding_demo.py
├── generate_embeddings.py
└── store_embeddings.py
```

### `embedding_demo.py`

Basic experimentation with embeddings.

It demonstrates:

* Generating an embedding for one sentence
* Generating embeddings for multiple sentences
* Checking embedding dimensions

### `generate_embeddings.py`

Demonstrates:

* Generating embeddings
* Comparing sentence embeddings
* Calculating semantic similarity

### `store_embeddings.py`

Demonstrates:

* Loading database configuration from `.env`
* Generating a text embedding
* Connecting Python to PostgreSQL
* Storing the embedding in a `vector(384)` column

---

## 9. Environment Configuration

Database credentials are stored in `.env`.

Example:

```env
POSTGRES_HOST=localhost
POSTGRES_PORT=5433
POSTGRES_DB=pgvector_learning
POSTGRES_USER=postgres
POSTGRES_PASSWORD=your_password_here
```

The `.env` file should **never be committed to Git**.

Instead, `.env.example` is committed as a template.

---

## 10. Running the Examples

Make sure the virtual environment is active:

```powershell
.venv\Scripts\activate
```

Run the basic embedding demo:

```powershell
python phase-4-embeddings/embedding_demo.py
```

Run the embedding generation and similarity example:

```powershell
python phase-4-embeddings/generate_embeddings.py
```

Store an embedding in PostgreSQL:

```powershell
python phase-4-embeddings/store_embeddings.py
```

---

## 11. PostgreSQL Verification

After storing an embedding, verify it using PostgreSQL:

```sql
SELECT
    id,
    text,
    embedding
FROM embedding_examples;
```

To check the number of stored records:

```sql
SELECT COUNT(*)
FROM embedding_examples;
```

---

## 12. Key Learnings

After completing Phase 4, we understand:

* What text embeddings are
* How text is converted into numerical vectors
* How Sentence Transformers generate embeddings
* How `all-MiniLM-L6-v2` produces 384-dimensional vectors
* How semantic similarity can be measured using embeddings
* How Python can generate embeddings
* How embeddings can be stored in PostgreSQL
* How pgvector's `vector(384)` type stores embeddings
* How Python and PostgreSQL work together
* Why environment variables should be used for database credentials

---

## Phase 4 Workflow

```text
Text
  ↓
Embedding Model
  ↓
384-Dimensional Vector
  ↓
Semantic Similarity
  ↓
PostgreSQL
  ↓
pgvector
  ↓
vector(384)
```

Phase 4 establishes the foundation for the next step: **Semantic Search using embeddings and pgvector**.
