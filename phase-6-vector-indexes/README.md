# Phase 6 — Vector Indexes and Performance

## Objectives

* Understand why vector indexes are useful for semantic search.
* Learn the differences between HNSW and IVFFlat.
* Inspect PostgreSQL query plans using `EXPLAIN (ANALYZE, BUFFERS)`.
* Benchmark exact search and approximate nearest-neighbor search.
* Understand how PostgreSQL chooses between sequential scans and index scans.

## 1. Baseline Vector Search

### Objective

Measure semantic-search performance before using a vector index.

### Query Plan

The baseline query used `EXPLAIN (ANALYZE, BUFFERS)` to inspect PostgreSQL's execution plan.

The plan included:

* `Seq Scan` — scans the table's rows.
* `Sort` — orders documents by cosine distance.
* `Limit` — returns the top 5 results.

### Initial Baseline Results

The original baseline experiment used 10 documents.

| Metric           |    Result |
| ---------------- | --------: |
| Documents        |        10 |
| Results returned |         5 |
| Planning time    | 32.239 ms |
| Execution time   |  0.422 ms |

PostgreSQL used a sequential scan because the table was very small. A sequential scan can be more efficient than using an index for a small dataset.

### Larger Dataset Baseline

A separate benchmark table, `semantic_documents_benchmark`, was created with 5,000 documents and 384-dimensional embeddings.

An exact-search experiment returned the following representative result:

| Metric           |               Result |
| ---------------- | -------------------: |
| Documents        |                5,000 |
| Results returned |                    5 |
| Execution time   | Approximately 5.1 ms |

These timings are specific to the test environment and may vary between runs.

## 2. HNSW Index

HNSW stands for Hierarchical Navigable Small World. It organizes vectors into a graph that helps find nearby vectors efficiently.

### Index Creation

```sql
CREATE INDEX semantic_documents_benchmark_hnsw_idx
ON semantic_documents_benchmark
USING hnsw (embedding vector_cosine_ops);
```

### Important Parameters

* `m` — controls graph connectivity.
* `ef_construction` — controls the search effort during index construction.
* `hnsw.ef_search` — controls the search effort during querying.

Higher search effort can improve recall but may increase query latency.

### Benchmark Status

The HNSW index was created on the benchmark table. However, the initial benchmark query plan used a sequential scan, so a confirmed HNSW-specific timing has not yet been recorded.

## 3. IVFFlat Index

IVFFlat stands for Inverted File with Flat compression. It divides vectors into clusters and searches selected clusters.

### Index Creation

```sql
CREATE INDEX semantic_documents_benchmark_ivfflat_idx
ON semantic_documents_benchmark
USING ivfflat (embedding vector_cosine_ops)
WITH (lists = 50);
```

The index was created on the 5,000-document benchmark table.

### Important Parameters

* `lists` — controls the number of clusters created by the index.
* `ivfflat.probes` — controls how many clusters are searched during a query.

Searching more clusters can improve recall but may increase latency.

### Benchmark Result

The benchmark used the IVFFlat index scan with sequential scans discouraged for the test session.

| Metric                                |   Result |
| ------------------------------------- | -------: |
| Documents                             |    5,000 |
| Results returned                      |        5 |
| Average execution time across 10 runs | 0.061 ms |
| Minimum execution time                | 0.040 ms |
| Maximum execution time                | 0.104 ms |

These are preliminary measurements from the current environment, not a controlled comparison against HNSW. Planner settings, cache state, and other factors can affect timings.

## 4. Cosine Distance

The `<=>` operator calculates cosine distance between vectors.

```sql
SELECT
    id,
    content,
    embedding <=> '[...]'::vector AS distance
FROM semantic_documents_benchmark
ORDER BY embedding <=> '[...]'::vector
LIMIT 5;
```

Replace the placeholder with a valid embedding containing the expected 384 dimensions.

Lower cosine distance indicates greater similarity under this distance metric.

The index operator class `vector_cosine_ops` matches cosine-distance searches.

## 5. Query Plan Analysis

Use `EXPLAIN (ANALYZE, BUFFERS)` to inspect how PostgreSQL executes a search.

```sql
EXPLAIN (ANALYZE, BUFFERS)
SELECT id, content
FROM semantic_documents_benchmark
ORDER BY embedding <=> '[...]'::vector
LIMIT 5;
```

Look for:

* `Seq Scan` — PostgreSQL scans table rows.
* `Index Scan` — PostgreSQL uses an index.
* `Sort` — rows are ordered to identify the nearest results.
* `Execution Time` — reported database execution time.

PostgreSQL may choose a sequential scan even when a vector index exists. Forcing a planner setting can help diagnose index usage, but forced-plan timings should be distinguished from normal planner behavior.

## 6. HNSW vs. IVFFlat

| Feature                 | HNSW                                | IVFFlat                                     |
| ----------------------- | ----------------------------------- | ------------------------------------------- |
| Structure               | Graph                               | Clusters                                    |
| Main tuning parameters  | `m`, `ef_construction`, `ef_search` | `lists`, `probes`                           |
| Search type             | Approximate nearest-neighbor search | Approximate nearest-neighbor search         |
| Index building          | Builds a graph                      | Builds clusters using the available vectors |
| Important consideration | Memory and index-build cost         | Choose `lists` and `probes` appropriately   |

Neither index is universally faster or more accurate. The best choice depends on the dataset, recall requirements, available memory, and query workload.

## 7. Lessons Learned

* Vector indexes can accelerate nearest-neighbor searches on larger datasets.
* PostgreSQL's query planner decides whether to use an index.
* HNSW and IVFFlat use different data structures and tuning parameters.
* `EXPLAIN (ANALYZE, BUFFERS)` helps investigate query performance.
* Benchmark results should be interpreted in context and measured under comparable conditions.
* Approximate search performance should be considered alongside result quality and recall.

## 8. Current Status

Completed:

* Created a 5,000-document benchmark dataset.
* Created HNSW and IVFFlat indexes.
* Ran an exact-search baseline.
* Executed a benchmark using the IVFFlat index.
* Practiced reading PostgreSQL execution plans.

Remaining:

* A controlled HNSW benchmark and a fair HNSW-versus-IVFFlat comparison have not been completed.

## 9. Run the Benchmark

From the repository root, activate the Python virtual environment and run:

```powershell
python phase-6-vector-indexes/benchmark_search.py
```

Database connection settings are supplied through environment variables. Keep `.env` out of version control and use `.env.example` to document the required settings.
