
import os
import statistics

import psycopg
from dotenv import load_dotenv
from sentence_transformers import SentenceTransformer


load_dotenv()

MODEL_NAME = "all-MiniLM-L6-v2"
SOURCE_TABLE = "semantic_documents_benchmark"
QUERY = "artificial intelligence and information retrieval"

TOP_K = 5
RUNS = 10
IVFFLAT_LISTS = 50

HNSW_EF_SEARCH_VALUES = [10, 40, 100]
IVFFLAT_PROBES_VALUES = [1, 5, 10, 25, 50]


def fetch_ids(cursor, table, query_embedding):
    cursor.execute(
        f"""
        SELECT id
        FROM {table}
        ORDER BY embedding <=> %s::vector
        LIMIT %s;
        """,
        (query_embedding, TOP_K),
    )
    return [row[0] for row in cursor.fetchall()]


def benchmark_configuration(
    cursor,
    method,
    table,
    parameter_value,
    query_embedding,
    exact_ids,
):
    # Force the intended search access path for this experiment.
    cursor.execute("SET enable_seqscan = off;")
    cursor.execute("SET enable_indexscan = on;")
    cursor.execute("SET enable_bitmapscan = off;")

    if method == "HNSW":
        cursor.execute(
            f"SET hnsw.ef_search = {parameter_value};"
        )
    elif method == "IVFFlat":
        cursor.execute(
            f"SET ivfflat.probes = {parameter_value};"
        )

    # Warm-up query: excluded from measured timings.
    fetch_ids(cursor, table, query_embedding)

    timings = []
    final_plan = []

    for _ in range(RUNS):
        cursor.execute(
            f"""
            EXPLAIN (ANALYZE, BUFFERS)
            SELECT id
            FROM {table}
            ORDER BY embedding <=> %s::vector
            LIMIT %s;
            """,
            (query_embedding, TOP_K),
        )

        final_plan = [row[0] for row in cursor.fetchall()]

        for line in final_plan:
            stripped = line.strip()

            if stripped.startswith("Execution Time:"):
                timings.append(
                    float(stripped.split(":")[1].strip().split()[0])
                )

    result_ids = fetch_ids(cursor, table, query_embedding)

    recall = (
        len(set(result_ids) & set(exact_ids)) / len(exact_ids)
        if exact_ids
        else 0.0
    )

    plan_summary = [
        line.strip()
        for line in final_plan
        if (
            line.strip().startswith("->  Index Scan")
            or line.strip().startswith("->  Seq Scan")
            or line.strip().startswith("Execution Time:")
        )
    ]

    average = statistics.mean(timings) if timings else None

    return {
        "method": method,
        "parameter": parameter_value,
        "average_ms": average,
        "minimum_ms": min(timings) if timings else None,
        "maximum_ms": max(timings) if timings else None,
        "recall": recall,
        "plan": plan_summary,
    }


def print_result(result):
    print(
        f"\n{result['method']} | "
        f"parameter={result['parameter']}"
    )

    if result["average_ms"] is None:
        print("Execution timing unavailable.")
    else:
        print(f"Average: {result['average_ms']:.3f} ms")
        print(f"Minimum: {result['minimum_ms']:.3f} ms")
        print(f"Maximum: {result['maximum_ms']:.3f} ms")

    print(f"Recall@{TOP_K}: {result['recall']:.0%}")

    for line in result["plan"]:
        print(line)


def main():
    print("Loading embedding model...")
    model = SentenceTransformer(MODEL_NAME)
    query_embedding = model.encode(QUERY).tolist()

    connection = psycopg.connect(
        host=os.getenv("POSTGRES_HOST"),
        port=os.getenv("POSTGRES_PORT", "5433"),
        dbname=os.getenv("POSTGRES_DB"),
        user=os.getenv("POSTGRES_USER"),
        password=os.getenv("POSTGRES_PASSWORD"),
    )

    try:
        with connection.cursor() as cursor:
            cursor.execute(
                f"SELECT COUNT(*) FROM {SOURCE_TABLE};"
            )
            document_count = cursor.fetchone()[0]

            if document_count == 0:
                raise ValueError("The benchmark table contains no documents.")

            # Build isolated temporary copies for this experiment.
            for table in (
                "phase7_tune_exact",
                "phase7_tune_hnsw",
                "phase7_tune_ivfflat",
            ):
                cursor.execute(
                    f"""
                    CREATE TEMP TABLE {table} AS
                    SELECT id, content, embedding
                    FROM {SOURCE_TABLE};
                    """
                )

            cursor.execute(
                """
                CREATE INDEX phase7_tune_hnsw_idx
                ON phase7_tune_hnsw
                USING hnsw (embedding vector_cosine_ops);
                """
            )

            cursor.execute(
                f"""
                CREATE INDEX phase7_tune_ivfflat_idx
                ON phase7_tune_ivfflat
                USING ivfflat (embedding vector_cosine_ops)
                WITH (lists = {IVFFLAT_LISTS});
                """
            )

            for table in (
                "phase7_tune_exact",
                "phase7_tune_hnsw",
                "phase7_tune_ivfflat",
            ):
                cursor.execute(f"ANALYZE {table};")

            # Calculate exact nearest neighbors as the reference.
            cursor.execute("SET enable_seqscan = on;")
            cursor.execute("SET enable_indexscan = off;")
            cursor.execute("SET enable_bitmapscan = off;")

            exact_ids = fetch_ids(
                cursor, "phase7_tune_exact", query_embedding
            )

            print("\n=== Phase 7: Parameter Tuning ===")
            print(f"Source table: {SOURCE_TABLE}")
            print(f"Documents: {document_count}")
            print(f"Query: {QUERY}")
            print(f"Top K: {TOP_K}")
            print(f"Measured runs per configuration: {RUNS}")
            print(f"IVFFlat lists: {IVFFLAT_LISTS}")

            results = []

            # Tune HNSW while keeping the dataset and query fixed.
            for value in HNSW_EF_SEARCH_VALUES:
                result = benchmark_configuration(
                    cursor,
                    "HNSW",
                    "phase7_tune_hnsw",
                    value,
                    query_embedding,
                    exact_ids,
                )
                results.append(result)
                print_result(result)

            # Tune IVFFlat independently.
            for value in IVFFLAT_PROBES_VALUES:
                result = benchmark_configuration(
                    cursor,
                    "IVFFlat",
                    "phase7_tune_ivfflat",
                    value,
                    query_embedding,
                    exact_ids,
                )
                results.append(result)
                print_result(result)

            print("\n=== Tuning Summary ===")
            print(
                f"{'Method':<10} {'Parameter':>10} "
                f"{'Average (ms)':>14} {'Recall@5':>12}"
            )

            for result in results:
                average = result["average_ms"]
                average_text = (
                    f"{average:.3f}" if average is not None else "N/A"
                )

                print(
                    f"{result['method']:<10} "
                    f"{result['parameter']:>10} "
                    f"{average_text:>14} "
                    f"{result['recall']:>11.0%}"
                )

    finally:
        connection.close()


if __name__ == "__main__":
    main()