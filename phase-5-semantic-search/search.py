import os

import psycopg
from dotenv import load_dotenv
from sentence_transformers import SentenceTransformer


# Load database configuration from .env
load_dotenv()


MODEL_NAME = "all-MiniLM-L6-v2"
DEFAULT_TOP_K = 5
DEFAULT_SIMILARITY_THRESHOLD = 0.0


def get_search_input():
    """Get and validate search parameters."""

    # Get user's search query
    query = input("Enter your search query: ").strip()

    if not query:
        raise ValueError("Search query cannot be empty.")

    # Get number of results
    top_k_input = input(
        f"Enter number of results (default: {DEFAULT_TOP_K}): "
    ).strip()

    top_k = int(top_k_input) if top_k_input else DEFAULT_TOP_K

    if top_k <= 0:
        raise ValueError("Top-K must be greater than 0.")

    # Get minimum similarity required for results
    threshold_input = input(
        f"Enter minimum similarity "
        f"(default: {DEFAULT_SIMILARITY_THRESHOLD}): "
    ).strip()

    similarity_threshold = (
        float(threshold_input)
        if threshold_input
        else DEFAULT_SIMILARITY_THRESHOLD
    )

    if not 0 <= similarity_threshold <= 1:
        raise ValueError(
            "Similarity threshold must be between 0 and 1."
        )

    return query, top_k, similarity_threshold


def semantic_search(model, query, top_k):
    """Generate query embedding and search PostgreSQL."""

    # Convert the query into a 384-dimensional embedding
    query_embedding = model.encode(query)

    connection = psycopg.connect(
        host=os.getenv("POSTGRES_HOST"),
        port=os.getenv("POSTGRES_PORT"),
        dbname=os.getenv("POSTGRES_DB"),
        user=os.getenv("POSTGRES_USER"),
        password=os.getenv("POSTGRES_PASSWORD")
    )

    try:
        with connection.cursor() as cursor:

            # <=> calculates cosine distance
            cursor.execute(
                """
                SELECT
                    id,
                    content,
                    embedding <=> %s::vector AS distance
                FROM semantic_documents
                ORDER BY embedding <=> %s::vector
                LIMIT %s
                """,
                (
                    query_embedding.tolist(),
                    query_embedding.tolist(),
                    top_k
                )
            )

            return cursor.fetchall()

    finally:
        connection.close()


def display_results(query, results, similarity_threshold):
    """Filter and display search results."""

    print(f"\nSearch Query: {query}")
    print(f"Similarity Threshold: {similarity_threshold:.2f}")
    print("Results:\n")

    rank = 1

    for document_id, content, distance in results:

        # Convert cosine distance into similarity
        similarity = 1 - distance

        if similarity >= similarity_threshold:
            print(f"{rank}. {content}")
            print(f"   Distance: {distance:.4f}")
            print(f"   Similarity: {similarity:.4f}\n")

            rank += 1

    if rank == 1:
        print("No sufficiently similar results found.")


def main():
    """Run the semantic search application."""

    try:
        query, top_k, similarity_threshold = get_search_input()

        # Load embedding model
        model = SentenceTransformer(MODEL_NAME)

        # Search documents using pgvector
        results = semantic_search(model, query, top_k)

        # Filter and display results
        display_results(
            query,
            results,
            similarity_threshold
        )

    except ValueError as error:
        print(f"Input error: {error}")

    except Exception as error:
        print(f"Error: {error}")


if __name__ == "__main__":
    main()