
import json
import os
from pathlib import Path
from statistics import mean

import psycopg
from dotenv import load_dotenv
from sentence_transformers import SentenceTransformer


# --------------------------------------------------
# Configuration
# --------------------------------------------------

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent
DATASET_FILE = BASE_DIR / "evaluation_queries.json"

MODEL_NAME = "all-MiniLM-L6-v2"
SOURCE_TABLE = "semantic_documents_benchmark"

TOP_K = 5
HNSW_EF_SEARCH = 40
IVFFLAT_LISTS = 50
IVFFLAT_PROBES = 10


# --------------------------------------------------
# Load evaluation queries
# --------------------------------------------------

def load_queries():
    """Load and validate the evaluation query dataset."""

    with open(DATASET_FILE, "r", encoding="utf-8-sig") as file:
        queries = json.load(file)

    if not isinstance(queries, list) or not queries:
        raise ValueError("The evaluation dataset must be a non-empty JSON list.")

    query_ids = set()

    for item in queries:
        if not isinstance(item, dict):
            raise ValueError("Every dataset entry must be a JSON object.")

        if not item.get("id") or not item.get("query", "").strip():
            raise ValueError("Every entry must have a non-empty id and query.")

        if item["id"] in query_ids:
            raise ValueError(f"Duplicate query ID: {item['id']}")

        query_ids.add(item["id"])

    return queries


# --------------------------------------------------
# Database helpers
# --------------------------------------------------


def get_connection():
    """Connect using the project's existing PostgreSQL configuration."""

    return psycopg.connect(
        host=os.getenv("POSTGRES_HOST", "localhost"),
        port=int(os.getenv("POSTGRES_PORT", "5433")),
        dbname=os.getenv("POSTGRES_DB"),
        user=os.getenv("POSTGRES_USER"),
        password=os.getenv("POSTGRES_PASSWORD"),
    )


def fetch_ids(cursor, table_name, embedding):
    """Return the top-K document IDs ordered by cosine distance."""

    cursor.execute(
        f"""
        SELECT id
        FROM {table_name}
        ORDER BY embedding <=> %s::vector
        LIMIT %s
        """,
        (embedding, TOP_K),
    )

    return [row[0] for row in cursor.fetchall()]


def calculate_recall(exact_ids, approximate_ids):
    """Calculate the fraction of exact top-K results retrieved."""

    if not exact_ids:
        return 0.0

    matching_ids = set(exact_ids).intersection(approximate_ids)
    return len(matching_ids) / len(exact_ids)


# --------------------------------------------------
# Prepare independent search tables
# --------------------------------------------------

def prepare_search_tables(cursor):
    """Create temporary tables for exact and approximate searches."""

    cursor.execute(
        f"""
        SELECT COUNT(*)
        FROM {SOURCE_TABLE}
        WHERE embedding IS NOT NULL
        """
    )
    document_count = cursor.fetchone()[0]

    if document_count < TOP_K:
        raise ValueError(
            f"At least {TOP_K} documents with embeddings are required; "
            f"found {document_count}."
        )

    cursor.execute(
        f"""
        CREATE TEMP TABLE phase8_exact AS
        SELECT * FROM {SOURCE_TABLE}
        WHERE embedding IS NOT NULL
        """
    )

    cursor.execute(
        """
        CREATE TEMP TABLE phase8_hnsw AS
        SELECT * FROM phase8_exact
        """
    )

    cursor.execute(
        """
        CREATE TEMP TABLE phase8_ivfflat AS
        SELECT * FROM phase8_exact
        """
    )

    cursor.execute(
        """
        CREATE INDEX phase8_hnsw_embedding_idx
        ON phase8_hnsw
        USING hnsw (embedding vector_cosine_ops)
        """
    )

    cursor.execute(
        f"""
        CREATE INDEX phase8_ivfflat_embedding_idx
        ON phase8_ivfflat
        USING ivfflat (embedding vector_cosine_ops)
        WITH (lists = {IVFFLAT_LISTS})
        """
    )

    cursor.execute("ANALYZE phase8_exact")
    cursor.execute("ANALYZE phase8_hnsw")
    cursor.execute("ANALYZE phase8_ivfflat")

    return document_count


# --------------------------------------------------
# Search configuration
# --------------------------------------------------

def configure_exact_search(cursor):
    """Encourage a sequential scan for the exact reference results."""

    cursor.execute("SET enable_indexscan = off")
    cursor.execute("SET enable_bitmapscan = off")
    cursor.execute("SET enable_seqscan = on")


def configure_hnsw_search(cursor):
    """Configure HNSW approximate search."""

    cursor.execute("SET enable_seqscan = off")
    cursor.execute("SET enable_indexscan = on")
    cursor.execute("SET enable_bitmapscan = off")
    cursor.execute(f"SET hnsw.ef_search = {HNSW_EF_SEARCH}")


