import os
from pathlib import Path

from dotenv import load_dotenv
from langchain.agents import create_agent
from langchain_deepseek import ChatDeepSeek

from RAG_AGENT.tools import rag_search
from src.chat_history import MongoChatHistory
from config import Config


env_path = Path(__file__).resolve().parents[1] / ".env"
load_dotenv(dotenv_path=env_path, override=True)


chat_history_store = MongoChatHistory(
    mongo_uri=Config.MONGO_URI,
    db_name=Config.MONGO_DB_NAME
)


def build_agent():
    api_key = Config.DEEPSEEK_API_KEY
    if not api_key:
        raise ValueError("DeepSeek API key is not found in .env")

    llm = ChatDeepSeek(
        model="deepseek-chat",
        api_key=api_key,
        temperature=0.2,
        max_tokens=1024,
    )

    agent = create_agent(
        model=llm,
        tools=[rag_search],
        system_prompt=(
            "You are a helpful RAG agent. "
            "Use the rag_search tool when the user asks about uploaded or indexed documents. "
            "If you use the tool, base your answer on the retrieved chunks. "
            "If no relevant context is found, say that the knowledge base did not return enough information. "
            "Do not invent facts that are not supported by the retrieved context."
        ),
    )
    return agent


agent = build_agent()


def run_agentic_rag(question: str, session_id: str | None = None):
    session_id = chat_history_store.ensure_session(session_id)

    chat_history_store.add_message(
        session_id=session_id,
        role="user",
        content=question,
        meta={"mode": "agentic_rag"}
    )

    history_messages = chat_history_store.get_messages(session_id=session_id, limit=10)

    previous_messages = history_messages[:-1] if len(history_messages) > 1 else []

    history_text = "\n".join(
        f"{msg['role'].capitalize()}: {msg['content']}"
        for msg in previous_messages
    )

    user_prompt = (
        
    "You MUST use the conversation history to answer the question.\n\n"
    f"Conversation history:\n{history_text}\n\n"
    f"User question:\n{question}\n\n"
    "If the answer depends on previous messages, use them."
)
    

    result = agent.invoke({
        "messages": [
            {
                "role": "user",
                "content": user_prompt
            }
        ]
    })

    answer = None

    if isinstance(result, dict):
        if "output" in result:
            answer = result["output"]
        elif "messages" in result and result["messages"]:
            last_message = result["messages"][-1]
            answer = getattr(last_message, "content", str(last_message))

    if not answer:
        answer = str(result)

    chat_history_store.add_message(
        session_id=session_id,
        role="assistant",
        content=answer,
        meta={"mode": "agentic_rag"}
    )

    return {
        "session_id": session_id,
        "question": question,
        "answer": answer,
        "success": True
    }