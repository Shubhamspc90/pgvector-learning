import os

import psycopg
from dotenv import load_dotenv
from sentence_transformers import SentenceTransformer


# Load PostgreSQL configuration from the .env file
load_dotenv()


MODEL_NAME = "all-MiniLM-L6-v2"
QUERY = "machine learning and artificial intelligence"
TOP_K = 5


# Load the embedding model and convert the query into a vector
model = SentenceTransformer(MODEL_NAME)
query_embedding = model.encode(QUERY).tolist()


# Connect to PostgreSQL using environment variables
connection = psycopg.connect(
    host=os.getenv("POSTGRES_HOST"),
    port=os.getenv("POSTGRES_PORT"),
    dbname=os.getenv("POSTGRES_DB"),
    user=os.getenv("POSTGRES_USER"),
    password=os.getenv("POSTGRES_PASSWORD"),
)


try:
    with connection.cursor() as cursor:
        cursor.execute("SET enable_seqscan = off")
        # Display the execution plan for vector similarity search.
        # The ORDER BY expression matches the cosine HNSW index.
        cursor.execute(
            """
            EXPLAIN ANALYZE
            SELECT
                id,
                content,
                embedding <=> %s::vector AS distance
            FROM semantic_documents
            ORDER BY embedding <=> %s::vector
            LIMIT %s;
            """,
            (
                query_embedding,
                query_embedding,
                TOP_K,
            ),
        )

        query_plan = cursor.fetchall()

        print("\nHNSW Search Query Plan:\n")

        # Print each line of PostgreSQL's execution plan
        for row in query_plan:
            print(row[0])

finally:
    # Always close the database connection
    connection.close()
