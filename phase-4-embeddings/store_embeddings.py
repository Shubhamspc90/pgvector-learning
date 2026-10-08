import os

import psycopg
from dotenv import load_dotenv
from sentence_transformers import SentenceTransformer


# Load environment variables from .env
load_dotenv()


# Load embedding model
model = SentenceTransformer("all-MiniLM-L6-v2")


# Text to embed
text = "I love programming"


# Generate embedding
embedding = model.encode(text)


# Connect to PostgreSQL
connection = psycopg.connect(
    host=os.getenv("POSTGRES_HOST"),
    port=os.getenv("POSTGRES_PORT"),
    dbname=os.getenv("POSTGRES_DB"),
    user=os.getenv("POSTGRES_USER"),
    password=os.getenv("POSTGRES_PASSWORD")
)


# Insert text and embedding
with connection.cursor() as cursor:
    cursor.execute(
        """
        INSERT INTO embedding_examples (text, embedding)
        VALUES (%s, %s)
        """,
        (text, embedding.tolist())
    )


connection.commit()
connection.close()

print("Embedding stored successfully.")