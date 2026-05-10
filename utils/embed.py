from openai import OpenAI
from sqlalchemy import create_engine, Column, Integer, String, LargeBinary, Text, select, desc
from sqlalchemy.orm import declarative_base, sessionmaker
import os
import numpy as np
from typing import List

# Setup OpenAI client for embeddings
client = OpenAI(api_key=os.getenv("API_KEYS").split(',')[0] if os.getenv("API_KEYS") else None)
embedding_model_name = os.getenv("EMBEDDING_MODEL", "text-embedding-3-small")

def _embed_text(text: str) -> np.ndarray:
    """Get embeddings via OpenAI API instead of local model."""
    try:
        response = client.embeddings.create(
            input=[text.replace("\n", " ")],
            model=embedding_model_name
        )
        return np.array(response.data[0].embedding, dtype=np.float32)
    except Exception as e:
        print(f"Embedding error: {e}")
        # Fallback to zero vector if API fails
        return np.zeros(1536, dtype=np.float32) # Default size for text-embedding-3-small


# Database setup
# Use /tmp on Vercel for writable database
IS_VERCEL = os.environ.get("VERCEL") == "1"
if IS_VERCEL:
    db_path = "/tmp/chat_history.db"
else:
    db_path = os.getenv("DATABASE_PATH", "./data/chat_history.db")

os.makedirs(os.path.dirname(db_path), exist_ok=True)
engine = create_engine(f"sqlite:///{db_path}")
Base = declarative_base()
Session = sessionmaker(bind=engine)


class Message(Base):
    __tablename__ = "messages"
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(String, nullable=True)
    role = Column(String, nullable=False)
    content = Column(Text, nullable=False)
    embedding = Column(LargeBinary, nullable=False)

Base.metadata.create_all(engine)



def add_message(user_id: str | None, role: str, content: str):
    emb = _embed_text(content)
    with Session() as session:
        msg = Message(user_id=user_id, role=role, content=content, embedding=emb.tobytes())
        session.add(msg)
        session.commit()

def search_memory(query: str, limit: int = 5) -> List[str]:
    """Perform a vector search to find relevant context from the embedding table."""
    query_emb = _embed_text(query)
    
    with Session() as session:
        rows = session.execute(select(Message)).scalars().all()
        if not rows:
            return []
            
        # Calculate cosine similarities (simple loop for SQLite)
        results = []
        for row in rows:
            row_emb = np.frombuffer(row.embedding, dtype=np.float32)
            # Re-ensure shapes match if model changed
            if row_emb.shape == query_emb.shape:
                similarity = np.dot(query_emb, row_emb) / (np.linalg.norm(query_emb) * np.linalg.norm(row_emb))
                results.append((similarity, row))
        
        # Sort by similarity
        results.sort(key=lambda x: x[0], reverse=True)
        
        # Return the top N formatted strings
        context = []
        for sim, row in results[:limit]:
            if sim > 0.4: # Only include if reasonably relevant
                context.append(f"{row.role}: {row.content}")
        return context

def get_recent_context(max_tokens: int = 2000) -> str:
    """Fallback: get recent conversation for immediate context."""
    with Session() as session:
        rows = session.execute(select(Message).order_by(desc(Message.id)).limit(10)).scalars().all()
        context_parts = []
        for msg in reversed(rows):
            context_parts.append(f"{msg.role}: {msg.content}")
        return "\n".join(context_parts)
