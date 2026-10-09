import os

import psycopg
from dotenv import load_dotenv
from sentence_transformers import SentenceTransformer


load_dotenv()

MODEL_NAME = "all-MiniLM-L6-v2"
TOTAL_DOCUMENTS = 5000
BATCH_SIZE = 100

# Load the embedding model
model = SentenceTransformer(MODEL_NAME)

# Connect using the project's PostgreSQL configuration
connection = psycopg.connect(
    host=os.getenv("POSTGRES_HOST"),
    port=os.getenv("POSTGRES_PORT"),
    dbname=os.getenv("POSTGRES_DB"),
    user=os.getenv("POSTGRES_USER"),
    password=os.getenv("POSTGRES_PASSWORD"),
)

try:
    with connection.cursor() as cursor:
        for start in range(0, TOTAL_DOCUMENTS, BATCH_SIZE):
            end = min(start + BATCH_SIZE, TOTAL_DOCUMENTS)

            # Generate varied text for the benchmark dataset
            documents = [
                (
                    f"Benchmark document {i}: "
                    f"This document discusses topic {i % 20}, "
                    f"including artificial intelligence, data processing, "
                    f"software engineering, and information retrieval."
                )
                for i in range(start + 1, end + 1)
            ]

            # Convert each document into a 384-dimensional embedding
            embeddings = model.encode(
                documents,
                batch_size=32,
                show_progress_bar=False,
            )

            # Insert each document and its embedding
            cursor.executemany(
                """
                INSERT INTO semantic_documents_benchmark
                    (content, embedding)
                VALUES (%s, %s::vector)
                """,
                [
                    (content, embedding.tolist())
                    for content, embedding in zip(documents, embeddings)
                ],
            )

            connection.commit()
            print(f"Inserted {end}/{TOTAL_DOCUMENTS} documents")

    print("Benchmark dataset created successfully.")

finally:
    connection.close()
