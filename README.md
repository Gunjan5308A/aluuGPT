# AluuGPT | Enterprise AI & Animation Platform

AluuGPT is a high-performance, enterprise-grade AI platform built with FastAPI. It is designed for seamless integration with OpenAI-compatible LLM providers and features a specialized pipeline for automated animation generation.

## 🧠 System Architecture & Mechanics

AluuGPT is built on a modular architecture that separates the conversational AI logic from the heavy computational tasks required for animation rendering.

### 1. Conversational Pipeline
The core chat experience uses an asynchronous flow to communicate with LLM providers. It includes a persistent memory layer backed by a user-scoped database table so each account keeps its own chat history.

### 2. Animation Pipeline
The animation engine is triggered by specific tokens in the user's message. It leverages a subprocess-based rendering model to generate high-quality video content without blocking the main application event loop.

> [!TIP]
> For a detailed deep-dive into how animations are generated, see [animation.md](/home/goodname/code/AluuGPT/animation.md).

## 🚀 Key Features

- **Advanced Chat Interface**: A premium, responsive UI with dark/light mode and micro-animations.
- **Multi-Model Support**: Easily switch between different LLM providers (Groq, Together AI, OpenAI, etc.) via `.env` configuration.
- **AI Animation Engine**: Generate dynamic animations directly from your prompts using a specialized rendering pipeline (triggered with the `[animation]` token).
- **Persistent Memory**: User-specific chat history stored in a database table.
- **Username Login**: New accounts use a username and password on top of the server database.
- **Mathematical Support**: Full LaTeX rendering for technical and scientific explanations via KaTeX.

## 🛠️ Tech Stack

- **Backend**: Python 3.10+, FastAPI, Uvicorn
- **Frontend**: HTML5, Vanilla CSS, Javascript
- **AI Integration**: OpenAI SDK (compatible with any OpenAI-style API)
- **Animation**: FFmpeg (for video encoding), Subprocess orchestration
- **Database**: PostgreSQL via `DATABASE_URL` for Vercel and server hosting

## 📦 Project Structure

```text
AluuGPT/
├── api/                # Core API entry points
├── data/               # Persistent database storage
├── static/             # Frontend assets (HTML, CSS, JS)
│   └── animations/     # Local storage for generated videos
├── utils/              # Backend logic (chat, animation, etc.)
├── main.py             # Main FastAPI application
├── animScript.py       # Core animation rendering script
└── .env.example        # Environment variable template
```

## ⚙️ Installation & Setup

### 1. Clone the Repository
```bash
git clone https://github.com/Gunjan5308A/aluuGPT.git
cd aluuGPT
```

### 2. Create a Virtual Environment
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Configure Environment Variables
Copy `.env.example` to `.env` and fill in your API keys:
```bash
cp .env.example .env
```
Ensure `BASE_URLS` includes the `/v1` suffix for OpenAI-compatible providers.
Set `DATABASE_URL` to a managed Postgres service such as Neon or Supabase.

### 5. Run Locally
```bash
./start.sh
```
The application will be available at `http://localhost:8000`.

## 🔐 Authentication

- Users sign up and log in with a username and password.
- Passwords are hashed with PBKDF2 before storage.
- Logged-in users receive an HttpOnly session cookie.
- Chat history is stored per user instead of in one shared session bucket.

## ☁️ Vercel Database Setup

To fit Vercel, use a serverless Postgres database:

1. Create a managed Postgres database, such as Neon or Supabase.
2. Copy its connection string into `DATABASE_URL`.
3. Deploy the app to Vercel with that environment variable set.
4. Keep `VERCEL=1` in the deployment environment so the app knows to use Vercel-safe paths.

The app requires `DATABASE_URL` and will use your server Postgres database.

## 🎨 UI Controls

- **Think Token**: Wraps thoughts in `<|think|>` tags for detailed reasoning.
- **Fast Token**: Triggers high-speed response modes.
- **Animation Token**: Requests the AI to generate a visual animation based on the prompt.
