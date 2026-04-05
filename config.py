import os
from dotenv import load_dotenv

load_dotenv()


class Config:
    DEEPSEEK_API_KEY = os.getenv("API_KEY") or os.getenv("DEEPSEEK_API_KEY", "")

    MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017")
    MONGO_DB_NAME = os.getenv("MONGO_DB_NAME", "rag_chat_db")


    POSTGRES_HOST = os.getenv("POSTGRES_HOST", "localhost")
    POSTGRES_PORT = int(os.getenv("POSTGRES_PORT", 5432))
    POSTGRES_DB = os.getenv("POSTGRES_DB", "postgres")
    POSTGRES_USER = os.getenv("POSTGRES_USER", "postgres")
    POSTGRES_PASSWORD = os.getenv("POSTGRES_PASSWORD", "postgres")



    class Embeddings:
        MODEL_NAME = os.getenv("EMBEDDING_MODEL", "BAAI/bge-small-en-v1.5")

    class DeepSeek:
        API_KEY = os.getenv("DEEPSEEK_API_KEY", "")
        MODEL_NAME = os.getenv("DEEPSEEK_MODEL", "deepseek-chat")
        TEMPERATURE = float(os.getenv("DEEPSEEK_TEMPERATURE", 0.2))
        MAX_TOKENS = int(os.getenv("DEEPSEEK_MAX_TOKENS", 1024))

    class Document:
        CHUNK_SIZE = int(os.getenv("CHUNK_SIZE", 1000))
        CHUNK_OVERLAP = int(os.getenv("CHUNK_OVERLAP", 200))

    class RAG:
        TOP_K_RESULTS = int(os.getenv("TOP_K_RESULTS", 5))




RAG_PROMPT_TEMPLATE = """
You are a helpful RAG assistant.

Use the provided context to answer the user's question.
If the answer is not in the context, say that the information was not found in the documents.

Context:
{context}

Question:
{question}

Answer:
"""