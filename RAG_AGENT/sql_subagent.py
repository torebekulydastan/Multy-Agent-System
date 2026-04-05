from pathlib import Path
from dotenv import load_dotenv
from langchain.agents import create_agent
from langchain_core.tools import tool
from langchain_deepseek import ChatDeepSeek

from config import Config
from src.sql_database import PostgresManager
from RAG_AGENT.prompts import SQL_SUBAGENT_SYSTEM_PROMPT


env_path = Path(__file__).resolve().parents[1] / ".env"
load_dotenv(dotenv_path=env_path, override=True)

postgres_manager = PostgresManager()


@tool
def get_postgres_schema() -> str:
    """
    Return PostgreSQL public schema tables and columns.
    """
    return postgres_manager.get_schema_info()


@tool
def run_postgres_select(sql: str) -> list:
    """
    Execute a read-only PostgreSQL SELECT query and return rows.
    """
    return postgres_manager.run_select_query(sql)


def build_sql_subagent():
    api_key = Config.DEEPSEEK_API_KEY
    if not api_key:
        raise ValueError("DeepSeek API key is not found in .env")

    llm = ChatDeepSeek(
        model="deepseek-chat",
        api_key=api_key,
        temperature=0.0,
        max_tokens=1024,
    )

    agent = create_agent(
        model=llm,
        tools=[get_postgres_schema, run_postgres_select],
        system_prompt=SQL_SUBAGENT_SYSTEM_PROMPT,
    )
    return agent


sql_subagent = build_sql_subagent()


def ask_sql_subagent(question: str) -> str:
    result = sql_subagent.invoke({
        "messages": [
            {
                "role": "user",
                "content": question
            }
        ]
    })

    if isinstance(result, dict):
        if "output" in result:
            return result["output"]

        if "messages" in result and result["messages"]:
            last_message = result["messages"][-1]
            return getattr(last_message, "content", str(last_message))

    return str(result)