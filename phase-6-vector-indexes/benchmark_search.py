
import os

import psycopg
from dotenv import load_dotenv
from sentence_transformers import SentenceTransformer

load_dotenv()

QUERY = "artificial intelligence and information retrieval"
TOP_K = 5
RUNS = 10

model = SentenceTransformer("all-MiniLM-L6-v2")
query_embedding = model.encode(QUERY).tolist()

connection = psycopg.connect(
    host=os.getenv("POSTGRES_HOST"),
    port=os.getenv("POSTGRES_PORT"),
    dbname=os.getenv("POSTGRES_DB"),
    user=os.getenv("POSTGRES_USER"),
    password=os.getenv("POSTGRES_PASSWORD"),
)

try:
    with connection.cursor() as cursor:
        # Warm up the same nearest-neighbor query.
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

        print("\nHNSW Benchmark Results")
        print(f"Runs completed: {len(timings)}")

        print("\nRelevant query plan:")
        for line in final_plan:
            if (
                "Index Scan" in line
                or "Seq Scan" in line
                or "Sort  " in line
                or line.strip().startswith("Execution Time:")
            ):
                print(line)

        if timings:
            print(f"\nAverage execution: {sum(timings) / len(timings):.3f} ms")
            print(f"Minimum execution: {min(timings):.3f} ms")
            print(f"Maximum execution: {max(timings):.3f} ms")

finally:
    connection.close()