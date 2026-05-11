import os

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from utils.animation import run_animation_script
from utils.chat import process_user_message
from utils.database import (
    create_session,
    create_user,
    delete_session,
    get_history,
    get_session,
    get_user_by_id,
    get_user_by_username,
)
from utils.security import build_password_record, verify_password

app = FastAPI(title="AluuGPT")

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
app.mount("/static", StaticFiles(directory=os.path.join(BASE_DIR, "static")), name="static")


SESSION_COOKIE = "aluu_session"
SESSION_MAX_AGE = 60 * 60 * 24 * 14


class ChatRequest(BaseModel):
    message: str | None = None
    prompt: str | None = None


class AuthRequest(BaseModel):
    username: str
    password: str


def _normalize_username(username: str) -> str:
    return username.strip().lower()


def _get_current_user(request: Request):
    token = request.cookies.get(SESSION_COOKIE)
    if not token:
        return None

    session = get_session(token)
    if not session:
        return None

    return get_user_by_id(session["user_id"])


def _set_session_cookie(response: JSONResponse, token: str) -> None:
    response.set_cookie(
        key=SESSION_COOKIE,
        value=token,
        httponly=True,
        samesite="lax",
        secure=os.environ.get("VERCEL") == "1",
        max_age=SESSION_MAX_AGE,
        path="/",
    )


def _serialize_user(user: dict) -> dict:
    return {
        "id": user["id"],
        "username": user["username"],
        "created_at": user.get("created_at"),
    }


@app.get("/")
async def index():
    try:
        with open(os.path.join(BASE_DIR, "static/index.html"), "r") as f:
            return HTMLResponse(content=f.read())
    except Exception as e:
        return JSONResponse(status_code=500, content={"detail": str(e)})


@app.get("/auth/me")
async def auth_me(request: Request):
    user = _get_current_user(request)
    if not user:
        return {"authenticated": False}
    return {"authenticated": True, "user": _serialize_user(user)}


@app.post("/auth/register")
async def register(payload: AuthRequest):
    username = _normalize_username(payload.username)
    if len(username) < 3:
        return JSONResponse(status_code=400, content={"detail": "Username must be at least 3 characters"})
    if len(payload.password) < 8:
        return JSONResponse(status_code=400, content={"detail": "Password must be at least 8 characters"})
    if not username.replace("_", "").replace("-", "").isalnum():
        return JSONResponse(status_code=400, content={"detail": "Username can only include letters, numbers, dash, and underscore"})

    if get_user_by_username(username):
        return JSONResponse(status_code=409, content={"detail": "That username is already taken"})

    password_salt, password_hash = build_password_record(payload.password)
    user = create_user(username, password_hash, password_salt)
    session = create_session(user["id"])
    response = JSONResponse(content={"user": _serialize_user(user)})
    _set_session_cookie(response, session["token"])
    return response


@app.post("/auth/login")
async def login(payload: AuthRequest):
    username = _normalize_username(payload.username)
    user = get_user_by_username(username)
    if not user or not verify_password(payload.password, user["password_hash"]):
        return JSONResponse(status_code=401, content={"detail": "Invalid username or password"})

    session = create_session(user["id"])
    response = JSONResponse(content={"user": _serialize_user(user)})
    _set_session_cookie(response, session["token"])
    return response


@app.post("/auth/logout")
async def logout(request: Request):
    token = request.cookies.get(SESSION_COOKIE)
    if token:
        delete_session(token)
    response = JSONResponse(content={"ok": True})
    response.delete_cookie(key=SESSION_COOKIE, path="/")
    return response


@app.get("/history")
async def history(request: Request):
    user = _get_current_user(request)
    if not user:
        return JSONResponse(status_code=401, content={"detail": "Login required"})
    return {"messages": get_history(user["id"], limit=20)}


@app.post("/chat")
async def chat(req: ChatRequest, request: Request):
    message = req.message or req.prompt
    if not message:
        return JSONResponse(status_code=400, content={"detail": "Message or prompt required"})
    user = _get_current_user(request)
    if not user:
        return JSONResponse(status_code=401, content={"detail": "Login required"})
    response = await process_user_message(message, user["id"])
    return {"response": response}


@app.post("/generate_animation")
async def animation(req: ChatRequest, request: Request):
    prompt = req.prompt or req.message
    if not prompt:
        return JSONResponse(status_code=400, content={"detail": "Prompt or message required"})
    user = _get_current_user(request)
    if not user:
        return JSONResponse(status_code=401, content={"detail": "Login required"})
    video_url = await run_animation_script(prompt)
    if video_url:
        return {"video_url": video_url}
    return JSONResponse(status_code=500, content={"detail": "Animation failed"})


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=int(os.environ.get("PORT", 8000)))
