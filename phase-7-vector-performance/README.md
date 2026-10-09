# Phase 7: Vector Search Performance

## 1. Objective

Understand and evaluate vector-search performance in PostgreSQL using pgvector.

This phase focuses on:

* Measuring vector-search execution time.
* Understanding query execution plans.
* Comparing exact search, HNSW, and IVFFlat.
* Tuning HNSW and IVFFlat search parameters.
* Evaluating the trade-off between search speed and retrieval accuracy using Recall@5.

## 2. Dataset and Environment

| Property             | Configuration                  |
| -------------------- | ------------------------------ |
| Database             | `pgvector_learning`            |
| PostgreSQL port      | `5433`                         |
| Source table         | `semantic_documents_benchmark` |
| Dataset size         | 5,000 documents                |
| Embedding model      | `all-MiniLM-L6-v2`             |
| Embedding dimensions | 384                            |
| Result limit (K)     | 5                              |
| Measured runs        | 10 per configuration           |
| Distance metric      | Cosine distance                |
| Vector extension     | pgvector                       |

All experiments use the existing benchmark dataset. The comparison and tuning scripts create temporary tables and indexes, leaving the original benchmark table and its indexes unchanged.

## 3. Milestone 1: Initial Benchmark

**Script:** `benchmark_search.py`

The initial benchmark establishes a baseline for vector-search execution time.

The script uses `EXPLAIN (ANALYZE, BUFFERS)` to inspect the query execution plan and collect execution-time measurements across repeated runs.

### Results

| Metric                 |   Result |
| ---------------------- | -------: |
| Average execution time | 0.047 ms |
| Minimum execution time | 0.029 ms |
| Maximum execution time | 0.087 ms |
| Measured runs          |       10 |
| Observed index         |  IVFFlat |

### Analysis

PostgreSQL used `semantic_documents_benchmark_ivfflat_idx` for the observed query plan.

These measurements establish a baseline for the existing database configuration. They do not provide a controlled comparison between exact search, HNSW, and IVFFlat.

The reported execution time measures database query execution, not the complete application response time. The initial benchmark also does not measure recall.

## 4. Milestone 2: Exact Search vs. HNSW vs. IVFFlat

**Script:** `compare_search_methods.py`

This experiment compares exact search with two approximate nearest-neighbor search methods.

Exact search provides the reference top-5 results. HNSW and IVFFlat results are compared against this reference to evaluate retrieval quality.

### Experimental Configuration

| Parameter                | Value                                               |
| ------------------------ | --------------------------------------------------- |
| Dataset size             | 5,000 documents                                     |
| Query                    | `artificial intelligence and information retrieval` |
| Result limit             | 5                                                   |
| Measured runs per method | 10                                                  |
| HNSW `ef_search`         | 40                                                  |
| IVFFlat `lists`          | 50                                                  |
| IVFFlat `probes`         | 10                                                  |
| Distance metric          | Cosine distance                                     |

### Results

| Method       |  Average |  Minimum |  Maximum | Recall@5 |
| ------------ | -------: | -------: | -------: | -------: |
| Exact search | 6.610 ms | 5.515 ms | 9.385 ms |     100% |
| HNSW         | 0.264 ms | 0.164 ms | 0.555 ms |     100% |
| IVFFlat      | 0.401 ms | 0.300 ms | 0.591 ms |      80% |

### Analysis

Exact search was used as the reference for determining the five nearest documents.

In this experiment:

* HNSW was approximately 25 times faster than exact search and achieved 100% Recall@5.
* IVFFlat was approximately 16.5 times faster than exact search and achieved 80% Recall@5.
* HNSW performed better than IVFFlat for this particular query and configuration.

These results demonstrate that approximate search can substantially reduce query execution time while retaining most or all of the reference results.

However, these measurements are specific to this experiment. They do not establish a universal ranking of the algorithms.

### Limitations

* Only one query was used to evaluate recall.
* Only one set of index parameters was tested for each method.
* Results depend on hardware, cache state, dataset characteristics, and configuration.
* Index construction and dataset preparation time are excluded from query execution measurements.
* Database execution time does not include embedding generation or end-to-end application overhead.

## 5. Milestone 3: HNSW and IVFFlat Parameter Tuning

**Script:** `tune_search_parameters.py`

This experiment investigates how HNSW `ef_search` and IVFFlat `probes` affect execution time and Recall@5.

The dataset size, query, result limit, and number of measured runs remain consistent across configurations.

### 5.1 HNSW Results

| `ef_search` | Average execution time | Recall@5 |
| ----------: | ---------------------: | -------: |
|          10 |               0.104 ms |      20% |
|          40 |               0.320 ms |     100% |
|         100 |               0.515 ms |     100% |

**Observations:**

