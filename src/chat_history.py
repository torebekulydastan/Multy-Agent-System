from datetime import datetime, timezone
from typing import Optional, List, Dict
import uuid

from pymongo import MongoClient, ASCENDING, DESCENDING


class MongoChatHistory:
    def __init__(
        self,
        mongo_uri: str,
        db_name: str = "rag_chat_db",
        sessions_collection: str = "chat_sessions",
        messages_collection: str = "chat_messages",
    ):
        self.client = MongoClient(mongo_uri)
        self.db = self.client[db_name]

        self.sessions = self.db[sessions_collection]
        self.messages = self.db[messages_collection]

        self._create_indexes()

    def _create_indexes(self):
        self.sessions.create_index([("updated_at", DESCENDING)])
        self.messages.create_index([("session_id", ASCENDING), ("created_at", ASCENDING)])

    def create_session(self, title: Optional[str] = None) -> str:
        session_id = str(uuid.uuid4())
        now = datetime.now(timezone.utc)

        self.sessions.insert_one({
            "_id": session_id,
            "title": title or "New Chat",
            "created_at": now,
            "updated_at": now,
        })
        return session_id

    def session_exists(self, session_id: str) -> bool:
        return self.sessions.find_one({"_id": session_id}) is not None

    def ensure_session(self, session_id: Optional[str] = None, title: Optional[str] = None) -> str:
        if session_id and self.session_exists(session_id):
            return session_id
        return self.create_session(title=title)

    def add_message(
        self,
        session_id: str,
        role: str,
        content: str,
        meta: Optional[Dict] = None,
    ) -> str:
        message_id = str(uuid.uuid4())
        now = datetime.now(timezone.utc)

        self.messages.insert_one({
            "_id": message_id,
            "session_id": session_id,
            "role": role,
            "content": content,
            "meta": meta or {},
            "created_at": now,
        })

        self.sessions.update_one(
            {"_id": session_id},
            {"$set": {"updated_at": now}},
        )

        return message_id

    def get_messages(self, session_id: str, limit: int = 10) -> List[Dict]:
        cursor = self.messages.find(
            {"session_id": session_id}
        ).sort("created_at", ASCENDING)

        messages = list(cursor)

        if limit and len(messages) > limit:
            messages = messages[-limit:]

        for msg in messages:
            msg["_id"] = str(msg["_id"])

        return messages

    def build_history_text(self, session_id: str, limit: int = 10) -> str:
        messages = self.get_messages(session_id=session_id, limit=limit)

        lines = []
        for msg in messages:
            role = msg.get("role", "user").capitalize()
            content = msg.get("content", "").strip()
            if content:
                lines.append(f"{role}: {content}")

        return "\n".join(lines)

    def list_sessions(self, limit: int = 20) -> List[Dict]:
        sessions = list(
            self.sessions.find().sort("updated_at", DESCENDING).limit(limit)
        )

        for session in sessions:    
            session["_id"] = str(session["_id"])

        return sessions

    def delete_session(self, session_id: str) -> bool:
        result = self.sessions.delete_one({"_id": session_id})
        self.messages.delete_many({"session_id": session_id})
        return result.deleted_count > 0