from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity


model = SentenceTransformer("all-MiniLM-L6-v2")


sentences = [
    "I love programming",
    "I enjoy coding",
    "The weather is very hot today"
]


embeddings = model.encode(sentences)


similarity_1 = cosine_similarity(
    [embeddings[0]],
    [embeddings[1]]
)[0][0]

similarity_2 = cosine_similarity(
    [embeddings[0]],
    [embeddings[2]]
)[0][0]


print("Similarity between:")
print(f"'{sentences[0]}'")
print(f"'{sentences[1]}'")
print("=", similarity_1)


print("\nSimilarity between:")
print(f"'{sentences[0]}'")
print(f"'{sentences[2]}'")
print("=", similarity_2)