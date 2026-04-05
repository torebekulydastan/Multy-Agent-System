from typing import List, Dict, Any
import logging

from sqlalchemy import create_engine, text
from sqlalchemy.engine import Engine

from config import Config

logger = logging.getLogger(__name__)


class PostgresManager:
    def __init__(self):
        self.connection_url = (
            f"postgresql+psycopg2://{Config.POSTGRES_USER}:"
            f"{Config.POSTGRES_PASSWORD}@{Config.POSTGRES_HOST}:"
            f"{Config.POSTGRES_PORT}/{Config.POSTGRES_DB}"
        )
        self.engine: Engine = create_engine(self.connection_url, pool_pre_ping=True)

    def test_connection(self) -> bool:
        try:
            with self.engine.connect() as conn:
                conn.execute(text("SELECT 1"))
            return True
        except Exception as e:
            logger.error(f"Postgres connection failed: {e}")
            return False

    def get_schema_info(self) -> str:
        query = """
        SELECT
            table_name,
            column_name,
            data_type
        FROM information_schema.columns
        WHERE table_schema = 'public'
        ORDER BY table_name, ordinal_position;
        """

        try:
            with self.engine.connect() as conn:
                rows = conn.execute(text(query)).mappings().all()

            if not rows:
                return "No tables found in public schema."

            grouped = {}
            for row in rows:
                table = row["table_name"]
                col = row["column_name"]
                dtype = row["data_type"]
                grouped.setdefault(table, []).append(f"{col} ({dtype})")

            lines = []
            for table_name, cols in grouped.items():
                lines.append(f"Table: {table_name}")
                for c in cols:
                    lines.append(f"  - {c}")

            return "\n".join(lines)

        except Exception as e:
            logger.error(f"Failed to get schema info: {e}")
            return f"Error reading schema: {e}"

    def run_select_query(self, sql: str, limit: int = 50) -> List[Dict[str, Any]]:
        sql_clean = sql.strip().rstrip(";")

        forbidden = ["insert ", "update ", "delete ", "drop ", "alter ", "truncate ", "create "]
        lowered = sql_clean.lower()

        if any(word in lowered for word in forbidden):
            raise ValueError("Only read-only SELECT queries are allowed.")

        if not lowered.startswith("select"):
            raise ValueError("Only SELECT queries are allowed.")

        wrapped_sql = f"SELECT * FROM ({sql_clean}) AS subquery LIMIT :limit_value"

        with self.engine.connect() as conn:
            result = conn.execute(text(wrapped_sql), {"limit_value": limit})
            rows = result.mappings().all()

        return [dict(row) for row in rows]