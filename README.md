# 🎮 Genshin Lore Assistant (RAG + Local LLM)

A structured Lore Assistant built using Retrieval-Augmented Generation (RAG).

The system answers questions about Genshin Impact characters using only retrieved lore data — no hallucinated answers.

---

## 🚀 What It Does

- Fetches character data from the Genshin Wiki
- Cleans and structures lore sections
- Chunks text for retrieval
- Embeds chunks using sentence-transformers
- Stores embeddings in a vector index
- Uses a local LLM (LM Studio) to generate answers
- Restricts responses to retrieved context only

---

## 🧠 Architecture

User Question  
→ Embed question  
→ Retrieve top-k relevant lore chunks  
→ Inject chunks into prompt  
→ Local LLM generates answer  
→ Structured output with character + section citation  

---

## 🔒 Hallucination Control

The model is explicitly instructed to:

- Only answer using retrieved content
- Refuse if information is missing
- Cite character and section
- Avoid inventing lore

This ensures factual consistency.

---

## 🛠️ Tech Stack

- Python
- requests (wiki scraping)
- BeautifulSoup (HTML parsing)
- sentence-transformers
- numpy
- cosin similarity
- LM Studio (local LLM inference)
- Dolphin / LLaMA 3.1 8B (local model)

---

## 🛠️ Environment Setup

Install dependencies:

```bash
pip install pandas numpy sentence-transformers torch scikit-learn requests
```

---

## 📂 Key Components

- `fetch_character.py` → Scrapes and structures lore
- `build_embeddings.py` → Creates chunk embeddings
- `rag_pipeline.py` → Retrieval + generation
- Local vector index for similarity search

---

## 🎯 Why This Project

This project demonstrates:

- RAG architecture implementation
- Prompt control for hallucination reduction
- Local LLM deployment
- Vector search integration
- Structured answer formatting
- End-to-end AI system design

It focuses on building a reliable knowledge assistant rather than a generic chatbot.
