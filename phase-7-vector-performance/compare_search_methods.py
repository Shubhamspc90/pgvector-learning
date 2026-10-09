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
HNSW_EF_SEARCH = 40
IVFFLAT_PROBES = 10
IVFFLAT_LISTS = 50


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


def benchmark_method(cursor, name, table, query_embedding, exact_ids):
    # Each temporary table has only the index intended for its experiment.
    if name == "Exact search":
        cursor.execute("SET enable_seqscan = on;")
        cursor.execute("SET enable_indexscan = off;")
        cursor.execute("SET enable_bitmapscan = off;")
    else:
        cursor.execute("SET enable_seqscan = off;")
        cursor.execute("SET enable_indexscan = on;")
        cursor.execute("SET enable_bitmapscan = off;")

    if name == "HNSW":
        cursor.execute(f"SET hnsw.ef_search = {HNSW_EF_SEARCH};")

    if name == "IVFFlat":
        cursor.execute(f"SET ivfflat.probes = {IVFFLAT_PROBES};")

    # Warm-up: do not include this execution in the timings.
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
            if line.strip().startswith("Execution Time:"):
                timings.append(
                    float(line.split(":")[1].strip().split()[0])
                )

    result_ids = fetch_ids(cursor, table, query_embedding)
    recall = len(set(result_ids) & set(exact_ids)) / len(exact_ids)

    print(f"\n--- {name} ---")
    print(f"Runs measured: {len(timings)}")
    for line in final_plan:
        stripped = line.strip()
    
        if (
            stripped.startswith("->  Index Scan")
            or stripped.startswith("->  Seq Scan")
            or stripped.startswith("->  Sort")
            or stripped.startswith("Execution Time:")
        ):
            print(stripped)

    if timings:
        print(f"Average execution: {statistics.mean(timings):.3f} ms")
        print(f"Minimum execution: {min(timings):.3f} ms")
        print(f"Maximum execution: {max(timings):.3f} ms")

    print(f"Recall@{TOP_K} against exact search: {recall:.0%}")

    return statistics.mean(timings) if timings else None, recall


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
                f"""
                SELECT COUNT(*)
                FROM {SOURCE_TABLE};
                """
            )
            document_count = cursor.fetchone()[0]

            if document_count == 0:
                raise ValueError("The benchmark table contains no documents.")

            # Temporary copies isolate each method's index.
            # The original table and its indexes are not modified.
            for table in (
                "phase7_exact",
                "phase7_hnsw",
                "phase7_ivfflat",
            ):
                cursor.execute(f"DROP TABLE IF EXISTS {table};")

            for table in (
                "phase7_exact",
                "phase7_hnsw",
                "phase7_ivfflat",
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
                CREATE INDEX phase7_hnsw_idx
                ON phase7_hnsw
                USING hnsw (embedding vector_cosine_ops);
                """
            )

            cursor.execute(
                f"""
                CREATE INDEX phase7_ivfflat_idx
                ON phase7_ivfflat
                USING ivfflat (embedding vector_cosine_ops)
                WITH (lists = {IVFFLAT_LISTS});
                """
            )

            for table in (
                "phase7_exact",
                "phase7_hnsw",
                "phase7_ivfflat",
            ):
                cursor.execute(f"ANALYZE {table};")

            # Exact search establishes the reference top-K result set.
            cursor.execute("SET enable_seqscan = on;")
            cursor.execute("SET enable_indexscan = off;")
            cursor.execute("SET enable_bitmapscan = off;")
            exact_ids = fetch_ids(cursor, "phase7_exact", query_embedding)

            print("\n=== Phase 7: Search Method Comparison ===")
            print(f"Source dataset: {SOURCE_TABLE}")
            print(f"Document count: {document_count}")
            print(f"Query: {QUERY}")
            print(f"Top K: {TOP_K}")
            print(f"Measured runs per method: {RUNS}")
            print(f"HNSW ef_search: {HNSW_EF_SEARCH}")
            print(f"IVFFlat lists: {IVFFLAT_LISTS}")
            print(f"IVFFlat probes: {IVFFLAT_PROBES}")

            results = {}

            for name, table in (
                ("Exact search", "phase7_exact"),
                ("HNSW", "phase7_hnsw"),
                ("IVFFlat", "phase7_ivfflat"),
            ):
                results[name] = benchmark_method(
                    cursor, name, table, query_embedding, exact_ids
                )

            print("\n=== Summary ===")
            print(f"{'Method':<15} {'Average (ms)':>14} {'Recall@5':>12}")
            for name, (average, recall) in results.items():
                avg_text = f"{average:.3f}" if average is not None else "N/A"
                print(f"{name:<15} {avg_text:>14} {recall:>11.0%}")

    finally:
        connection.close()


if __name__ == "__main__":
    main()
