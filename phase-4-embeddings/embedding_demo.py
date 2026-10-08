from sentence_transformers import SentenceTransformer


# Load the embedding model
model = SentenceTransformer("all-MiniLM-L6-v2")


# ---------------------------------------------------------
# Example 1: Generate embedding for a single sentence
# ---------------------------------------------------------

text = "I love programming"

embedding = model.encode(text)

print("Text:", text)
print("Embedding:", embedding)
print("Number of dimensions:", len(embedding))


# ---------------------------------------------------------
# Example 2: Generate embeddings for multiple sentences
# ---------------------------------------------------------

sentences = [
    "I love programming",
    "I enjoy coding",
    "The weather is very hot today"
]

embeddings = model.encode(sentences)

for sentence, embedding in zip(sentences, embeddings):
    print("\nText:", sentence)
    print("Dimensions:", len(embedding))