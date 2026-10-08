-- Create a table to store documents and their embeddings

CREATE TABLE semantic_documents (
    id SERIAL PRIMARY KEY,
    content TEXT NOT NULL,
    embedding vector(384) NOT NULL
);