def configure_ivfflat_search(cursor):
    """Configure IVFFlat approximate search."""

    cursor.execute("SET enable_seqscan = off")
    cursor.execute("SET enable_indexscan = on")
    cursor.execute("SET enable_bitmapscan = off")
    cursor.execute(f"SET ivfflat.probes = {IVFFLAT_PROBES}")

            
# --------------------------------------------------
# verify_search_plans
# --------------------------------------------------
def verify_search_plans(cursor, embedding):
    """Print query plans to confirm the intended search methods."""

    checks = [
        ("Exact search", configure_exact_search, "phase8_exact"),
        ("HNSW search", configure_hnsw_search, "phase8_hnsw"),
        ("IVFFlat search", configure_ivfflat_search, "phase8_ivfflat"),
    ]

    for label, configure, table_name in checks:
        configure(cursor)

        cursor.execute(
            f"""
            EXPLAIN
            SELECT id
            FROM {table_name}
            ORDER BY embedding <=> %s::vector
            LIMIT %s
            """,
            (embedding, TOP_K),
        )

        print(f"\n{label} query plan:")
        for row in cursor.fetchall():
            print(row[0])
            
# --------------------------------------------------
# Evaluate all queries
# --------------------------------------------------

def evaluate_queries(cursor, queries, model):
    """Compare approximate results with exact results per query."""

    results = []

    for item in queries:
        query_id = item["id"]
        query_text = item["query"]

        query_vector = model.encode(
            query_text,
            normalize_embeddings=False,
        )

        # Convert the embedding to pgvector's text representation.
        embedding = "[" + ",".join(
            str(float(value)) for value in query_vector
        ) + "]"
        
        if query_id == queries[0]["id"]:
             verify_search_plans(cursor, embedding)
        
        # Exact search is our reference for this query.
        configure_exact_search(cursor)
        exact_ids = fetch_ids(cursor, "phase8_exact", embedding)

        # HNSW approximate search.
        configure_hnsw_search(cursor)
        hnsw_ids = fetch_ids(cursor, "phase8_hnsw", embedding)

        # IVFFlat approximate search.
        configure_ivfflat_search(cursor)
        ivfflat_ids = fetch_ids(cursor, "phase8_ivfflat", embedding)

        hnsw_recall = calculate_recall(exact_ids, hnsw_ids)
        ivfflat_recall = calculate_recall(exact_ids, ivfflat_ids)

        results.append(
            {
                "id": query_id,
                "query": query_text,
                "hnsw_recall": hnsw_recall,
                "ivfflat_recall": ivfflat_recall,
                "exact_ids": exact_ids,
                "hnsw_ids": hnsw_ids,
                "ivfflat_ids": ivfflat_ids,
            }
        )

        print(f"\nQuery {query_id}: {query_text}")
        print(f"  Exact top-{TOP_K}:    {exact_ids}")
        print(f"  HNSW top-{TOP_K}:     {hnsw_ids}")
        print(f"  IVFFlat top-{TOP_K}:  {ivfflat_ids}")
        print(f"  HNSW Recall@{TOP_K}:    {hnsw_recall:.0%}")
        print(f"  IVFFlat Recall@{TOP_K}: {ivfflat_recall:.0%}")

    return results


# --------------------------------------------------
# Summary
# --------------------------------------------------

def print_summary(results):
    """Print average Recall@K across all evaluation queries."""

    average_hnsw = mean(
        result["hnsw_recall"] for result in results
    )

    average_ivfflat = mean(
        result["ivfflat_recall"] for result in results
    )

    print("\n" + "=" * 60)
    print("SEARCH QUALITY EVALUATION SUMMARY")
    print("=" * 60)
    print(f"Queries evaluated: {len(results)}")
    print(f"Top-K: {TOP_K}")
    print(f"HNSW ef_search: {HNSW_EF_SEARCH}")
    print(f"IVFFlat lists: {IVFFLAT_LISTS}")
    print(f"IVFFlat probes: {IVFFLAT_PROBES}")
    print(f"Average HNSW Recall@{TOP_K}:    {average_hnsw:.1%}")
    print(f"Average IVFFlat Recall@{TOP_K}: {average_ivfflat:.1%}")


def main():
    queries = load_queries()

    print(f"Loading embedding model: {MODEL_NAME}")
    model = SentenceTransformer(MODEL_NAME)

    with get_connection() as connection:
        with connection.cursor() as cursor:
            document_count = prepare_search_tables(cursor)

            print(f"\nDocuments evaluated: {document_count}")
            print(f"Evaluation queries: {len(queries)}")

            results = evaluate_queries(cursor, queries, model)
            print_summary(results)

    print("\nEvaluation completed.")


if __name__ == "__main__":
    main()