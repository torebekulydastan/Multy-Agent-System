from langchain_core.tools import tool
from src.rag_engine import RAGEngine
import logging
from RAG_AGENT.sql_subagent import ask_sql_subagent

logger = logging.getLogger(__name__)


rag_engine = RAGEngine()


@tool
def rag_search(query: str, k: int = 5) -> list:
    """
    Search relevant documents from the knowledge base.

    Args:
        query (str): user question
        k (int): number of documents to retrieve

    Returns:
        list: list of relevant document chunks with text, score, metadata
    """
    try:
        relevant_docs = rag_engine.retrive_relevan_documents(query, k)

        if not relevant_docs:
            logger.warning("No relevant documents found")
            return []

        # делаем удобный формат для агента (очень важно)
        results = []
        for doc in relevant_docs:
            results.append({
                "text": doc.get("text", ""),
                "score": doc.get("score", 0),
                "metadata": doc.get("metadata", {})
            })

        logger.info(f"Found {len(results)} relevant documents")
        return results

    except Exception as e:
        logger.error(f"Error in rag_search tool: {e}")
        return []


@tool
def sql_subagent_tool(question: str) -> str:
    """
    Use the SQL subagent to answer questions that require PostgreSQL data.
    """
    try:
        return ask_sql_subagent(question)
    except Exception as e:
        logger.error(f"Error in sql_subagent_tool: {e}")
        return f"SQL subagent error: {str(e)}"