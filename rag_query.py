import json
import numpy as np
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity

# Load chunks
with open("rag-data/chunks.json", "r", encoding="utf-8") as f:
    chunks = json.load(f)

# Load embeddings
embeddings = np.load("rag-data/embeddings.npy")

# Load embedding model
model = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")


def search(query, top_k=5):
    # Encode the query
    query_embedding = model.encode([query])

    # Compute cosine similarity
    similarities = cosine_similarity(query_embedding, embeddings)[0]

    # Get top matches
    top_indices = similarities.argsort()[-top_k:][::-1]

    results = []
    for idx in top_indices:
        results.append({
            "score": similarities[idx],
            "character": chunks[idx]["character"],
            "section": chunks[idx]["section"],
            "text": chunks[idx]["text"]
        })

    return results


if __name__ == "__main__":
    query = input("Ask something about Genshin lore: ")

    results = search(query)

    print("\nTop Results:\n")
    for r in results:
        print(f"[{r['character']} - {r['section']}] (score: {r['score']:.3f})")
        print(r["text"][:300])
        print("-" * 60)