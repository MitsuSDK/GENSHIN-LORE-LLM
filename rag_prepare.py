import os
import json

from sentence_transformers import SentenceTransformer
import numpy as np

RAG_DATA_FOLDER = "rag-data"

CHARACTER_FOLDER = "lore-data/characters"

def load_character_files():
    characters = []

    for filename in os.listdir(CHARACTER_FOLDER):
        if filename.endswith(".json"):
            path = os.path.join(CHARACTER_FOLDER, filename)

            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)
                characters.append(data)

    return characters

def create_chunks(characters):
    chunks = []

    for character in characters:
        name = character["name"]

        # Descriptions
        for desc in character["lore"]["descriptions"]:
            chunks.append({
                "character": name,
                "section": "description",
                "text": desc
            })

        # Character stories
        for story in character["lore"]["character_stories"]:
            chunks.append({
                "character": name,
                "section": story["title"],
                "text": story["text"]
            })

        # Additional lore (voice overs)
        for extra in character["lore"]["additional_lore"]:
            chunks.append({
                "character": name,
                "section": extra["title"],
                "text": extra["text"]
            })

    return chunks


# 2) Add save_chunks function
def save_chunks(chunks):
    os.makedirs(RAG_DATA_FOLDER, exist_ok=True)
    path = os.path.join(RAG_DATA_FOLDER, "chunks.json")

    with open(path, "w", encoding="utf-8") as f:
        json.dump(chunks, f, ensure_ascii=False, indent=2)

    print(f"Chunks saved to {path}")


# 3) Add generate_embeddings function
def generate_embeddings(chunks):
    print("Loading embedding model...")
    model = SentenceTransformer("all-MiniLM-L6-v2")

    texts = [chunk["text"] for chunk in chunks]

    print("Generating embeddings...")
    embeddings = model.encode(texts, show_progress_bar=True)

    path = os.path.join(RAG_DATA_FOLDER, "embeddings.npy")
    np.save(path, embeddings)

    print(f"Embeddings saved to {path}")

if __name__ == "__main__":
    characters = load_character_files()
    chunks = create_chunks(characters)

    print(f"Total characters loaded: {len(characters)}")
    print(f"Total chunks created: {len(chunks)}\n")

    save_chunks(chunks)
    generate_embeddings(chunks)