# Phase 8: Vector Search Quality Evaluation

## Objective

Evaluate approximate vector search quality across multiple queries by comparing HNSW and IVFFlat results against exact cosine-distance search using PostgreSQL and pgvector.

## Dataset and Configuration

* Source table: `semantic_documents_benchmark`
* Documents with embeddings: 5,000
* Evaluation queries: 10
* Embedding model: `all-MiniLM-L6-v2`
* Embedding dimensions: 384
* Similarity metric: Cosine distance
* Evaluation metric: Recall@5

### Search configurations

| Method       | Configuration               |
| ------------ | --------------------------- |
| Exact search | Sequential scan reference   |
| HNSW         | `ef_search = 40`            |
| IVFFlat      | `lists = 50`, `probes = 10` |

## Results

Results from the latest verified local run:

| Metric            | HNSW | IVFFlat |
| ----------------- | ---: | ------: |
| Queries evaluated |   10 |      10 |
| Average Recall@5  |  60% |     74% |

The query plans confirmed that PostgreSQL used a sequential scan for the exact reference and the intended HNSW and IVFFlat indexes for approximate searches.

### Per-query Recall@5

| Query ID | HNSW | IVFFlat |
| -------- | ---: | ------: |
| q1       | 100% |     80% |
| q2       |   0% |    100% |
| q3       | 100% |     80% |
| q4       |  40% |    100% |
| q5       |  80% |     60% |
| q6       |  60% |     80% |
| q7       |  80% |     80% |
| q8       |  40% |     60% |
| q9       |  20% |      0% |
| q10      |  80% |    100% |

## Interpretation

* IVFFlat achieved a higher average Recall@5 than HNSW in this run.
* HNSW achieved perfect recall on q1 and q3 but returned none of the exact top-five documents for q2.
* IVFFlat achieved perfect recall on q2, q4, and q10, but returned none of the exact top-five documents for q9.
* Neither method performed equally well for every query.
* These findings describe this dataset and these particular index settings; they do not establish a universal ranking between HNSW and IVFFlat.

## Methodology

For each query:

1. Generate an embedding using `all-MiniLM-L6-v2`.
2. Retrieve the exact top-five document IDs using cosine distance.
3. Retrieve the top-five IDs using HNSW.
4. Retrieve the top-five IDs using IVFFlat.
5. Calculate Recall@5 for each approximate method against the exact results.
6. Aggregate recall across all ten queries.

Recall@5 is calculated as:

Recall@5 = number of exact top-five documents retrieved / number of exact top-five documents

## Limitations

* Exact nearest-neighbor results are a reference for retrieval agreement, not human-annotated relevance judgments.
* Only ten queries and one 5,000-document dataset were evaluated.
* The experiment uses one HNSW configuration and one IVFFlat configuration.
* Approximate-index results may vary with index construction and search settings.
* This phase evaluates retrieval quality, not search latency.
* The recorded results represent a local run and may differ on another machine or database state.

## Reproducibility

Run the evaluation from the repository root:

```powershell
python .\phase-8-search-quality\evaluate_search_quality.py
```

The script uses the project's `.env` database configuration and PostgreSQL port 5433. Temporary evaluation tables are created for each run and removed when the connection closes.

## Conclusion

In the latest verified run, IVFFlat achieved 74% average Recall@5, compared with 60% for HNSW. Further testing across additional queries and index configurations is needed before making broader performance or quality recommendations.
