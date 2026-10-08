# pgvector Learning

A hands-on learning repository for PostgreSQL and pgvector, covering vector databases, embeddings, similarity search, semantic search, HNSW, IVFFlat, and practical vector search workflows.

## 🎯 Objective

The goal of this repository is to learn PostgreSQL and pgvector from the fundamentals to advanced vector-search concepts through practical exercises.

The learning process follows a professional software-development workflow using Git and GitHub.

## 🛠️ Technologies

* PostgreSQL
* pgvector
* pgAdmin 4
* Python
* Sentence Transformers
* Git
* GitHub

## 📚 Learning Roadmap

### Phase 1 — PostgreSQL Fundamentals

* Database
* Tables
* Data Types
* CRUD Operations
* Constraints
* Indexes

### Phase 2 — Understanding Vectors

* What is a Vector?
* Dimensions
* Vector Representation
* Embeddings
* Vector Space
* Similarity vs Distance

### Phase 3 — pgvector

* pgvector Extension
* `vector(n)` Data Type
* Euclidean Distance
* Cosine Distance
* Inner Product
* Nearest-Neighbor Search

### Phase 4 — Embeddings

* Embedding Models
* Sentence Transformers
* Generating Embeddings
* Vector Dimensions
* Storing Embeddings

### Phase 5 — Semantic Search

* Document Storage
* Document Embeddings
* Query Embeddings
* Similarity Search
* Top-K Search Results

### Phase 6 — Vector Indexes

* HNSW
* IVFFlat
* Index Configuration
* Performance Comparison

### Phase 7 — Performance

* Filtering with Vector Search
* Metadata Filtering
* Query Performance
* `EXPLAIN`

### Phase 8 — Advanced pgvector

* Different Distance Metrics
* Half-Precision Vectors
* Sparse Vectors
* Binary Vectors
* Advanced Indexing

### Phase 9 — Practical Exercises

Standalone exercises and mini projects to apply the concepts learned throughout the repository.

## 🗂️ Repository Structure

```text
pgvector-learning/
│
├── README.md
│
├── phase-1-postgresql/
│   ├── 01-database.sql
│   ├── 02-tables.sql
│   ├── 03-crud.sql
│   ├── 04-constraints.sql
│   └── 05-indexes.sql
│
├── phase-2-vectors/
│   ├── README.md
│   └── vector-basics.md
│
├── phase-3-pgvector/
│   ├── 01-extension.sql
│   ├── 02-vector-type.sql
│   ├── 03-euclidean-distance.sql
│   ├── 04-cosine-distance.sql
│   ├── 05-inner-product.sql
│   └── 06-nearest-neighbor.sql
│
├── phase-4-embeddings/
│   ├── requirements.txt
│   ├── generate_embeddings.py
│   └── README.md
│
├── phase-5-semantic-search/
│
├── phase-6-vector-indexes/
│   ├── hnsw.sql
│   └── ivfflat.sql
│
├── phase-7-performance/
│
├── phase-8-advanced-pgvector/
│
└── .gitignore
```

## 🔄 Development Workflow

This repository follows a feature-branch workflow.

```text
main
  │
  ├── feature/phase-1-postgresql
  │
  ├── feature/phase-2-vectors
  │
  ├── feature/phase-3-pgvector
  │
  ├── feature/phase-4-embeddings
  │
  └── ...
```

For each phase:

1. Create a feature branch.
2. Implement the required SQL/code.
3. Test everything locally.
4. Review the changes.
5. Commit with a meaningful commit message.
6. Push the feature branch to GitHub.
7. Create a Pull Request.
8. Review the Pull Request.
9. Merge it into `main`.

## ⚙️ Environment Setup

This repository uses a Python virtual environment to keep project dependencies isolated from the system Python installation.

### Create Virtual Environment

```bash
python -m venv .venv
```

### Activate Virtual Environment

Windows PowerShell:

```powershell
.venv\Scripts\Activate.ps1
```

Windows CMD:

```cmd
.venv\Scripts\activate
```

Git Bash:

```bash
source .venv/Scripts/activate
```

### Install Dependencies

```bash
pip install -r requirements.txt
```

### Environment Variables

Create a local `.env` file based on `.env.example`.

```bash
.env.example
```

contains placeholder configuration and is safe to commit to GitHub.

The actual `.env` file contains local credentials and is intentionally excluded from Git using `.gitignore`.

## 🗄️ Database Environment

PostgreSQL is used as the database system and pgAdmin 4 is used as the database management interface.

SQL files in this repository will contain the commands used during the learning process. These commands will be executed and tested through the PostgreSQL Query Tool in pgAdmin 4.

## 🔒 Security

Never commit passwords, API keys, tokens, or other secrets to GitHub.

Use `.env` for local secrets and `.env.example` for shareable configuration templates.


## 📌 Learning Approach

The repository is built progressively.

Each phase contains the concepts, SQL queries, Python code, and practical exercises required to understand that particular topic.

The focus is on understanding **why** each concept is used rather than simply memorizing commands.