* At `ef_search = 10`, search was fastest but retrieved only 20% of the exact top-5 results.
* At `ef_search = 40`, Recall@5 reached 100%.
* Increasing `ef_search` to 100 did not improve recall further for this query and increased execution time.

The results illustrate how increasing the search effort can improve recall at the cost of additional execution time.

### 5.2 IVFFlat Results

The number of index lists was fixed at `lists = 50`.

| `probes` | Average execution time | Recall@5 |
| -------: | ---------------------: | -------: |
|        1 |               0.065 ms |       0% |
|        5 |               0.152 ms |      60% |
|       10 |               0.418 ms |      80% |
|       25 |               0.960 ms |     100% |
|       50 |               4.290 ms |     100% |

**Observations:**

* Low `probes` values provided faster searches but lower recall.
* At `probes = 25`, Recall@5 reached 100%.
* At `probes = 50`, all 50 lists were examined. Execution time increased substantially without improving recall for this query.

Searching all lists increases the amount of work performed and can remove the usual benefit of limiting the search to selected lists. The observed query plan and result quality should still be evaluated rather than assuming that an index scan is necessarily faster.

### 5.3 Comparing the Tuned Configurations

For this particular query:

| Configuration          | Average execution time | Recall@5 |
| ---------------------- | ---------------------: | -------: |
| HNSW, `ef_search = 40` |               0.320 ms |     100% |
| IVFFlat, `probes = 25` |               0.960 ms |     100% |

Both configurations achieved 100% Recall@5 in the experiment. HNSW was approximately three times faster than IVFFlat under these settings.

This is a local experimental observation, not a guarantee that HNSW will outperform IVFFlat on every workload.

## 6. Overall Findings

The three milestones demonstrate the main performance considerations when using pgvector.

### Exact Search

* Provides the reference results for evaluating approximate search.
* Can require more work as the dataset grows.
* Is useful for establishing retrieval-quality baselines.

### HNSW

* Uses a graph-based index for approximate nearest-neighbor search.
* The `ef_search` parameter controls the search effort at query time.
* Higher settings can improve recall but may increase execution time.

### IVFFlat

* Organizes vectors into lists of clusters.
* The `lists` parameter controls index construction, while `probes` controls how many lists are searched at query time.
* Higher `probes` values can improve recall but may increase query execution time.

### Practical Conclusion

There is no single configuration that is best for every application.

A suitable configuration depends on the required retrieval quality, acceptable latency, dataset size, hardware, and query workload.

For the query tested in this phase, HNSW with `ef_search = 40` achieved 100% Recall@5 with lower average execution time than IVFFlat with `probes = 25`.

These findings should be validated with additional queries and datasets before choosing production settings.

## 7. Understanding Recall@5

Recall@5 measures how many of the exact search's top-five results are also returned by the approximate search.

The formula is:

`Recall@5 = (Number of matching results / 5) × 100`

For example, if an approximate method returns four of the five exact top results:

`Recall@5 = (4 / 5) × 100 = 80%`

A higher recall means the approximate search retrieved more of the reference results. Recall alone does not measure execution speed or every aspect of semantic relevance.

## 8. Reproducibility

Run these commands from the repository root after activating the virtual environment and configuring the PostgreSQL connection in `.env`.

### Initial benchmark

```powershell
python .\phase-7-vector-performance\benchmark_search.py
```

### Compare search methods

```powershell
python .\phase-7-vector-performance\compare_search_methods.py
```

### Tune search parameters

```powershell
python .\phase-7-vector-performance\tune_search_parameters.py
```

The comparison and tuning scripts use temporary tables and indexes for their experiments. The temporary objects are removed when the database connection closes. The source benchmark table is not modified by these scripts.

Execution times can vary between runs because of system load, caching, PostgreSQL configuration, and other environmental factors.

## 9. Limitations and Future Work

The current experiments are a learning benchmark, not a comprehensive production evaluation.

Current limitations:

* Recall was evaluated using only one query.
* The dataset contains 5,000 documents.
* Each configuration was measured over 10 runs.
* The experiments use a single embedding model and distance metric.
* Measurements focus on PostgreSQL query execution time rather than end-to-end latency.

Potential future experiments:

1. Evaluate recall across a larger collection of representative queries.
2. Compare performance on larger datasets.
3. Investigate the effects of index parameters on index size and memory usage.
4. Measure end-to-end latency, including query embedding generation.
5. Evaluate different workloads before selecting production configurations.

## 10. Key Learning Outcomes

After completing this phase, the main concepts learned are:

* How to measure PostgreSQL query execution time using `EXPLAIN (ANALYZE, BUFFERS)`.
* How to inspect query plans and verify index usage.
* How exact search differs from approximate nearest-neighbor search.
* How HNSW and IVFFlat index parameters influence latency and recall.
* How to calculate and interpret Recall@5.
* Why performance benchmarks must document their configuration, limitations, and experimental conditions.
