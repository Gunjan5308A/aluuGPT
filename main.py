import os
from fastapi import FastAPI, Request
from fastapi.responses import FileResponse, JSONResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from utils.chat import process_user_message
from utils.animation import run_animation_script, ANIMATION_OUTPUT_DIR

app = FastAPI(title="AluuGPT")

# Statics
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
app.mount("/static", StaticFiles(directory=os.path.join(BASE_DIR, "static")), name="static")

# Vercel /tmp mount for animations
IS_VERCEL = os.environ.get("VERCEL") == "1"
if IS_VERCEL:
    app.mount("/static/animations", StaticFiles(directory="/tmp/animations"), name="animations_tmp")

class ChatRequest(BaseModel):
    message: str | None = None
    prompt: str | None = None

@app.get("/")
async def index():
    try:
        with open(os.path.join(BASE_DIR, "static/index.html"), "r") as f:
            content = f.read()
        return HTMLResponse(content=content)
    except Exception as e:
        return JSONResponse(status_code=500, content={"detail": str(e)})

@app.post("/chat")
async def chat(req: ChatRequest):
    message = req.message or req.prompt
    if not message:
        return JSONResponse(status_code=400, content={"detail": "Message or prompt required"})
    response = await process_user_message(message)
    return {"response": response}

@app.post("/generate_animation")
async def animation(req: ChatRequest):
    prompt = req.prompt or req.message
    if not prompt:
        return JSONResponse(status_code=400, content={"detail": "Prompt or message required"})
    video_url = await run_animation_script(prompt)
    if video_url:
        return {"video_url": video_url}
    return JSONResponse(status_code=500, content={"detail": "Animation failed"})

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=int(os.environ.get("PORT", 8000)))
