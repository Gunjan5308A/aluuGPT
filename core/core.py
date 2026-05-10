from openai import OpenAI
from dotenv import load_dotenv
import os

load_dotenv() 
api_key = os.getenv("OPENAI_API_KEY")
base_url = os.getenv("OPENAI_BASE_URL")
model_name = os.getenv("OPENAI_MODEL_NAME")
model_timeout = int(os.getenv("OPENAI_MODEL_TIMEOUT", "30"))

client = OpenAI(api_key=api_key, base_url=base_url)

response = client.chat.completions.create(
    base_url=base_url,
    model=model_name,
    messages=[
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": "Hello!"}
    ],
    timeout=model_timeout
)

print(response.choices[0].message.content)
