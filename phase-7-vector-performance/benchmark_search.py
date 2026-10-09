import os
import statistics

import psycopg
from dotenv import load_dotenv
from sentence_transformers import SentenceTransformer

load_dotenv()

MODEL_NAME = "all-MiniLM-L6-v2"
QUERY = "artificial intelligence and information retrieval"
TOP_K = 5
RUNS = 10

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
                "SELECT COUNT(*) FROM semantic_documents_benchmark;"
            )
            document_count = cursor.fetchone()[0]

            # Warm-up query: exclude its execution from measured runs.
            cursor.execute(
                """
                SELECT id
                FROM semantic_documents_benchmark
                ORDER BY embedding <=> %s::vector
                LIMIT %s;
                """,
                (query_embedding, TOP_K),
            )
            cursor.fetchall()

            timings = []
            final_plan = []

            for _ in range(RUNS):
                cursor.execute(
                    """
                    EXPLAIN (ANALYZE, BUFFERS)
                    SELECT id, content,
                           embedding <=> %s::vector AS distance
                    FROM semantic_documents_benchmark
                    ORDER BY embedding <=> %s::vector
                    LIMIT %s;
                    """,
                    (query_embedding, query_embedding, TOP_K),
                )

                final_plan = [row[0] for row in cursor.fetchall()]

                for line in final_plan:
                    if line.strip().startswith("Execution Time:"):
                        timings.append(
                            float(line.split(":")[1].strip().split()[0])
                        )

            print("\n=== Vector Search Benchmark ===")
            print(f"Dataset: semantic_documents_benchmark")
            print(f"Document count: {document_count}")
            print(f"Query: {QUERY}")
            print(f"Top K: {TOP_K}")
            print(f"Measured runs: {len(timings)}")

            print("\nQuery plan details:")
            for line in final_plan:
                if any(
                    label in line
                    for label in (
                        "Index Scan",
                        "Seq Scan",
                        "Sort",
                        "Execution Time:",
                    )
                ):
                    print(line.strip())

            if timings:
                print("\nDatabase execution time:")
                print(f"Average: {statistics.mean(timings):.3f} ms")
                print(f"Minimum: {min(timings):.3f} ms")
                print(f"Maximum: {max(timings):.3f} ms")
            else:
                print("No execution-time measurements were collected.")

    finally:
        connection.close()


if __name__ == "__main__":
    main()
