import os
import openai
from typing import List, Tuple
from dotenv import find_dotenv, load_dotenv

load_dotenv(find_dotenv())

def _parse_csv(env_var: str) -> List[str]:
    val = os.getenv(env_var, "")
    return [v.strip() for v in val.split(",") if v.strip()]

MODELS = _parse_csv("MODELS") or [os.getenv("PRIMARY_MODEL", "gpt-4")]
API_KEYS = _parse_csv("API_KEYS") or [os.getenv("PRIMARY_API_KEY")]
BASE_URLS = _parse_csv("BASE_URLS") or [os.getenv("PRIMARY_BASE_URL", "https://api.openai.com/v1")]

def get_openai_client(index: int = 0):
    client = openai.OpenAI(
        api_key=API_KEYS[index] if index < len(API_KEYS) else API_KEYS[0],
        base_url=BASE_URLS[index] if index < len(BASE_URLS) else BASE_URLS[0]
    )
    return client

async def call_llm(messages: List[dict], model_index: int = 0, temperature: float = 0.7) -> str:
    client = get_openai_client(model_index)
    model_name = MODELS[model_index] if model_index < len(MODELS) else MODELS[0]
    
    response = client.chat.completions.create(
        model=model_name,
        messages=messages,
        temperature=temperature,
        max_tokens=512,
    )
    return response.choices[0].message.content

def detect_tokens(text: str) -> Tuple[bool, bool, bool]:
    return "<|think|>" in text, "<|fast|>" in text, "[animation]" in text

async def process_user_message(message: str, user_id: str | None = None) -> str:
    from .embed import add_message, get_recent_context, search_memory
    
    think, fast, animation = detect_tokens(message)
    
    # Temperature based on tokens
    temp = 0.7
    if think: temp = 0.2
    if fast: temp = 1.0
    
    # 1. RAG: Search memory for relevant past info
    relevant_past = search_memory(message, limit=3)
    
    # 2. Get recent history for flow
    recent_history = get_recent_context()
    
    # 3. Build System Prompt
    system_msg = (
        "You are AluuGPT, a high-performance enterprise AI. "
        "Your responses must be clean, scannable, and high-impact. "
        "Use bullet points for lists, and for each point, provide exactly one sentence of insightful explanation. "
        "Avoid long paragraphs and fluff, but ensure every key term is clearly defined in its context. "
        "Focus on 'dense' but readable information. "
    )
    if relevant_past:
        system_msg += "Here is some relevant context from previous conversations:\n" + "\n".join(relevant_past)
    
    messages = [{"role": "system", "content": system_msg}]
    
    # Add history (simple parse)
    valid_roles = {"system", "user", "assistant"}
    for line in recent_history.split("\n"):
        if ":" in line:
            role_part, content = line.split(":", 1)
            role = role_part.strip().lower()
            if role in valid_roles:
                messages.append({"role": role, "content": content.strip()})
            else:
                # If the role is invalid, treat the whole line as content from the last role
                if messages:
                    messages[-1]["content"] += "\n" + line.strip()
            
    messages.append({"role": "user", "content": message})
    
    # 4. Call Model (Using first model for main chat)
    try:
        response = await call_llm(messages, model_index=0, temperature=temp)
    except Exception as e:
        return f"System Error: Unable to reach the AI model. Please ensure your .env file has a valid API_KEY. (Detail: {str(e)})"
    
    # Strip <think>...</think> or <|think|>...</|think|> blocks
    import re
    response = re.sub(r'<\|?think\|?>.*?</\|?think\|?>', '', response, flags=re.DOTALL).strip()
    
    # 5. Store both
    add_message(user_id, "user", message)
    add_message(user_id, "assistant", response)
    
    return response
