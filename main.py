from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import os
from dotenv import load_dotenv
from utils.chat import process_user_message
from core.plugin.animGenPlugin import generate_animation

load_dotenv()

BASE_DIR = os.path.dirname(os.path.abspath(__file__))


app = FastAPI()

# Setup animation directory (use /tmp on Vercel)
IS_VERCEL = os.environ.get("VERCEL") == "1"
if IS_VERCEL:
    ANIMATION_DIR = "/tmp/animations"
    os.makedirs(ANIMATION_DIR, exist_ok=True)
else:
    ANIMATION_DIR = os.path.join(BASE_DIR, "static/animations")


# CORS configuration for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class ChatRequest(BaseModel):
    message: str
    user_id: str | None = None

@app.post("/chat")
async def chat_endpoint(request: ChatRequest):
    try:
        response = await process_user_message(request.message, request.user_id)
        return JSONResponse(content={"response": response})
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

class AnimationRequest(BaseModel):
    prompt: str
    user_id: str | None = None

@app.post("/generate_animation")
async def generate_animation_endpoint(request: AnimationRequest):
    try:
        video_path = await generate_animation(request.prompt, request.user_id)
        video_url = f"/static/animations/{os.path.basename(video_path)}"
        return JSONResponse(content={"video_url": video_url})
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Serve static assets (frontend)
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

@app.get("/")
async def read_index():
    return FileResponse(os.path.join(BASE_DIR, 'static/index.html'))

app.mount("/static", StaticFiles(directory=os.path.join(BASE_DIR, "static")), name="static")

# Special mount for animations if on Vercel (since static/animations is read-only)
if IS_VERCEL:
    app.mount("/static/animations", StaticFiles(directory=ANIMATION_DIR), name="animations_tmp")


