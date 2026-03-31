# RAG System (FastAPI + Qdrant + DeepSeek)

## Overview

This project is a simple RAG (Retrieval-Augmented Generation) system.
It allows uploading documents and asking questions based on their content.

The idea is:

* upload a file
* split it into chunks
* store embeddings in Qdrant
* retrieve relevant parts
* send them to DeepSeek to generate the answer

---

## Features

* Supports multiple file types:

  * PDF
  * TXT
  * DOC/DOCX
  * CSV

* Basic RAG pipeline:

  * document parsing
  * chunking
  * embeddings
  * vector search
  * answer generation

* Uses DeepSeek API as LLM

* FastAPI backend with several endpoints

* Qdrant is used as vector database (runs in Docker)

---

## Project Structure

```
.
├── src/
│   ├── doc_proc.py
│   ├── embeddings.py
│   ├── rag_engine.py
│   └── vectorstore.py
│
├── uploads/
├── api.py
├── config.py
├── compose.yml
├── requirements.txt
└── README.md
```

---

## API Endpoints

* `POST /upload` → upload a file
* `POST /ask` → ask a question
* `GET /health` → check if system works
* `DELETE /delete` → delete documents
* `/docs` → Swagger UI

---

## Installation

Clone repo:

```
git clone https://github.com/your-username/your-repo.git
cd your-repo
```

Install dependencies:

```
pip install -r requirements.txt
```

Create `.env` file:

```
DEEPSEEK_API_KEY=your_api_key
```

Run Qdrant (Docker required):

```
docker-compose up -d
```

Run API:

```
uvicorn api:app --reload
```

---

## How it works

1. User uploads a file
2. File is processed and split into chunks
3. Each chunk is converted into embeddings
4. Embeddings are stored in Qdrant
5. User asks a question
6. Relevant chunks are retrieved
7. Context + question → sent to DeepSeek
8. Answer is returned

---

## Example

Request:

```json
{
  "query": "What is this document about?"
}
```

---

## Tech Stack

* FastAPI
* Qdrant
* DeepSeek API
* Docker
* Python

---

## Notes

* Make sure Docker is running before starting Qdrant
* DeepSeek API key is required
* Large files may take some time to process

---

## Future improvements

* better retrieval (hybrid search)
* streaming responses
* caching
* background tasks

---
