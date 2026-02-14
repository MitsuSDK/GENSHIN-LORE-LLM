import json
import numpy as np
import requests
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
import os
from dotenv import load_dotenv

# Load data

with open("rag-data/chunks.json", "r", encoding="utf-8") as f:
    chunks = json.load(f)

embeddings = np.load("rag-data/embeddings.npy")

model = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")
load_dotenv()
LM_STUDIO_URL = os.getenv("LM_STUDIO_URL", "http://localhost:1234/v1/chat/completions")


# Retrieval

def search(query, top_k=5):
    query_embedding = model.encode([query])
    similarities = cosine_similarity(query_embedding, embeddings)[0]
    top_indices = similarities.argsort()[-top_k:][::-1]

    results = []
    for idx in top_indices:
        results.append({
            "score": float(similarities[idx]),
            "character": chunks[idx]["character"],
            "section": chunks[idx]["section"],
            "text": chunks[idx]["text"]
        })

    return results


# Prompt Builder

def build_prompt(query, retrieved_chunks):
    context_text = ""

    for i, chunk in enumerate(retrieved_chunks):
        context_text += f"""
Source {i+1}:
Character: {chunk['character']}
Section: {chunk['section']}
Text:
{chunk['text']}
---
"""

    prompt = f"""
You are a Genshin Impact Lore Assistant.

Rules:
- ONLY use the provided context.
- DO NOT invent information.
- If the answer is not contained in the context, say:
  "The answer is not found in the provided lore."
- Always cite your sources using this format:
  (Character - Section)

Context:
{context_text}

Question:
{query}

Provide a clear, structured answer.
"""

    return prompt


# LLM Call

def generate_answer(prompt):
    payload = {
        "model": "local-model",
        "messages": [
            {"role": "system", "content": "You are a precise and reliable lore assistant."},
            {"role": "user", "content": prompt}
        ],
        "temperature": 0.2
    }

    response = requests.post(LM_STUDIO_URL, json=payload)
    result = response.json()

    return result["choices"][0]["message"]["content"]


# Main

if __name__ == "__main__":
    query = input("Ask something about Genshin lore: ")

    retrieved = search(query, top_k=5)
    prompt = build_prompt(query, retrieved)

    answer = generate_answer(prompt)

    print("\n===== ANSWER =====\n")
    print(answer)