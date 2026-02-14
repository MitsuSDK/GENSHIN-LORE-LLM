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

    query_lower = query.lower()
    query_words = set(query_lower.split())

    scored_results = []

    for idx, base_score in enumerate(similarities):
        base_score = float(base_score)

        # Ignore very weak semantic matches early
        if base_score < 0.30:
            continue

        chunk = chunks[idx]
        score = base_score

        # --- Character name boost ---
        if chunk["character"].lower() in query_lower:
            score += 0.15

        # --- Section priority boost ---
        section = chunk["section"]
        if "Character Story" in section:
            score += 0.07
        elif "Character Details" in section:
            score += 0.05
        elif "description" in section.lower():
            score += 0.02

        # --- Keyword overlap boost ---
        chunk_text_lower = chunk["text"].lower()
        overlap = sum(1 for word in query_words if word in chunk_text_lower)
        score += overlap * 0.01

        scored_results.append((score, idx))

    # Sort after all boosts applied
    scored_results.sort(reverse=True, key=lambda x: x[0])

    results = []
    seen_texts = set()

    for score, idx in scored_results:
        if score < 0.40:
            continue

        chunk = chunks[idx]
        text = chunk["text"]

        # Deduplicate similar chunks
        text_key = text[:200]
        if text_key in seen_texts:
            continue
        seen_texts.add(text_key)

        results.append({
            "score": score,
            "character": chunk["character"],
            "section": chunk["section"],
            "text": text
        })

        if len(results) >= top_k:
            break

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
    if not retrieved or retrieved[0]["score"] < 0.45:
        print("\nThe answer is not found in the lore database.")
        exit()
    prompt = build_prompt(query, retrieved)

    answer = generate_answer(prompt)

    print("\n===== ANSWER =====\n")
    print(answer)