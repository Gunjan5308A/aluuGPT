"""
Chat History & Embedding Management
Stores user conversations in SQLite with semantic embeddings for memory
"""

import json
from datetime import datetime
from typing import List, Dict, Optional
from sqlalchemy import create_engine, Column, String, DateTime, Float, Integer, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sentence_transformers import SentenceTransformer
from core.config import settings

Base = declarative_base()


class ChatMessage(Base):
    """Chat message storage model"""

    __tablename__ = "chat_messages"

    id = Column(Integer, primary_key=True)
    session_id = Column(String(255), nullable=False, index=True)
    role = Column(String(20), nullable=False)  # user, assistant
    content = Column(Text, nullable=False)
    mode = Column(String(20), nullable=False)  # think, fast, animation
    timestamp = Column(DateTime, default=datetime.utcnow, index=True)
    embedding_text = Column(Text, nullable=True)

    def __repr__(self):
        return f"<ChatMessage(role={self.role}, mode={self.mode}, timestamp={self.timestamp})>"


class ChatHistoryManager:
    """Manage chat history with embeddings"""

    def __init__(self):
        self.engine = create_engine(f"sqlite:///{settings.database_path}")
        Base.metadata.create_all(self.engine)
        self.Session = sessionmaker(bind=self.engine)

        # Load embedding model
        if settings.enable_chat_history:
            self.embedding_model = SentenceTransformer(settings.embedding_model)
        else:
            self.embedding_model = None

    def add_message(
        self,
        session_id: str,
        role: str,
        content: str,
        mode: str = "normal",
    ) -> ChatMessage:
        """Add a message to chat history"""
        session = self.Session()
        try:
            message = ChatMessage(
                session_id=session_id,
                role=role,
                content=content,
                mode=mode,
                embedding_text=content[:500],  # Store first 500 chars for embedding
            )
            session.add(message)
            session.commit()
            return message
        finally:
            session.close()

    def get_session_history(
        self, session_id: str, limit: int = 20
    ) -> List[Dict[str, str]]:
        """Get recent chat history for a session"""
        session = self.Session()
        try:
            messages = (
                session.query(ChatMessage)
                .filter(ChatMessage.session_id == session_id)
                .order_by(ChatMessage.timestamp.desc())
                .limit(limit)
                .all()
            )

            result = []
            for msg in reversed(messages):
                result.append(
                    {
                        "role": msg.role,
                        "content": msg.content,
                        "mode": msg.mode,
                        "timestamp": msg.timestamp.isoformat(),
                    }
                )
            return result
        finally:
            session.close()

    def get_context_summary(
        self, session_id: str, max_tokens: int = 2000
    ) -> str:
        """Get context summary for reducing token usage"""
        session = self.Session()
        try:
            messages = (
                session.query(ChatMessage)
                .filter(ChatMessage.session_id == session_id)
                .order_by(ChatMessage.timestamp.desc())
                .limit(10)
                .all()
            )

            context_parts = []
            total_tokens = 0

            for msg in reversed(messages):
                text = f"{msg.role.upper()}: {msg.content}"
                tokens = len(text.split())

                if total_tokens + tokens > max_tokens:
                    break

                context_parts.append(text)
                total_tokens += tokens

            return "\n\n".join(context_parts)
        finally:
            session.close()

    def search_similar_messages(
        self, session_id: str, query: str, top_k: int = 5
    ) -> List[Dict]:
        """Search for similar past messages using embeddings"""
        if not self.embedding_model:
            return []

        session = self.Session()
        try:
            messages = (
                session.query(ChatMessage)
                .filter(ChatMessage.session_id == session_id)
                .all()
            )

            # Generate embedding for query
            query_embedding = self.embedding_model.encode(query)

            # Score and sort messages
            scored_messages = []
            for msg in messages:
                if msg.embedding_text:
                    msg_embedding = self.embedding_model.encode(msg.embedding_text)
                    score = (
                        query_embedding @ msg_embedding
                    )  # Cosine similarity via dot product
                    scored_messages.append((score, msg))

            # Return top-k similar messages
            scored_messages.sort(key=lambda x: x[0], reverse=True)
            return [
                {
                    "role": msg.role,
                    "content": msg.content,
                    "similarity": float(score),
                }
                for score, msg in scored_messages[:top_k]
            ]
        finally:
            session.close()

    def clear_session(self, session_id: str):
        """Clear all messages for a session"""
        session = self.Session()
        try:
            session.query(ChatMessage).filter(
                ChatMessage.session_id == session_id
            ).delete()
            session.commit()
        finally:
            session.close()


# Global instance
chat_manager = ChatHistoryManager()
