-- Create a table to store text and its embedding vector

CREATE TABLE embedding_examples (
    id SERIAL PRIMARY KEY,
    text TEXT NOT NULL,
    embedding vector(384)
);