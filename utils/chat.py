import os
from typing import List

import openai
import tiktoken
from dotenv import load_dotenv

from .database import add_history, get_history

load_dotenv()

# --- Config ---
MODELS = [m.strip() for m in os.getenv("MODELS", "llama-3.3-70b-versatile").split(",") if m.strip()]
API_KEYS = [k.strip() for k in os.getenv("API_KEYS", "").split(",") if k.strip()]
BASE_URLS = [u.strip() for u in os.getenv("BASE_URLS", "https://api.openai.com/v1").split(",") if u.strip()]


def get_client(index: int = 0):
    api_key = API_KEYS[index] if index < len(API_KEYS) else os.getenv("OPENAI_API_KEY", "").strip()
    base_url = BASE_URLS[index] if index < len(BASE_URLS) else BASE_URLS[0]
    if not api_key:
        raise RuntimeError("No API key configured. Set API_KEYS or OPENAI_API_KEY.")
    return openai.OpenAI(
        api_key=api_key,
        base_url=base_url,
    )


def count_tokens(messages: List[dict], model: str = "gpt-3.5-turbo") -> int:
    try:
        encoding = tiktoken.encoding_for_model(model)
    except (KeyError, ValueError):
        encoding = tiktoken.get_encoding("cl100k_base")

    num_tokens = 0
    for message in messages:
        num_tokens += 4
        for key, value in message.items():
            num_tokens += len(encoding.encode(str(value)))
    num_tokens += 2
    return num_tokens


async def process_user_message(message: str, user_id: str) -> str:
    client = get_client(0)
    model = MODELS[0]

    history = get_history(user_id, limit=5)

    system_prompt = (
        "You are AluuGPT, a high-performance enterprise AI. "
        "Keep responses clean, dense, and insightful. Use bullet points for technical explanations."
    )

    system_msg = {"role": "system", "content": system_prompt}
    user_msg = {"role": "user", "content": message}

    while len(history) > 0:
        msgs = [system_msg] + history + [user_msg]
        if count_tokens(msgs, model) <= 400:
            break
        history.pop(0)

    msgs = [system_msg] + history + [user_msg]

    try:
        response = client.chat.completions.create(
            model=model,
            messages=msgs,
            temperature=0.2,
            max_tokens=1024,
            repetition_penalty=1.3
        ).choices[0].message.content
    except Exception as e:
        return f"Error: {str(e)}"

    add_history(user_id, "user", message)
    add_history(user_id, "assistant", response)

    return response
