import os
import openai
import sqlite3
from typing import List, Tuple
from dotenv import load_dotenv

load_dotenv()

# --- Config ---
MODELS = [m.strip() for m in os.getenv("MODELS", "llama-3.3-70b-versatile").split(",") if m.strip()]
API_KEYS = [k.strip() for k in os.getenv("API_KEYS", "").split(",") if k.strip()]
BASE_URLS = [u.strip() for u in os.getenv("BASE_URLS", "https://api.openai.com/v1").split(",") if u.strip()]

DB_PATH = "/tmp/chat_history.db" if os.getenv("VERCEL") == "1" else "./data/history.db"
os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)

def init_db():
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute("CREATE TABLE IF NOT EXISTS history (id INTEGER PRIMARY KEY, session_id TEXT, role TEXT, content TEXT)")

init_db()

def get_client(index: int = 0):
    return openai.OpenAI(
        api_key=API_KEYS[index] if index < len(API_KEYS) else API_KEYS[0],
        base_url=BASE_URLS[index] if index < len(BASE_URLS) else BASE_URLS[0]
    )

async def process_user_message(message: str, session_id: str = "default") -> str:
    client = get_client(0)
    model = MODELS[0]
    
    # 1. Get Context Window (Last 10 messages)
    history = []
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.execute("SELECT role, content FROM history WHERE session_id = ? ORDER BY id DESC LIMIT 10", (session_id,))
        history = [{"role": r, "content": c} for r, c in reversed(cursor.fetchall())]
    
    # 2. Build Messages
    system_prompt = (
        "You are AluuGPT, a high-performance enterprise AI. "
        "Keep responses clean, dense, and insightful. Use bullet points for technical explanations."
    )
    msgs = [{"role": "system", "content": system_prompt}] + history + [{"role": "user", "content": message}]
    
    # 3. Call LLM
    try:
        response = client.chat.completions.create(
            model=model,
            messages=msgs,
            temperature=0.2,
            max_tokens=1024
        ).choices[0].message.content
    except Exception as e:
        return f"Error: {str(e)}"
    
    # 4. Save to History
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute("INSERT INTO history (session_id, role, content) VALUES (?, ?, ?)", (session_id, "user", message))
        conn.execute("INSERT INTO history (session_id, role, content) VALUES (?, ?, ?)", (session_id, "assistant", response))
    
    return response
