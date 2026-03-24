# 🧠 Genshin Lore RAG Assistant

### Local LLM + Retrieval-Augmented Generation Pipeline

An end-to-end Retrieval-Augmented Generation (RAG) system designed to answer lore-related questions about Genshin Impact using structured data and a local LLM.

This project focuses on building a robust, hallucination-aware AI system combining semantic search with grounded generation.

---

## 🚀 Project Overview

Large Language Models are powerful — but they hallucinate when lacking context.

This project solves that by:

- Structuring authoritative lore data via API  
- Embedding it into a semantic vector space  
- Retrieving relevant context  
- Injecting it into a local LLM  
- Enforcing grounded responses with source citation  

The result:

An AI assistant that answers questions strictly based on retrieved knowledge.

---

## 🏗️ Architecture

User Question  
↓  
Text Embedding (MiniLM)  
↓  
Cosine Similarity Search  
↓  
Top-k Relevant Sections  
↓  
Prompt Construction  
↓  
Local LLM (Llama 3.1)  
↓  
Grounded Answer + Citations  

---

## 🔬 Technical Components

### 📥 Data Ingestion

- MediaWiki API  
- Retrieval of 100+ lore entities  
- JSON parsing and normalization  
- Entity and section-level structuring  
- Cleaned and standardized dataset  

---

### 🧮 Semantic Embeddings

- Model: `all-MiniLM-L6-v2`  
- Framework: SentenceTransformers  
- Vector representation of text passages  
- Cosine similarity ranking  
- L2 normalization  

Concepts involved:

- Embedding space geometry  
- Vector similarity  
- Dot product  
- Cosine similarity  

---

### 🔎 Retrieval System

- Top-k similarity search  
- Boosting mechanism (entity + section weighting)  
- Ranked contextual selection  
- NumPy-based similarity optimization  

Goal:

Maximize relevant context while minimizing noise.

---

### 🧠 Generation (Local LLM)

- Model: Llama 3.1  
- Runtime: LM Studio  
- Structured prompt engineering  
- Controlled response format  

Key principle:

The model answers strictly using retrieved content.

---

### 🛑 Hallucination Control

- Strict context injection  
- Instruction-constrained prompting  
- Automatic citation of source sections  
- Grounded answer formatting  

This ensures transparency and traceability.

---

## 📦 Dependencies

### Core Language
- Python 3.10+

### Data Processing
- pandas
- numpy

### Embeddings & NLP
- sentence-transformers
- torch

### Similarity & Math
- scikit-learn (cosine similarity utilities)
- numpy (vector operations)

### LLM Runtime
- LM Studio (local inference server)
- Llama 3.1 (local model)

### API & Data Retrieval
- requests
- MediaWiki API

---

## 🛠️ Environment Setup

Install dependencies:

```bash
pip install pandas numpy sentence-transformers torch scikit-learn requests
```

---

## 📚 Core Concepts Explored

- Transformer embeddings  
- Vector similarity  
- Cosine similarity  
- Retrieval-Augmented Generation (RAG)  
- Context window management  
- Prompt engineering  
- Hallucination mitigation  
- Modular AI system design  

---

## 🚧 Future Improvements

- FAISS integration for scalable vector search  
- Hybrid retrieval (BM25 + embeddings)  
- Retrieval evaluation metrics  
- Web deployment (FastAPI + frontend)  
- Conversation memory handling  

---
