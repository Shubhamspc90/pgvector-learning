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


## Milestone 2: Exact Search vs. HNSW vs. IVFFlat

### Experimental Configuration

* Dataset: 5,000 documents
* Query: `artificial intelligence and information retrieval`
* Result limit: 5
* Measured runs per method: 10
* HNSW `ef_search`: 40
* IVFFlat `lists`: 50
* IVFFlat `probes`: 10
* Distance metric: cosine distance

### Results

| Method       | Average execution time |  Minimum |  Maximum | Recall@5 |
| ------------ | ---------------------: | -------: | -------: | -------: |
| Exact search |               6.610 ms | 5.515 ms | 9.385 ms |     100% |
| HNSW         |               0.264 ms | 0.164 ms | 0.555 ms |     100% |
| IVFFlat      |               0.401 ms | 0.300 ms | 0.591 ms |      80% |

### Analysis

Exact search was the reference method for determining the nearest five documents.

In this experiment, HNSW was approximately 25 times faster than exact search and achieved 100% Recall@5. IVFFlat was approximately 16.5 times faster than exact search and achieved 80% Recall@5.

HNSW performed better than IVFFlat for this particular query and configuration. These measurements are local experimental results, not a universal ranking of the algorithms.

Recall was evaluated for one query only. More queries are needed to draw conclusions about overall retrieval quality. Execution time also depends on the machine, cache state, dataset, and configuration.

### Limitations

* Only one query was used for the initial recall comparison.
* The results reflect one set of index parameters.
* The measurements represent PostgreSQL query execution, not end-to-end application latency.
* Index creation and dataset-copying time are excluded from the reported query timings.


## Milestone 3: HNSW and IVFFlat Parameter Tuning

### Experimental Configuration

* Dataset: 5,000 documents
* Query: `artificial intelligence and information retrieval`
* Result limit: 5
* Measured runs per configuration: 10
* IVFFlat lists: 50
* Distance metric: cosine distance

### HNSW Results

| `ef_search` | Average execution time | Recall@5 |
| ----------: | ---------------------: | -------: |
|          10 |               0.104 ms |      20% |
|          40 |               0.320 ms |     100% |
|         100 |               0.515 ms |     100% |

Increasing `ef_search` improved recall from 20% to 100% between values 10 and 40. Increasing it further to 100 did not improve recall for this query and increased execution time.

### IVFFlat Results

| `probes` | Average execution time | Recall@5 |
| -------: | ---------------------: | -------: |
|        1 |               0.065 ms |       0% |
|        5 |               0.152 ms |      60% |
|       10 |               0.418 ms |      80% |
|       25 |               0.960 ms |     100% |
|       50 |               4.290 ms |     100% |

Increasing `probes` improved recall in this experiment. At 50 probes, all lists were examined and Recall@5 reached 100%, but execution time increased substantially.

### Analysis

For this query and dataset, HNSW with `ef_search = 40` achieved 100% Recall@5 at an average execution time of 0.320 ms. IVFFlat with `probes = 25` also achieved 100% Recall@5, with an average execution time of 0.960 ms.

These are preliminary local measurements, not universal performance guarantees. Only one query was evaluated, so further queries are needed to assess general retrieval quality.

The measurements represent PostgreSQL query execution time. They exclude model loading, embedding generation, temporary-table creation, and index construction.

### Key Learning

* HNSW `ef_search` controls the search effort and can trade latency for recall.
* IVFFlat `probes` controls how many index lists are examined.
* Higher settings can improve recall but may increase execution time.
* Query plans should be checked to verify the intended index is being used.
