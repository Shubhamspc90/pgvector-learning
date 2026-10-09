import os

import psycopg
from dotenv import load_dotenv
from sentence_transformers import SentenceTransformer


# Load PostgreSQL configuration from .env
load_dotenv()


MODEL_NAME = "all-MiniLM-L6-v2"
QUERY = "artificial intelligence"
TOP_K = 5  # 5 nearest/relevant documents.


# Load the same embedding model used in Phase 5
model = SentenceTransformer(MODEL_NAME)


# Convert the search query into a 384-dimensional embedding
query_embedding = model.encode(QUERY)


# Connect to PostgreSQL
connection = psycopg.connect(
    host=os.getenv("POSTGRES_HOST"),
    port=os.getenv("POSTGRES_PORT"),
    dbname=os.getenv("POSTGRES_DB"),
    user=os.getenv("POSTGRES_USER"),
    password=os.getenv("POSTGRES_PASSWORD")
)


try:
    with connection.cursor() as cursor:  # A cursor allows Python to send SQL commands to PostgreSQL.

        # EXPLAIN ANALYZE executes the query and shows
        # how PostgreSQL performs the search.
        #
        # We are checking the baseline before creating
        # any vector index.
        cursor.execute(
            """
            EXPLAIN ANALYZE   
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
                TOP_K
            )
        )

        query_plan = cursor.fetchall()


        print("\nQuery Plan:\n")

        # Display PostgreSQL's execution plan
        for row in query_plan:
            print(row[0])


finally:
    # Close the database connection
    connection.close()