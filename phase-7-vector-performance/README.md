# Phase 7: Vector Search Performance

## Objective

Understand vector-search performance in PostgreSQL with pgvector by measuring execution time, examining query plans, tuning index parameters, and evaluating the trade-off between speed and recall.

## Dataset and Environment

* Database: `pgvector_learning`
* PostgreSQL port: `5433`
* Benchmark table: `semantic_documents_benchmark`
* Dataset size: 5,000 documents
* Embedding model: `all-MiniLM-L6-v2`
* Embedding dimensions: 384
* Result limit: 5
* Measured executions: 10

## Milestone 1: Initial Benchmark

The initial benchmark script, `benchmark_search.py`, warms up the query and collects PostgreSQL execution-time measurements using `EXPLAIN (ANALYZE, BUFFERS)`.

### Preliminary Results

| Metric                 |   Result |
| ---------------------- | -------: |
| Average execution time | 0.047 ms |
| Minimum execution time | 0.029 ms |
| Maximum execution time | 0.087 ms |
| Measured runs          |       10 |
| Observed index         |  IVFFlat |

### Interpretation

PostgreSQL used `semantic_documents_benchmark_ivfflat_idx` for the observed query plan.

These results are preliminary and reflect one query, the current database state, and the current search configuration. They are not a controlled comparison of HNSW and IVFFlat.

Database execution time excludes embedding generation and other application-level overhead. The initial benchmark also does not measure recall.

## Planned Experiments

1. Compare exact search with HNSW and IVFFlat.
2. Investigate HNSW `ef_search` and IVFFlat `probes`.
3. Measure recall against exact-search results.
4. Analyze performance results and document limitations.

## Reproducibility

Activate the project's virtual environment, configure the PostgreSQL connection in `.env`, and run from the repository root:

```powershell
python .\phase-7-vector-performance\benchmark_search.py
```

The script reads the existing benchmark dataset and does not generate new documents.
