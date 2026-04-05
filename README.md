# Multi-Agent RAG System with Streamlit UI

## Overview

This project is a multi-agent system where I combine RAG + Text-to-SQL + an orchestrator agent.

The main idea is that instead of using a simple pipeline, I use one main agent that decides what to do with the question:

- use RAG (search in documents)
- use SQL (query PostgreSQL)
- or just answer directly

---

## How the system works

### Main Agent (Orchestrator)

There is one main agent that receives the user question and decides:

- if the question is about documents → it uses RAG
- if the question is about structured data → it uses SQL subagent
- otherwise → it answers directly

---

### RAG System

- documents are uploaded by the user
- they are split into chunks
- embeddings are created
- stored in Qdrant

I use hybrid search (semantic + keyword), so retrieval is better than simple vector search.

---

### SQL Subagent

- takes natural language question
- converts it into SQL
- runs it on PostgreSQL
- returns the result

---

### Chat History

- stored in MongoDB
- every conversation has a session_id
- allows to continue chat with context

---

## Tech Stack

- FastAPI (backend)
- Streamlit (UI)
- DeepSeek (LLM)
- Qdrant (vector DB)
- PostgreSQL (SQL)
- MongoDB (chat history)
- LangChain (agents + tools)
- Docker Compose (databases)

---

## Features

### Chat with agent
- uses only `/rag_agent`
- not using naive RAG in UI
- agent decides what to use

### File upload
- upload PDF / TXT / CSV / DOCX
- files are indexed and used in RAG

### SQL queries
- ask questions about PostgreSQL
- agent automatically uses SQL

### Hybrid search
- vector + keyword search

### Chat history
- sessions stored in MongoDB
- can view and delete sessions

---

## API Endpoints

Available in Swagger:

- `/rag_agent` → main agent
- `/query` → naive RAG (not used in UI)
- `/upload` → upload documents
- `/documents` → list documents
- `/messages/grouped` → chat history
- `/sessions/{session_id}` → delete session
- `/health` → system status

Swagger:
http://localhost:8000/docs

---

## Databases

This project requires 3 databases:

- Qdrant → for RAG
- MongoDB → for chat history
- PostgreSQL → for SQL queries

All of them are started with Docker Compose.

---

## How to run

### 1. Start databases

```bash
docker-compose up -d   

uvicorn api:app --reload

streamlit run streamlit_app.py