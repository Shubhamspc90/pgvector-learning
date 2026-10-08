import os

import psycopg
from dotenv import load_dotenv
from sentence_transformers import SentenceTransformer


# Load database configuration from .env
load_dotenv()


MODEL_NAME = "all-MiniLM-L6-v2"


# Documents for semantic search
documents = [
    "I love programming",
    "I enjoy writing code",
    "Python is a popular programming language",
    "Software development requires problem solving",
    "Machine learning is a branch of artificial intelligence",
    "Deep learning uses neural networks",
    "The weather is very hot today",
    "It is raining heavily outside",
    "I enjoy playing football",
    "Cricket is my favorite sport"
]


# Load the embedding model
model = SentenceTransformer(MODEL_NAME)


# Generate embeddings for all documents
embeddings = model.encode(documents)


# Connect to PostgreSQL
connection = psycopg.connect(
    host=os.getenv("POSTGRES_HOST"),
    port=os.getenv("POSTGRES_PORT"),
    dbname=os.getenv("POSTGRES_DB"),
    user=os.getenv("POSTGRES_USER"),
    password=os.getenv("POSTGRES_PASSWORD")
)


# Insert documents and embeddings
inserted_count = 0

with connection.cursor() as cursor:
    for document, embedding in zip(documents, embeddings):

        cursor.execute(
            """
            INSERT INTO semantic_documents (content, embedding)
            VALUES (%s, %s)
            ON CONFLICT (content) DO NOTHING
            """,
            (document, embedding.tolist())
        )

        if cursor.rowcount == 1:
            inserted_count += 1


connection.commit()
connection.close()


print(f"Successfully inserted {inserted_count} new documents.")